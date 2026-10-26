# `story/` — la historia del mod

Ren'Py carga **todos** los `.rpy` que estén debajo de `game/`, sin registrarlos en
ningún lado. Esta carpeta es una convención para ordenar la historia: un archivo
por capítulo, acto o ruta.

```
game/story/
  capitulo1.rpy
  capitulo2.rpy
  rutas/
    ruta_sayori.rpy
    ruta_yuri.rpy
```

Se llaman desde `label start` (en `game/script.rpy`):

```renpy
label start:
    $ chapter = 1
    call capitulo1

    $ chapter = 2
    call capitulo2

    call endgame
```

Cada archivo define sus propios `label`:

```renpy
label capitulo1:
    scene bg class
    show sayori at t11
    s "Primer día."
    return
```

Reglas:

- `label start` existe **una sola vez** en todo el proyecto.
- Los nombres de `label` son únicos (si repetís uno, Ren'Py falla al arrancar).
- Podés usar subcarpetas libremente: no cambian cómo se referencia un label.
- No hace falta declarar nada en ninguna lista.

También podés escribir la historia directamente en `game/script.rpy`; esta
carpeta es para cuando el guion crece.

Ver [`docs/01-historia.md`](../../docs/01-historia.md) para el flujo completo
(personajes, variables, guardado).
