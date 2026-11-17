# Historia

Carpeta pensada para los `.rpy` de tu historia: un archivo por capítulo.

Ren'Py carga **todos** los `.rpy` que estén debajo de `game/`, así que no hay
que registrar nada: creá `game/history/capitulo1.rpy` con su `label` y llamalo
desde `game/script.rpy`:

```renpy
label start:
    call capitulo1
    return
```

El nombre `history` es solo una convención de este template: no tiene relación
con la pantalla de historial de diálogo (esa vive en `screens.rpy`).
