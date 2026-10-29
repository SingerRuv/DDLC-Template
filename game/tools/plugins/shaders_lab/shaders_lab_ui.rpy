## shaders_lab_ui.rpy
## Shaders Lab — Interfaz: la ventana de controles de la demo.
## Usa los estilos globales `tool_*` (game/tools/ui_styles.rpy); los `shl_*`
## quedan como alias por compatibilidad.

style shl_panel is tool_panel
style shl_titulo is tool_title
style shl_caption is tool_caption
style shl_hint is tool_hint
style shl_boton is tool_button
style shl_boton_text is tool_button_text


# Ventana flotante de controles (se arrastra por la barra de título, que
# también tiene "Fijar" y "Restablecer").
screen shl_controles():

    frame:
        style "tool_window"
        xsize 330

        vbox:
            spacing 0

            use tool_barra("Shaders", "controls", SHL_PREFIJO, "shaders_lab")

            frame:
                background None
                padding (14, 12)

                vbox:
                    spacing 6

                    text "Vista previa de shaders para el fondo." style "tool_hint"

                    null height 4

                    use tool_dropdown("fondo", "Fondo", shl_state["fondo"],
                                      [(f, f) for f in shl_fondos()],
                                      shl_state, "fondo", columnas=2)

                    use tool_dropdown("efecto", "Efecto", shl_state["efecto"],
                                      [(e, e) for e in _SHL_EFECTOS],
                                      shl_state, "efecto", columnas=2)

                    use tool_dropdown("intensidad", "Intensidad", shl_state["intensidad"],
                                      [(0.2, "Suave"), (0.5, "Media"), (0.8, "Fuerte")],
                                      shl_state, "intensidad", columnas=0)

                    null height 4
                    text "Texto del diálogo → plugin Diálogo." style "tool_hint"


# Ventana flotante con el código del efecto elegido (se arrastra por la barra
# de título). Es la de PoseLab, con los estilos del hub.
screen shl_code(txt):

    frame:
        style "tool_window"
        xsize 460

        vbox:
            spacing 0

            use tool_barra("Código", "code", SHL_PREFIJO, "shaders_lab")

            frame:
                background None
                padding (14, 14)
                xfill True

                vbox:
                    spacing 8

                    if txt:
                        # El color es solo visual: lo que se copia es `txt` plano.
                        frame:
                            style "tool_code_box"
                            text "[tool_codigo_rico(txt)]" style "tool_code" xmaximum 395

                        # Copiar y "Copiar en…" viven en la barra de
                        # herramientas; acá solo queda el atajo.
                        text "Ctrl+C" style "tool_hint"
                    else:
                        text "Elegí un efecto." style "tool_hint"
