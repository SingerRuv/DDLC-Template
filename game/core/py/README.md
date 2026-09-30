# Contenido de la carpeta `core/py`

## Carpetas
- **\_\_pycache\_\_**: Contiene los archivos Python compilados para el código usado en las funcionalidades base del juego. Normalmente no debería aparecer en tu juego ni en builds empaquetados, pero si existe, ignóralo.

## Archivos
- **README.md**: Este archivo, que describe el contenido de la carpeta `py`.
- **\_\_init\_\_.py**: Un archivo vacío usado con fines de prueba.

## Archivos movidos (documentación del sistema original)
> [!DANGER]
> En el template original, los archivos de esta carpeta eran cruciales para que DDLC corriera. NO se han copiado porque contienen parches y checks específicos de DDLC.

- **[renpy_patches_ren.py](./renpy_patches_ren.py)**: En el original contenía varios parches para que DDLC corriera correctamente sobre Ren'Py 8.
- **[template_checks_ren.py](./template_checks_ren.py)**: En el original contenía excepciones personalizadas y checks que el template ejecutaba antes de que DDLC iniciara (combinaba los antiguos 'exceptions.rpy' y 'lockdown_check.rpy').
- **[0cleanup_ren.py](./0cleanup_ren.py)**: En el original contenía código de limpieza al iniciar.
- **[0imports_ren.py](./0imports_ren.py)**: En el original contenía los imports 'python early' del bootstrap.

> [!NOTE]
> Si tu juego necesita parches o checks propios al arrancar, crea aquí tus propios archivos `*_ren.py` siguiendo el mismo patrón: `0` de prefijo para cargar primero.
