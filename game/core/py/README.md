# Contenido de la carpeta `core/py`

## Archivos

| Archivo | Qué hace |
|---|---|
| `0checks_ren.py` | Chequeos de arranque (`init -100`): `.rpa` de DDLC y proyecto dentro de OneDrive |
| `0imports_ren.py` | Imports de bootstrap (`python early`): `math` y `subprocess` |
| `template_checks_ren.py` | Verifica que Ren'Py sea 8 o superior |
| `renpy_patches_ren.py` | Parches de Ren'Py para DDLC (`wmic` → PowerShell, ATL) |
| `console_ren.py` | Clase `Console` de la terminal de Monika |
| `personajes_ren.py` | `characters/`: borrar y restaurar `.chr` |
| `__init__.py` | Vacío: marca la carpeta como paquete de Python. No lo borres |

## Cómo escribir código acá

- Un `.py` normal es **módulo**: Ren'Py no lo ejecuta solo, hay que importarlo.
- Un `*_ren.py` es lo mismo **más** un script de Ren'Py: su cabecera
  `"""renpy\npython early:\n"""` le dice a Ren'Py qué bloque ejecutar al cargar.
  Usalo cuando el código tiene que correr al arrancar (parches, imports, checks).
- El prefijo numérico (`0`) ordena la carga: `0imports` corre antes que el resto.
- La lógica de Ren'Py (screens, labels, estilos) va en los `.rpy` de la carpeta
  padre, no acá.

## Qué NO hay acá

El *lock* de instancia única de Bronya no se copió: no hace falta para este
template. Si tu juego necesita algo así, creá tu propio `*_ren.py` con
`python early` siguiendo el patrón de `0imports_ren.py`.
