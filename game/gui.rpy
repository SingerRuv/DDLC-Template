## gui.rpy

# Este archivo define todas las posiciones, colores, rutas y demas de la interfaz
# grafica de DDLC.

## NOTA: para configurar ajustes de Android, baja hasta el bloque init python
## en la linea 379

init -2 python:
    # Esto define la resolucion de DDLC en 1280x720p
    gui.init(1280, 720)

## Sonidos de la GUI
# Estas variables definen los efectos de sonido de los elementos de la GUI.
define -2 gui.hover_sound = "gui/sfx/hover.ogg" # Sonido al pasar el mouse
define -2 gui.activate_sound = "gui/sfx/select.ogg" # Sonido al hacer clic

## Colores!
# Estas variables definen el color del texto de DDLC en el juego.

# Este color se usa para etiquetas y resaltar texto.
define -2 gui.accent_color = '#ffffff'

# Este color se usa en un boton de texto cuando no esta seleccionado ni con el mouse encima.
define -2 gui.idle_color = '#aaaaaa'

# El color small se usa para texto pequeno, que necesita ser mas claro/oscuro para
# lograr el mismo efecto.
define -2 gui.idle_small_color = '#333'

# Este color se usa para botones y barras con el mouse encima.
define -2 gui.hover_color = '#cc6699'

# Este color se usa en un boton de texto cuando esta seleccionado pero no enfocado.
define -2 gui.selected_color = '#bb5588'

# Este color se usa en un boton de texto cuando no se puede seleccionar.
define -2 gui.insensitive_color = '#aaaaaa7f'

# Estos colores se usan para barras no llenadas del todo. No se usan
# directamente, sino al regenerar las imagenes de las barras.
define -2 gui.muted_color = '#6666a3'
define -2 gui.hover_muted_color = '#9999c1'

# Este color se usa para el dialogo y el texto de las opciones del menu.
define -2 gui.text_color = '#ffffff'
define -2 gui.interface_text_color = '#ffffff'

# Fuentes y tamanos de fuente
# Estas variables definen la fuente y su tamano para el texto de DDLC en el juego.

# Esta fuente se usa para el texto dentro del juego.
define -2 gui.default_font = "gui/font/Aller_Rg.ttf"

# Esta fuente se usa para los nombres de los personajes.
define -2 gui.name_font = "gui/font/RifficFree-Bold.ttf"

# Esta fuente se usa para el texto fuera del juego.
define -2 gui.interface_font = "gui/font/Aller_Rg.ttf"

# El tamano del texto de dialogo normal.
define -2 gui.text_size = 24

# Esto determina el tamano del texto de los nombres de personajes.
define -2 gui.name_text_size = 24

# Esto determina el tamano del texto de la interfaz del juego.
define -2 gui.interface_text_size = 24

# Esto determina el tamano del texto de las etiquetas de la interfaz.
define -2 gui.label_text_size = 28

# Esto determina el tamano del texto de la pantalla de notificaciones.
define -2 gui.notify_text_size = 16

# Esto determina el tamano del texto del titulo del juego abajo a la derecha.
define -2 gui.title_text_size = 38

## Menu principal y menu de pausa
# Estas variables definen que se muestra en el menu.

# Esto define el fondo del menu principal
define -2 gui.main_menu_background = "menu_bg"

# Esto define el fondo del menu de pausa
define -2 gui.game_menu_background = "game_menu_bg"

## Dialogo
# Estas variables definen la posicion y colocacion del cuadro de dialogo en el juego.

# Esto controla la altura del cuadro de texto que contiene el dialogo.
define -2 gui.textbox_height = 182

# Esto controla la colocacion vertical del cuadro de texto en pantalla.
# 0.0 es arriba, 0.5 el centro y 1.0 abajo.
define -2 gui.textbox_yalign = 0.99

# Esto controla la colocacion del nombre del personaje que habla.
define gui.name_xpos = 350
define gui.name_ypos = -3

# Esto controla la alineacion horizontal del nombre del personaje.
define gui.name_xalign = 0.5

# Esto controla el ancho, alto y bordes de la caja que contiene el
# nombre de los personajes.
define gui.namebox_width = 168
define gui.namebox_height = 39

# Esto controla los bordes de la caja del nombre en
# orden izquierda, arriba, derecha, abajo.
define gui.namebox_borders = Borders(5, 5, 5, 2)

# Esto controla la visualizacion del marco que contiene el cuadro de nombre.
define gui.namebox_tile = False

# Esto controla la colocacion del dialogo respecto al cuadro de texto.
define gui.text_xpos = 268
define gui.text_ypos = 62

# Esto controla el ancho maximo del texto de dialogo.
define gui.text_width = 744

# Esto controla la alineacion horizontal del texto de dialogo.
define gui.text_xalign = 0.0

## Botones
# Estas variables definen los botones dentro del juego.

# Esto controla el ancho y alto de un boton.
# Si se declara None, Ren'Py calcula su tamano automaticamente.
define gui.button_width = None
define gui.button_height = 36

# Esto controla los bordes de cada lado del boton
# en orden izquierda, arriba, derecha, abajo.
define gui.button_borders = Borders(4, 4, 4, 4)

# Esto controla si el fondo del boton se mosaica y aumenta/disminuye
# su tamano, o se centra y escala.
#  True - Fondo mosaico | False - Fondo centrado.
define gui.button_tile = False

# Esto controla la fuente que usara el boton.
define gui.button_text_font = gui.interface_font

# Esto controla el tamano de fuente del texto del boton.
define gui.button_text_size = gui.interface_text_size

# Esto controla el color del texto del boton en sus distintos estados.
define gui.button_text_idle_color = gui.idle_color
define gui.button_text_hover_color = gui.hover_color
define gui.button_text_selected_color = gui.selected_color
define gui.button_text_insensitive_color = gui.insensitive_color

# Esto controla la alineacion horizontal del texto del boton.
define gui.button_text_xalign = 0.0

# Esto controla los bordes de cada lado de los botones
# check/radio en orden izquierda, arriba, derecha, abajo.
define gui.radio_button_borders = Borders(28, 4, 4, 4)
define gui.check_button_borders = Borders(28, 4, 4, 4)

# Esto controla la alineacion horizontal del boton de confirmar.
define gui.confirm_button_text_xalign = 0.5

# Esto controla los bordes de cada lado de los botones de pagina
# en orden izquierda, arriba, derecha, abajo.
define gui.page_button_borders = Borders(10, 4, 10, 4)

## Botones rapidos
# Estas variables definen los botones del menu rapido y su texto.

define gui.quick_button_text_size = 14

define gui.quick_button_text_idle_color = "#522"
define gui.quick_button_text_hover_color = "#fcc"
define gui.quick_button_text_selected_color = gui.accent_color
define gui.quick_button_text_insensitive_color = "#a66"

## Botones de opcion
# Estas variables definen los botones de las opciones (menu).

define gui.choice_button_width = 420
define gui.choice_button_height = None

define gui.choice_button_tile = False

define gui.choice_button_borders = Borders(100, 5, 100, 5)

define gui.choice_button_text_font = gui.default_font
define gui.choice_button_text_size = gui.text_size
define gui.choice_button_text_xalign = 0.5

define gui.choice_button_text_idle_color = "#000"
define gui.choice_button_text_hover_color = "#fa9"

## Botones de ranura de archivo
# Esto controla los botones de ranura en el menu de guardar/cargar. 

define gui.slot_button_width = 276
define gui.slot_button_height = 206

define gui.slot_button_borders = Borders(10, 10, 10, 10)

define gui.slot_button_text_size = 14
define gui.slot_button_text_xalign = 0.5
define gui.slot_button_text_idle_color = gui.idle_small_color
define gui.slot_button_text_hover_color = gui.hover_color

# Esto controla el ancho y alto de las miniaturas de las partidas guardadas.
define config.thumbnail_width = 256
define config.thumbnail_height = 144

# Esto controla el numero de columnas y filas de la pagina de ranuras.
define gui.file_slot_cols = 3
define gui.file_slot_rows = 2

## Posicionamiento y espaciado
# Estas variables controlan la posicion y el espaciado de varios elementos
# de la interfaz.

define gui.navigation_xpos = 80
define gui.skip_ypos = 10
define gui.notify_ypos = 45

# Esto controla el espaciado entre cada opcion en la pantalla de opciones.
define gui.choice_spacing = 22

# Esto controla el espaciado entre cada opcion de navegacion.
define gui.navigation_spacing = 6

# Esto controla el espaciado entre cada preferencia y boton de preferencia
# en la pantalla de ajustes.
define gui.pref_spacing = 10
define gui.pref_button_spacing = 0

# Esto controla el espaciado entre cada opcion de pagina.
define gui.page_spacing = 0

# Esto controla el espaciado entre cada ranura en la pantalla de guardar/cargar.
define gui.slot_spacing = 10

## Marcos
# Estas variables controlan los bordes de los marcos, como el aviso de confirmar.

# Esto controla el tamano de marco por defecto de los avisos.
define gui.frame_borders = Borders(4, 4, 4, 4)

# Esto controla el tamano de marco de los avisos de confirmar.
define gui.confirm_frame_borders = Borders(40, 40, 40, 40)

# Esto controla el tamano de marco de los avisos de skip.
define gui.skip_frame_borders = Borders(16, 5, 50, 5)

# Esto controla el tamano de marco de las notificaciones.
define gui.notify_frame_borders = Borders(16, 5, 40, 5)

# Esto controla si los marcos se mosaican o escalan.
#  True - Fondo mosaico | False - Fondo centrado.
define gui.frame_tile = False

## Barras, barras de desplazamiento y deslizadores

# Estas variables controlan el aspecto y tamano de barras, barras de desplazamiento y deslizadores.

# Esto controla el tamano de barras, barras de desplazamiento y deslizadores.
define gui.bar_size = 36
define gui.scrollbar_size = 12
define gui.slider_size = 30

# Esto controla si los marcos se mosaican o escalan.
#  True - Fondo mosaico | False - Fondo centrado.
define gui.bar_tile = False
define gui.scrollbar_tile = False
define gui.slider_tile = False

# Esto controla el tamano de marco por defecto de barras y deslizadores.
define gui.bar_borders = Borders(4, 4, 4, 4)
define gui.scrollbar_borders = Borders(4, 4, 4, 4)
define gui.slider_borders = Borders(4, 4, 4, 4)

# Esto controla el tamano de marco por defecto de barras y deslizadores verticales.
define gui.vbar_borders = Borders(4, 4, 4, 4)
define gui.vscrollbar_borders = Borders(4, 4, 4, 4)
define gui.vslider_borders = Borders(4, 4, 4, 4)

# Esto controla que hacer con las barras que no se pueden desplazar.
#   "hide" - oculta la barra | None - mantiene la barra visible
define gui.unscrollable = "hide"

## Historial
# Estas variables controlan como se muestra la pantalla de historial en el juego.

# Esto controla cuantas lineas de dialogo guarda Ren'Py
# en el historial del jugador.
define config.history_length = 50

# Esto controla la altura de la caja del historial.
# None hara variar la altura a costa del rendimiento.
define gui.history_height = None

# Esto controla la posicion, ancho y alineacion del nombre de los personajes
# en el historial.
define gui.history_name_xpos = 150
define gui.history_name_ypos = 0
define gui.history_name_width = 150
define gui.history_name_xalign = 1.0

# Esto controla la posicion, ancho y alineacion del dialogo de los personajes
# en el historial.
define gui.history_text_xpos = 170
define gui.history_text_ypos = 5
define gui.history_text_width = 740
define gui.history_text_xalign = 0.0

## NVL
# Estas variables controlan el aspecto de la pantalla NVL.

# Esto controla el tamano de marco por defecto de la ventana NVL.
define gui.nvl_borders = Borders(0, 10, 0, 20)

# Esto controla la altura de la entrada de dialogo NVL.
#   None permitira que cada entrada NVL varíe de tamano.
define gui.nvl_height = 115

# Esto controla el espaciado de las entradas de dialogo NVL.
define gui.nvl_spacing = 10

# Esto controla la posicion, ancho y alineacion del nombre de los personajes
# en la pantalla NVL.
define gui.nvl_name_xpos = 430
define gui.nvl_name_ypos = 0
define gui.nvl_name_width = 150
define gui.nvl_name_xalign = 1.0

# Esto controla la posicion, ancho y alineacion del dialogo de los personajes
# en la pantalla NVL.
define gui.nvl_text_xpos = 450
define gui.nvl_text_ypos = 8
define gui.nvl_text_width = 590
define gui.nvl_text_xalign = 0.0

# Esto controla la posicion, ancho y alineacion del dialogo del narrador
# en la pantalla NVL.
define gui.nvl_thought_xpos = 240
define gui.nvl_thought_ypos = 0
define gui.nvl_thought_width = 780
define gui.nvl_thought_xalign = 0.0

# Esto controla la posicion de los botones de la pantalla NVL.
define gui.nvl_button_xpos = 450
define gui.nvl_button_xalign = 0.0

## Telefonos y tablets
# Estas variables controlan como se muestra DDLC en plataformas moviles.

init python:

    # Aumenta el tamano de los botones rapidos para que sean mas faciles de tocar
    # en tablets y telefonos.
    if renpy.variant("touch"):

        gui.quick_button_borders = Borders(20, 14, 20, 0)

    # Cambia el tamano y espaciado de varios elementos de la GUI para que sean
    # facilmente visibles en dispositivos pequenos.
    if renpy.variant("small"):

        ## Tamano de fuente
        gui.text_size = 24
        gui.name_text_size = 24
        gui.notify_text_size = 24
        gui.interface_text_size = 26
        gui.button_text_size = 26
        gui.label_text_size = 28

        ## Posiciones, alturas y alineaciones del cuadro de dialogo/nombre.
        gui.textbox_height = 182
        gui.name_xpos = 350
        gui.text_xpos = 268
        gui.text_ypos = 62
        gui.text_width = 744
        gui.text_xalign = 0.0

        ## Ancho del boton de opcion
        gui.choice_button_width = 420

        ## Espaciado
        gui.navigation_spacing = 6
        gui.pref_button_spacing = 10

        ## Historial 
        gui.history_height = None
        gui.history_text_width = 740

        ## Ranuras de guardar/cargar
        gui.file_slot_cols = 3
        gui.file_slot_rows = 2

        ## NVL
        gui.nvl_height = 115

        gui.nvl_name_width = 150
        gui.nvl_name_xpos = 430

        gui.nvl_text_width = 590
        gui.nvl_text_xpos = 450
        gui.nvl_text_ypos = 8

        gui.nvl_thought_width = 780
        gui.nvl_thought_xpos = 240

        gui.nvl_button_width = 1240
        gui.nvl_button_xpos = 450

        ## Menu rapido
        gui.quick_button_text_size = 14
