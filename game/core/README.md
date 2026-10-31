# Contenido de la carpeta `core`

> [!DANGER]
> Los archivos de `core/` mantienen el template funcionando. No los borres ni los
> edites salvo que sepas lo que hacés.

## Archivos

| Archivo | Qué hace |
|---|---|
| `0imports.rpy` | Imports tempranos (`init -2`) y agrega `game/mod_assets/` al searchpath de Ren'Py, para poder referenciar tus assets con nombre corto (`"images/bg/mi_cuarto.png"`) |
| `functions.rpy` | Funciones de ayuda: `delete_all_saves()`, `get_process_list()`, `process_check()`, `is_user_streaming()` |
| `discord_rpc.rpy` | Motor del Rich Presence de Discord (hilo aparte + `RPC`). La configuración va en `definitions/discord.rpy` |
| `py/` | Código Python (`.py` y `*_ren.py`) que no necesita ser un `.rpy` |

## `py/`

- `0imports_ren.py` — imports de bootstrap (`python early`): `math`, `subprocess`.
- `__init__.py` — marca la carpeta como paquete de Python (así funciona
  `from game.core.py... import ...`). No es "de prueba": no lo borres.
- Los `*_ren.py` son módulos que además Ren'Py ejecuta como script (por la
  cabecera `"""renpy ... """`). Ver `py/README.md`.

## Qué NO hay acá

El template original de Bronya traía parches de Ren'Py, checks anti-cloud y un
lock de instancia única en `core/py/`. No se copiaron porque son lógica
específica de DDLC. Si los necesitás, agregalos como `*_ren.py` propios.

## Reglas

- Los `.rpy` y `.py` van en UTF-8 sin BOM y saltos LF.
- Para lógica nueva, preferí un archivo propio antes que editar los de acá.
