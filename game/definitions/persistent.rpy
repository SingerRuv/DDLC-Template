## persistent.rpy
# Define variables persistentes usadas en todo el juego.
# Persistente = se guarda entre sesiones en el archivo de datos persistentes.

init python:
    # Número de partidas completadas (0 = primera partida).
    if not hasattr(persistent, "playthrough"):
        persistent.playthrough = 0

    # Se pone en True tras aceptar el primer aviso legal.
    if not hasattr(persistent, "first_run"):
        persistent.first_run = False

    # Se pone en True tras elegir un idioma.
    if not hasattr(persistent, "has_chosen_language"):
        persistent.has_chosen_language = False

    # El nombre elegido por el jugador (cadena vacía = usar el predeterminado).
    if not hasattr(persistent, "playername"):
        persistent.playername = ""

    # Label al que auto-cargar (usado por el sistema de autoload).
    if not hasattr(persistent, "autoload"):
        persistent.autoload = ""

    # Token anti-cheat. Debe coincidir con la variable local `anticheat` de las partidas.
    if not hasattr(persistent, "anticheat"):
        persistent.anticheat = 0

    # Se pone en True en la primera carga — se usa para mostrar el consejo de "Skip".
    if not hasattr(persistent, "first_load"):
        persistent.first_load = False

    # El token anti-cheat local (no persistente) — debe coincidir con persistent.anticheat.
    # Se define al inicio del juego y se restablece al guardar/cargar.
    anticheat = persistent.anticheat
