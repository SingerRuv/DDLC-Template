## script.rpy

# Este es el script principal que Ren'Py ejecuta para iniciar la historia de tu juego.

label start:

    # Este label configura el número anti-cheat del juego.
    # Se recomienda dejar esto tal cual y usar lo siguiente en tu guion:
    #   $ persistent.anticheat = renpy.random.randint(X, Y)
    #   X - El número mínimo | Y - El número máximo
    $ anticheat = persistent.anticheat

    # Esta variable pone el número de capítulo en 0 para usarlo en el mod.
    $ chapter = 0

    # Esta variable controla si el jugador puede omitir una pausa en el juego.
    $ _dismiss_pause = config.developer

    ## Nombres de los personajes
    # Estas variables definen los nombres de los personajes del juego.
    # Para añadir un personaje, usa el siguiente ejemplo:
    #   $ mi_personaje = "Mi Nombre".
    # ¡No olvides añadir el personaje en 'definitions.rpy'!
    # Empiezan ocultos; revelalos en tu historia donde corresponda
    # (p. ej. $ s_name = "Sayori").
    $ s_name = "???"
    $ m_name = "Chica 3"
    $ n_name = "Chica 2"
    $ y_name = "Chica 1"

    # Esta variable controla si el menú rápido del cuadro de texto está activado.
    $ quick_menu = True

    # Esta variable controla si queremos diálogo normal o glitcheado.
    # Define tu propio estilo glitch y asignalo con 'style.say_dialogue'.
    $ style.say_dialogue = style.normal

    # Esta variable controla si Sayori está muerta. Se recomienda dejar esto tal cual.
    $ in_sayori_kill = None

    # Estas variables controlan si el jugador puede saltar diálogo o transiciones.
    $ allow_skipping = True
    $ config.allow_skipping = True

    ## La parte principal del guion
    # ¡Aquí es donde se llama al código de tu historia!
    # 'persistent.playthrough' controla el número de partida en el que está el jugador
    # (es decir, Acto 1, 2, 3, 4).

    # Quita esta línea cuando tengas tu historia.
    # Escribe el guion en cualquier archivo .rpy dentro de game/ (Ren'Py los carga
    # automáticamente) y llámalo aquí con:
    #     call nombre_de_tu_label
    call screen dialog(message="Este es un template, no un juego real: todavía no hay historia que jugar.\n\nEscribe tu historia en un archivo .rpy dentro de la carpeta game/ (Ren'Py lo carga automáticamente) y llámala desde 'script.rpy' con:\n\n    call nombre_de_tu_label\n\nDespués, borra esta línea.", ok_action=MainMenu(confirm=False))

    ## Ejemplo de cómo el template original de DDLC llamaba a sus capítulos:
    # Nota: el template original organizaba la historia en "chapters" (capitulos).
    # Cada capitulo era un archivo de script propio (ej: script-ch1.rpy) con un label
    # tipo 'ch1_main'. Desde aqui se llamaba con 'call ch1_main'.
    #
    # En tu template genérico puedes replicar el mismo sistema:
    #
    #   # La historia principal se divide en archivos (script-capitulo1.rpy, etc.)
    #   # cada uno con su label, y se llaman aqui en orden:
    #   # call capitulo1
    #
    # Si tu juego tiene multiples rutas/actos, crea una variable como
    # 'persistent.ruta' (ej: default persistent.ruta = 0) y ramifica con if/elif:
    #
    #   # if persistent.ruta == 0:
    #   #     call capitulo1_normal
    #   # elif persistent.ruta == 1:
    #   #     call capitulo1_alternativo
    #
    # Ejemplo completo del flujo original de DDLC (por actos/capítulos):
    #
    #   if persistent.playthrough == 0:
    #       $ chapter = 0
    #       call ch0_main
    #       call poem
    #
    #       $ chapter = 1
    #       call ch1_main
    #       call poemresponse_start
    #       call ch1_end
    #
    #       # ...sigue con ch2, ch3, ch4...
    #
    #       call endgame
    #       return

    return


# Este label es donde el juego 'termina'. Muestra la pantalla de fin y vuelve.
label endgame(pause_length=4.0):
    $ quick_menu = False
    stop music fadeout 2.0
    scene black
    show end
    with dissolve_scene_full
    pause pause_length
    $ quick_menu = True
    return
