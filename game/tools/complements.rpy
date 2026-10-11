## complements.rpy
## Hub "Herramientas": punto de entrada a las herramientas dev del template.
##
## Es dev-only: el botón aparece en el menú principal solo si
## config.developer = True.
##
## Las herramientas son PLUGINS autocontenidos: cada una es una carpeta en
## game/tools/plugins/<id>/ con un tool.json (metadatos) y su propio .rpy
## (el screen que nombra el manifiesto). El hub las descubre solo; no hay
## que registrar nada a mano.
##
## Ver game/tools/plugins/README.md para escribir tu propia herramienta.

init python:
    import json as _pl_json
    import builtins as _pl_builtins

    _PL_PLUGINS_DIR = "tools/plugins/"
    _PL_PLUGINS_LOG = "tools.plugins"

    # Version de la API de plugins; un tool.json puede exigir `min_version`.
    tools_api_version = "1.0"

    def _pl_ver(v):
        """'1.2.3' -> (1, 2, 3); None si no es una version valida."""
        try:
            return tuple(int(x) for x in str(v).split("."))
        except Exception:
            return None

    def _pl_diag(diagnosticos, id_, ruta, motivo, fatal=True):
        diagnosticos.append({
            "id": id_, "ruta": ruta, "motivo": motivo, "fatal": fatal})

    def pl_plugins():
        """Descubre las herramientas en tools/plugins/ y devuelve
        (herramientas, diagnosticos).

        Nunca descarta un plugin en silencio: todo problema (JSON roto, screen
        inexistente, id duplicado, icono faltante, etc.) queda en `diagnosticos`,
        con `fatal` indicando si el plugin se excluyo de la lista.

        Cada herramienta: id, titulo, descripcion, autor, version, categoria,
        orden, icono, palabras_clave, capturas, screen, args, modulo,
        min_version. Ordenadas por (orden, titulo)."""
        herramientas = []
        diagnosticos = []
        ids = set()

        for f in sorted(renpy.list_files()):
            if not f.startswith(_PL_PLUGINS_DIR) or not f.endswith("/tool.json"):
                continue
            carpeta = f[len(_PL_PLUGINS_DIR):-len("tool.json")].rstrip("/")
            if "/" in carpeta or not carpeta:
                continue  # solo plugins en el primer nivel

            try:
                with renpy.file(f) as fh:
                    datos = _pl_json.loads(fh.read().decode("utf-8"))
            except Exception as e:
                renpy.log("%s: tool.json ilegible en %s: %s" % (_PL_PLUGINS_LOG, f, e))
                _pl_diag(diagnosticos, carpeta, f, "JSON ilegible: %s" % e)
                continue

            # Ojo: en el store de Ren'Py `dict` es RevertableDict; usamos el
            # builtin para que json.loads (dict normal) pase la validacion.
            if not isinstance(datos, _pl_builtins.dict):
                _pl_diag(diagnosticos, carpeta, f, "tool.json no es un objeto JSON")
                continue

            id_ = str(datos.get("id") or carpeta)
            titulo = str(datos.get("titulo") or carpeta)
            screen = str(datos.get("screen") or "")
            categoria = str(datos.get("categoria") or "General")
            orden = datos.get("orden", 0)
            if not isinstance(orden, _pl_builtins.int):
                orden = 0
            min_version = str(datos.get("min_version") or "")

            if id_ in ids:
                _pl_diag(diagnosticos, id_, f, "id duplicado: '%s'" % id_)
                continue
            if not screen:
                _pl_diag(diagnosticos, id_, f, "falta 'screen'")
                continue
            if not renpy.has_screen(screen):
                _pl_diag(diagnosticos, id_, f, "no existe el screen '%s'" % screen)
                continue

            ids.add(id_)

            palabras = datos.get("palabras_clave") or []
            if not isinstance(palabras, _pl_builtins.list):
                palabras = []

            args = datos.get("args") or {}
            if not isinstance(args, _pl_builtins.dict):
                _pl_diag(diagnosticos, id_, f, "'args' no es un objeto; se ignora", fatal=False)
                args = {}

            icono = str(datos.get("icono") or "")
            icono_ruta = ""
            if icono:
                ruta = "%s%s/%s" % (_PL_PLUGINS_DIR, carpeta, icono)
                if renpy.loadable(ruta):
                    icono_ruta = ruta
                else:
                    _pl_diag(diagnosticos, id_, f, "icono no cargable: %s" % icono, fatal=False)

            if min_version:
                v_req, v_api = _pl_ver(min_version), _pl_ver(tools_api_version)
                if v_req and v_api and v_req > v_api:
                    _pl_diag(diagnosticos, id_, f,
                             "requiere API >= %s (actual %s)" % (min_version, tools_api_version),
                             fatal=False)

            capturas = []
            for cap in (datos.get("capturas") or []):
                if not isinstance(cap, _pl_builtins.str):
                    continue
                ruta = "%s%s/%s" % (_PL_PLUGINS_DIR, carpeta, cap)
                if renpy.loadable(ruta):
                    capturas.append(ruta)

            herramientas.append({
                "id": id_,
                "dir": carpeta,
                "titulo": titulo,
                "descripcion": str(datos.get("descripcion") or ""),
                "autor": str(datos.get("autor") or ""),
                "version": str(datos.get("version") or ""),
                "categoria": categoria,
                "orden": orden,
                "icono": icono_ruta,
                "palabras_clave": [str(p) for p in palabras],
                "capturas": capturas,
                "screen": screen,
                "args": args,
                "modulo": str(datos.get("modulo") or ""),
                "min_version": min_version,
            })

        for e in herramientas:
            _pl_aplicar_metadata(e)
        herramientas.sort(key=lambda d: (d["orden"], d["titulo"].lower()))
        return herramientas, diagnosticos

    def pl_herramientas():
        """Lista de herramientas visibles en el hub."""
        return pl_plugins()[0]

    def pl_diagnosticos():
        """Problemas de plugins detectados (fatales y warnings)."""
        return pl_plugins()[1]

    # ======================================================================
    # Hub: búsqueda, categorías y habilitar/deshabilitar (persistente).
    # ======================================================================

    def pl_coincide(t, texto):
        """True si la herramienta coincide con el texto de búsqueda (busca
        también en los metadatos traducidos, para el idioma actual)."""
        texto = (texto or "").strip().lower()
        if not texto:
            return True
        campos = (
            t["titulo"], _(t["titulo"]),
            t["descripcion"], _(t["descripcion"]),
            t["categoria"], _(t["categoria"]),
            " ".join(t["palabras_clave"]), t["id"])
        return any(texto in str(c).lower() for c in campos)

    def pl_tool_habilitada(id_):
        return id_ not in (persistent.pl_deshabilitadas or [])

    def pl_tool_alternar(id_):
        """Muestra/oculta una herramienta en el hub (persistente)."""
        actual = list(persistent.pl_deshabilitadas or [])
        if id_ in actual:
            actual.remove(id_)
        else:
            actual.append(id_)
        persistent.pl_deshabilitadas = actual

    def pl_tool_por_id(id_):
        """Devuelve el dict de una herramienta por su id (o None)."""
        for t in pl_plugins()[0]:
            if t["id"] == id_:
                return t
        return None

    # ======================================================================
    # Plugins Python (.py): un plugin puede declarar `"modulo": "nombre"` y
    # poner `nombre.py` en su carpeta. El hub agrega la carpeta al import path
    # y llama, si existen, los hooks:
    #   setup(tool)  -> una vez, al init
    #   open(tool)   -> al abrir la herramienta
    #   close(tool)  -> al cerrarla (detectado)
    #   metadata()   -> dict que sobreescribe campos cosmeticos del manifiesto
    # ======================================================================
    import importlib as _pl_importlib

    _PL_PLUGIN_MODULOS = {}     # id -> modulo importado (o None)
    _PL_PLUGIN_SETUP = set()    # ids con setup() ya llamado
    _PL_TOOL_ABIERTA = None     # herramienta abierta (dict) o None

    def _pl_cargar_modulo(tool):
        """Importa el .py declarado por el plugin (una vez por id)."""
        id_ = tool["id"]
        if id_ in _PL_PLUGIN_MODULOS:
            return _PL_PLUGIN_MODULOS[id_]
        mod = None
        nombre = tool.get("modulo") or ""
        if nombre:
            try:
                renpy.add_python_directory("%s%s/" % (_PL_PLUGINS_DIR, tool["dir"]))
                mod = _pl_importlib.import_module(nombre)
            except Exception as e:
                renpy.log("%s: no se pudo importar '%s' (%s): %s"
                          % (_PL_PLUGINS_LOG, nombre, id_, e))
        _PL_PLUGIN_MODULOS[id_] = mod
        return mod

    def _pl_aplicar_metadata(e):
        """Aplica metadata() del modulo (sobreescribe campos cosmeticos)."""
        mod = _PL_PLUGIN_MODULOS.get(e["id"])
        if mod is None:
            return
        try:
            md = getattr(mod, "metadata", None)
            md = md() if callable(md) else md
        except Exception as ex:
            renpy.log("%s: metadata() de '%s' fallo: %s" % (_PL_PLUGINS_LOG, e["id"], ex))
            return
        if isinstance(md, _pl_builtins.dict):
            for k in ("titulo", "descripcion", "autor", "version",
                      "categoria", "palabras_clave", "orden"):
                if k in md:
                    e[k] = md[k]

    def _pl_llamar(mod, nombre, *args):
        """Llama un hook opcional del modulo; los errores van al log."""
        hook = getattr(mod, nombre, None) if mod is not None else None
        if callable(hook):
            try:
                hook(*args)
            except Exception as e:
                renpy.log("%s: %s.%s() fallo: %s"
                          % (_PL_PLUGINS_LOG, getattr(mod, "__name__", "?"), nombre, e))

    def _pl_llamar_cierre():
        global _PL_TOOL_ABIERTA
        tool = _PL_TOOL_ABIERTA
        _PL_TOOL_ABIERTA = None
        if tool is not None:
            _pl_llamar(_PL_PLUGIN_MODULOS.get(tool["id"]), "close", tool)

    def _pl_vigilar_cierre():
        """Periodic: si la herramienta abierta ya no esta, llama close()."""
        if _PL_TOOL_ABIERTA is not None and not renpy.get_screen(_PL_TOOL_ABIERTA["screen"]):
            _pl_llamar_cierre()

    def pl_abrir(tool):
        """Abre una herramienta: cierra la anterior, corre open() y muestra el screen."""
        global _PL_TOOL_ABIERTA
        _pl_llamar_cierre()
        mod = _PL_PLUGIN_MODULOS.get(tool["id"]) or _pl_cargar_modulo(tool)
        _pl_llamar(mod, "open", tool)
        _PL_TOOL_ABIERTA = tool
        renpy.show_screen(tool["screen"], **tool["args"])


init 999 python:
    # Carga los modulos .py de los plugins y llama setup() una vez por cada uno.
    for _t in pl_plugins()[0]:
        if _t.get("modulo") and _t["id"] not in _PL_PLUGIN_SETUP:
            _mod = _pl_cargar_modulo(_t)
            if _mod is not None:
                _pl_llamar(_mod, "setup", _t)
            _PL_PLUGIN_SETUP.add(_t["id"])

    # Vigila el cierre de la herramienta abierta (para el hook close()).
    if _pl_vigilar_cierre not in config.periodic_callbacks:
        config.periodic_callbacks.append(_pl_vigilar_cierre)


screen complements():
    tag menu
    modal True
    zorder 200

    default busqueda = ""
    default cat = ""
    default ver_ocultas = False

    # Volver al menú principal (el hub se abre desde allí).
    key "K_ESCAPE" action ShowMenu("main_menu")

    # Mismo fondo animado que el menú principal.
    add gui.main_menu_background

    $ herramientas, diagnosticos = pl_plugins()
    $ categorias = sorted({t["categoria"] for t in herramientas})
    $ visibles = [
        t for t in herramientas
        if (not cat or t["categoria"] == cat)
        and (ver_ocultas or pl_tool_habilitada(t["id"]))
        and pl_coincide(t, busqueda)
    ]

    # ----- Panel izquierdo: búsqueda, categorías y opciones -----
    frame:
        style "main_menu_frame"

        vbox:
            style_prefix "main_navigation"
            xpos gui.navigation_xpos
            xoffset -50
            yalign 0.0
            yoffset 24
            spacing 5

            text _("Herramientas") style "complements_title"

            frame:
                style "pl_search_frame"
                input:
                    value ScreenVariableInputValue("busqueda")
                    style "pl_search"
                    length 40

            for c in [""] + categorias:
                textbutton (_(c) if c else _("Todas")):
                    style "main_navigation_button"
                    text_style "main_navigation_button_text"
                    selected (cat == c)
                    action SetScreenVariable("cat", c)

            textbutton (_("Ocultar las ocultas") if ver_ocultas else _("Mostrar ocultas")):
                style "main_navigation_button"
                text_style "main_navigation_button_text"
                selected ver_ocultas
                action SetScreenVariable("ver_ocultas", not ver_ocultas)

            textbutton _("Back"):
                style "main_navigation_button"
                text_style "main_navigation_button_text"
                action ShowMenu("main_menu")

    # ----- Panel derecho: grilla de tarjetas + diagnóstico -----
    frame:
        style "complements_detail"
        xpos 340
        ypos 24
        xsize 900
        ysize 672

        vbox:
            spacing 8

            if not visibles:
                text _("No hay herramientas que coincidan.") style "complements_detail_desc"

            vpgrid:
                cols 3
                spacing 12
                xsize 862
                ysize 540
                scrollbars "vertical"
                mousewheel True
                draggable True

                for t in visibles:
                    use pl_card(t)

            if diagnosticos:
                text _("Diagnóstico") style "complements_section"
                for d in diagnosticos:
                    $ _col = "#cc3333" if d["fatal"] else "#a9791c"
                    text "[d['id']]: [d['motivo']]" style "complements_detail_desc" size 13 color _col


# Tarjeta de una herramienta en la grilla del hub.
screen pl_card(t):
    $ habilitada = pl_tool_habilitada(t["id"])
    $ _img = t["icono"] or (t["capturas"][0] if t["capturas"] else "")

    frame:
        style "pl_card"

        vbox:
            spacing 4

            button:
                style "pl_card_open"
                action Function(pl_abrir, t)

                vbox:
                    spacing 4
                    if _img:
                        add _img at pl_thumb xalign 0.5
                    text _(t["titulo"]) style "pl_card_title" xalign 0.5

            text _(t["descripcion"]) style "pl_card_desc" xmaximum 250

            textbutton (_("Mostrar") if not habilitada else _("Ocultar")):
                style "pl_card_toggle"
                action Function(pl_tool_alternar, t["id"])


# Shell reutilizable para herramientas simples: fondo del menú, título, ESC y
# botón "Volver" al hub, y el frame de tarjeta. Tu screen define tag/modal/zorder
# (las propiedades de screen NO se transfieren con `use`) y aporta el contenido:
#
#   screen mi_herramienta():
#       tag menu
#       modal True
#       zorder 200
#       use tool_shell("Mi Herramienta"):
#           text "Contenido..." style "complements_detail_desc"
screen tool_shell(titulo):
    key "K_ESCAPE" action Show("complements")

    add gui.main_menu_background

    frame:
        style "complements_detail"
        xalign 0.5
        yalign 0.5
        xsize 800

        vbox:
            spacing 14

            text "[titulo]" style "complements_detail_title"

            transclude

            textbutton _("Volver"):
                style "complements_open"
                text_style "main_navigation_button_text"
                action Show("complements")
                at nav_button_anim


style complements_detail is frame:
    background "#ffffffcc"
    padding (28, 24)

style complements_detail_title is text:
    size 34
    bold True
    color "#cc6699"
    outlines []

style complements_meta is text:
    size 15
    color "#999999"
    outlines []

style complements_detail_desc is text:
    size 18
    color "#333333"
    outlines []

style complements_section is text:
    size 18
    bold True
    color "#666666"
    outlines []

style complements_shot_frame is frame:
    background "#e6e6e6"
    padding (20, 30)
    xsize 620

style complements_shot_empty is text:
    size 16
    color "#888888"
    outlines []

# Botón "Abrir": mismo diseño que los textbuttons de navegación del menú,
# sin el size_group (para no atar su ancho a los de la izquierda).
style complements_open is main_navigation_button:
    size_group None

style complements_title is text:
    size 26
    color "#ffffff"
    outlines [(4, text_outline_color, 0, 0), (2, text_outline_color, 2, 2)]

style complements_hint is text:
    size 14
    color "#888888"
    outlines []

# --- Hub: búsqueda, tarjetas y grilla ---

transform pl_thumb:
    fit "contain"
    xysize (64, 64)

style pl_search_frame is frame:
    background "#ffffffcc"
    padding (10, 6)
    xsize 250

style pl_search is input:
    color "#333333"
    size 18
    outlines []

style pl_card is frame:
    background "#ffffffdd"
    padding (14, 10)
    xsize 280
    ysize 180

style pl_card_open is button:
    background None
    hover_background "#ffccdd66"
    padding (4, 4)
    xfill True

style pl_card_title is text:
    size 20
    bold True
    color "#cc6699"
    outlines []

style pl_card_desc is text:
    size 13
    color "#555555"
    outlines []

style pl_card_toggle is button:
    background "#e6e6e6"
    hover_background "#d6d6d6"
    padding (8, 4)
    xalign 0.5

style pl_card_toggle_text is text:
    size 13
    color "#333333"
    outlines []
