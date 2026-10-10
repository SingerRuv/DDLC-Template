## pose_lab_preview.rpy
## PoseLab — Preview: compone el lienzo 1280x720 con el fondo elegido y la
## pose aplicando su TRANSFORM REAL (animado), para que se vea igual que en
## el juego.

init python:
    def _pl_mostrar(tag, nombre):
        """Displayable de la pose: imagen registrada, o composite de archivos
        (custom suelto). None si no hay nombre."""
        if not nombre:
            return None
        if pl_es_custom(tag):
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
        return renpy.displayable("%s %s" % (pl_tag(tag), nombre))

    def _pl_pose_transformada(tag, nombre, trans):
        """La pose con su transform real aplicado (animado). Si el transform
        no existe, se devuelve la pose sin transformar."""
        disp = _pl_mostrar(tag, nombre)
        if disp is None:
            return None
        transform = getattr(store, trans, None)
        if transform is None:
            return disp
        try:
            return transform(child=disp)
        except Exception:
            return disp

    @_pl_cacheado
    def pl_preview(tag, nombre, trans, fondo):
        """Lienzo 1280x720: fondo + la pose con su transform real.

        Se cachea por (tag, nombre, trans, fondo): así el displayable es estable
        entre re-renders (no reinicia la animación), y al cambiar de pose/transform
        se crea uno nuevo (re-anima)."""
        c = Fixed(xysize=(1280, 720))
        if fondo:
            c.add("images/bg/%s.png" % fondo)
        disp = _pl_pose_transformada(tag, nombre, trans)
        if disp is not None:
            c.add(disp)
        return c
