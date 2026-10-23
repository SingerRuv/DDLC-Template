## shaders_lab_ui.rpy
## Shaders Lab — Interfaz: estilos de la herramienta (limpios, oscuros, sin
## depender del template) y la ventana de controles de la demo.

style shl_panel is frame:
    background "#20232ae6"
    padding (16, 14)

style shl_titulo is text:
    size 17
    bold True
    color "#ffffff"

style shl_caption is text:
    size 13
    bold True
    color "#7fb0ff"

style shl_hint is text:
    size 13
    color "#8a8f98"

style shl_boton is button:
    background "#2c313a"
    hover_background "#3a4150"
    selected_background "#2f4d7a"
    selected_hover_background "#3a5d92"
    padding (10, 5)

style shl_boton_text is text:
    size 14
    color "#cfd3da"


screen shl_controles():

    $ _shl_efecto = shl_state["efecto"]
    $ _shl_intensidad = shl_state["intensidad"]

    frame:
        style "shl_panel"
        xpos 24
        ypos 24
        xsize 320

        vbox:
            spacing 8

            text "Shaders" style "shl_titulo"
            text "Vista previa de los efectos incluidos." style "shl_hint"

            null height 6
            text "Efecto" style "shl_caption"
            for e in _SHL_EFECTOS:
                textbutton e:
                    style "shl_boton"
                    selected e == _shl_efecto
                    action SetDict(shl_state, "efecto", e)

            null height 6
            text "Intensidad" style "shl_caption"
            hbox:
                spacing 6
                for v, etiqueta in ((0.2, "Suave"), (0.5, "Media"), (0.8, "Fuerte")):
                    textbutton etiqueta:
                        style "shl_boton"
                        selected abs(_shl_intensidad - v) < 0.01
                        action SetDict(shl_state, "intensidad", v)

            null height 8
            text "En tu historia:" style "shl_caption"
            text "show yuri 1a at sh_scanlines\nshow bg class at sh_crt" style "shl_hint"

            null height 6
            text "ESC para volver a Plugins." style "shl_hint"
