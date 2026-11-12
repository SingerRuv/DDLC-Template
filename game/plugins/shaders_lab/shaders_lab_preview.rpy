## shaders_lab_preview.rpy
## Shaders Lab — Preview: el lienzo de la demo. Dibuja el fondo y le aplica
## el efecto elegido.
##
## Los efectos de texto del diálogo viven en el plugin Diálogo (`dialogo_lab`).

screen shl_preview():

    $ _shl_efecto = shl_state["efecto"]
    $ _shl_intensidad = shl_state["intensidad"]
    $ _shl_tr = shl_transform(_shl_efecto, _shl_intensidad)
    $ _shl_bg = "bg %s" % shl_state["fondo"]

    add Solid("#151515")

    $ _shl_env = shl_envolver(_shl_efecto, renpy.displayable(_shl_bg), _shl_intensidad)
    if _shl_env is not None:
        add _shl_env
    elif _shl_tr is not None:
        add _shl_bg at _shl_tr
    else:
        add _shl_bg
