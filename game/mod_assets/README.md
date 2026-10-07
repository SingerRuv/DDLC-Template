# `mod_assets/` — carpeta de assets propios

Aquí van **solo los archivos** (PNG, OGG…) de tus assets propios, no los de DDLC.
Es una carpeta de orden: el motor de Ren'Py resuelve cualquier archivo relativo a
`game/`, así que un asset aquí se referencia con la ruta completa `"mod_assets/..."`.

> **Importante:** aquí **solo se guardan archivos**. Las *definiciones*
> (`image`, `define audio`, `im.Composite`, etc.) van en
> `game/definitions/definitions.rpy` (y `sprites.rpy` para los sprites).

## Estructura

```
mod_assets/
  images/
    bg/          fondos
    cg/          CG (imágenes de evento)
    <personaje>/ sprites de un personaje
  audio/
    bgm/         música
    sfx/         efectos de sonido
```

Ejemplos de nombres de archivo:
- `mod_assets/images/bg/mi_cuarto.png`
- `mod_assets/images/cg/mi_evento.png`
- `mod_assets/images/mi_pj/1l.png`, `1r.png`, `a.png`, … (patrón DDLC)
- `mod_assets/audio/bgm/mi_tema.ogg`
- `mod_assets/audio/sfx/mi_click.ogg`

## Dónde se definen

En `game/definitions/definitions.rpy` (o `sprites.rpy` para sprites):

```renpy
# Fondos
image bg mi_cuarto = "mod_assets/images/bg/mi_cuarto.png"

# CG
image cg mi_evento = "mod_assets/images/cg/mi_evento.png"

# Música y sonidos
define audio.mi_tema  = "<loop 0>mod_assets/audio/bgm/mi_tema.ogg"
define audio.mi_click = "mod_assets/audio/sfx/mi_click.ogg"
```

Y en `sprites.rpy`, un sprite propio (patrón DDLC: mitades + caras):

```renpy
image mi_pj 1a = im.Composite((960, 960), (0, 0), "mod_assets/images/mi_pj/1l.png", (0, 0), "mod_assets/images/mi_pj/1r.png", (0, 0), "mod_assets/images/mi_pj/a.png")
```

> Nota: los assets **oficiales de DDLC** vienen de los `.rpa` y se referencian
> como `"images/..."`, `"bgm/..."`, `"sfx/..."` (sin `mod_assets/`). No los
> mezcles con los tuyos.
