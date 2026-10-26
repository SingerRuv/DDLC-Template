## shaders_lab_preview.rpy
## Shaders Lab — Preview: el lienzo de la demo. Dibuja el fondo y un personaje,
## y aplica el efecto elegido al sujeto seleccionado (fondo o personaje).
## Los shaders se aplican como transforms vía `at`; los efectos por slices
## (ChromaGlitch) envuelven el displayable.

transform shl_pos:
    subpixel True
    xcenter 940
    yanchor 1.0
    ypos 1.0
    zoom 0.85


screen shl_preview():

    $ _shl_sujeto = shl_state["sujeto"]
    $ _shl_efecto = shl_state["efecto"]
    $ _shl_intensidad = shl_state["intensidad"]
    $ _shl_tr = shl_transform(_shl_efecto, _shl_intensidad)
    $ _shl_pj = "%s 1a" % shl_state["doki"]

    add Solid("#151515")

    if _shl_sujeto == "Fondo":
        $ _shl_env = shl_envolver(_shl_efecto, renpy.displayable("bg class"), _shl_intensidad)
        if _shl_env is not None:
            add _shl_env
        elif _shl_tr is not None:
            add "bg class" at _shl_tr
        else:
            add "bg class"
        add _shl_pj at shl_pos

    else:
        add "bg class"
        $ _shl_env = shl_envolver(_shl_efecto, renpy.displayable(_shl_pj), _shl_intensidad)
        if _shl_env is not None:
            add _shl_env at shl_pos
        elif _shl_tr is not None:
            add _shl_pj at [shl_pos, _shl_tr]
        else:
            add _shl_pj at shl_pos
