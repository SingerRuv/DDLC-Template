# Contenido de la carpeta `core`
> [!DANGER]
> Los archivos y carpetas de la carpeta `core` son los que mantienen el template funcionando. No los borres ni edites a menos que sepas lo que haces.

## Carpetas

- **[py](./py)**: Contiene el código Python de las funcionalidades base del template.
- **\_\_pycache\_\_**: Contiene los archivos Python compilados para el código usado en las funcionalidades base. Normalmente no debería aparecer en tu juego, pero si existe, ignóralo.

## Archivos
- **[0imports.rpy](./0imports.rpy)**: Este archivo importa ciertos módulos Python tras el bootstrap pero antes del inicio del juego.
- **[functions.rpy](./functions.rpy)**: Contiene funciones de ayuda usadas en todo el juego (borrado de guardados, detección de streaming).
