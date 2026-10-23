## shaders_lab_preview.rpy
## Shaders Lab — Preview: el lienzo de la demo. Dibuja el fondo con el transform
## del efecto elegido (aplicado vía `at`, igual que en el juego) y un sprite de
## referencia para ver el efecto sobre un personaje.

transform shl_pos:
    subpixel True
    xcenter 940
    yanchor 1.0
    ypos 1.0
    zoom 0.85


screen shl_preview():

    $ _shl_efecto = shl_state["efecto"]
    $ _shl_intensidad = shl_state["intensidad"]
    $ _shl_tr = shl_transform(_shl_efecto, _shl_intensidad)

    add Solid("#151515")

    if _shl_tr is None:
        add "bg class"
    else:
        add "bg class" at _shl_tr

    add "yuri 1a" at shl_pos
