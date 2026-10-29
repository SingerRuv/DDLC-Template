## dialogo_lab_preview.rpy
## Diálogo — Vista previa: la línea con los tags, tal como sale en el juego.
##
## Replica el say: el textbox de `gui/textbox.png` con el texto del diálogo y
## el namebox con el nombre del personaje. Los estilos son los del juego
## (`say_dialogue`, `say_label`), así que lo que se ve es lo que sale.
##
## El textbox del juego mide 816 px y el texto 744 px; acá se reproduce esa
## misma proporción (el texto arranca 36 px desde el borde de la imagen).

style dlg_preview_dialogue is say_dialogue:
    xpos 36
    xsize 744

style dlg_preview_namebox is namebox:
    xpos 118
    ypos 0
    xanchor 0.5


screen dlg_preview():

    $ _dlg_texto = dlg_texto()
    $ _dlg_nombre = dlg_personaje()[1]

    frame:
        style "tool_window"
        xsize 844

        vbox:
            spacing 0

            use tool_barra("Vista previa", "preview", DLG_PREFIJO, "dialogo_lab")

            frame:
                background None
                padding (14, 14)
                xfill True

                vbox:
                    spacing 6

                    if not _dlg_texto:
                        text "Escribí una línea para ver la vista previa." style "tool_hint"

                    fixed:
                        xysize (816, 182)

                        # Textbox del juego, anclado abajo como en el say.
                        add Transform("gui/textbox.png", xalign=0.5, yalign=1.0)

                        # Texto del diálogo (los tags los interpreta Ren'Py).
                        text _dlg_texto style "dlg_preview_dialogue"

                        # Namebox con el nombre del personaje.
                        frame:
                            style "dlg_preview_namebox"

                            text _dlg_nombre style "say_label"

                    # La línea tal como se copia (los tags, literales).
                    if dlg_linea():
                        frame:
                            style "tool_code_box"
                            xfill True

                            add Text(dlg_codigo(), style="tool_code")
