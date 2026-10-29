## pose_lab_ui.rpy
## PoseLab — Interfaz: estilos, dropdown reutilizable y las ventanas flotantes
## (arrastrables) de controles y de código.

# ---------------------------------------------------------------------------
# Estilos de la herramienta (limpios, oscuros, sin depender del template).
# ---------------------------------------------------------------------------

style pl_text is text:
    color "#cfd3da"
    size 15

style pl_title is pl_text:
    size 22
    bold True
    color "#ffffff"

style pl_caption is pl_text:
    size 13
    bold True
    color "#7fb0ff"

style pl_hint is pl_text:
    size 13
    color "#8a8f98"

style pl_code is text:
    size 15
    color "#e6e6e6"
    kerning 1

# Bloque del código (fondo oscuro tipo editor).
style pl_code_box is frame:
    background "#181b21"
    padding (12, 10)
    xfill True

style pl_field is button:
    background "#2c313a"
    hover_background "#3a4150"
    padding (12, 6)

style pl_field_text is pl_text:
    size 15
    color "#ffffff"
    text_align 0.0
    xalign 0.0

style pl_option is button:
    background None
    hover_background "#2c313a"
    selected_background "#2f4d7a"
    selected_hover_background "#3a5d92"
    padding (10, 6)
    ysize 33
    xfill True

style pl_option_text is pl_text:
    size 15
    text_align 0.5
    xalign 0.5

# Bandeja de opciones: recuadro bajo el campo abierto. Se ajusta al alto de
# las opciones (sin alto fijo) y flota sobre el juego.
style pl_tray is frame:
    background "#1a1d23"
    padding (6, 6)
    xfill True

style pl_button is button:
    background "#3a5d92"
    hover_background "#4a72ad"
    padding (16, 8)

style pl_button_text is pl_text:
    size 15
    color "#ffffff"

style pl_copy is button:
    background "#2c313a"
    hover_background "#3a4150"
    padding (12, 6)

style pl_copy_text is pl_text:
    size 14
    color "#9fc3ff"

# La barra de título de las ventanas flotantes es la del hub (`tool_barra`).
style pl_window_bar is tool_window_bar

style pl_window_bar_text is tool_window_title

# Cuerpo de la ventana.
style pl_window is tool_window

# Panel "Copiar en…": elegir archivo destino y punto de inserción.
style pl_destino_frame is frame:
    background "#20232af2"
    padding (16, 14)

style pl_destino_title is pl_title:
    size 20

style pl_archivo is button:
    background None
    hover_background "#2c313a"
    selected_background "#2f4d7a"
    selected_hover_background "#3a5d92"
    padding (10, 6)
    xfill True

style pl_archivo_text is pl_text:
    size 13

style pl_linea is button:
    background None
    hover_background "#2c313a"
    selected_background "#2f4d7a"
    selected_hover_background "#3a5d92"
    padding (2, 1)
    xfill True

style pl_linea_text is text:
    size 13
    color "#cfd3da"


# ---------------------------------------------------------------------------
# Animaciones.
# ---------------------------------------------------------------------------
# La barra de título de las ventanas flotantes es la del hub: `tool_barra`.


# Ventana flotante de controles (se arrastra por la barra de título).
#
# Los campos se ubican en una grilla 2 columnas de posición explícita dentro de
# un `fixed`. El dropdown del campo abierto se dibuja como overlay anclado justo
# debajo de su campo: flota por encima del resto sin desplazarlo. La ventana se
# ajusta al alto de los campos (sin reservar la zona del dropdown): el dropdown
# puede salir por debajo del marco, sobre el juego.
screen pl_controls(r):
    $ menus = pl_menus(r)
    $ cw = 130            # ancho de columna
    $ gx = 12             # separación horizontal entre columnas
    $ pitch = 58         # alto de fila (título + campo + espacio)
    # Alto de cada opción (`pl_option` mide 33 + 2 de separación) y alto
    # máximo de la bandeja: con pocas opciones la bandeja se ajusta al
    # contenido; con muchas, scrollea.
    $ opt_h = 35
    $ bandeja_max = 160
    # Celdas de la grilla: los campos + el botón "Reescanear" (va en la celda
    # siguiente a Zorder, así que reservamos su fila).
    $ filas = (len(menus) + 2) // 2
    $ idx = next((j for j, m in enumerate(menus) if m[2] == pl_state["open"]), -1)

    frame:
        style "pl_window"
        xsize 300

        vbox:
            spacing 0

            use tool_barra("PoseLab", "controls", PL_PREFIJO, "pose_lab")

            frame:
                background None
                padding (14, 12)

                fixed:
                    xysize (2 * cw + gx, 22 + filas * pitch)

                    text "Arma una pose y copia el código." style "pl_hint" xpos 0 ypos 0

                    # Campos (título + botón que abre/cierra su dropdown).
                    for i, (titulo, actual, clave, opciones) in enumerate(menus):
                        vbox:
                            xpos (i % 2) * (cw + gx)
                            ypos 22 + (i // 2) * pitch
                            spacing 2
                            text "[titulo]" style "pl_caption"
                            textbutton "[actual]":
                                style "pl_field"
                                xsize cw
                                action ToggleDict(pl_state, "open", clave, "")

                    # "Reescanear": en la misma grilla, en la celda a la derecha
                    # de Zorder (no agranda ni desplaza la ventana).
                    vbox:
                        xpos (len(menus) % 2) * (cw + gx)
                        ypos 22 + (len(menus) // 2) * pitch
                        spacing 2
                        text " " style "pl_caption"
                        textbutton "Reescanear":
                            style "pl_copy"
                            xsize cw
                            action Function(pl_reescanear)

                    # Dropdown del campo abierto, encima de los campos siguientes.
                    #
                    # La bandeja se ajusta al alto de las opciones: con pocas
                    # no queda hueco, con muchas scrollea (un viewport con
                    # `ymaximum` fijo reservaba siempre 160 px de alto).
                    if idx >= 0:
                        frame:
                            style "pl_tray"
                            xfill False
                            xpos (idx % 2) * (cw + gx)
                            ypos 22 + (idx // 2) * pitch + 50
                            xsize cw

                            viewport:
                                ysize min(bandeja_max - 12, len(menus[idx][3]) * opt_h)
                                scrollbars "vertical"
                                mousewheel True

                                vbox:
                                    xfill True
                                    spacing 2

                                    for texto, accion, elegido in menus[idx][3]:
                                        textbutton "[texto]":
                                            style "pl_option"
                                            selected elegido
                                            action accion


# Ventana flotante del bloque de código (se arrastra por la barra de título).
screen pl_code(txt):

    frame:
        style "pl_window"
        xsize 460

        vbox:
            spacing 0

            use tool_barra("Código", "code", PL_PREFIJO, "pose_lab")

            frame:
                background None
                padding (14, 14)
                xfill True

                vbox:
                    spacing 8

                    if txt:
                        frame:
                            style "pl_code_box"
                            text "[tool_codigo_rico(txt)]" style "pl_code" xmaximum 395

                        # Copiar y "Copiar en…" viven en la barra de
                        # herramientas; acá solo queda el atajo.
                        text "Ctrl+C" style "pl_hint"
                    else:
                        text "Elige personaje, outfit, pose y cara." style "pl_hint"


# Pregunta automática: personajes custom sin definiciones propias.
screen pl_definir(tags=[]):
    modal True
    zorder 300
    key "K_ESCAPE" action Hide("pl_definir")

    add Solid("#00000099")

    frame:
        style "pl_destino_frame"
        xalign 0.5
        yalign 0.5
        xsize 560

        vbox:
            spacing 12

            text "ATENCIÓN" style "pl_destino_title"

            if len(tags) == 1:
                text "Este sprite no cuenta con definiciones propias. ¿Te gustaría que las cree?" style "pl_text"
            else:
                text "Estos sprites no cuentan con definiciones propias. ¿Te gustaría que las cree?" style "pl_text"

            vbox:
                spacing 2
                for t in tags:
                    text ("• " + t) style "pl_hint"

            hbox:
                spacing 10
                textbutton "Crear":
                    style "pl_button"
                    action [Function(pl_crear_definiciones, tags), Hide("pl_definir")]
                textbutton "Ahora no":
                    style "pl_copy"
                    action Hide("pl_definir")
