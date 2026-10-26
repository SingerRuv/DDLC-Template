# Contenido de la carpeta `definitions/py`

## Archivos

| Archivo | Qué hace |
|---|---|
| `core_ren.py` | Define `persistent` y `store` en `init -3`, para que los módulos `*_ren.py` puedan acceder al store de Ren'Py sin repetir el import |
| `android_assets_ren.py` | Soporte Android: extrae los assets de DDLC desde el APK/XAPK que elige el jugador en el primer arranque |
| `__init__.py` | Vacío: marca la carpeta como paquete de Python. No lo borres |

## Cómo escribir código acá

- Un `.py` normal es **módulo**: Ren'Py no lo ejecuta solo, hay que importarlo.
- Un `*_ren.py` además se ejecuta como script (cabecera
  `"""renpy\ninit -N python:\n"""`). Es el patrón que usa el template: la lógica
  Python en `py/`, la parte Ren'Py en los `.rpy` de la carpeta padre.
- Mantené el orden de carga explícito en la cabecera (`init -3`, `init -2`, …).

## Qué NO hay acá

En el template original había más código Python movido desde los `.rpy`
(`0core_ren.py` con el lock de instancia única, `splash_ren.py` con los checks de
RPA/anti-cloud, y un `core_ren.py` enorme con el núcleo de DDLC). No se copiaron
porque son lógica específica de DDLC.

Si tu juego necesita algo así, creá tus propios `*_ren.py` en esta carpeta.
