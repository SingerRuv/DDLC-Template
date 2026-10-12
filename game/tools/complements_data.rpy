## complements_data.rpy
## Hub de Plugins — Lógica (sin UI): descubrimiento de plugins, manifiesto
## (tool.json), validación/diagnóstico, búsqueda, y el soporte de módulos .py
## con sus hooks (setup/open/close/metadata).
##
## La interfaz vive en complements_ui.rpy y el screen raíz del hub en
## complements.rpy. Ver game/tools/plugins/README.md para escribir un plugin.

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
        """Descubre los plugins en tools/plugins/ y devuelve
        (plugins, diagnosticos).

        Nunca descarta un plugin en silencio: todo problema (JSON roto, screen
        inexistente, id duplicado, icono faltante, etc.) queda en `diagnosticos`,
        con `fatal` indicando si el plugin se excluyo de la lista.

        Cada plugin: id, titulo, descripcion, autor, version, categoria,
        orden, icono, palabras_clave, capturas, screen, args, modulo,
        min_version. Ordenadas por (orden, titulo)."""
        plugins = []
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
                    _pl_diag(diagnosticos, id_, f, "requiere API >= %s (actual %s)" % (min_version, tools_api_version), fatal=False)

            capturas = []
            for cap in (datos.get("capturas") or []):
                if not isinstance(cap, _pl_builtins.str):
                    continue
                ruta = "%s%s/%s" % (_PL_PLUGINS_DIR, carpeta, cap)
                if renpy.loadable(ruta):
                    capturas.append(ruta)

            plugins.append({
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

        for e in plugins:
            _pl_aplicar_metadata(e)
        plugins.sort(key=lambda d: (d["orden"], d["titulo"].lower()))
        return plugins, diagnosticos

    # ======================================================================
    # Hub: búsqueda.
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

    def pl_tool_por_id(id_):
        """Devuelve el dict de una herramienta por su id (o None)."""
        for t in pl_plugins()[0]:
            if t["id"] == id_:
                return t
        return None

    def pl_corto(texto, n=110):
        """Recorta un texto para la tarjeta (con '…')."""
        texto = texto or ""
        return texto if len(texto) <= n else texto[:n - 1].rstrip() + "…"

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
                renpy.log("%s: no se pudo importar '%s' (%s): %s" % (_PL_PLUGINS_LOG, nombre, id_, e))
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
            for k in ("titulo", "descripcion", "autor", "version", "categoria", "palabras_clave", "orden"):
                if k in md:
                    e[k] = md[k]

    def _pl_llamar(mod, nombre, *args):
        """Llama un hook opcional del modulo; los errores van al log."""
        hook = getattr(mod, nombre, None) if mod is not None else None
        if callable(hook):
            try:
                hook(*args)
            except Exception as e:
                renpy.log("%s: %s.%s() fallo: %s" % (_PL_PLUGINS_LOG, getattr(mod, "__name__", "?"), nombre, e))

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
