## menu_screens.rpy
# Screens de los menús: principal y de pausa, separados y customizables.
#
# PARA EL MODDER:
#   - Cambia las `define` de abajo para personalizar fondos, layout y botones.
#   - Cada botón puede ser `textbutton` (texto) o `imagebutton` (imagen).
#     Pon tus assets en `gui/buttons/` (carpeta estándar) y sigue el ejemplo.
#   - Para deshabilitar el botón Language (y que no aparezca en el menú),
#     pon `enable_language_button = False`. El selector de idioma del
#     arranque (splash) NO se ve afectado.

# ============================================================================
# CONFIG DEL MODDER — MENÚS
# ============================================================================

# Fondo del frame de navegación del menú principal.
# Reemplaza por tu propio PNG (p. ej. "gui/buttons/mi_frame.png").
define gui.menu_nav_background = "gui/overlay/main_menu.png"

# Fondo del frame de navegación del menú de pausa.
define gui.game_nav_background = "gui/overlay/game_menu.png"

# ¿Mostrar el botón Language en el menú principal?
#   True  → se muestra (si hay traducciones cargadas)
#   False → se oculta (el idioma se elige igual en el splash al arrancar)
default enable_language_button = True

# Layout del menú de pausa (game_menu)
define gui.game_nav_xsize = 280          # ancho del panel de navegación
define gui.game_content_left_margin = 40  # margen izquierdo del contenido
define gui.game_content_right_margin = 20 # margen derecho del contenido

# Posición y espaciado general de los botones de navegación.
# (gui.navigation_xpos y gui.navigation_spacing se definen en gui.rpy)

# --- Menú principal: fondo, logo y efectos -----------------------------------

# El fondo del menú principal usa gui.main_menu_background (gui.rpy).

# Logo del menú principal.
define gui.main_menu_logo = "menu_logo"

# Partículas del menú principal (tag de imagen) y cuántas capas se muestran.
define gui.main_menu_particles = "menu_particles"
define gui.main_menu_particle_count = 4

# Fade final del menú principal.
define gui.main_menu_fade = "menu_fade"

# --- Sprites del menú principal ----------------------------------------------
# Cada entrada: (tag_imagen, x, y, zoom, z_anim)
#   x, y     → posición final (xcenter / ycenter)
#   zoom     → tamaño final
#   z_anim   → parámetro de la animación fly-in (altura inicial; normalmente = zoom)
# Para mover un sprite: cambia x/y/zoom.
# Para ocultarlo: quita su línea.
# Para añadir un sprite nuevo: define tu `image` (en splash.rpy o un .rpy tuyo)
# y añade una línea aquí con su tag.
default menu_sprites = [
    ("menu_art_y", 600, 335, 0.60, 0.54),
    ("menu_art_n", 750, 385, 0.58, 0.58),
    ("menu_art_s", 510, 500, 0.68, 0.68),
    ("menu_art_m", 1000, 640, 1.00, 1.00),
]

# --- Quick Menu (menú rápido durante el juego) --------------------------------

# ¿Mostrar el quick_menu durante el juego? (True/False).
# NOTA: la variable global `quick_menu` (que controla el menú de pausa en
# options.rpy) se mantiene intacta; esto solo controla si se muestra el screen.
default enable_quick_menu = True

# Esquina donde se coloca el quick_menu (hbox). Valores:
#   "bottom"      → abajo centrado (default)
#   "top"         → arriba centrado
#   "topleft"     → esquina superior izquierda
#   "topright"    → esquina superior derecha
#   "bottomleft"  → esquina inferior izquierda
#   "bottomright" → esquina inferior derecha
default quick_menu_corner = "bottom"

# Separación entre los botones del quick_menu.
default quick_menu_spacing = 10

# ============================================================================
# ANIMACIÓN DE BOTONES DE NAVEGACIÓN
# ============================================================================

# Desplazamiento y duración del "nudge" al pasar el mouse por un botón.
# Ajusta estos valores para cambiar la animación.
define nav_hover_offset = 18      # píxeles que se desplaza hacia la derecha (hover)
define nav_hover_time = 0.15      # duración de la animación (segundos)

# Animación de hover: el botón se desliza suavemente al pasar el mouse.
# Se desactiva si el jugador apaga la animación en Ajustes.
# Se aplica a cada textbutton con:  at nav_button_anim
transform nav_button_anim:
    on idle:
        easeout nav_hover_time xoffset 0
    on hover:
        easein nav_hover_time xoffset (nav_hover_offset if persistent.menu_nav_anim else 0)


# ============================================================================
# NAVEGACIÓN DEL MENÚ PRINCIPAL
# ============================================================================

screen main_navigation():

    # Frame de fondo de los botones (cambiable con gui.menu_nav_background).
    frame:
        style "main_menu_frame"

        vbox:
            style_prefix "main_navigation"

            xpos gui.navigation_xpos
            xoffset -50
            yalign 0.8

            spacing gui.navigation_spacing

            # --- Ejemplo: botón de texto -----------------------------------
            textbutton _("New Game") action If(persistent.playername, true=Start(), false=Show(screen="name_input", message="Please enter your name", ok_action=Function(FinishEnterName))) at nav_button_anim

            # --- Ejemplo: botón con imagen (imagebutton) --------------------
            # Para usarlo: descomenta estas líneas y comenta el textbutton.
            # Pon tus PNGs en gui/buttons/ y cambia las rutas.
            #imagebutton:
            #    idle "gui/buttons/btn_example_idle.png"
            #    hover "gui/buttons/btn_example_hover.png"
            #    xalign 0.5
            #    action Start()

            textbutton _("Load Game") action [ShowMenu("load"), SensitiveIf(renpy.get_screen("load") == None)] at nav_button_anim

            textbutton _("Settings") action [ShowMenu("preferences"), SensitiveIf(renpy.get_screen("preferences") == None)] at nav_button_anim

            if renpy.variant("pc"):
                textbutton _("Quit") action Quit(confirm=True) at nav_button_anim


# ============================================================================
# NAVEGACIÓN DEL MENÚ DE PAUSA
# ============================================================================

screen game_navigation():

    frame:
        style "game_menu_nav_frame"

        vbox:
            style_prefix "game_navigation"

            xpos gui.navigation_xpos
            xoffset -50
            yalign 0.8

            spacing gui.navigation_spacing

            textbutton _("History") action [ShowMenu("history"), SensitiveIf(renpy.get_screen("history") == None)] at nav_button_anim

            textbutton _("Save Game") action [ShowMenu("save"), SensitiveIf(renpy.get_screen("save") == None)] at nav_button_anim

            textbutton _("Load Game") action [ShowMenu("load"), SensitiveIf(renpy.get_screen("load") == None)] at nav_button_anim

            if _in_replay:
                textbutton _("End Replay") action EndReplay(confirm=True) at nav_button_anim
            else:
                textbutton _("Main Menu") action MainMenu(confirm=True) at nav_button_anim

            textbutton _("Settings") action [ShowMenu("preferences"), SensitiveIf(renpy.get_screen("preferences") == None)] at nav_button_anim

            if renpy.variant("pc"):
                textbutton _("Quit") action Quit(confirm=True) at nav_button_anim


# ============================================================================
# MENÚ PRINCIPAL
# ============================================================================

screen main_menu():

    # Esto asegura que cualquier otra screen de menu sea reemplazada.
    tag menu

    style_prefix "main_menu"

    # Fondo del menú (configurable con gui.main_menu_background).
    add gui.main_menu_background

    # Sprites de personaje (configurables con menu_sprites).
    # Cada entrada: (tag, x, y, zoom, z_anim) → posición + animación fly-in.
    for img, x, y, zoom, z in menu_sprites:
        add img at transform:
            subpixel True
            xcenter x ycenter y zoom zoom
            menu_art_move(z, x, zoom)

    ## La sentencia use incluye la screen de navegacion dentro de esta.
    use main_navigation

    # Partículas del menú (configurables).
    if gui.main_menu_particle_count > 0 and persistent.menu_particles:
        for i in range(gui.main_menu_particle_count):
            add gui.main_menu_particles

    # Fade final del menú.
    add gui.main_menu_fade

    # Logo del menú (configurable; se muestra tras el fade, como en el
    # template original).
    add gui.main_menu_logo

    if gui.show_name:

        vbox:
            text "[config.name!t]":
                style "main_menu_title"

            text "[config.version]":
                style "main_menu_version"

    # Botones fuera de la columna de navegación.
    # (Sin nav_button_anim: su deslizamiento a la derecha desbordaría el borde.)

    # Herramientas (dev): esquina superior derecha.
    if config.developer:
        hbox:
            xalign 1.0 yalign 0.0
            xoffset -20 yoffset 20
            textbutton _("Herramientas"):
                style "main_navigation_button"
                text_style "main_navigation_button_text"
                action Show("complements")

    # Idioma: esquina inferior derecha, justo encima del nombre del juego.
    if enable_language_button and enable_languages and translations:
        hbox:
            xalign 1.0 yalign 1.0
            xoffset -20 yoffset -85
            textbutton _("Language"):
                style "main_navigation_button"
                text_style "main_navigation_button_text"
                action Show("choose_language")

    key "K_ESCAPE" action Quit(confirm=False)


# ============================================================================
# MENÚ DE PAUSA (game_menu)
# ============================================================================

screen game_menu(title, scroll=None):

    # Anade los fondos.
    if main_menu:
        add gui.main_menu_background
    else:
        key "mouseup_3" action Return()
        add gui.game_menu_background

    style_prefix "game_menu"

    frame:
        style "game_menu_outer_frame"

        hbox:

            # Reserva espacio para la seccion de navegacion.
            frame:
                style "game_menu_navigation_frame"

            frame:
                style "game_menu_content_frame"

                if scroll == "viewport":

                    viewport:
                        scrollbars "vertical"
                        mousewheel True
                        draggable True
                        yinitial 1.0

                        side_yfill True

                        vbox:
                            transclude

                elif scroll == "vpgrid":

                    vpgrid:
                        cols 1
                        yinitial 1.0

                        scrollbars "vertical"
                        mousewheel True
                        draggable True

                        side_yfill True

                        transclude

                else:

                    transclude

    use game_navigation

    # Aviso de musica de pausa (solo dev). Ver screens.rpy.
    use pause_music_notify

    textbutton _("Return"):
        style "return_button"

        action Return()

    label title

    if main_menu:
        key "game_menu" action ShowMenu("main_menu")


# ============================================================================
# ESTILOS
# ============================================================================

# --- Menú principal: navegación -------------------------------------------

style main_navigation_button is gui_button
style main_navigation_button_text is gui_button_text

style main_navigation_button:
    size_group "navigation"
    properties gui.button_properties("main_navigation")
    hover_sound gui.hover_sound
    activate_sound gui.activate_sound

style main_navigation_button_text:
    properties gui.button_text_properties("main_navigation")
    font "gui/font/RifficFree-Bold.ttf"
    color "#fff"
    outlines [(4, text_outline_color, 0, 0), (2, text_outline_color, 2, 2)]
    hover_outlines [(4, "#fac", 0, 0), (2, "#fac", 2, 2)]
    insensitive_outlines [(4, "#fce", 0, 0), (2, "#fce", 2, 2)]

# --- Menú de pausa: navegación ----------------------------------------------

style game_navigation_button is gui_button
style game_navigation_button_text is gui_button_text

style game_navigation_button:
    size_group "navigation"
    properties gui.button_properties("game_navigation")
    hover_sound gui.hover_sound
    activate_sound gui.activate_sound

style game_navigation_button_text:
    properties gui.button_text_properties("game_navigation")
    font "gui/font/RifficFree-Bold.ttf"
    color "#fff"
    outlines [(4, text_outline_color, 0, 0), (2, text_outline_color, 2, 2)]
    hover_outlines [(4, "#fac", 0, 0), (2, "#fac", 2, 2)]
    insensitive_outlines [(4, "#fce", 0, 0), (2, "#fce", 2, 2)]

# --- Navegación genérica (pestañas de Ajustes, Sí/No del confirm, final) ------
# Hereda del menú principal para que esos botones se vean igual que la
# navegación del menú (fuente RifficFree-Bold, outlines blancos/#fac/#fce).

style navigation_button is main_navigation_button
style navigation_button_text is main_navigation_button_text

# --- Frame del menú principal ------------------------------------------------

style main_menu_frame is empty
style main_menu_vbox is vbox
style main_menu_text is gui_text
style main_menu_title is main_menu_text
style main_menu_version is main_menu_text:
    color "#000000"
    size 16
    outlines []

style main_menu_frame:
    xsize 310
    yfill True

    background gui.menu_nav_background

style main_menu_vbox:
    xalign 1.0
    xoffset -20
    xmaximum 800
    yalign 1.0
    yoffset -20

style main_menu_text:
    xalign 1.0

    layout "subtitle"
    text_align 1.0
    color gui.accent_color

style main_menu_title:
    size gui.title_text_size

# --- Frame del menú de pausa ------------------------------------------------

style game_menu_outer_frame is empty
style game_menu_navigation_frame is empty
style game_menu_content_frame is empty
style game_menu_viewport is gui_viewport
style game_menu_side is gui_side
style game_menu_scrollbar is gui_vscrollbar

style game_menu_label is gui_label
style game_menu_label_text is gui_label_text

style return_button is game_navigation_button
style return_button_text is game_navigation_button_text

style game_menu_nav_frame is empty:
    xsize gui.game_nav_xsize
    yfill True

style game_menu_outer_frame:
    bottom_padding 30
    top_padding 120

    background gui.game_nav_background

style game_menu_navigation_frame:
    xsize gui.game_nav_xsize
    yfill True

style game_menu_content_frame:
    left_margin gui.game_content_left_margin
    right_margin gui.game_content_right_margin
    top_margin 10

style game_menu_viewport:
    xsize 920

style game_menu_vscrollbar:
    unscrollable gui.unscrollable

style game_menu_side:
    spacing 10

style game_menu_label:
    xpos 50
    ysize 120

style game_menu_label_text:
    font "gui/font/RifficFree-Bold.ttf"
    size gui.title_text_size
    color "#fff"
    outlines [(6, text_outline_color, 0, 0), (3, text_outline_color, 2, 2)]
    yalign 0.5

style return_button:
    xpos gui.navigation_xpos
    yalign 1.0
    yoffset -30

# ============================================================================
# QUICK MENU (menú rápido durante el juego)
# ============================================================================

screen quick_menu():

    # Asegura que aparezca por encima de las demas screens.
    zorder 100

    if enable_quick_menu and quick_menu and persistent.show_quick_menu:

        # Anade el menu rapido dentro del juego.
        hbox:
            style_prefix "quick"

            # Posición según la esquina elegida (quick_menu_corner).
            if quick_menu_corner == "top":
                xalign 0.5
                yalign 0.005
            elif quick_menu_corner == "topleft":
                xalign 0.0
                yalign 0.0
            elif quick_menu_corner == "topright":
                xalign 1.0
                yalign 0.0
            elif quick_menu_corner == "bottomleft":
                xalign 0.0
                yalign 1.0
            elif quick_menu_corner == "bottomright":
                xalign 1.0
                yalign 1.0
            else:
                # "bottom" (default)
                xalign 0.5
                yalign 0.995

            spacing quick_menu_spacing

            textbutton _("Back") action Rollback()

            textbutton _("History") action ShowMenu('history')
            textbutton _("Skip") action Skip() alternate Skip(fast=True, confirm=True)
            textbutton _("Auto") action Preference("auto-forward", "toggle")
            textbutton _("Save") action ShowMenu('save')
            textbutton _("Load") action ShowMenu('load')
            textbutton _("Q.Save") action QuickSave()
            textbutton _("Q.Load") action QuickLoad()
            textbutton _("Settings") action ShowMenu('preferences')

            # --- Ejemplo: botón con imagen (imagebutton) ----------------------
            # Para usarlo: descomenta estas líneas. Pon tus PNGs en gui/buttons/
            # y cambia las rutas.
            #imagebutton:
            #    idle "gui/buttons/btn_example_idle.png"
            #    hover "gui/buttons/btn_example_hover.png"
            #    action ShowMenu('save')


# Este default controla la variable global `quick_menu` que el juego usa para
# saber si el quick menu está visible (p. ej. en options.rpy). No eliminar.
default quick_menu = True

# --- Quick Menu: estilos ------------------------------------------------------

style quick_button:
    properties gui.button_properties("quick_button")
    activate_sound gui.activate_sound

style quick_button_text:
    properties gui.button_text_properties("quick_button")
    outlines []
