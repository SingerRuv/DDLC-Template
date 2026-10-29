# Referencia — Shaders

> Generado por `tools/gen_docs.py` desde `game/tools/plugins/shaders_lab/shaders_lab_data.rpy`.
> **No editar a mano**: corré `python tools/gen_docs.py` después de tocar el código.

## Transforms listos (`sh_*`)

| Transform | Parámetros | Shader | Uniforms |
|---|---|---|---|
| `sh_scanlines` | `intensidad=0.35, lineas=240.0` | `bd.scanlines` | `u_intensidad`, `u_lineas` |
| `sh_aberracion` | `offset=0.002` | `bd.aberracion` | `u_offset` |
| `sh_vigneta` | `fuerza=0.55` | `bd.vigneta` | `u_fuerza` |
| `sh_glitch` | `intensidad=0.8, bandas=24.0, velocidad=0.5` | `bd.glitch` | `u_intensidad`, `u_bandas`, `u_fase` |
| `sh_crt` | `intensidad=0.30, offset=0.002, fuerza=0.45` | `bd.crt` | `u_intensidad`, `u_lineas`, `u_offset`, `u_fuerza` |

## Shaders registrados

`bd.scanlines`, `bd.aberracion`, `bd.glitch`, `bd.vigneta`, `bd.crt`

## Combinar

`sh_combinar(d, shaders, **uniformes)` — Aplica VARIOS shaders a un displayable (un Transform admite uno solo).

## Listas de la demo

| Lista | Valores |
|---|---|
| `_SHL_EFECTOS` | Ninguno, Scanlines, Aberración, Viñeta, Glitch, CRT, Cuadros |
