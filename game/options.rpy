## options.rpy
# Este archivo personaliza que es tu juego y como arranca y se compila!

# Esto controla como se llama tu juego.
define config.name = "DDLC DokifileModTemplate"

# Esto controla si quieres que el nombre del juego se vea en el menu principal.
# Si el nombre es largo, se sugiere desactivarlo.
define gui.show_name = True

# Esto controla el numero de version de tu juego.
define config.version = "0.0.0"

# Esto controla el nombre del build al empaquetar tu juego
# en el Launcher de Ren'Py.
# Nota:
#   El nombre de build es solo ASCII, sin numeros, espacios ni punto y coma.
#   Ejemplo: Mi Nuevo Juego -> MiNuevoJuego
define build.name = "DDLCDokifileModTemplate"

# Esto configura si tu juego tiene efectos de sonido.
define config.has_sound = True

# Esto configura si tu juego tiene musica.
define config.has_music = True

# Esto configura si tu juego tiene voces.
define config.has_voice = False

# Esto configura que musica suena al arrancar tu juego y en el
# menu principal.
define config.main_menu_music = audio.t1

# Estas variables controlan los efectos de transicion al entrar y salir
# de un menu.
#   config.enter_transition controla el efecto al entrar al menu del juego.
#   config.exit_transition controla el efecto al volver al juego.
#   Dissolve(X) disuelve el menu o la ultima pantalla durante X segundos.
define config.enter_transition = Dissolve(.2)
define config.exit_transition = Dissolve(.2)

# Esto controla el efecto de transicion tras cargar la partida.
define config.after_load_transition = None

# Esto controla el efecto de transicion cuando el juego llega al final de su historia.
define config.end_game_transition = Dissolve(.5)

# Esto controla el cuadro de texto que usan los personajes para hablar.
#   "auto" oculta el cuadro durante las escenas y lo muestra cuando alguien habla
#   "show" muestra el cuadro siempre
#   "hide" solo muestra el dialogo cuando un personaje habla.
define config.window = "auto"

# Esto controla los efectos de transicion del cuadro de texto.
define config.window_show_transition = Dissolve(.2)
define config.window_hide_transition = Dissolve(.2)

# Esto define la velocidad del texto de tu juego.
default preferences.text_cps = 50

# Esto controla la velocidad de avance automatico del texto.
default preferences.afm_time = 15

# Esto controla el nivel de audio de tu juego.
default preferences.music_volume = 0.75
default preferences.sfx_volume = 0.75

# Esto controla el nombre de la carpeta de guardado de tu juego.
# Donde encontrar tus partidas:
#   Windows: %AppData%/RenPy/
#   macOS: $HOME/Library/RenPy/ (desoculta la carpeta Library)
#   Linux: $HOME/.renpy/
define config.save_directory = "DDLCDokifileModTemplate"

# Esto controla el icono de la ventana de tu juego.
define config.window_icon = "gui/window_icon.png"

# Esto controla si tu juego permite al jugador saltar dialogo.
define config.allow_skipping = True

# Esto controla si tu juego guarda automaticamente.
define config.has_autosave = False

# Esto controla si tu juego guarda automaticamente al salir.
define config.autosave_on_quit = False

# Esto controla cuantas ranuras puede usar el auto-guardado.
define config.autosave_slots = 0

# Esto controla si el jugador puede retroceder al dialogo anterior en el juego.
define config.rollback_enabled = config.developer

# Estas variables controlan la colocacion de capas de screens, imagenes y mas.
# Se recomienda encarecidamente no tocar estas variables.
define config.layers = [ 'master', 'transient', 'screens', 'overlay', 'front' ]
define config.image_cache_size = 64
define config.predict_statements = 50
define config.menu_clear_layers = ["front"]
define config.gl_test_image = "white"

init python:
    if len(renpy.loadsave.location.locations) > 1: del(renpy.loadsave.location.locations[1])
    renpy.game.preferences.pad_enabled = False

    def replace_text(s):
        s = s.replace('--', u'\u2014')
        s = s.replace(' - ', u'\u2014')
        return s
    config.replace_text = replace_text

    def game_menu_check():
        if quick_menu: renpy.call_in_new_context('_game_menu')
    config.game_menu_action = game_menu_check

    # Pedir siempre confirmacion al salir (boton X de la ventana).
    config.quit_action = Quit(confirm=True)

    # Variable que usa after_load para restaurar config.allow_skipping despues de
    # que el splash lo desactive.
    allow_skipping = True

## Configuración del build ####################################################
##
## Esta seccion controla como Ren'Py convierte tu proyecto en archivos de distribucion.

init python:
    # Estas variables declaran los paquetes para compilar tu juego.
    build.package("DDLCDokifileModTemplate", 'zip', 'windows linux mac renpy mod',
        description="Ren'Py 8 Game")

    # Estas variables declaran los archivos que se crearan para tu juego empaquetado.
    # Para anadir otro archivo, crea una variable build.archive como en este ejemplo:
    build.archive("scripts", 'all')

    #############################################################
    # Estas variables clasifican archivos para el empaquetado.
    # Asegurate de anadir 'all' a tu build.classify si planeas
    # compilar tu juego en Android, como en este ejemplo.
    #   Ejemplo: build.classify("game/**.pdf", "scripts all")
    build.classify("game/presplash.png", "scripts all")
    build.classify("game/**.rpyc", "scripts all")
    build.classify("game/README.md", None)
    build.classify("game/**/README.md", None)
    build.classify("game/**.txt", "scripts all")
    build.classify("game/tl/**", "scripts all") ## Carpeta de traducciones

    build.classify('**~', None)
    build.classify('**.bak', None)
    build.classify('**/.**', None)
    build.classify('**#**', None)
    build.classify('**/thumbs.db', None)
    build.classify('**.rpy', None)
    build.classify('**.psd', None)
    build.classify('**.sublime-project', None)
    build.classify('**.sublime-workspace', None)
    build.classify('script-regex.txt', None)
    build.classify('**/cache/*.*', None)
    build.classify('**.rpa', None)

    # Esto define README.html como documentacion
    build.documentation('README.html')

    build.include_old_themes = False
