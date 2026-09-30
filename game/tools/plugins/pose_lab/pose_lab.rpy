## pose_lab.rpy
## Herramienta in-game para armar poses (complemento del template).
##
## Es dev-only: se abre desde el hub "Herramientas" del menú principal, que
## solo aparece si config.developer = True. Se puede borrar la carpeta del
## plugin sin afectar al juego. No incluye assets de DDLC: lee los del propio
## template vía renpy.list_files() / renpy.list_images(), que soportan
## carpetas y .rpa.
##
## Genera dos salidas:
##   - show <tag> <pose> at <transform> zorder 2     (para tu guion)
##   - image <tag> <pose> = im.Composite(...)        (para definitions/sprites.rpy)

init python:
    import re as _pl_re
    import pygame as _pl_pygame

    # Posiciones del template (mismas que transforms.rpy).
    # ponytail: vocabulario fijo del template; parsear transforms.rpy sería frágil.
    _PL_TRANSFORMS = [
        "t11",
        "t21", "t22",
        "t31", "t32", "t33",
        "t41", "t42", "t43", "t44",
    ]

    _PL_X = {
        "t11": 640,
        "t21": 400, "t22": 880,
        "t31": 240, "t32": 640, "t33": 1040,
        "t41": 200, "t42": 493, "t43": 786, "t44": 1080,
    }

    _PL_CACHE = {}

    def _pl_listar(carpeta):
        """Nombres (sin .png) de los PNG directamente dentro de images/<carpeta>/."""
        key = ("listar", carpeta)
        if key in _PL_CACHE:
            return _PL_CACHE[key]
        prefijo = "images/" + (carpeta or "") + "/"
        nombres = []
        for f in renpy.list_files():
            if not f.startswith(prefijo) or not f.lower().endswith(".png"):
                continue
            resto = f[len(prefijo):]
            if "/" not in resto:
                nombres.append(resto[:-4])
        _PL_CACHE[key] = nombres
        return nombres

    def pl_personajes():
        """Carpetas de personaje dentro de images/ (excluye bg/ y menu/)."""
        key = ("personajes",)
        if key in _PL_CACHE:
            return _PL_CACHE[key]
        chars = set()
        for f in renpy.list_files():
            partes = f.split("/")
            if len(partes) != 3 or partes[0] != "images":
                continue
            if partes[1] in ("bg", "menu") or not partes[2].lower().endswith(".png"):
                continue
            chars.add(partes[1])
        orden = ("sayori", "natsuki", "yuri", "monika")
        lower = {c.lower(): c for c in chars}
        vanilla = [lower[d] for d in orden if d in lower]
        resto = sorted(c for c in chars if c.lower() not in orden)
        _PL_CACHE[key] = vanilla + resto
        return _PL_CACHE[key]

    def pl_fondos():
        """Nombres (sin .png) de los fondos en images/bg/."""
        key = ("fondos",)
        if key in _PL_CACHE:
            return _PL_CACHE[key]
        fondos = []
        for f in renpy.list_files():
            partes = f.split("/")
            if len(partes) != 3 or partes[0] != "images" or partes[1] != "bg":
                continue
            if partes[2].lower().endswith(".png"):
                fondos.append(partes[2][:-4])
        _PL_CACHE[key] = sorted(fondos)
        return _PL_CACHE[key]

    def pl_brazos(carpeta):
        return sorted(n for n in _pl_listar(carpeta) if _pl_re.fullmatch(r"\d+b?[lr]", n))

    def pl_caras(carpeta):
        return sorted(n for n in _pl_listar(carpeta) if _pl_re.fullmatch(r"[a-z]", n))

    def pl_poses5(carpeta):
        """Codigos de pose completa (5a, 5b, ...) registrados como imagen.

        Se leen de renpy.list_images() y no de los archivos, porque el
        template arma la pose 5 distinto por personaje (p. ej. natsuki 5b
        compone cabeza + cuerpo, sayori 5a es un solo PNG)."""
        key = ("poses5", carpeta)
        if key in _PL_CACHE:
            return _PL_CACHE[key]
        tag = pl_tag(carpeta)
        res = set()
        for name in renpy.list_images():
            if not name.startswith(tag + " "):
                continue
            seg = name[len(tag) + 1:]
            if len(seg) >= 2 and seg[0] == "5" and seg[1:].isalpha():
                res.add(seg)
        _PL_CACHE[key] = sorted(res)
        return _PL_CACHE[key]

    _PL_POZAS = {
        ("1l", "1r"): "1", ("1l", "2r"): "2",
        ("2l", "1r"): "3", ("2l", "2r"): "4",
    }

    def pl_pose(izq, der):
        return _PL_POZAS.get((izq, der), "5")

    def pl_tag(carpeta):
        """Tag de Ren'Py: los nombres de image no admiten espacios."""
        return (carpeta or "").replace(" ", "")

    def pl_code(cuerpo, izq, der, cara):
        """Codigo de pose resultante ('' si esta incompleta)."""
        if cuerpo:
            return cuerpo
        if izq and der and cara:
            return pl_pose(izq, der) + cara
        return ""

    def pl_componer(carpeta, izq, der, cara):
        """im.Composite en vivo para el preview (None si no hay nada)."""
        partes = [p for p in (izq, der, cara) if p]
        if not partes:
            return None
        args = []
        for p in partes:
            args.append((0, 0))
            args.append("images/%s/%s.png" % (carpeta, p))
        return im.Composite((960, 960), *args)

    def pl_show(carpeta, code, trans):
        """Linea `show ...` para el guion ('' si no hay pose valida)."""
        if not code:
            return ""
        return "show %s %s at %s zorder 2" % (pl_tag(carpeta), code, trans)

    def pl_definicion(carpeta, izq, der, cara):
        """Linea `image ... = ...` para definitions/sprites.rpy ('' si no aplica).

        Solo aplica a poses armadas con brazos + cara. Las poses completas (5)
        ya existen registradas, asi que no necesitan definicion nueva."""
        if not (izq and der and cara):
            return ""
        tag = pl_tag(carpeta)
        code = pl_pose(izq, der) + cara
        capas = ", ".join('(0, 0), "images/%s/%s.png"' % (carpeta, p) for p in (izq, der, cara))
        return "image %s %s = im.Composite((960, 960), %s)" % (tag, code, capas)

    def pl_preview(carpeta, cuerpo, izq, der, cara, trans, fondo):
        """Lienzo 1280x720: fondo + sprite posicionado con el transform real.

        El zoom del preview es un poco menor que el del juego (0.80) para que
        el sprite 960x960 entre completo dentro del recuadro, sin recortarse."""
        c = Fixed(xysize=(1280, 720))
        if fondo:
            c.add("images/bg/%s.png" % fondo)
        if cuerpo:
            disp = renpy.displayable(pl_tag(carpeta) + " " + cuerpo)
        else:
            disp = pl_componer(carpeta, izq, der, cara)
        if disp is not None:
            c.add(Transform(child=disp, xcenter=_PL_X.get(trans, 493),
                            yanchor=1.0, ypos=1.0, zoom=0.72))
        return c

    # Estado de la herramienta. Vive en el store (no en variables de screen)
    # para que el sub-screen pl_menu pueda leerlo/escribirlo via SetDict.
    pl_state = {
        "doki": "", "cuerpo": "", "izq": "", "der": "", "cara": "",
        "trans": "t42", "fondo": "", "open": "",
    }
    pl_initialized = False

    def pl_ensure_init():
        """Inicializa la seleccion la primera vez que se abre la herramienta."""
        global pl_initialized
        if pl_initialized:
            return
        chars = pl_personajes()
        fondos = pl_fondos()
        pl_state.update(
            doki=(chars[0] if chars else ""), cuerpo="", izq="", der="",
            cara="", trans="t42", fondo=(fondos[0] if fondos else ""), open="")
        pl_initialized = True

    def pl_choose(name, value):
        return [SetDict(pl_state, name, value), SetDict(pl_state, "open", "")]

    def pl_choose_doki(d):
        return [SetDict(pl_state, k, v) for k, v in (
            ("doki", d), ("cuerpo", ""), ("izq", ""), ("der", ""),
            ("cara", ""), ("open", ""))]

    def pl_copiar(texto):
        if not texto:
            return
        try:
            _pl_pygame.scrap.put(_pl_pygame.scrap.SCRAP_TEXT, texto.encode("utf-8"))
            renpy.notify("Copiado al portapapeles")
        except Exception:
            renpy.notify("No se pudo copiar")

    def pl_music_on():
        """Musica propia de la herramienta (Ohayou Sayori!)."""
        renpy.music.play(audio.t2)

    def pl_music_off():
        """Restaura la musica del menu principal al cerrar la herramienta."""
        renpy.music.play(config.main_menu_music)


# Dropdown limpio y reutilizable: titulo + boton de campo que despliega opciones.
screen pl_menu(titulo, actual, clave, opciones):
    vbox:
        spacing 4
        text "[titulo]" style "pl_caption"
        textbutton "[actual]":
            style "pl_field"
            action ToggleDict(pl_state, "open", clave, "")
        if pl_state["open"] == clave:
            vbox:
                style "pl_options"
                for texto, accion, elegido in opciones:
                    textbutton "[texto]":
                        style "pl_option"
                        selected elegido
                        action accion


# Escala el lienzo 1280x720 del preview para que ocupe su panel a pantalla completa.
transform pl_scaled:
    zoom 0.64


# ---------------------------------------------------------------------------
# Estilos de la herramienta (limpios, oscuros, sin depender del template).
# ---------------------------------------------------------------------------

style pl_text is text:
    color "#cfd3da"
    size 15

style pl_title is pl_text:
    size 28
    bold True
    color "#ffffff"

style pl_caption is pl_text:
    size 13
    bold True
    color "#7fb0ff"

style pl_hint is pl_text:
    size 13
    color "#8a8f98"

style pl_code is pl_text:
    size 15
    color "#e6e6e6"

style pl_panel is frame:
    background "#20232a"
    padding (14, 14)
    xfill True

style pl_field is button:
    background "#2c313a"
    hover_background "#3a4150"
    padding (12, 8)
    xfill True

style pl_field_text is pl_text:
    size 15
    color "#ffffff"
    text_align 0.0
    xalign 0.0

style pl_options is vbox:
    background "#1a1d23"
    padding (6, 6)
    spacing 2
    xfill True

style pl_option is button:
    background None
    hover_background "#2c313a"
    selected_background "#2f4d7a"
    selected_hover_background "#3a5d92"
    padding (10, 6)
    xfill True

style pl_option_text is pl_text:
    size 14
    text_align 0.0
    xalign 0.0

style pl_button is button:
    background "#3a5d92"
    hover_background "#4a72ad"
    padding (16, 8)

style pl_button_text is pl_text:
    size 15
    color "#ffffff"

style pl_copy is button:
    background "#2c313a"
    hover_background "#3a4150"
    padding (12, 6)

style pl_copy_text is pl_text:
    size 14
    color "#9fc3ff"


screen pose_lab():
    modal True
    zorder 200

    # Al mostrarse: inicializa la seleccion (primera vez) y pone la musica
    # propia de la herramienta. Al cerrarla, restaura la del menu.
    on "show" action [Function(pl_ensure_init), Function(pl_music_on)]
    on "hide" action Function(pl_music_off)

    $ pl_doki = pl_state["doki"]
    $ pl_cuerpo = pl_state["cuerpo"]
    $ pl_izq = pl_state["izq"]
    $ pl_der = pl_state["der"]
    $ pl_cara = pl_state["cara"]
    $ pl_trans = pl_state["trans"]
    $ pl_fondo = pl_state["fondo"]

    $ left = [b for b in pl_brazos(pl_doki) if b.endswith("l")]
    $ right = [b for b in pl_brazos(pl_doki) if b.endswith("r")]
    $ caras = pl_caras(pl_doki)
    $ poses5 = pl_poses5(pl_doki)
    $ izq_eff = pl_izq or (left[0] if left else "")
    $ der_eff = pl_der or (right[0] if right else "")
    $ cara_eff = pl_cara or (caras[0] if caras else "")
    $ code = pl_code(pl_cuerpo, izq_eff, der_eff, cara_eff)
    $ txt_show = pl_show(pl_doki, code, pl_trans)
    $ txt_def = pl_definicion(pl_doki, izq_eff, der_eff, cara_eff)

    key "K_ESCAPE" action Hide("pose_lab")

    add Solid("#151515")

    hbox:
        spacing 16
        xalign 0.5
        yalign 0.5

        # ----- Columna de controles -----
        frame:
            style "pl_panel"
            xsize 320
            ysize 700

            viewport:
                yfill True
                scrollbars "vertical"
                mousewheel True
                draggable True

                vbox:
                    spacing 10

                    text "PoseLab" style "pl_title"
                    text "Arma una pose y copia el codigo para tu guion." style "pl_hint"

                    use pl_menu("Personaje", pl_doki or "—", "doki", [
                        (d, pl_choose_doki(d), d == pl_doki) for d in pl_personajes()
                    ])

                    use pl_menu("Pose completa (5)", pl_cuerpo or "— usar brazos + cara", "cuerpo", [
                        ("— usar brazos + cara", pl_choose("cuerpo", ""), pl_cuerpo == "")
                    ] + [
                        (c, pl_choose("cuerpo", c), c == pl_cuerpo) for c in poses5
                    ])

                    if pl_cuerpo == "":
                        use pl_menu("Brazo izquierdo", izq_eff or "—", "izq", [
                            (b, pl_choose("izq", b), b == pl_izq) for b in left
                        ])

                        use pl_menu("Brazo derecho", der_eff or "—", "der", [
                            (b, pl_choose("der", b), b == pl_der) for b in right
                        ])

                        use pl_menu("Cara", cara_eff or "—", "cara", [
                            (e, pl_choose("cara", e), e == pl_cara) for e in caras
                        ])

                    use pl_menu("Posicion (transform)", pl_trans, "trans", [
                        (t, pl_choose("trans", t), t == pl_trans) for t in _PL_TRANSFORMS
                    ])

                    use pl_menu("Fondo", pl_fondo or "—", "fondo", [
                        (f, pl_choose("fondo", f), f == pl_fondo) for f in pl_fondos()
                    ])

                    textbutton "Cerrar":
                        style "pl_button"
                        action Hide("pose_lab")

        # ----- Preview + salidas -----
        vbox:
            spacing 14
            xsize 880

            frame:
                style "pl_panel"
                xsize 880
                padding (0, 0)
                fixed:
                    at pl_scaled
                    xalign 0.5
                    xysize (1280, 720)
                    add pl_preview(pl_doki, pl_cuerpo, izq_eff, der_eff, cara_eff, pl_trans, pl_fondo)

            frame:
                style "pl_panel"
                xfill True

                vbox:
                    spacing 10

                    if txt_show:
                        vbox:
                            spacing 4
                            hbox:
                                spacing 8
                                text "show" style "pl_caption"
                                textbutton "Copiar":
                                    style "pl_copy"
                                    action Function(pl_copiar, txt_show)
                            text "[txt_show]" style "pl_code" xmaximum 800

                    if txt_def:
                        vbox:
                            spacing 4
                            hbox:
                                spacing 8
                                text "image (para definitions/sprites.rpy)" style "pl_caption"
                                textbutton "Copiar":
                                    style "pl_copy"
                                    action Function(pl_copiar, txt_def)
                            text "[txt_def]" style "pl_code" xmaximum 800

                    if not code:
                        text "Elegi una pose completa, o brazo izq + brazo der + cara." style "pl_hint"
