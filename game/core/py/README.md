# Contenido de la carpeta `core/py`

## Archivos

| Archivo | Qué hace |
|---|---|
| `0imports_ren.py` | Imports de bootstrap (`python early`): `math` y `subprocess` |
| `__init__.py` | Vacío: marca la carpeta como paquete de Python para que funcionen los imports del estilo `from game.core.py...`. No lo borres |

## Cómo escribir código acá

- Un `.py` normal es **módulo**: Ren'Py no lo ejecuta solo, hay que importarlo.
- Un `*_ren.py` es lo mismo **más** un script de Ren'Py: su cabecera
  `"""renpy\npython early:\n"""` le dice a Ren'Py qué bloque ejecutar al cargar.
  Usalo cuando el código tiene que correr al arrancar (parches, imports, checks).
- El prefijo numérico (`0`) ordena la carga: `0imports` corre antes que el resto.
- La lógica de Ren'Py (screens, labels, estilos) va en los `.rpy` de la carpeta
  padre, no acá.

## Qué NO hay acá

En el template original esta carpeta también tenía `renpy_patches_ren.py`,
`template_checks_ren.py` y `0cleanup_ren.py`: parches de Ren'Py, checks de arranque
(versión mínima, RPAs faltantes, anti-cloud) y limpieza inicial. No se copiaron
porque son lógica específica de DDLC.

Si tu juego necesita algo parecido, creá tu propio `*_ren.py` con `python early`
siguiendo el patrón de `0imports_ren.py`.
