# Escribir la historia

## Punto de entrada

Ren'Py arranca en `label start` (`game/script.rpy`). Ahí se preparan las
variables de la partida y se llama a tu historia:

```renpy
label start:
    $ chapter = 1
    call capitulo1
    call endgame
```

`label start` tiene que existir **una sola vez**. Los capítulos pueden vivir en
archivos separados dentro de `game/story/`; Ren'Py los carga solo.

## Personajes

Ya están definidos en `game/definitions/definitions.rpy`:

| Variable | Quién habla | Nombre en pantalla |
|---|---|---|
| `s` | Sayori | `s_name` |
| `m` | Monika | `m_name` |
| `n` | Natsuki | `n_name` |
| `y` | Yuri | `y_name` |
| `mc` | El jugador | `player` (se pide en Ajustes) |
| `narrator` | Narración | — |

Los nombres se definen al empezar la partida:

```renpy
label start:
    $ s_name = "Sayori"
    $ n_name = "Natsuki"
    ...
```

Por defecto `script.rpy` los deja en `"???"` / `"Chica 1"` para que los reveles
cuando quieras. También podés cambiar los valores por defecto en
`game/definitions/definitions.rpy`.

### Diálogo

```renpy
    s "Hola, ¿cómo estás?"
    "Texto de narración, sin personaje."
    mc "Mi línea."
```

El estilo del diálogo se controla con `style.say_dialogue` (por defecto
`style.normal`). Si querés un estilo "glitcheado", definí el tuyo y asignaló:

```renpy
$ style.say_dialogue = mi_estilo_glitch
```

## Escenas, sprites y transforms

```renpy
    scene bg class                       # fondo
    show sayori 1a at t21                # sprite en la posición 1 de 2
    show yuri 2b at t22
    hide sayori at lhide                 # se va deslizándose
    with dissolve
```

- Nomenclatura de sprites: `<tag> <pose><expresión>` (por ejemplo `sayori 1a`).
  Tabla completa en [`referencia/sprites.md`](referencia/sprites.md).
- Posiciones: `t11` (un personaje), `t21`/`t22` (dos), `t31`–`t33` (tres),
  `t41`–`t44` (cuatro). Familias y variantes en
  [`referencia/transforms.md`](referencia/transforms.md).
- Se pueden encadenar: `at t22, hop`.

Detalle de cada familia en [`02-referencia.md`](02-referencia.md).

## Música y sonido

```renpy
    play music audio.t1 fadein 1.0
    play sound audio.slap
    stop music fadeout 2.0
```

Lista completa (nombres, archivos y descripción) en
[`referencia/audio.md`](referencia/audio.md). Para música propia, poné el `.ogg`
en `mod_assets/audio/bgm/` y declaráralo en `game/definitions/music.rpy`.

## Variables de partida

| Variable | Para qué |
|---|---|
| `chapter` | Capítulo actual (lo lee la historia y las herramientas) |
| `persistent.playthrough` | Número de partida (0 = primera) |
| `anticheat` | Valor anti-cheat; usar `$ persistent.anticheat = renpy.random.randint(X, Y)` |
| `in_sayori_kill` | Marca la escena especial de Sayori; dejar como está |
| `quick_menu` | Si el menú rápido está visible ahora mismo |
| `allow_skipping` / `config.allow_skipping` | Si se puede saltar diálogo |

## Guardado: `default`, `define` y `persistent`

- `define` → valor fijo, no se guarda (colores, imágenes, personajes).
- `default` → valor por partida, se guarda en el save.
- `persistent.*` → se guarda entre partidas (preferencias, progreso).

```renpy
default mi_contador = 0
default persistent.mi_logro = False
```

> Cambiar el **nombre** de una variable guardada rompe los saves viejos: el save
> tiene la clave anterior y Ren'Py no la migra. Si necesitás renombrarla,
> declarala de nuevo y copiá el valor en `label after_load`.

## Fin de partida

`label endgame` (en `script.rpy`) hace el cierre estándar de DDLC: fundido a
negro, cartel de fin y espera. Se puede llamar con otra duración:

```renpy
    call endgame(2.0)
```

## Personajes propios

1. Definí el personaje en `definitions.rpy`:

   ```renpy
   define p = DynamicCharacter('p_name', image='mi_pj', what_prefix='"', what_suffix='"')
   default p_name = "Mi Personaje"
   ```

2. Declará sus sprites con `Composite` en `definitions/sprites.rpy` (o en tu
   propio `.rpy`). Ver el ejemplo de `game/mod_assets/README.md`.
3. Para armar poses sin escribir código a mano, usá **PoseLab** (ver
   [`03-herramientas.md`](03-herramientas.md)).

## Errores comunes

- **Dos `label start`** → error al arrancar.
- **`show sayori 1aa`** → la variante no existe; mirá la tabla generada.
- **`$` de más o de menos** → `$` es una línea de Python; un bloque `python:` no
  lleva `$` adentro.
- **Variables sin `default`** → se pierden al guardar/cargar.

## Siguiente

- [`02-referencia.md`](02-referencia.md) — sprites, transforms, audio, efectos.
- [`03-herramientas.md`](03-herramientas.md) — hub de Plugins y PoseLab.
