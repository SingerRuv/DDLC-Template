# Referencia rápida

Guía práctica de lo que podés usar en el guion. Las tablas completas las genera
`tools/gen_docs.py` y viven en [`referencia/`](referencia/):

- [`sprites.md`](referencia/sprites.md) — cada personaje, pose por pose.
- [`transforms.md`](referencia/transforms.md) — posiciones, animaciones y transiciones.
- [`audio.md`](referencia/audio.md) — música y efectos.
- [`efectos.md`](referencia/efectos.md) — displayables, screens y animaciones.

## Sprites

Nomenclatura: **`<tag> <pose><expresión>`**

```renpy
show sayori 1a      # pose 1, expresión a
show yuri 2b        # pose 2b (uniforme casual), sin expresión
show natsuki 12b    # pose especial 12, expresión b
```

- Poses normales: `1`, `2`, `3`, `4`.
- Poses con uniforme casual: `1b`, `2b`, `3b`, `4b`.
- Pose `5`: cuerpo completo (la cara ya viene en la imagen); algunas variantes
  son de una sola capa (`5a`, `5b`, …).
- Natsuki tiene dos poses especiales: `12` y `42` (cabeza alternativa).
- Expresiones: letras (`a`–`z`), más variantes con nombre (`scream`).

> Ojo: en `1b`, la `b` **no** es una expresión. `sayori 1b` es el uniforme
> casual; `sayori 1ba` es ese uniforme con la expresión `a`.

### Sprites propios

Se declaran con `image` + `Composite`, igual que los del template:

```renpy
image mi_pj 1a = Composite((960, 960), (0, 0), "mod_assets/images/mi_pj/1l.png", (0, 0), "mod_assets/images/mi_pj/1r.png", (0, 0), "mod_assets/images/mi_pj/a.png")
```

Las imágenes Bronya ya vienen dibujadas en su posición final dentro del PNG de
960×960, por eso todas las capas van en `(0, 0)`. Para armar esto sin escribir
código a mano, usá **PoseLab** ([`03-herramientas.md`](03-herramientas.md)).

## Transforms

Se aplican con `at` y se pueden encadenar:

```renpy
show yuri 2b at t22
show sayori 1a at t21, hop
hide sayori at lhide
```

| Familia | Qué hace | Ejemplo |
|---|---|---|
| `t##` | Posición normal (aparece con fade + zoom) | `t21` |
| `i##` | Igual, pero instantáneo (sin animación) | `i21` |
| `f##` | Posición con foco (zoom de "hablando") | `f22` |
| `h##` | Hop: salta al aparecer | `h21` |
| `hf##` | Hop y queda en foco | `hf21` |
| `d##` | Dip: baja y vuelve | `d21` |
| `s##` | Sink: se hunde y queda más abajo | `s21` |
| `l##` / `r##` | Entra "volando" desde la izquierda / derecha | `l21`, `r22` |
| `lhide` / `rhide` / `thide` | Salidas (deslizar / achicar) | `hide yuri at lhide` |
| `leftin` / `rightin` | Entradas sueltas, con posición a mano | `at leftin(640)` |

El `##` es **número de personajes + slot**: `t21` = primero de dos, `t42` =
segundo de cuatro. Lista completa de posiciones en
[`referencia/transforms.md`](referencia/transforms.md).

### Transiciones

```renpy
scene bg class with dissolve
show yuri 2b with dissolve_cg
scene black with dissolve_scene_full
```

Están todas en [`referencia/transforms.md`](referencia/transforms.md):
`dissolve`, `dissolve_cg`, `dissolve_scene`, `dissolve_scene_full`,
`dissolve_scene_half`, `close_eyes`, `open_eyes`, `trueblack`, `wipeleft`,
`wipeleft_scene`, `wiperight`, `wiperight_scene` y `tpause`.

## Audio

```renpy
play music audio.t1 fadein 1.0
play sound audio.slap
stop music fadeout 2.0
```

La tabla completa (nombre → archivo → descripción) está en
[`referencia/audio.md`](referencia/audio.md). Los nombres `audio.*` están
declarados en `game/definitions/music.rpy`; para música propia, agregá el `.ogg`
en `mod_assets/audio/bgm/` y declaráralo ahí.

## Efectos

| Efecto | Uso |
|---|---|
| Invertir pantalla | `show screen invert(0.5)` (duración en segundos) |
| Cortar la pantalla (tear) | `show screen tear(10)` |
| Mareo | `show yuri 1a at dizzy(1, 1)` |
| Recolorear un displayable | `$ mi_img = recolorize("images/bg/class.png", "#102040", "#ffffff", 0.8)` |

Detalle y parámetros en [`referencia/efectos.md`](referencia/efectos.md).
