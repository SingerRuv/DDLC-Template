# template_checks_ren.py
# Chequeos de arranque del template: versión de Ren'Py.
# Corre en `python early`, antes de cualquier init, para cortar temprano
# con un mensaje claro en vez de fallar más adelante.

import renpy  # type: ignore

"""renpy
python early:
"""

if renpy.version_tuple < (8, 0, 0, 22062402):
    raise Exception(
        "Este template es para Ren'Py 8.\n"
        "Actualizá tu Ren'Py (o usá la versión del template para Ren'Py 7)."
    )
