# ejemplo.rpy
# Ejemplos de assets propios. Descomenta y edita con tus rutas reales.
# (Todo está comentado, así que este archivo no afecta al juego.)

# --- Fondos (mod_assets/images/bg/) ---
# image bg mi_cuarto = "mod_assets/images/bg/mi_cuarto.png"

# --- CG (mod_assets/images/cg/) ---
# image cg mi_evento = "mod_assets/images/cg/mi_evento.png"

# --- Música (mod_assets/audio/bgm/) ---
# define audio.mi_tema = "<loop 0>mod_assets/audio/bgm/mi_tema.ogg"

# --- Efectos de sonido (mod_assets/audio/sfx/) ---
# define audio.mi_click = "mod_assets/audio/sfx/mi_click.ogg"

# --- Sprite propio (mod_assets/images/<personaje>/) ---
# Coloca los PNG con el patrón DDLC (1l/1r, caras a-z) y define así:
# image mi_pj 1a = im.Composite((960, 960), (0, 0), "mod_assets/images/mi_pj/1l.png", (0, 0), "mod_assets/images/mi_pj/1r.png", (0, 0), "mod_assets/images/mi_pj/a.png")
