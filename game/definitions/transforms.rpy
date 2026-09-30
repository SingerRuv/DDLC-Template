# transforms.rpy
# Transforms de personajes y animaciones. Adaptado del Mod Template original
# (Azariel Del Carmen / bronya_rand) y reescrito para usar im.Composite.

# ----------------------------------------------------------------------------
# Transforms base parametrizados (Bronya)
#   x -> posición X en píxeles (640 = centro en 1280x720)
#   z -> zoom base (0.80 reduce el sprite 960x960 para que quepa bien)
# ----------------------------------------------------------------------------

transform tcommon(x=640, z=0.80):
    yanchor 1.0 subpixel True ypos 1.03
    on show:
        zoom z*0.95 alpha 0.00
        xcenter x yoffset -20
        easein .25 yoffset 0 zoom z*1.00 alpha 1.00
    on replace:
        alpha 1.00
        parallel:
            easein .25 xcenter x zoom z*1.00
        parallel:
            easein .15 yoffset 0 ypos 1.03

transform tinstant(x=640, z=0.80):
    xcenter x yoffset 0 zoom z*1.00 alpha 1.00 yanchor 1.0 ypos 1.03

transform t_focus(x=640, z=0.80):
    yanchor 1.0 ypos 1.03 subpixel True
    on show:
        zoom z*0.95 alpha 0.00
        xcenter x yoffset -20
        easein .25 yoffset 0 zoom z*1.05 alpha 1.00
        yanchor 1.0 ypos 1.03
    on replace:
        alpha 1.00
        parallel:
            easein .25 xcenter x zoom z*1.05
        parallel:
            easein .15 yoffset 0

transform hop(x=640, z=0.80):
    xcenter x yoffset 0 yanchor 1.0 ypos 1.03 zoom z*1.00 alpha 1.00 subpixel True
    easein .1 yoffset -20
    easeout .1 yoffset 0

transform dip(x=640, z=0.80):
    xcenter x yoffset 0 yanchor 1.0 ypos 1.03 zoom z*1.00 alpha 1.00 subpixel True
    easein .25 yoffset 25
    easeout .25 yoffset 0

# ----------------------------------------------------------------------------
# Posiciones DDLC (nomenclatura: primera cifra = nº personajes, segunda = slot)
#   1 personaje: t11
#   2 personajes: t21 (izq), t22 (der)
#   3 personajes: t31, t32, t33
#   4 personajes: t41, t42, t43, t44
# ----------------------------------------------------------------------------

transform t11:
    tcommon(640)
transform t21:
    tcommon(400)
transform t22:
    tcommon(880)
transform t31:
    tcommon(240)
transform t32:
    tcommon(640)
transform t33:
    tcommon(1040)
transform t41:
    tcommon(200)
transform t42:
    tcommon(493)
transform t43:
    tcommon(786)
transform t44:
    tcommon(1080)

# Versiones instant (sin animación de entrada)
transform i11:
    tinstant(640)
transform i21:
    tinstant(400)
transform i22:
    tinstant(880)
transform i31:
    tinstant(240)
transform i32:
    tinstant(640)
transform i33:
    tinstant(1040)
transform i41:
    tinstant(200)
transform i42:
    tinstant(493)
transform i43:
    tinstant(786)
transform i44:
    tinstant(1080)

# Versiones focus (zoom al hablar)
transform f11:
    t_focus(640)
transform f21:
    t_focus(400)
transform f22:
    t_focus(880)
transform f31:
    t_focus(240)
transform f32:
    t_focus(640)
transform f33:
    t_focus(1040)
transform f41:
    t_focus(200)
transform f42:
    t_focus(493)
transform f43:
    t_focus(786)
transform f44:
    t_focus(1080)

# ----------------------------------------------------------------------------
# Entrada / salida de personajes
# ----------------------------------------------------------------------------

# Oculta el personaje moviéndolo hacia la izquierda.
transform lhide:
    subpixel True
    on hide:
        easeout .25 xcenter -300

# Oculta el personaje moviéndolo hacia la derecha.
transform rhide:
    subpixel True
    on hide:
        easeout .25 xcenter 2000

# Hace entrar al personaje "volando" desde la izquierda.
transform leftin(x=640, z=0.80):
    xcenter -300 yoffset 0 yanchor 1.0 ypos 1.03 zoom z*1.00 alpha 1.00 subpixel True
    easein .25 xcenter x

# Hace entrar al personaje "volando" desde la derecha.
transform rightin(x=640, z=0.80):
    xcenter 2000 yoffset 0 yanchor 1.0 ypos 1.03 zoom z*1.00 alpha 1.00 subpixel True
    easein .25 xcenter x

# Versiones leftin (entran desde la izquierda)
transform l21:
    leftin(400)
transform l22:
    leftin(880)
transform l31:
    leftin(240)
transform l32:
    leftin(640)
transform l33:
    leftin(1040)
transform l41:
    leftin(200)
transform l42:
    leftin(493)
transform l43:
    leftin(786)
transform l44:
    leftin(1080)

# Versiones rightin (entran desde la derecha)
transform r21:
    rightin(400)
transform r22:
    rightin(880)
transform r31:
    rightin(240)
transform r32:
    rightin(640)
transform r33:
    rightin(1040)
transform r41:
    rightin(200)
transform r42:
    rightin(493)
transform r43:
    rightin(786)
transform r44:
    rightin(1080)

# ----------------------------------------------------------------------------
# Transiciones de escena
# ----------------------------------------------------------------------------
define dissolve = Dissolve(0.25)

define dissolve_cg = Dissolve(0.75)
define dissolve_scene = Dissolve(1.0)

define dissolve_scene_full = MultipleTransition([
    False, Dissolve(1.0),
    Solid("#000"), Pause(1.0),
    Solid("#000"), Dissolve(1.0),
    True])

define dissolve_scene_half = MultipleTransition([
    Solid("#000"), Pause(1.0),
    Solid("#000"), Dissolve(1.0),
    True])

define close_eyes = MultipleTransition([
    False, Dissolve(0.5),
    Solid("#000"), Pause(0.25),
    True])

define open_eyes = MultipleTransition([
    False, Dissolve(0.5),
    True])

define trueblack = MultipleTransition([
    Solid("#000"), Pause(0.25),
    Solid("#000")
    ])

define wipeleft = ImageDissolve("mod_assets/images/menu/wipeleft.png", 0.5, ramplen=64)

define wipeleft_scene = MultipleTransition([
    False, ImageDissolve("mod_assets/images/menu/wipeleft.png", 0.5, ramplen=64),
    Solid("#000"), Pause(0.25),
    Solid("#000"), ImageDissolve("mod_assets/images/menu/wipeleft.png", 0.5, ramplen=64),
    True])

define wiperight = ImageDissolve("mod_assets/images/menu/wipeleft.png", 0.5, ramplen=64, reverse=True)

define wiperight_scene = MultipleTransition([
    False, ImageDissolve("mod_assets/images/menu/wipeleft.png", 0.5, ramplen=64, reverse=True),
    Solid("#000"), Pause(0.25),
    Solid("#000"), ImageDissolve("mod_assets/images/menu/wipeleft.png", 0.5, ramplen=64, reverse=True),
    True])

define tpause = Pause(0.25)
