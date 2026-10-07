# `mod_assets/` — assets propios del mod

Aquí van los assets **tuyos** (no los de DDLC). El template resuelve las rutas
de forma relativa a `game/`, así que se referencia cada archivo con la ruta
completa `"mod_assets/..."`.

## Estructura

```
mod_assets/
  images/
    bg/          fondos propios
    cg/          CG (imágenes de evento) propias
    <personaje>/ sprites propios de un personaje
  audio/
    bgm/         música propia
    sfx/         efectos de sonido propios
```

## Cómo se referencian

Fondos
```renpy
image bg mi_cuarto = "mod_assets/images/bg/mi_cuarto.png"
# En el guion:
scene bg mi_cuarto
```

CG
```renpy
image cg mi_evento = "mod_assets/images/cg/mi_evento.png"
scene cg mi_evento with dissolve_cg
```

Música
```renpy
define audio.mi_tema = "<loop 0>mod_assets/audio/bgm/mi_tema.ogg"
play music audio.mi_tema
```

Efectos de sonido
```renpy
define audio.mi_click = "mod_assets/audio/sfx/mi_click.ogg"
play sound audio.mi_click
```

Sprites propios (personaje nuevo)
- Coloca los PNG en `mod_assets/images/<personaje>/` siguiendo el patrón DDLC:
  mitades `1l.png`, `1r.png`, `2l.png`, `2r.png` (y `1bl.png`, `1br.png`, … para
  el outfit casual) y caras `a.png`, `b.png`, `c.png`, …
- Luego defínelos con `im.Composite`, igual que en `definitions/sprites.rpy`:
```renpy
image mi_pj 1a = im.Composite((960, 960), (0, 0), "mod_assets/images/mi_pj/1l.png", (0, 0), "mod_assets/images/mi_pj/1r.png", (0, 0), "mod_assets/images/mi_pj/a.png")
# En el guion:
show mi_pj 1a at t11
```

> Ver `ejemplo.rpy` en esta misma carpeta: tiene las líneas listas para
> descomentar y editar.

> Nota: los assets **oficiales de DDLC** vienen de los `.rpa` y se referencian
> como `"images/..."`, `"bgm/..."`, `"sfx/..."` (sin `mod_assets/`). No los
> mezcles con los tuyos.
