# Personajes en disco (`.chr`)

Esta carpeta es la que DDLC usa para los archivos `.chr` de los personajes.
El template **no incluye** esos archivos (son datos de DDLC): copialos desde tu
instalación en `characters/` (junto a `game/`).

Si además querés que el juego pueda **restaurarlos** cuando se borran, poné una
copia en `game/chrs/`:

```
characters/          <- archivos que el juego borra/usa
  sayori.chr
  natsuki.chr
  yuri.chr
  monika.chr
game/chrs/           <- copias para restaurar (el template no las trae)
  sayori.chr
  ...
```

Uso desde el guion:

```renpy
    $ delete_character("sayori")     # borra characters/sayori.chr
    $ restore_characters()           # repone los que falten según persistent.playthrough
```

`restore_characters()` corre al arrancar y al cargar una partida. Solo restaura
lo que falta: no borra otros `.chr` que tengas en la carpeta.

Ver `docs/01-historia.md`.
