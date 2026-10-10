# ¡Este archivo define cosas importantes para tu juego!

# Esta variable declara si se activan las Herramientas de Desarrollador de Ren'Py.
# Con "auto", Ren'Py la activa al lanzar desde el launcher y la desactiva
# sola en el build publicado. (Para forzarla, usa True/False.)
define config.developer = "auto"

# Si se permiten cuadrículas incompletas en el juego.
define config.allow_underfull_grids = True

## Fondos

image black = "#000000"
image dark = "#000000e4"
image darkred = "#110000c8"
image white = "#ffffff"

# Esta imagen se usa en el menú fantasma (ghost menu) del template original.
image end:
    truecenter
    "gui/end.png"

image bg club_day = "images/bg/club.png"

## Fondos de escenario (los PNGs viven en images/bg/)
# Para fondos/CG/audio propios, poné los archivos en 'game/mod_assets/' y
# definílos aquí apuntando a esa ruta, p. ej.:
#   image bg mi_cuarto = "mod_assets/images/bg/mi_cuarto.png"

image bg bedroom = "images/bg/bedroom.png"
image bg corridor = "images/bg/corridor.png"
image bg class = "images/bg/class.png"
image bg closet = "images/bg/closet.png"
image bg house = "images/bg/house.png"
image bg kitchen = "images/bg/kitchen.png"
image bg residential = "images/bg/residential.png"
image bg sayori_bedroom = "images/bg/sayori_bedroom.png"
image bg club_skill = "images/bg/club-skill.png"

## Variables de personajes
# Los sprites de cada personaje se declaran en 'definitions/sprites.rpy' con
# 'image' + 'im.Composite' (sistema Bronya). Los DynamicCharacter usan el tag
# del personaje (sayori, monika, natsuki, yuri) para mostrar esos sprites.

define narrator = Character(ctc="ctc", ctc_position="fixed")
define mc = DynamicCharacter('player', what_prefix='"', what_suffix='"', ctc="ctc", ctc_position="fixed")
define s = DynamicCharacter('s_name', image='sayori', what_prefix='"', what_suffix='"', ctc="ctc", ctc_position="fixed")
define m = DynamicCharacter('m_name', image='monika', what_prefix='"', what_suffix='"', ctc="ctc", ctc_position="fixed")
define n = DynamicCharacter('n_name', image='natsuki', what_prefix='"', what_suffix='"', ctc="ctc", ctc_position="fixed")
define y = DynamicCharacter('y_name', image='yuri', what_prefix='"', what_suffix='"', ctc="ctc", ctc_position="fixed")

# Esta variable determina si se le permite al jugador omitir pausas.
define _dismiss_pause = config.developer

## Variables
# Variables que persisten entre partidas.

default persistent.uncensored_mode = False
default persistent.enable_discord = False
default persistent.playername = ""
default player = persistent.playername

# Preferencias de interfaz del jugador (Ajustes → Template Settings).
default persistent.show_quick_menu = True   # Mostrar el menú rápido durante el juego
default persistent.menu_nav_anim = True     # Animación hover de los botones del menú
default persistent.menu_particles = True    # Partículas del menú principal

# Nombres de los personajes (los DynamicCharacter usan estas variables).
default s_name = "Sayori"
default m_name = "Monika"
default n_name = "Natsuki"
default y_name = "Yuri"

# Capítulo actual de la historia (lo usa el guion para organizar el flujo).
default chapter = 0

# Si Sayori está muerta (usado por escenas especiales). Dejar como está.
default in_sayori_kill = None
