# Contenido de la carpeta `definitions/py`

## Carpetas
- **\_\_pycache\_\_**: Contiene los archivos Python compilados para el código usado en las definiciones del juego. Normalmente no debería aparecer en tu juego ni en builds empaquetados, pero si existe, ignóralo.

## Archivos
- **README.md**: Este archivo, que describe el contenido de la carpeta `py`.
- **\_\_init\_\_.py**: Un archivo vacío usado con fines de prueba.

## Archivos movidos (documentación del sistema original)
En el template original, esta carpeta contenía código Python que movía lógica de los archivos `.rpy` a archivos `.py` para organizarlos:

- **[0core_ren.py](./0core_ren.py)**: En el original contenía el código singleton para evitar que varias instancias del juego corrieran a la vez en el PC.
- **[core_ren.py](./core_ren.py)**: En el original contenía el código principal de todo DDLC y del template (funciones, variables, parches).
- **[splash_ren.py](./splash_ren.py)**: En el original manejaba los checks de archivos RPA y anti-cloud.

> [!NOTE]
> Estos archivos NO se han copiado porque contienen lógica específica de DDLC. Si tu juego necesita código Python reutilizable, crea tus propios archivos `*_ren.py` aquí siguiendo el mismo patrón de organización: lógica Python en `py/` y lógica Ren'Py en los `.rpy` de la carpeta padre.
