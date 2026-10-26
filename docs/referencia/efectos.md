# Referencia — Efectos

> Generado por `tools/gen_docs.py` desde `game/definitions/effects.rpy`.
> **No editar a mano**: corré `python tools/gen_docs.py` después de tocar el código.

Los efectos se invocan desde el guion: `show screen invert(0.5)` o `show screen tear(10)`; las animaciones, con `at`.

## Displayables

| Clase | Qué hace |
|---|---|
| `Invert` | Displayable que muestra la pantalla invertida. |
| `ParticleBurst` | Ráfaga de partículas que irradia desde un punto (usada en el menú principal). |
| `Piece` | Una franja horizontal usada por el efecto Tear. |
| `Tear` | Corta la pantalla en franjas horizontales que se desplazan arriba/abajo. |

## Screens

| Screen | Parámetros |
|---|---|
| `invert` | `length, delay=0.0` |
| `tear` | `number=10, offtimeMult=1, ontimeMult=1, offsetMin=0, offsetMax=50, srf=None` |

## Animaciones

| Transform | Parámetros | Qué hace |
|---|---|---|
| `dizzy` | `m, t, subpixel=True` | Sacude la imagen como si el jugador estuviera mareado (usado en escenas de muerte). |

## Funciones auxiliares

| Función | Qué hace |
|---|---|
| `screenshot_srf_size()` | Devuelve el tamaño de una superficie de captura 16:9 que coincide con la ventana. |
| `screenshot_srf()` | Devuelve una superficie de captura que coincide con el tamaño de la ventana. |
| `invert()` | Devuelve una copia con los colores invertidos de la pantalla actual. |
| `recolorize()` | Devuelve `image` (displayable) recoloreada: los píxeles oscuros se tiñen hacia `blackColor` y los claros hacia `whiteColor`; `tintAmount` (0..1) controla la intensidad del recoloreado. Usa una matriz de color (`matrixcolor`), que es la API vigente de Ren'Py 8; reemplaza al obsoleto `im.MatrixColor`. |
