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
## Organización: complements_data.rpy (lógica), complements_ui.rpy (estilos,
## tarjeta de la grilla y tool_shell). Este archivo solo compone el screen
## del hub.
##
## Ver game/tools/plugins/README.md para escribir tu propia herramienta.

screen complements():
    tag menu
    modal True
    zorder 200

    default busqueda = ""
    default cat = ""

    # Volver al menú principal (el hub se abre desde allí).
    key "K_ESCAPE" action ShowMenu("main_menu")

    # Mismo fondo animado que el menú principal.
    add gui.main_menu_background

    $ herramientas, diagnosticos = pl_plugins()
    $ categorias = sorted({t["categoria"] for t in herramientas})
    $ visibles = [
        t for t in herramientas
        if (not cat or t["categoria"] == cat) and pl_coincide(t, busqueda)
    ]

    # ----- Panel izquierdo: título y categorías -----
    frame:
        style "main_menu_frame"

        vbox:
            style_prefix "main_navigation"
            xpos gui.navigation_xpos
            xoffset -50
            yalign 0.0
            yoffset 24
            spacing 10

            text _("Herramientas") style "complements_title"

            vbox:
                spacing 4
                for c in [""] + categorias:
                    textbutton (_(c) if c else _("Todas")):
                        style "pl_chip"
                        text_style "pl_chip_text"
                        selected (cat == c)
                        action SetScreenVariable("cat", c)

            textbutton _("Back"):
                style "main_navigation_button"
                text_style "main_navigation_button_text"
                action ShowMenu("main_menu")

    # ----- Área derecha: buscador + grilla de tarjetas + diagnóstico -----
    vbox:
        xpos 340
        ypos 24
        xsize 900
        spacing 10

        frame:
            style "pl_search_border"
            frame:
                style "pl_search_frame"
                fixed:
                    xysize (380, 30)
                    if not busqueda:
                        text _("Buscar…") style "pl_search_hint" xoffset 4 yalign 0.5
                    input:
                        value ScreenVariableInputValue("busqueda")
                        style "pl_search"
                        length 40
                        yalign 0.5

        if not visibles:
            text _("No hay herramientas que coincidan.") style "complements_detail_desc"

        vpgrid:
            cols 2
            spacing 12
            xsize 892
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
