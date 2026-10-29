# Contenido de la carpeta `definitions`

Todo lo que se **define** (imágenes, sprites, audio, efectos, transforms, menús,
splash y variables persistentes). Los archivos de assets van en `mod_assets/`.

| Archivo | Qué define | Dónde se usa |
|---|---|---|
| `definitions.rpy` | Fondos (`image bg …`), personajes (`DynamicCharacter`), variables por partida y `config.developer` | Todo el guion |
| `sprites.rpy` | Sprites de las dokis con `Composite`: pose + expresión | `show sayori 1a at t21` |
| `transforms.rpy` | Posiciones (`t##`, `f##`, …), animaciones (`hop`, `dip`, …) y transiciones (`dissolve`, `wipe…`) | `at` y `with` |
| `music.rpy` | Música y sonidos (`define audio.*`) | `play music audio.t1`, `play sound audio.slap` |
| `effects.rpy` | Efectos visuales: `invert`, `tear`, `dizzy`, `recolorize`, partículas | `show screen invert(0.5)` |
| `menu_screens.rpy` | Menú principal, de pausa y quick menu, con sus `define` de layout, logo, partículas y animación hover | El botón **Plugins** también vive acá (solo en dev) |
| `splash.rpy` | Splash, aviso legal, autoload y chequeo anti-cheat | Arranque del juego |
| `persistent.rpy` | Variables persistentes (`persistent.playthrough`, preferencias del template) | Todo el juego |
| `cgs.rpy` | CGs (imágenes de evento) | `scene cg nombre` |
| `textshaders.rpy` | Text shaders propios (`ts_glitch`) para el diálogo (dev) | `what_textshader="ts_glitch:0.6"` |
| `py/` | Código Python de soporte (`core_ren.py`, `android_assets_ren.py`) | Ver `py/README.md` |

## Referencia generada

Las tablas completas de sprites, transforms, audio y efectos se generan desde
estos archivos:

- [`docs/referencia/sprites.md`](../../docs/referencia/sprites.md)
- [`docs/referencia/transforms.md`](../../docs/referencia/transforms.md)
- [`docs/referencia/audio.md`](../../docs/referencia/audio.md)
- [`docs/referencia/efectos.md`](../../docs/referencia/efectos.md)

Después de tocar estos `.rpy`, regenerala con `python tools/gen_docs.py`.

## Cómo agregar cosas

- **Fondo/CG propios:** archivo en `mod_assets/images/…` y `image bg/cg …` acá
  (o en `cgs.rpy`).
- **Audio propio:** archivo en `mod_assets/audio/…` y `define audio.…` en
  `music.rpy`.
- **Sprite propio:** `Composite` en `sprites.rpy`, o armalo con PoseLab.
- **Menús:** los `define` de `menu_screens.rpy` (fondos, logo, partículas,
  offsets, tiempos).
