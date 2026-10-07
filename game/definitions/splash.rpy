# splash.rpy
# Splash screen, aviso legal, sistema de autoload y logica anti-cheat.
# Adaptado del DDLC Mod Template (Azariel Del Carmen / bronya_rand).

# ---- Imagen de texto del mensaje de splash ---------------------------------------------

image splash_warning = ParameterizedText(style="splash_text", xalign=0.5, yalign=0.5)

# ---- Imagenes del menu principal -----------------------------------------------------

image menu_logo:
    "gui/window_icon.png"
    subpixel True
    xcenter 240
    ycenter 120
    zoom 0.60
    menu_logo_move

image menu_bg:
    topleft
    "gui/menu_bg.png"
    menu_bg_move

image game_menu_bg:
    topleft
    "gui/menu_bg.png"
    menu_bg_loop

image menu_fade:
    "white"
    menu_fadeout

image menu_art_y = "gui/menu_art_y.png"

image menu_art_n = "gui/menu_art_n.png"

image menu_art_s = "gui/menu_art_s.png"

image menu_art_m = "gui/menu_art_m.png"

image menu_nav:
    "gui/overlay/main_menu.png"
    menu_nav_move

# ---- Efectos del menu principal ----------------------------------------------------

image menu_particles:
    2.481
    xpos 224
    ypos 104
    ParticleBurst("gui/menu_particle.png", explodeTime=0, numParticles=40,
        particleTime=2.0, particleXSpeed=3, particleYSpeed=3).sm
    particle_fadeout

transform particle_fadeout:
    easeout 1.5 alpha 0

transform menu_bg_move:
    subpixel True
    topleft
    parallel:
        xoffset 0 yoffset 0
        linear 3.0 xoffset -100 yoffset -100
        repeat
    parallel:
        ypos 0
        time 0.65
        ease_cubic 2.5 ypos -500

transform menu_bg_loop:
    subpixel True
    topleft
    parallel:
        xoffset 0 yoffset 0
        linear 3.0 xoffset -100 yoffset -100
        repeat

transform menu_logo_move:
    subpixel True
    yoffset -300
    time 1.925
    easein_bounce 1.5 yoffset 0

transform menu_nav_move:
    subpixel True
    xoffset -500
    time 1.5
    easein_quint 1 xoffset 0

transform menu_fadeout:
    easeout 0.75 alpha 0
    time 2.481
    alpha 0.4
    linear 0.5 alpha 0

transform menu_art_move(z, x, z2):
    subpixel True
    yoffset 0 + (1200 * z)
    xoffset (740 - x) * z * 0.5
    zoom z2 * 0.75
    time 1.0
    parallel:
        ease 1.75 yoffset 0
    parallel:
        pause 0.75
        ease 1.5 zoom z2 xoffset 0

# ---- Fondos del splash ---------------------------------------------------

image tos = "images/bg/warning.png"
image tos2 = "images/bg/warning2.png"

image intro:
    truecenter
    "white"
    0.5
    "images/bg/splash.png" with Dissolve(0.5, alpha=True)
    2.5
    "white" with Dissolve(0.5, alpha=True)
    0.5

image warning:
    truecenter
    "white"
    "splash_warning" with Dissolve(0.5, alpha=True)
    2.5
    "white" with Dissolve(0.5, alpha=True)
    0.5

# ---- Mensajes del splash ------------------------------------------------------

init python:
    # El mensaje de splash por defecto que se muestra al arrancar el juego.
    splash_message_default = (
        "This game is an unofficial fan game, created by Dokifiles."
    )

    # Conjunto de mensajes de splash. Se elige uno al azar por arranque.
    splash_messages = [
        "Just Monika.",
        "Remember to save regularly!",
        "Don't forget to drink water~",
        "Press ESC for the menu.",
        "You can use the Skip button to fast-forward.",
        "Made with Ren'Py 8.",
        "Doki Doki Literature Club is by Team Salvato.",
        "Hxppy thxughts!",
        ":)",
        "Every day is a gift.",
        "Press F to pay respects.",
    ]

# ---- Label del splash screen --------------------------------------------------

label splashscreen:
    $ quick_menu = False

    # Borra los datos de guardado previos si el jugador aun no ha aceptado el aviso legal.
    if not persistent.first_run and len(renpy.list_saved_games(fast=True)) > 0:
        scene black

        menu:
            "A previous save file has been found. Would you like to delete your save data and start over?"
            "Yes, delete my existing data.":
                "Deleting save data...{nw}"
                python:
                    delete_all_saves()
                    renpy.utter_restart()
            "No, continue where I left off.":
                python:
                    persistent.first_run = True

    if not persistent.first_run:
        scene white
        pause 0.5
        scene tos
        with Dissolve(1.0)
        pause 1.0

        # Selector de idioma (solo si hay mas de un idioma registrado
        # Y el jugador aun no lo ha elegido).
        if not persistent.has_chosen_language and translations:
            if _preferences.language is None:
                call screen choose_language

        "Este es un juego de fans no oficial, no afiliado a Team Salvato ni al autor del DDLC Mod Template, Azariel Del Carmen (bronya_rand)."
        "Está diseñado para jugarse después de haber completado la historia original, y contiene spoilers de la historia original."
        "Se requieren los archivos del juego original para jugar. Doki Doki Literature Club es de Team Salvato y puede descargarse en {a=https://ddlc.moe}https://ddlc.moe{/a}."
        "Hecho por Studio Dokifiles, basado en el DDLC Mod Template de Azariel Del Carmen (bronya_rand)."

        menu:
            "By playing this game you agree that you have completed the original story and accept any spoilers contained within."
            "I agree.":
                $ persistent.first_run = True

        scene tos2
        with Dissolve(1.5)
        pause 1.0

        # Aviso de privacidad si hay una app de streaming ejecutandose.
        if is_user_streaming():
            call screen dialog("A streaming/recording program has been detected. Let's Play Mode has been enabled to protect your privacy.",
                [Hide("dialog"), Return()])
        scene white

    # Carga el label de autoload si se definio uno.
    if persistent.autoload:
        jump autoload

    # Desactiva el salto durante la intro del splash.
    $ config.allow_skipping = False

    # Intro del logo.
    show white
    $ splash_message = splash_message_default
    $ config.main_menu_music = audio.t1
    $ renpy.music.play(config.main_menu_music)
    show intro with Dissolve(0.5, alpha=True)
    pause 2.5
    hide intro with Dissolve(0.5, alpha=True)
    show splash_warning "[splash_message]" with Dissolve(0.5, alpha=True)
    pause 1.5
    hide splash_warning with Dissolve(0.5, alpha=True)
    pause 0.5
    $ config.allow_skipping = True
    return

# ---- Logica anti-cheat + post-carga -----------------------------------------

label after_load:
    $ config.allow_skipping = allow_skipping
    $ _dismiss_pause = config.developer
    $ style.say_dialogue = style.normal

    # Compara el token anti-cheat local con el persistente. Si no
    # coinciden, la partida fue alterada - se expulsa al jugador.
    if anticheat != persistent.anticheat:
        stop music
        scene black
        "The save file could not be loaded."
        "Are you trying to cheat?"
        $ m_name = "Monika"
        show monika 5a at t11
        if persistent.playername == "":
            m "You're so funny."
        else:
            m "You're so funny, [persistent.playername]."
        $ renpy.utter_restart()
    else:
        # Consejo en la primera carga sobre el botón "Skip".
        if persistent.playthrough == 0 and not persistent.first_load and not config.developer:
            $ persistent.first_load = True
            call screen dialog("Hint: You can use the \"Skip\" button to\nfast-forward through text you've already read.", ok_action=Return())
    return

# ---- Autoload -------------------------------------------------------------

label autoload:
    python:
        if "_old_game_menu_screen" in globals():
            _game_menu_screen = _old_game_menu_screen
            del _old_game_menu_screen
        if "_old_history" in globals():
            _history = _old_history
            del _old_history
        renpy.block_rollback()
        renpy.context()._menu = False
        renpy.context()._main_menu = False
        main_menu = False
        _in_replay = None
    if renpy.get_return_stack():
        $ renpy.pop_call()
    jump expression persistent.autoload

# ---- Musica + hooks de salida ---------------------------------------------

label before_main_menu:
    $ config.main_menu_music = audio.t1
    return

# Se ejecuta al entrar al menu de pausa, antes de que el motor reproduzca
# config.game_menu_music. Desactiva la musica de pausa fuera de modo dev.
label enter_game_menu:
    if not config.developer:
        $ config.game_menu_music = None
    return

label quit:
    return
