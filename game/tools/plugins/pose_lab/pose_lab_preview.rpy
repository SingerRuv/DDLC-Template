## pose_lab_preview.rpy
## PoseLab — Preview: compone el lienzo 1280x720 con el fondo elegido y la
## pose aplicando su TRANSFORM REAL vía `at` (screen-language), de modo que
## se dispare el bloque `on show`/`on replace` del transform y se vea (y
## anime) igual que en el juego.

init python:
    def _pl_mostrar(tag, nombre):
        """Displayable de la pose: imagen registrada, composite custom (3 capas)
        o composite "cuerpo + expresión" (2 capas). None si no hay nombre."""
        if not nombre:
            return None
        nombre_img = "%s %s" % (pl_tag(tag), nombre)
        # La definición solo sirve si YA está cargada en el juego: las recién
        # escritas en sprites.rpy existen en disco pero no hasta reiniciar.
        if pl_tiene_defs(tag) and renpy.image_exists(nombre_img, exact=True):
            return renpy.displayable(nombre_img)
        if tag in _pl_carpetas_body_expr():
            b, e = _pl_paths_body_expr(tag, nombre)
            if b and e:
                return Composite((960, 960), (0, 0), b, (0, 0), e)
            return None
        if tag in _pl_carpetas_outfit():
            for ref in _pl_indice_outfit(tag).values():
                if ref["nombre"] == nombre:
                    if ref.get("full"):
                        return Composite((960, 960), (0, 0), ref["full"],
                                         (0, 0), ref["cara"])
                    return Composite((960, 960), (0, 0), ref["izq"],
                                     (0, 0), ref["der"], (0, 0), ref["cara"])
            return None
        if tag in _pl_carpetas():
            carpeta = _pl_carpetas().get(tag, "")
            if nombre.startswith("5"):  # cuerpo completo: archivo 3x.png directo
                return "%s/3%s.png" % (carpeta, nombre[1:])
            for ref in _pl_indice_archivos(tag).values():
                if ref["nombre"] == nombre:
                    i, d, c = ref["izq"], ref["der"], ref["cara"]
                    return Composite(
                        (960, 960), (0, 0), "%s/%s.png" % (carpeta, i),
                        (0, 0), "%s/%s.png" % (carpeta, d),
                        (0, 0), "%s/%s.png" % (carpeta, c))
            return None
        if renpy.image_exists(nombre_img, exact=True):
            return renpy.displayable(nombre_img)
        return None

    # Posiciones x de la familia Focus (`f11..f44`). Debe seguir a transforms.rpy.
    _PL_FOCUS_X = {"11": 640, "21": 400, "22": 880, "31": 240, "32": 640,
                   "33": 1040, "41": 200, "42": 493, "43": 786, "44": 1080}

    def pl_trans_objeto(trans):
        """Transform a aplicar en el preview.

        Los transforms de posición (`t11..t44`) heredan de `tcommon`, cuyo
        `xcenter`/`zoom` viven dentro de su bloque `on show`. Dentro de un
        screen ese evento no se dispara (config.containers_pass_transform_events
        no incluye "show"), así que el sprite quedaría sin posición y a zoom
        1.0. La variante instantánea `iNN` fija esos mismos valores como
        propiedades estáticas (misma pose de reposo), por eso se prefiere.
        La familia Focus (`fNN`) no tiene variante instantánea: se arma acá el
        mismo estado de reposo de `t_focus` (zoom 1.05, alpha 1)."""
        if trans.startswith("t"):
            inst = getattr(store, "i" + trans[1:], None)
            if inst is not None:
                return inst
        if trans.startswith("f"):
            x = _PL_FOCUS_X.get(trans[1:])
            if x is not None:
                return Transform(xcenter=x, yanchor=1.0, ypos=1.03,
                                 yoffset=0, zoom=0.80 * 1.05, alpha=1.0,
                                 subpixel=True)
        return getattr(store, trans, None)


# Preview: fondo + pose, directos en el screen.
# Un segundo personaje (referencia) se dibuja fijo en zorder 2 para mostrar el
# layering: el actual queda detrás suyo con zorder < 2 y delante con zorder > 2.
screen pl_preview(tag, nombre, trans, fondo, zorder):
    if fondo:
        add "images/bg/%s.png" % fondo

    $ _disp = _pl_mostrar(tag, nombre)
    $ _tr = pl_trans_objeto(trans)
    $ _ref = pl_referencia(tag)
    $ _refdisp = _pl_mostrar(_ref[0], _ref[1]) if _ref else None

    if _refdisp is not None and zorder < 2:
        # El actual queda detrás de la referencia (que está en zorder 2).
        if _disp is not None:
            if _tr is not None:
                add _disp at _tr
            else:
                add _disp
        add _refdisp at i22
    else:
        if _refdisp is not None:
            add _refdisp at i22
        if _disp is not None:
            if _tr is not None:
                add _disp at _tr
            else:
                add _disp
