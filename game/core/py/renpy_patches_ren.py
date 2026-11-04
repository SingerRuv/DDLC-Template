# renpy_patches_ren.py
# Parches necesarios para que DDLC funcione bien en Ren'Py 8.
# Corre en `python early`.

import os

import renpy  # type: ignore

"""renpy
python early:
"""

# Windows 11 ya no trae `wmic`: redirigimos los comandos que usa DDLC.
if renpy.windows:
    os.environ["wmic process get Description"] = "powershell (Get-Process).ProcessName"
    os.environ["wmic os get version"] = (
        "powershell (Get-WmiObject -class Win32_OperatingSystem).Version"
    )

# Los ATL de DDLC arrancan su animación cuando aparece la screen, no el
# displayable. Ren'Py 7.4.7 cambió ese comportamiento; lo volvemos atrás.
if renpy.version_tuple >= (7, 4, 7, 1862):
    renpy.config.atl_start_on_show = False
