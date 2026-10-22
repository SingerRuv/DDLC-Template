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

# Toast propio de la herramienta (notificación animada).
style pl_toast is frame:
    background "#2b303ae6"
    padding (16, 8)

style pl_toast_text is pl_text:
    size 15
    color "#73e08d"

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
    xfill True

style pl_option_text is pl_text:
    size 15
    text_align 0.5
    xalign 0.5

# Bandeja de opciones: recuadro de altura fija bajo los campos. Muestra las
# opciones del campo abierto sin desplazar ni agrandar la ventana.
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

# Barra de título de las ventanas flotantes (zona para arrastrar).
style pl_window_bar is frame:
    background "#2b303a"
    xfill True
    padding (12, 8)

style pl_window_bar_text is pl_text:
    size 15
    bold True
    color "#ffffff"

# Botones de la barra de título (fijar / restablecer).
style pl_pin is button:
    background "#3a4150"
    hover_background "#49536a"
    selected_background "#2f4d7a"
    selected_hover_background "#3a5d92"
    padding (10, 4)

style pl_pin_text is pl_text:
    size 13
    color "#cfd3da"

# Cuerpo de la ventana.
style pl_window is frame:
    background "#20232ae6"
    xfill True

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

# Toast: aparece deslizando desde arriba + fade; se va con fade al ocultarlo.
transform pl_notify_anim:
    on show:
        alpha 0.0
        yoffset -20
        linear 0.25 alpha 1.0 yoffset 0
    on hide:
        linear 0.30 alpha 0.0

# Toast propio de PoseLab, por encima de las ventanas (zorder > pose_lab).
# Reemplaza a renpy.notify solo dentro de la herramienta, para poder animarlo.
screen pl_notify(message):
    zorder 300

    frame:
        style "pl_toast"
        at pl_notify_anim
        xalign 0.5
        ypos 16

        text "[message]" style "pl_toast_text"

    timer 2.0 action Hide("pl_notify")


# Barra de título reutilizable: título a la izquierda y botones Fijar/Restablecer
# a la derecha. `nombre` identifica la ventana ("controls" / "code") para el
# estado persistente (posición y fijado).
screen pl_barra(titulo, nombre):
    frame:
        style "pl_window_bar"

        fixed:
            xysize (1.0, 26)
            text "[titulo]" style "pl_window_bar_text" xpos 0 yalign 0.5

            hbox:
                xalign 1.0
                yalign 0.5
                spacing 6

                textbutton ("Fijada" if pl_ventana_fija(nombre) else "Fijar"):
                    style "pl_pin"
                    selected pl_ventana_fija(nombre)
                    action Function(pl_ventana_alternar_fija, nombre)

                textbutton "Restablecer":
                    style "pl_pin"
                    action Function(pl_ventana_reiniciar, nombre)


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
    $ dz = 160            # alto de la zona reservada para el dropdown
    # Celdas de la grilla: los campos + el botón "Reescanear" (va en la celda
    # siguiente a Zorder, así que reservamos su fila).
    $ filas = (len(menus) + 2) // 2
    $ idx = next((j for j, m in enumerate(menus) if m[2] == pl_state["open"]), -1)

    frame:
        style "pl_window"
        xsize 300

        vbox:
            spacing 0

            use pl_barra("PoseLab", "controls")

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
                    if idx >= 0:
                        frame:
                            style "pl_tray"
                            xfill False
                            xpos (idx % 2) * (cw + gx)
                            ypos 22 + (idx // 2) * pitch + 50
                            xsize cw
                            ysize dz

                            viewport:
                                ysize dz - 12
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
screen pl_code(txt_show, txt_code):

    frame:
        style "pl_window"
        xsize 460

        vbox:
            spacing 0

            use pl_barra("Código", "code")

            frame:
                background None
                padding (14, 14)
                xfill True

                vbox:
                    spacing 8

                    if txt_show:
                        frame:
                            style "pl_code_box"
                            text "[txt_code]" style "pl_code" xmaximum 395

                        hbox:
                            spacing 10
                            textbutton "Copiar":
                                style "pl_copy"
                                action Function(pl_copiar, txt_show)
                            textbutton "Copiar en…":
                                style "pl_copy"
                                action Show("pl_aviso", texto=txt_show)
                            text "Ctrl+C" style "pl_hint" yalign 0.5
                    else:
                        text "Elige personaje, outfit, pose y cara." style "pl_hint"


# Aviso previo a "Copiar en…": explica cómo habilitar un .rpy como destino.
screen pl_aviso(texto):
    modal True
    zorder 260

    key "K_ESCAPE" action Hide("pl_aviso")

    frame:
        style "pl_destino_frame"
        xalign 0.5
        yalign 0.5
        xsize 520

        vbox:
            spacing 12

            text "Copiar en…" style "pl_destino_title"
            text "Escribe `# poselab` al principio del .rpy donde quieres pegar el código. Si no lo tiene, ese archivo no aparece en la lista." style "pl_text"

            hbox:
                spacing 8
                textbutton "Entendido":
                    style "pl_button"
                    action [Hide("pl_aviso"), Show("pl_destino", texto=texto)]
                textbutton "Cancelar":
                    style "pl_copy"
                    action Hide("pl_aviso")


# Panel "Copiar en…": escribe el código dentro de un .rpy del guion.
# Un archivo aparece en la lista si tiene una línea `# poselab` en cualquier
# parte (marcador que lo habilita como destino).
screen pl_destino(texto):
    modal True
    zorder 250

    default confirmando = False

    on "show" action Function(pl_destino_init, texto)

    key "K_ESCAPE" action Hide("pl_destino")

    frame:
        style "pl_destino_frame"
        xalign 0.5
        yalign 0.5
        xsize 1000
        ysize 560

        vbox:
            spacing 10

            text "Copiar en…" style "pl_destino_title"

            $ objs = pl_objetivos()

            if not objs:
                text "Agrega una línea `# poselab` a un .rpy para que aparezca aquí." style "pl_hint"

                textbutton "Cerrar":
                    style "pl_copy"
                    action Hide("pl_destino")
            else:
                $ rel = pl_state["destino_archivo"]
                $ lineas = pl_leer_objetivo(rel)

                hbox:
                    spacing 12

                    # Lista de archivos destino (los que tienen el marcador).
                    frame:
                        style "pl_tray"
                        xsize 250
                        ysize 360

                        viewport:
                            ysize 348
                            scrollbars "vertical"
                            mousewheel True

                            vbox:
                                xfill True
                                spacing 2
                                for o in objs:
                                    textbutton "[o]":
                                        style "pl_archivo"
                                        selected o == rel
                                        action [SetDict(pl_state, "destino_archivo", o),
                                                SetDict(pl_state, "destino_linea", 0)]

                    # Preview del archivo: clic en una línea elige dónde insertar.
                    frame:
                        style "pl_tray"
                        xsize 700
                        ysize 360

                        viewport:
                            ysize 348
                            scrollbars "vertical"
                            mousewheel True

                            vbox:
                                xfill True
                                spacing 0
                                for i, linea in enumerate(lineas):
                                    $ etiqueta = "%d  %s" % (i + 1, linea)
                                    textbutton "[etiqueta]":
                                        style "pl_linea"
                                        selected i == pl_state["destino_linea"]
                                        action SetDict(pl_state, "destino_linea", i)

                # Línea que se insertará (solo lectura).
                hbox:
                    spacing 8
                    text "Línea a pegar:" style "pl_caption" yalign 0.5
                    frame:
                        style "pl_tray"
                        xfill True
                        text "[pl_state['destino_texto']]" style "pl_code"

                # Confirmación y acciones.
                hbox:
                    spacing 8

                    if confirmando:
                        $ aviso = "Se insertará tras la línea %d de %s. Reinicia el juego para recompilar." % (pl_state["destino_linea"] + 1, rel)
                        text "[aviso]" style "pl_hint" yalign 0.5 xmaximum 520

                        textbutton "Sí, escribir":
                            style "pl_button"
                            action [Function(pl_escribir_destino), SetScreenVariable("confirmando", False)]
                        textbutton "Cancelar":
                            style "pl_copy"
                            action SetScreenVariable("confirmando", False)
                    else:
                        textbutton "Confirmar":
                            style "pl_button"
                            action SetScreenVariable("confirmando", True)
                        textbutton "Abrir archivo":
                            style "pl_copy"
                            action Function(pl_abrir_destino)
                        textbutton "Deshacer":
                            style "pl_copy"
                            action Function(pl_deshacer_destino)
                        textbutton "Cerrar":
                            style "pl_copy"
                            action Hide("pl_destino")


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
