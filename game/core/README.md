# Contenido de la carpeta `core`

> [!DANGER]
> Los archivos de `core/` mantienen el template funcionando. No los borres ni los
> edites salvo que sepas lo que hacés.

## Archivos

| Archivo | Qué hace |
|---|---|
| `0imports.rpy` | Imports tempranos (`init -2`) y agrega `game/mod_assets/` al searchpath de Ren'Py, para poder referenciar tus assets con nombre corto (`"images/bg/mi_cuarto.png"`) |
| `console.rpy` | Consola de Monika (la terminal de DDLC): screen, estilos y `default console` |
| `functions.rpy` | Funciones de ayuda: `delete_all_saves()`, `get_process_list()`, `process_check()`, `is_user_streaming()` |
| `discord_rpc.rpy` | Motor del Rich Presence de Discord (hilo aparte + `RPC`). La configuración va en `definitions/discord.rpy` |
| `py/` | Código Python (`.py` y `*_ren.py`) que no necesita ser un `.rpy` |

## `py/`

- `0checks_ren.py` - chequeos de arranque (`init -100`): RPAs de DDLC y carpeta en OneDrive.
- `0imports_ren.py` - imports de bootstrap (`python early`): `math`, `subprocess`.
- `template_checks_ren.py` - versión mínima de Ren'Py (8).
- `renpy_patches_ren.py` - parches de Ren'Py para DDLC (`wmic` → PowerShell, ATL).
- `console_ren.py` - clase `Console` de la terminal de Monika.
- `personajes_ren.py` - `characters/`: borrar y restaurar `.chr`.
- `__init__.py` - marca la carpeta como paquete de Python (así funciona
  `from game.core.py... import ...`). No es "de prueba": no lo borres.
- Los `*_ren.py` son módulos que además Ren'Py ejecuta como script (por la
  cabecera `"""renpy ... """`). Ver `py/README.md`.

## Qué NO hay acá

Del template de Bronya queda sin copiar el *lock* de instancia única. El resto
(parches de Ren'Py, chequeos de arranque y personajes `.chr`) sí está, adaptado
a este template.

## Reglas

- Los `.rpy` y `.py` van en UTF-8 sin BOM y saltos LF.
- Para lógica nueva, preferí un archivo propio antes que editar los de acá.
