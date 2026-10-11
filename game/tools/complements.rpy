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

        herramientas.sort(key=lambda d: (d["orden"], d["titulo"].lower()))
        return herramientas, diagnosticos

    def pl_herramientas():
        """Lista de herramientas visibles en el hub."""
        return pl_plugins()[0]

    def pl_diagnosticos():
        """Problemas de plugins detectados (fatales y warnings)."""
        return pl_plugins()[1]


screen complements():
    tag menu
    modal True
    zorder 200

    default sel = 0

    # Volver al menú principal (el hub se abre desde allí).
    key "K_ESCAPE" action ShowMenu("main_menu")

    # Mismo fondo animado que el menú principal.
    add gui.main_menu_background

    $ herramientas, diagnosticos = pl_plugins()

    # ----- Panel izquierdo: lista de herramientas -----
    frame:
        style "main_menu_frame"

        vbox:
            style_prefix "main_navigation"
            xpos gui.navigation_xpos
            xoffset -50
            yalign 0.0
            yoffset 40
            spacing gui.navigation_spacing

            text _("Herramientas") style "complements_title"

            if not herramientas:
                text _("No hay herramientas instaladas.") style "complements_hint"

            for i, tool in enumerate(herramientas):
                textbutton "[tool['titulo']]":
                    style "main_navigation_button"
                    text_style "main_navigation_button_text"
                    selected sel == i
                    action SetScreenVariable("sel", i)

            textbutton _("Back"):
                style "main_navigation_button"
                text_style "main_navigation_button_text"
                action ShowMenu("main_menu")

    # ----- Panel derecho: detalle de la herramienta + diagnóstico -----
    frame:
        style "complements_detail"
        xpos 360
        ypos 60
        xsize 880

        vbox:
            spacing 12

            if herramientas:
                $ tool = herramientas[min(sel, len(herramientas) - 1)]

                text "[tool['titulo']]" style "complements_detail_title"

                $ meta = " · ".join(s for s in (
                    ("v" + tool["version"]) if tool["version"] else "",
                    tool["autor"],
                    tool["categoria"] if tool["categoria"] != "General" else "") if s)
                if meta:
                    text "[meta]" style "complements_meta"

                text "[tool['descripcion']]" style "complements_detail_desc"

                text _("Capturas de pantalla") style "complements_section"

                if tool["capturas"]:
                    hbox:
                        spacing 12
                        for cap in tool["capturas"]:
                            add cap zoom 0.4
                else:
                    frame:
                        style "complements_shot_frame"
                        text _("Sin capturas todavía.") style "complements_shot_empty"

                textbutton "Abrir [tool['titulo']]":
                    style "complements_open"
                    text_style "main_navigation_button_text"
                    action Show(tool["screen"], **tool["args"])
                    at nav_button_anim
            else:
                text _("No hay herramientas instaladas.") style "complements_detail_desc"

            # Diagnóstico: plugins con problemas, nunca se descartan en silencio.
            if diagnosticos:
                text _("Diagnóstico") style "complements_section"
                for d in diagnosticos:
                    $ _col = "#cc3333" if d["fatal"] else "#a9791c"
                    text "[d['id']]: [d['motivo']]" style "complements_detail_desc" size 14 color _col


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
