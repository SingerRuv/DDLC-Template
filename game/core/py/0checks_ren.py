# 0checks_ren.py
# Chequeos de arranque del template: RPAs de DDLC y carpeta en la nube.
# Corre en `init -100`, antes del init normal.

import os

import renpy  # type: ignore

"""renpy
init -100 python:
"""

if not renpy.android:
    for _archive in ("audio", "images", "fonts"):
        if _archive not in renpy.config.archives:
            raise Exception(
                "Falta '%s.rpa' en la carpeta game/.\n"
                "Copiá audio.rpa, images.rpa y fonts.rpa desde tu instalación "
                "de DDLC (ver docs/00-empezar.md)." % _archive
            )

    if renpy.windows:
        _onedrive = os.environ.get("OneDrive")
        if _onedrive and _onedrive in renpy.config.basedir:
            raise Exception(
                "El proyecto está dentro de OneDrive (u otra carpeta en la nube).\n"
                "Ren'Py no funciona bien ahí: movelo a una carpeta local."
            )
