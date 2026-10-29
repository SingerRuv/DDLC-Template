## dialogo_lab_ui.rpy
## Diálogo — Controles del editor (ventana flotante).
##
## Usa los estilos globales `tool_*` del hub (game/tools/ui_styles.rpy); solo
## define `dlg_input_boton`, el botón invisible que pone el foco en un campo.
##
## Los controles no van en secciones plegables: son pocos y todos se usan a
## la vez (escribir la línea, marcar la frase, elegir el efecto). Cada
## apartado muestra a la derecha un resumen de lo que está activo.
##
## Los inputs escriben directo en `dlg_state` (DictInputValue), así que la
## vista previa se actualiza al escribir.
##
## Ren'Py deja editable un solo input a la vez (el primero que encuentra) y
## el `input` no atiende clicks: para poder escribir en cualquier campo, cada
## uno va dentro de un botón transparente que lo habilita al clickearlo.


# Botón invisible: solo sirve para habilitar el input que contiene.
style dlg_input_boton is button:
    background None
    hover_background None
    selected_background None
    padding (0, 0)
    xfill True


# Ventana flotante de controles (se arrastra por la barra de título, que
# también tiene "Fijar" y "Restablecer").
screen dlg_controles():

    # Los valores de los inputs (los usa el botón que pone el foco).
    $ _dlg_val_linea = DictInputValue(dlg_state, "linea")
    $ _dlg_val_frase = DictInputValue(dlg_state, "frase")
    $ _dlg_val_color = DictInputValue(dlg_state, "color_hex")

    frame:
        style "tool_window"
        xsize 372

        vbox:
            spacing 0

            use tool_barra("Diálogo", "controls", DLG_PREFIJO, "dialogo_lab")

            frame:
                background None
                padding (14, 12)
                xfill True

                vbox:
                    spacing 4
                    xfill True

                    text "Escribí la línea y marcá la frase a resaltar." style "tool_hint"

                    null height 2

                    # ---- Línea -------------------------------------------

                    hbox:
                        spacing 8
                        xfill True

                        text "Texto del diálogo" style "tool_caption"

                        frame:
                            background None
                            xfill True

                            text dlg_resumen_linea() style "tool_dropdown_value" xalign 1.0

                    frame:
                        style "tool_input_frame"
                        xfill True

                        button:
                            style "dlg_input_boton"
                            action _dlg_val_linea.Enable()

                            input:
                                value _dlg_val_linea
                                style "tool_input"
                                xsize DLG_INPUT_ANCHO
                                length 200

                    text "Frase a resaltar (opcional)" style "tool_caption"

                    frame:
                        style "tool_input_frame"
                        xfill True

                        button:
                            style "dlg_input_boton"
                            action _dlg_val_frase.Enable()

                            input:
                                value _dlg_val_frase
                                style "tool_input"
                                xsize DLG_INPUT_ANCHO
                                length 120

                    if dlg_aviso():
                        text "[dlg_aviso()]" style "tool_hint" color "#ff9e64"

                    null height 8

                    # ---- Efectos -----------------------------------------

                    hbox:
                        spacing 8
                        xfill True

                        text "Efectos" style "tool_caption"

                        frame:
                            background None
                            xfill True

                            text dlg_resumen_efectos() style "tool_dropdown_value" xalign 1.0

                    hbox:
                        spacing 4

                        textbutton "Negrita":
                            style "tool_chip"
                            selected dlg_state["negrita"]
                            action SetDict(dlg_state, "negrita", not dlg_state["negrita"])

                        textbutton "Itálica":
                            style "tool_chip"
                            selected dlg_state["italica"]
                            action SetDict(dlg_state, "italica", not dlg_state["italica"])

                        textbutton "Subrayado":
                            style "tool_chip"
                            selected dlg_state["subrayado"]
                            action SetDict(dlg_state, "subrayado", not dlg_state["subrayado"])

                        textbutton "Tachado":
                            style "tool_chip"
                            selected dlg_state["tachado"]
                            action SetDict(dlg_state, "tachado", not dlg_state["tachado"])

                    use tool_dropdown("color", "Color", dlg_state["color"],
                                      _DLG_COLORES, dlg_state, "color",
                                      columnas=2)

                    if dlg_state["color"] == "Personalizado":

                                frame:
                                    style "tool_input_frame"
                                    xfill True

                                    button:
                                        style "dlg_input_boton"
                                        action _dlg_val_color.Enable()

                                        input:
                                            value _dlg_val_color
                                            style "tool_input"
                                            xsize DLG_INPUT_ANCHO
                                            length 9

                    use tool_dropdown("tamano", "Tamaño", dlg_state["tamano"],
                                      [(n, n) for n, _ in _DLG_TAMANOS],
                                      dlg_state, "tamano")

                    null height 8

                    # ---- Salida ------------------------------------------

                    hbox:
                        spacing 8
                        xfill True

                        text "Salida" style "tool_caption"

                        frame:
                            background None
                            xfill True

                            text dlg_resumen_salida() style "tool_dropdown_value" xalign 1.0

                    use tool_dropdown("personaje", "Personaje",
                                      dlg_state["personaje"],
                                      [(k, v[1]) for k, v in _DLG_PERSONAJES.items()],
                                      dlg_state, "personaje")

                    hbox:
                        spacing 4

                        textbutton "Incluir personaje":
                            style "tool_chip"
                            selected dlg_state["con_personaje"]
                            action SetDict(dlg_state, "con_personaje",
                                           not dlg_state["con_personaje"])
