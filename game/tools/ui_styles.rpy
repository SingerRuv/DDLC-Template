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

# Valor elegido, a la derecha del título del apartado.
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
# Secciones plegables
# ---------------------------------------------------------------------------

# Encabezado de una sección: el marker, el título y (a la derecha) un resumen
# corto de lo que está activo.
style tool_section_header is button:
    background None
    hover_background "#2c313a"
    padding (4, 3)
    xfill True

style tool_section_marker is tool_caption:
    size 13

style tool_section_title is tool_text:
    size 15
    bold True
    color "#ffffff"

style tool_section_summary is tool_text:
    size 12
    color "#8a8f98"

# ---------------------------------------------------------------------------
# Inputs, feedback y barras
# ---------------------------------------------------------------------------

style tool_input_frame is frame:
    background "#181b21"
    padding (8, 5)

style tool_input is input:
    color "#ffffff"
    size 15
    # El input se posiciona y alinea a la izquierda del marco (por defecto
    # el estilo `input` del juego centra el texto).
    xalign 0.0
    text_align 0.0

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
    right_bar "#7fb0ff"
    thumb None


# Toast: aparece deslizando desde arriba + fade; se va con fade al ocultarlo.
transform tool_notify_anim:
    on show:
        alpha 0.0
        yoffset -20
        linear 0.25 alpha 1.0 yoffset 0
    on hide:
        linear 0.30 alpha 0.0


# Aviso flotante de las herramientas, por encima de las ventanas del hub.
# Reemplaza a renpy.notify solo dentro de las herramientas, para poder
# animarlo y usar los estilos `tool_*`.
screen tool_notify(message):
    zorder 300

    frame:
        style "tool_toast"
        at tool_notify_anim
        xalign 0.5
        # Bajo la barra de herramientas (que ocupa la franja superior).
        ypos 56

        text "[message]" style "tool_toast_text"

    timer 2.0 action Hide("tool_notify")


# ---------------------------------------------------------------------------
# Ventanas flotantes (arrastrables) compartidas por los plugins.
#
# Cada plugin registra sus ventanas (nombre -> posición por defecto) y usa su
# propio prefijo para no chocar en `persistent` (ej. "pl", "shl"). El id del
# `drag` sigue la convención "<prefijo>_drag_<nombre>".
# ---------------------------------------------------------------------------

init python:

    _TOOL_VENTANAS = {}      # (prefijo, nombre) -> (x, y) por defecto
    _TOOL_FIJAS = {}         # (prefijo, nombre) -> bool (solo esta sesión)

    def tool_ventanas_defecto(defectos, prefijo="tool"):
        """Registra las posiciones por defecto: {nombre: (x, y)}."""
        for nombre, pos in defectos.items():
            _TOOL_VENTANAS[(prefijo, nombre)] = (int(pos[0]), int(pos[1]))

    def tool_ventana_pos(nombre, prefijo="tool"):
        # `persistent` devuelve None para atributos no definidos (no AttributeError).
        pos = getattr(persistent, "%s_pos_%s" % (prefijo, nombre), None)
        if pos is not None:
            return pos
        return _TOOL_VENTANAS.get((prefijo, nombre), (24, 24))

    def tool_ventana_fija(nombre, prefijo="tool"):
        return bool(_TOOL_FIJAS.get((prefijo, nombre), False))

    def tool_ventana_mover(nombre, x, y, prefijo="tool"):
        setattr(persistent, "%s_pos_%s" % (prefijo, nombre), (int(x), int(y)))

    def tool_ventana_alternar_fija(nombre, prefijo="tool"):
        _TOOL_FIJAS[(prefijo, nombre)] = not tool_ventana_fija(nombre, prefijo)
        renpy.restart_interaction()

    def tool_drag_mover(nombre, prefijo="tool"):
        """Callback para `dragged`: guarda dónde quedó la ventana al soltarla."""
        def cb(drags, drop):
            if drags:
                tool_ventana_mover(nombre, drags[0].x, drags[0].y, prefijo)
        return cb

    def tool_ventana_reiniciar(nombre, prefijo="tool", pantalla=""):
        """Devuelve la ventana a su posición por defecto (persistente + snap)."""
        x, y = _TOOL_VENTANAS.get((prefijo, nombre), (24, 24))
        tool_ventana_mover(nombre, x, y, prefijo)
        if pantalla:
            d = renpy.get_displayable(pantalla, "%s_drag_%s" % (prefijo, nombre))
            if d is not None:
                d.snap(x, y, delay=0.2)


# Barra de título de una ventana flotante: zona para arrastrar + Fijar/Restablecer.
screen tool_barra(titulo, nombre, prefijo="tool", pantalla=""):

    frame:
        style "tool_window_bar"

        fixed:
            xysize (1.0, 26)
            text "[titulo]" style "tool_window_title" xpos 0 yalign 0.5

            hbox:
                xalign 1.0
                yalign 0.5
                spacing 6

                textbutton ("Fijada" if tool_ventana_fija(nombre, prefijo) else "Fijar"):
                    style "tool_pin"
                    selected tool_ventana_fija(nombre, prefijo)
                    action Function(tool_ventana_alternar_fija, nombre, prefijo)

                textbutton "Restablecer":
                    style "tool_pin"
                    action Function(tool_ventana_reiniciar, nombre, prefijo, pantalla)


init python:

    try:
        import pygame as _tool_pygame
    except Exception:
        _tool_pygame = None

    def tool_toast(mensaje):
        """Muestra el aviso flotante de las herramientas."""
        renpy.hide_screen("tool_notify")
        renpy.show_screen("tool_notify", message=mensaje)

    def tool_copiar(texto, mensaje="Código copiado"):
        """Copia texto al portapapeles del sistema y avisa."""
        if not texto:
            return False
        try:
            if _tool_pygame is None:
                raise RuntimeError("pygame no disponible")
            _tool_pygame.scrap.put(
                _tool_pygame.scrap.SCRAP_TEXT, texto.encode("utf-8"),
            )
            tool_toast(mensaje)
            ok = True
        except Exception:
            tool_toast("No se pudo copiar")
            ok = False
        renpy.restart_interaction()
        return ok


# ---------------------------------------------------------------------------
# Resaltado de código (solo visual).
#
# `tool_codigo_rico` devuelve el código con tags de color de Ren'Py para
# mostrarlo en la UI. Lo que se COPIA va plano: el color es de pantalla.
# ---------------------------------------------------------------------------

init python:

    import re as _tool_re

    # Palabras clave de Ren'Py (guion + sentencias comunes).
    _TOOL_CODE_CLAVES = {
        "show", "hide", "at", "as", "expression", "with", "scene", "play",
        "image", "define", "transform", "python", "label", "menu", "screen",
        "call", "jump", "if", "elif", "else", "return", "camera", "layer",
        "window", "style", "text", "sprite", "add", "pause", "queue", "stop",
        "voice", "music", "sound", "default", "init", "for", "while", "in",
        "and", "or", "not", "pass",
    }

    # Paleta (la misma que usa PoseLab).
    _TOOL_CODE_COLORES = {
        "clave": "#7fb0ff",     # palabras clave
        "nombre": "#ffd479",    # nombres de imagen/objeto
        "funcion": "#c792ea",   # transforms y funciones
        "numero": "#e2a06a",    # números
        "texto": "#8fd18f",     # cadenas
        "otro": "#8a8f98",      # paréntesis, comas, operadores
    }

    _TOOL_CODE_RE = _tool_re.compile(
        r'(?P<texto>"[^"]*"|\'[^\']*\')'
        r'|(?P<funcion>[A-Za-z_][A-Za-z_0-9]*(?=\())'
        r'|(?P<numero>\d+\.\d+|\d+)(?![A-Za-z0-9_])'
        r'|(?P<palabra>[A-Za-z_0-9][A-Za-z_0-9]*)'
        r'|(?P<espacio>\s+)'
        r'|(?P<otro>.)'
    )

    def tool_codigo_rico(codigo):
        """Colorea una línea de código para mostrarla (no para copiarla)."""
        if not codigo:
            return ""
        partes = []
        anterior = ""
        for m in _TOOL_CODE_RE.finditer(codigo):
            tipo, txt = m.lastgroup, m.group()
            if tipo == "espacio":
                partes.append(txt)
                continue
            if tipo == "palabra":
                if txt in _TOOL_CODE_CLAVES:
                    tipo = "clave"
                elif anterior == "at":
                    tipo = "funcion"      # `at t11`: el nombre es un transform
                else:
                    tipo = "nombre"
            partes.append("{color=%s}%s{/color}" % (_TOOL_CODE_COLORES[tipo], txt))
            anterior = txt
        return "".join(partes)



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

    # ------------------------------------------------------------------
    # Secciones plegables (una abierta a la vez).
    # ------------------------------------------------------------------

    tool_sec_state = {"abierto": ""}

    def tool_sec_toggle(id):
        tool_sec_state["abierto"] = "" if tool_sec_state["abierto"] == id else id
        renpy.restart_interaction()


screen tool_dropdown(id, etiqueta, valor, opciones, destino, clave, despues=None,
                    columnas=1):

    $ _tool_dd_lab = next((lab for v, lab in opciones if v == valor), str(valor))
    $ _tool_dd_abierto = (tool_dd_state["abierto"] == id)
    # columnas: 1 = una opción por fila (default), 2 = dos columnas,
    # 0 = todas en una sola fila.
    $ _tool_dd_cols = len(opciones) if columnas == 0 else max(1, columnas)
    # El grid necesita las filas exactas: si sobran celdas, Ren'Py se queja.
    $ _tool_dd_rows = max(1, (len(opciones) + _tool_dd_cols - 1) // _tool_dd_cols)

    # Encabezado clickeable, en una línea: título a la izquierda y valor
    # elegido a la derecha.
    button:
        style "tool_dropdown_header"
        action Function(tool_dd_toggle, id)

        hbox:
            spacing 8
            xfill True

            text etiqueta style "tool_dropdown_header_text"

            # El frame ocupa el espacio que sobra: el valor queda a la
            # derecha sin depender de un ancho fijo.
            frame:
                background None
                xfill True

                text _tool_dd_lab style "tool_dropdown_value" xalign 1.0

    # Opciones: cada una en su propio recuadro, debajo del encabezado.
    #
    # Sin viewport: un viewport reserva su `ymaximum` aunque la lista sea
    # corta y dejaba un hueco enorme. Un vbox/grid toma solo el alto que
    # necesita.
    if _tool_dd_abierto:

        key "K_ESCAPE" action Function(tool_dd_cerrar)

        null height 4

        if _tool_dd_cols == 1:
            vbox:
                xfill True
                spacing 2

                for v, lab in opciones:
                    use tool_dropdown_opcion(lab, v == destino.get(clave),
                                            [SetDict(destino, clave, v),
                                            Function(tool_dd_cerrar)] + list(despues or []))
        else:
            # Varias columnas: el grid reparte por filas y las celdas
            # quedan alineadas (los botones toman el ancho de la columna).
            grid _tool_dd_cols _tool_dd_rows:
                allow_underfull True
                spacing 2

                for v, lab in opciones:
                    use tool_dropdown_opcion(lab, v == destino.get(clave),
                                            [SetDict(destino, clave, v),
                                            Function(tool_dd_cerrar)] + list(despues or []))

    # Aire entre apartados (el dropdown es un bloque dentro de un vbox).
    null height 4


# Una opción del dropdown (la usa `tool_dropdown`).
screen tool_dropdown_opcion(texto, elegida, accion):

    textbutton texto:
        style "tool_dropdown_item"
        selected elegida
        action accion


# Bloque plegable: el contenido va entre `use` y `transclude`.
#
#     use tool_section("mi_id", "Mi sección", "resumen"):
#         use tool_dropdown(...)
#
# `resumen` es un texto corto que se muestra a la derecha del título.
screen tool_section(id, titulo, resumen=""):

    $ _tool_sec_abierto = (tool_sec_state["abierto"] == id)

    button:
        style "tool_section_header"
        action Function(tool_sec_toggle, id)

        hbox:
            spacing 6
            xfill True

            # ASCII a proposito: la fuente del juego (Aller) no tiene las
            # flechasgeometricas y se verian como glifos vacios.
            text ("-" if _tool_sec_abierto else "+") style "tool_section_marker"
            text titulo style "tool_section_title"

            frame:
                background None
                xfill True

                text resumen style "tool_section_summary" xalign 1.0

    if _tool_sec_abierto:
        null height 4
        transclude
