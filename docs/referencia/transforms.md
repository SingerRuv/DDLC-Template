# Referencia — Transforms y transiciones

> Generado por `tools/gen_docs.py` desde `game/definitions/transforms.rpy`.
> **No editar a mano**: corré `python tools/gen_docs.py` después de tocar el código.

Se usan con `at`: `show yuri 2b at t22`. Se pueden encadenar (`at t22, hop`).

## Transforms base

| Transform | Parámetros |
|---|---|
| `tcommon` | `x=640, z=0.80` |
| `tinstant` | `x=640, z=0.80` |
| `t_focus` | `x=640, z=0.80` |

## Familias

La nomenclatura `##` es `nº de personajes` + `slot`: `t21` es el primero de dos, `t42` el segundo de cuatro.

| Familia | Cantidad | Nombres |
|---|---|---|
| Base | 3 | `t_focus`, `tcommon`, `tinstant` |
| Posición (`t##`) | 10 | `t11`, `t21`, `t22`, `t31`, `t32`, `t33`, `t41`, `t42`, `t43`, `t44` |
| Focus (`f##`) | 10 | `f11`, `f21`, `f22`, `f31`, `f32`, `f33`, `f41`, `f42`, `f43`, `f44` |
| Instantáneo (`i##`) | 10 | `i11`, `i21`, `i22`, `i31`, `i32`, `i33`, `i41`, `i42`, `i43`, `i44` |
| Hop (`h##`) | 10 | `h11`, `h21`, `h22`, `h31`, `h32`, `h33`, `h41`, `h42`, `h43`, `h44` |
| Hop + focus (`hf##`) | 10 | `hf11`, `hf21`, `hf22`, `hf31`, `hf32`, `hf33`, `hf41`, `hf42`, `hf43`, `hf44` |
| Dip (`d##`) | 10 | `d11`, `d21`, `d22`, `d31`, `d32`, `d33`, `d41`, `d42`, `d43`, `d44` |
| Sink (`s##`) | 10 | `s11`, `s21`, `s22`, `s31`, `s32`, `s33`, `s41`, `s42`, `s43`, `s44` |
| Entrada desde la izquierda (`l##`) | 10 | `l11`, `l21`, `l22`, `l31`, `l32`, `l33`, `l41`, `l42`, `l43`, `l44` |
| Entrada desde la derecha (`r##`) | 10 | `r11`, `r21`, `r22`, `r31`, `r32`, `r33`, `r41`, `r42`, `r43`, `r44` |
| Entradas especiales | 2 | `leftin`, `rightin` |
| Salidas | 3 | `lhide`, `rhide`, `thide` |
| Otras animaciones | 5 | `dip`, `hop`, `hopfocus`, `musica_slide_in`, `sink` |

## Transiciones (`with …`)

| Nombre | Definición |
|---|---|
| `dissolve` | `Dissolve(0.25)` |
| `dissolve_cg` | `Dissolve(0.75)` |
| `dissolve_scene` | `Dissolve(1.0)` |
| `dissolve_scene_full` | `MultipleTransition (compuesta)` |
| `dissolve_scene_half` | `MultipleTransition (compuesta)` |
| `close_eyes` | `MultipleTransition (compuesta)` |
| `open_eyes` | `MultipleTransition (compuesta)` |
| `trueblack` | `MultipleTransition (compuesta)` |
| `wipeleft` | `ImageDissolve("images/menu/wipeleft.png", 0.5, ramplen=64)` |
| `wipeleft_scene` | `MultipleTransition (compuesta)` |
| `wiperight` | `ImageDissolve("images/menu/wipeleft.png", 0.5, ramplen=64, reverse=True)` |
| `wiperight_scene` | `MultipleTransition (compuesta)` |
| `tpause` | `Pause(0.25)` |
