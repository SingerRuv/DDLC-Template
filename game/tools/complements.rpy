## complements.rpy
## Hub de Plugins: punto de entrada a los plugins dev del template.
##
## Es dev-only: el botón aparece en el menú principal solo si
## config.developer = True.
##
## Los plugins son autocontenidos: cada uno es una carpeta en
## game/tools/plugins/<id>/ con un tool.json (metadatos) y su propio .rpy
## (el screen que nombra el manifiesto). El hub los descubre solo; no hay
## que registrar nada a mano.
##
## Organización: complements_data.rpy (lógica), complements_ui.rpy (estilos,
## tarjeta de la grilla y tool_shell). Este archivo solo compone el screen
## del hub.
##
## Ver game/tools/plugins/README.md para escribir tu propio plugin.

screen complements():
    tag menu
    modal True
    zorder 200

    default busqueda = ""
    default cat = ""
    default cat_open = False

    # Volver al menú principal (el hub se abre desde allí).
    key "K_ESCAPE" action ShowMenu("main_menu")

    # Mismo fondo animado que el menú principal.
    add gui.main_menu_background

    $ plugins, diagnosticos = pl_plugins()
    $ categorias = sorted({t["categoria"] for t in plugins})
    $ visibles = [
        t for t in plugins
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

            text _("Plugins") style "pl_hub_title"

            button:
                style "pl_dropdown"
                action SetScreenVariable("cat_open", not cat_open)
                hbox:
                    spacing 8
                    text (_(cat) if cat else _("Todas")) style "pl_dropdown_text" yalign 0.5
                    text "▼" style "pl_dropdown_arrow" yalign 0.5

            if cat_open:
                vbox:
                    spacing 2
                    for c in [""] + categorias:
                        textbutton (_(c) if c else _("Todas")):
                            style "pl_dropdown_item"
                            text_style "pl_dropdown_item_text"
                            selected (cat == c)
                            action [SetScreenVariable("cat", c),
                                    SetScreenVariable("cat_open", False)]

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
            text _("No hay plugins que coincidan.") style "complements_detail_desc"

        vpgrid:
            cols 2
            spacing 12
            xsize 900
            ysize 580
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

    # Volver al menú principal (esquina inferior derecha).
    textbutton _("Back"):
        style "main_navigation_button"
        text_style "main_navigation_button_text"
        xalign 1.0
        yalign 1.0
        xoffset -30
        yoffset -18
        action ShowMenu("main_menu")
