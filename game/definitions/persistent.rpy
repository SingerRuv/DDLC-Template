## persistent.rpy
# Variables persistentes del template (se guardan entre partidas).
# Se declaran con `default` para que Ren'Py (y el editor) sepan que existen.

# Número de partidas completadas (0 = primera partida).
default persistent.playthrough = 0

# Se pone en True tras aceptar el primer aviso legal.
default persistent.first_run = False

# Se pone en True tras elegir un idioma.
default persistent.has_chosen_language = False

# Label al que auto-cargar (usado por el sistema de autoload).
default persistent.autoload = ""

# Token anti-cheat. Debe coincidir con la variable local `anticheat` de las partidas.
default persistent.anticheat = 0

# Se pone en True en la primera carga — se usa para mostrar el consejo de "Skip".
default persistent.first_load = False

# El token anti-cheat local (no persistente). Se define al inicio del juego y se
# restablece al guardar/cargar; debe coincidir con persistent.anticheat.
default anticheat = 0

# ---- Sistema de migración de assets -----------------------------------------
# Caché del chequeo de la última release en GitHub: {ts, version, url} o None.
default persistent.mg_cache = None

# Versión del template que el modder pidió no volver a ofrecer.
default persistent.mg_ignorar = None

# Marca del último reporte de migración ya mostrado (evita repetirlo).
default persistent.mg_ultimo_reporte = None

# ---- PoseLab (herramienta dev) ---------------------------------------------
# Personajes que PoseLab ya vio (para avisar cuáles son nuevos al abrirlo).
default persistent.pl_personajes_visto = None
