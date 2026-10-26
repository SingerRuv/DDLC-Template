## ui_styles.rpy
## Estilos y componentes GLOBALES de las herramientas (hub de Plugins y plugins).
## No afecta al look de DDLC: menús/choice del juego siguen con sus estilos.
##
## Namespace: `tool_*`. Si un plugin necesita un estilo propio, lo define
## heredando de estos (`style mi_x is tool_button`).

# ---------------------------------------------------------------------------
# Textos
# ---------------------------------------------------------------------------

style tool_text is text:
    color "#cfd3da"
    size 15

style tool_title is tool_text:
    size 22
    bold True
    color "#ffffff"

style tool_caption is tool_text:
    size 13
    bold True
    color "#7fb0ff"

style tool_hint is tool_text:
    size 13
    color "#8a8f98"

style tool_keyhint is tool_text:
    size 12
    color "#6b7280"

# ---------------------------------------------------------------------------
# Ventanas y paneles
# ---------------------------------------------------------------------------

style tool_panel is frame:
    background "#20232ae6"
    padding (14, 10)

style tool_window is frame:
    background "#20232ae6"
    xfill True

style tool_window_bar is frame:
    background "#2b303a"
    xfill True
    padding (12, 8)

style tool_window_title is tool_text:
    size 15
    bold True
    color "#ffffff"

style tool_pin is button:
    background "#3a4150"
    hover_background "#49536a"
    selected_background "#2f4d7a"
    selected_hover_background "#3a5d92"
    padding (10, 4)

style tool_pin_text is tool_text:
    size 13
    color "#cfd3da"

# ---------------------------------------------------------------------------
# Botones
# ---------------------------------------------------------------------------

style tool_button is button:
    background "#2c313a"
    hover_background "#3a4150"
    selected_background "#2f4d7a"
    selected_hover_background "#3a5d92"
    insensitive_background "#20232a"
    padding (10, 4)

style tool_button_text is tool_text:
    size 14
    color "#cfd3da"

style tool_button_small is tool_button:
    padding (8, 2)

style tool_copy is tool_button

style tool_copy_text is tool_button_text:
    color "#9fc3ff"

style tool_chip is tool_button:
    padding (10, 4)

style tool_chip_text is tool_button_text:
    size 13

# ---------------------------------------------------------------------------
# Listas, opciones y separadores
# ---------------------------------------------------------------------------

style tool_tray is frame:
    background "#181b21"
    padding (10, 8)

style tool_option is tool_button

style tool_option_text is tool_button_text

style tool_line is button:
    background None
    hover_background "#2c313a"
    selected_background "#2f4d7a"
    padding (4, 1)
    xfill True

style tool_line_text is text:
    size 13
    color "#cfd3da"

style tool_separator is frame:
    background "#3a4150"
    xfill True
    ysize 1

# ---------------------------------------------------------------------------
# Código
# ---------------------------------------------------------------------------

style tool_code is text:
    size 15
    color "#e6e6e6"
    kerning 1

style tool_code_box is frame:
    background "#181b21"
    padding (12, 10)
    xfill True

# ---------------------------------------------------------------------------
# Dropdown
# ---------------------------------------------------------------------------

# Encabezado clickeable (el "texto del apartado").
style tool_dropdown_header is button:
    background None
    hover_background "#2c313a"
    padding (4, 2)
    xfill True

style tool_dropdown_header_text is tool_caption:
    size 13

# Valor elegido, debajo del título del apartado.
style tool_dropdown_value is tool_text:
    size 15
    bold True
    color "#ffffff"

# Cada opción va en su propio recuadro.
style tool_dropdown_item is button:
    # `button` hereda yminimum 36 (gui.button_height): acá va más apretado.
    yminimum 0
    background "#2c313a"
    hover_background "#3a4150"
    selected_background "#2f4d7a"
    selected_hover_background "#3a5d92"
    padding (10, 5)

style tool_dropdown_item_text is tool_text:
    size 16
    color "#cfd3da"

# ---------------------------------------------------------------------------
# Inputs, feedback y barras
# ---------------------------------------------------------------------------

style tool_input_frame is frame:
    background "#181b21"
    padding (8, 5)

style tool_input is input:
    color "#ffffff"
    size 15

style tool_input_hint is tool_hint

style tool_toast is frame:
    background "#2b303aee"
    padding (18, 10)

style tool_toast_text is tool_text:
    size 16
    color "#ffffff"

style tool_bar is bar:
    left_bar "#7fb0ff"
    right_bar "#3a4150"
    thumb None

style tool_slider is slider:
    left_bar "#7fb0ff"
    right_bar "#3a4150"


init python:

    # ------------------------------------------------------------------
    # Dropdown global (acordeón inline).
    #
    # opciones: lista de pares (valor, etiqueta).
    # destino:  dict donde se guarda el valor elegido (p. ej. shl_state).
    # clave:    clave dentro de `destino`.
    #
    # El estado vive en el store para que funcione igual dentro de un `use`.
    # Al abrir, la lista se despliega DEBAJO de la fila y empuja el contenido.
    # ------------------------------------------------------------------

    tool_dd_state = {"abierto": ""}

    def tool_dd_toggle(id):
        tool_dd_state["abierto"] = "" if tool_dd_state["abierto"] == id else id
        renpy.restart_interaction()

    def tool_dd_cerrar():
        tool_dd_state["abierto"] = ""
        renpy.restart_interaction()


screen tool_dropdown(id, etiqueta, valor, opciones, destino, clave, despues=None):

    $ _tool_dd_lab = next((lab for v, lab in opciones if v == valor), str(valor))
    $ _tool_dd_abierto = (tool_dd_state["abierto"] == id)

    # Encabezado clickeable: "Aplicar a" arriba y el valor debajo en blanco.
    button:
        style "tool_dropdown_header"
        action Function(tool_dd_toggle, id)

        vbox:
            spacing 1

            text etiqueta style "tool_dropdown_header_text"
            text _tool_dd_lab style "tool_dropdown_value"

    # Opciones: cada una en su propio recuadro, debajo del encabezado.
    if _tool_dd_abierto:

        key "K_ESCAPE" action Function(tool_dd_cerrar)

        null height 4

        viewport:
            ymaximum 320
            scrollbars "vertical"
            mousewheel True

            vbox:
                xfill True
                spacing 2

                for v, lab in opciones:
                    textbutton lab:
                        style "tool_dropdown_item"
                        selected v == destino.get(clave)
                        action ([SetDict(destino, clave, v),
                                Function(tool_dd_cerrar)] + list(despues or []))

    # Aire entre apartados (el dropdown es un bloque dentro de un vbox).
    null height 10
