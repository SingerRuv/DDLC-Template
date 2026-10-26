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


screen shl_controles():

    $ _shl_sujeto = shl_state["sujeto"]

    frame:
        style "tool_panel"
        xpos 24
        ypos 24
        xsize 330

        vbox:
            spacing 6

            text "Shaders" style "tool_title"
            text "Vista previa de los efectos incluidos." style "tool_hint"

            null height 4

            use tool_dropdown("sujeto", "Aplicar a", _shl_sujeto,
                              [("Fondo", "Fondo"), ("Personaje", "Personaje")],
                              shl_state, "sujeto",
                              despues=[Function(shl_reset_efecto)])

            if _shl_sujeto == "Personaje":
                use tool_dropdown("doki", "Personaje", shl_state["doki"],
                                  [(d, d.capitalize()) for d in _SHL_DOKIS],
                                  shl_state, "doki")

            if _shl_sujeto == "Fondo":
                use tool_dropdown("efecto", "Efecto", shl_state["efecto"],
                                  [(e, e) for e in _SHL_EFECTOS],
                                  shl_state, "efecto")
            else:
                use tool_dropdown("efecto", "Efecto", shl_state["efecto"],
                                  [(e, e) for e in _SHL_EFECTOS_PJ],
                                  shl_state, "efecto")

            use tool_dropdown("intensidad", "Intensidad", shl_state["intensidad"],
                              [(0.2, "Suave"), (0.5, "Media"), (0.8, "Fuerte")],
                              shl_state, "intensidad")

            null height 6
            text "En tu historia:" style "tool_caption"
            if _shl_sujeto == "Fondo":
                text "show bg class at sh_crt" style "tool_hint"
            else:
                text "show yuri 1a at sh_contorno\nshow sayori 1a at sh_palidez(0.8)" style "tool_hint"

            null height 4
            text "ESC para volver a Plugins." style "tool_hint"
