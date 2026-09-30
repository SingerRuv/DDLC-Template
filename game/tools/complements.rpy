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
    _PL_PLUGINS_LOG = "poselab.plugins"

    def pl_plugins():
        """Descubre las herramientas en tools/plugins/ y devuelve una lista de
        dicts ordenada por titulo. Cada item:
            {id, titulo, descripcion, autor, version, capturas, screen, carpeta}

        Un plugin sin tool.json valido, sin screen 'screen', o con JSON roto
        se salta con un aviso en el log (el hub nunca falla por un plugin mal
        hecho). `capturas` solo incluye archivos que existen de verdad."""
        encontrados = {}
        for f in renpy.list_files():
            if not f.startswith(_PL_PLUGINS_DIR) or not f.endswith("/tool.json"):
                continue
            carpeta = f[len(_PL_PLUGINS_DIR):-len("tool.json")].rstrip("/")
            if "/" in carpeta or not carpeta:
                continue  # solo plugins en el primer nivel
            try:
                with renpy.file(f) as fh:
                    datos = _pl_json.loads(fh.read().decode("utf-8"))
            except Exception as e:
                renpy.log("%s: tool.json ilegible en %s: %s"
                          % (_PL_PLUGINS_LOG, f, e))
                continue
            # Ojo: en el store de Ren'Py `dict` es RevertableDict; usamos el
            # builtin para que json.loads (dict normal) pase la validacion.
            if not isinstance(datos, _pl_builtins.dict):
                continue
            screen = datos.get("screen", "")
            if not screen or not renpy.has_screen(screen):
                renpy.log("%s: plugin '%s' sin screen valido (%r)"
                          % (_PL_PLUGINS_LOG, carpeta, screen))
                continue

            capturas = []
            for cap in (datos.get("capturas") or []):
                ruta = "%s%s/%s" % (_PL_PLUGINS_DIR, carpeta, cap)
                if renpy.loadable(ruta):
                    capturas.append(ruta)

            encontrados[carpeta] = {
                "id": datos.get("id") or carpeta,
                "titulo": datos.get("titulo") or carpeta,
                "descripcion": datos.get("descripcion", ""),
                "autor": datos.get("autor", ""),
                "version": datos.get("version", ""),
                "capturas": capturas,
                "screen": screen,
                "carpeta": carpeta,
            }
        return sorted(encontrados.values(), key=lambda d: d["titulo"].lower())

    def pl_herramientas():
        """Lista de herramientas visibles en el hub."""
        return pl_plugins()


screen complements():
    tag menu
    modal True
    zorder 200

    default sel = 0

    # Volver al menú principal (el hub se abre desde allí).
    key "K_ESCAPE" action ShowMenu("main_menu")

    # Mismo fondo animado que el menú principal.
    add gui.main_menu_background

    $ herramientas = pl_herramientas()

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

    # ----- Panel derecho: detalle de la herramienta elegida -----
    if herramientas:
        $ tool = herramientas[min(sel, len(herramientas) - 1)]

        frame:
            style "complements_detail"
            xpos 360
            ypos 60
            xsize 880

            vbox:
                spacing 12

                text "[tool['titulo']]" style "complements_detail_title"

                $ meta = " · ".join(s for s in (
                    ("v" + tool["version"]) if tool["version"] else "",
                    tool["autor"]) if s)
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
                    action Show(tool["screen"])
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
