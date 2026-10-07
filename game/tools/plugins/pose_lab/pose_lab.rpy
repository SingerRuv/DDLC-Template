## pose_lab.rpy
## PoseLab: arma poses de los personajes leyendo las definiciones REALES de
## im.Composite de todos los .rpy del proyecto. No hay reglas fijas de nombres:
## lo que existe en sprites.rpy (o en cualquier .rpy) es lo que se puede armar.
## Esto funciona con los personajes del template y con personajes propios:
## basta con que definan `image <tag> <pose> = im.Composite(...)`.
##
## Es dev-only: se abre desde el hub "Herramientas" del menú principal.
## Salida: solo la línea `show <tag> <pose> at <transform> zorder 2`.

init python:
    import re as _pl_re
    import pygame as _pl_pygame

    def _pl_cacheado(fn):
        """Cachea el resultado de `fn` por (nombre, argumentos).

        Las definiciones no cambian en runtime, así que se leen una sola vez."""
        cache = {}

        def wrapper(*args):
            key = (fn.__name__, args)
            if key not in cache:
                cache[key] = fn(*args)
            return cache[key]

        return wrapper

    # ======================================================================
    # Posiciones del template (mismas que transforms.rpy).
    # ponytail: vocabulario fijo del template; parsear transforms.rpy sería frágil.
    # ======================================================================

    _PL_X = {
        "t11": 640,
        "t21": 400, "t22": 880,
        "t31": 240, "t32": 640, "t33": 1040,
        "t41": 200, "t42": 493, "t43": 786, "t44": 1080,
    }
    _PL_TRANSFORMS = list(_PL_X)

    # ======================================================================
    # Parser de sprites: lee todos los `image <tag> <nombre> = ...` de los .rpy
    # del proyecto (excluye traducciones y la propia carpeta tools/) y guarda
    # las capas. Es la fuente de verdad; nada se adivina.
    # ======================================================================

    _PL_LINEA_RE = _pl_re.compile(r'^\s*image\s+(\w+)\s+(\w+)\s*=\s*(.+)$')
    _PL_IZQ_RE = _pl_re.compile(r"^\d+[a-z]*l$")
    _PL_DER_RE = _pl_re.compile(r"^\d+[a-z]*r$")
    _PL_CARA_RE = _pl_re.compile(r"^[a-z]$")

    @_pl_cacheado
    def _pl_sprites():
        """{tag: {nombre: [capas]}} de todos los .rpy (excluye tl/ y tools/)."""
        datos = {}
        for f in renpy.list_files():
            if not f.endswith(".rpy") or f.startswith(("tl/", "tools/")):
                continue
            try:
                with renpy.file(f) as fh:
                    texto = fh.read().decode("utf-8")
            except Exception:
                continue
            for linea in texto.splitlines():
                if not linea.lstrip().startswith("image"):
                    continue
                m = _PL_LINEA_RE.match(linea)
                if not m:
                    continue
                # sirve tanto para im.Composite(...) como para = "ruta.png"
                rutas = _pl_re.findall(r'"([^"]+\.png)"', m.group(3))
                if not rutas:
                    continue
                capas = [r.split("/")[-1][:-4] for r in rutas]
                datos.setdefault(m.group(1).lower(), {})[m.group(2)] = capas
        return datos

    def _pl_capas_normales(capas):
        """(izq, der, cara) si las capas son una pose normal; si no, None."""
        izq = der = cara = None
        for c in capas:
            if _PL_IZQ_RE.fullmatch(c):
                izq = c
            elif _PL_DER_RE.fullmatch(c):
                der = c
            elif _PL_CARA_RE.fullmatch(c):
                cara = c
        if izq and der and cara:
            return izq, der, cara
        return None

    def _pl_digitos(arm):
        return int(_pl_re.match(r"\d+", arm).group(0))

    def _pl_outfit(arm):
        """Letras del brazo, sin dígitos ni lado: '1bl' -> 'b', '2l' -> ''."""
        return _pl_re.sub(r"^\d+", "", arm).rstrip("lr")

    @_pl_cacheado
    def _pl_indice(tag):
        """{(outfit, pose, cara): nombre} de las poses normales del tag."""
        res = {}
        for nombre, capas in _pl_sprites().get(tag, {}).items():
            if nombre.startswith("5"):
                continue  # pose 5 = cuerpo completo, va en su propia sección
            t = _pl_capas_normales(capas)
            if not t:
                continue
            izq, der, cara = t
            outfit = _pl_outfit(izq)
            pose = 1 + 2 * (_pl_digitos(izq) - 1) + (_pl_digitos(der) - 1)
            res[(outfit, pose, cara)] = nombre
        return res

    # ======================================================================
    # Personajes custom: carpetas con PNGs sueltos (brazos + caras) que no
    # tienen definiciones im.Composite. Siguen el patrón DDLC (960x960, (0,0)).
    # ======================================================================

    _PL_EXCLUIR = {"bg", "menu", "gui", "tl", "tools", "cache", "saves"}

    @_pl_cacheado
    def _pl_carpetas():
        """{tag: carpeta} de carpetas con brazos y caras, sin definiciones."""
        por_carpeta = {}
        for f in renpy.list_files():
            if not f.lower().endswith(".png"):
                continue
            partes = f.split("/")
            if len(partes) < 2 or any(p in _PL_EXCLUIR for p in partes[:-1]):
                continue
            por_carpeta.setdefault("/".join(partes[:-1]), []).append(partes[-1][:-4])
        res = {}
        for carpeta, nombres in por_carpeta.items():
            tiene_brazo = any(_PL_IZQ_RE.fullmatch(n) or _PL_DER_RE.fullmatch(n)
                              for n in nombres)
            tiene_cara = any(_PL_CARA_RE.fullmatch(n) for n in nombres)
            if tiene_brazo and tiene_cara:
                res[carpeta.split("/")[-1]] = carpeta
        return res

    @_pl_cacheado
    def _pl_archivos_carpeta(tag):
        carpeta = _pl_carpetas().get(tag)
        if not carpeta:
            return []
        return sorted(f.split("/")[-1][:-4] for f in renpy.list_files() if f.startswith(carpeta + "/") and f.lower().endswith(".png"))

    def pl_tiene_defs(tag):
        return bool(_pl_sprites().get(tag))

    def pl_es_custom(tag):
        return tag in _pl_carpetas() and not pl_tiene_defs(tag)

    @_pl_cacheado
    def _pl_indice_archivos(tag):
        """Como _pl_indice pero derivado de los nombres de archivo (custom)."""
        nombres = _pl_archivos_carpeta(tag)
        izqs = [n for n in nombres if _PL_IZQ_RE.fullmatch(n)]
        ders = [n for n in nombres if _PL_DER_RE.fullmatch(n)]
        caras = [n for n in nombres if _PL_CARA_RE.fullmatch(n)]
        res = {}
        for izq in izqs:
            for der in ders:
                outfit = _pl_outfit(izq)
                if outfit != _pl_outfit(der):
                    continue
                pose = 1 + 2 * (_pl_digitos(izq) - 1) + (_pl_digitos(der) - 1)
                for cara in caras:
                    res[(outfit, pose, cara)] = {
                        "nombre": "%d%s%s" % (pose, outfit, cara),
                        "izq": izq, "der": der, "cara": cara}
        return res

    def _pl_indice_tag(tag):
        """{(outfit, pose, cara): nombre}, según el modo del personaje."""
        if pl_tiene_defs(tag):
            return _pl_indice(tag)
        return {k: v["nombre"] for k, v in _pl_indice_archivos(tag).items()}

    # ======================================================================
    # Consultas (cascada): personajes -> outfit -> pose -> cara.
    # ======================================================================

    @_pl_cacheado
    def pl_personajes():
        """Tags con poses normales o cuerpo completo (definidos o custom)."""
        tags = set()
        for t in _pl_sprites():
            if _pl_indice(t) or pl_cuerpos(t):
                tags.add(t)
        for t in _pl_carpetas():
            if _pl_indice_archivos(t) or pl_cuerpos(t):
                tags.add(t)
        orden = ("sayori", "natsuki", "yuri", "monika")
        vanilla = [t for t in orden if t in tags]
        resto = sorted(t for t in tags if t not in orden)
        return vanilla + resto

    @_pl_cacheado
    def pl_cuerpos(tag):
        """Poses completas. En definidos son las imágenes '5x'; en custom son
        los archivos '3x' (convención DDLC: 3a.png -> 5a), mostrados como '5x'."""
        if pl_tiene_defs(tag):
            return sorted(n for n in _pl_sprites().get(tag, {}) if n.startswith("5"))
        return sorted("5" + n[1:] for n in _pl_archivos_carpeta(tag)
                      if _pl_re.fullmatch(r"3\d*[a-z]*", n))

    @_pl_cacheado
    def pl_outfits(tag):
        return sorted({o for (o, p, c) in _pl_indice_tag(tag)})

    @_pl_cacheado
    def pl_poses(tag, outfit):
        return sorted({p for (o, p, c) in _pl_indice_tag(tag) if o == outfit})

    @_pl_cacheado
    def pl_caras(tag, outfit, pose):
        return sorted({c for (o, p, c) in _pl_indice_tag(tag)
                       if o == outfit and p == pose})

    def pl_nombre(tag, outfit, pose, cara):
        """Nombre de la pose (funciona en modo definido y custom)."""
        return _pl_indice_tag(tag).get((outfit, pose, cara), "")

    def pl_outfit_label(outfit):
        return "Uniforme" if outfit == "" else ("Casual" if outfit == "b" else outfit.upper())

    def pl_label(tag):
        return "%s (custom)" % tag if pl_es_custom(tag) else tag

    @_pl_cacheado
    def pl_fondos():
        """Nombres (sin .png) de los fondos en images/bg/."""
        fondos = []
        for f in renpy.list_files():
            partes = f.split("/")
            if len(partes) == 3 and partes[0] == "images" and partes[1] == "bg":
                if partes[2].lower().endswith(".png"):
                    fondos.append(partes[2][:-4])
        return sorted(fondos)

    def pl_tag(tag):
        """Tag de Ren'Py: los nombres de image no admiten espacios."""
        return (tag or "").replace(" ", "")

    # ======================================================================
    # Preview y salida.
    # ======================================================================

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
                    return im.Composite(
                        (960, 960), (0, 0), "%s/%s.png" % (carpeta, i),
                        (0, 0), "%s/%s.png" % (carpeta, d),
                        (0, 0), "%s/%s.png" % (carpeta, c))
            return None
        return renpy.displayable("%s %s" % (pl_tag(tag), nombre))

    def pl_preview(tag, nombre, trans, fondo):
        """Lienzo 1280x720: fondo + la pose en su transform real."""
        c = Fixed(xysize=(1280, 720))
        if fondo:
            c.add("images/bg/%s.png" % fondo)
        disp = _pl_mostrar(tag, nombre)
        if disp is not None:
            c.add(Transform(child=disp, xcenter=_PL_X.get(trans, 493),
                            yanchor=1.0, ypos=1.0, zoom=0.72))
        return c

    def pl_show(tag, nombre, trans):
        """Línea `show ...` para el guion ('' si no hay pose)."""
        if not nombre:
            return ""
        return "show %s %s at %s zorder 2" % (pl_tag(tag), nombre, trans)

    def pl_definicion(tag, nombre):
        """Línea `image ... = im.Composite(...)` para un custom suelto.

        Devuelve '' si el personaje es definido o el nombre no es una pose
        normal (p. ej. cuerpo completo)."""
        if not pl_es_custom(tag):
            return ""
        carpeta = _pl_carpetas().get(tag, "")
        if nombre.startswith("5"):  # cuerpo completo: 3x.png directo
            return ('image %s %s = "%s/3%s.png"'
                    % (pl_tag(tag), nombre, carpeta, nombre[1:]))
        for ref in _pl_indice_archivos(tag).values():
            if ref["nombre"] == nombre:
                return ('image %s %s = im.Composite((960, 960), '
                        '(0, 0), "%s/%s.png", (0, 0), "%s/%s.png", '
                        '(0, 0), "%s/%s.png")'
                        % (pl_tag(tag), nombre, carpeta, ref["izq"],
                           carpeta, ref["der"], carpeta, ref["cara"]))
        return ""

    def pl_definiciones_todas(tag):
        """Todas las líneas `image ...` del custom, ordenadas (para pegar)."""
        if not pl_es_custom(tag):
            return ""
        carpeta = _pl_carpetas().get(tag, "")
        idx = _pl_indice_archivos(tag)
        lineas = []
        for clave in sorted(idx):
            ref = idx[clave]
            lineas.append(
                'image %s %s = im.Composite((960, 960), '
                '(0, 0), "%s/%s.png", (0, 0), "%s/%s.png", (0, 0), "%s/%s.png")'
                % (pl_tag(tag), ref["nombre"], carpeta, ref["izq"],
                   carpeta, ref["der"], carpeta, ref["cara"]))
        for c in pl_cuerpos(tag):
            lineas.append('image %s %s = "%s/3%s.png"'
                          % (pl_tag(tag), c, carpeta, c[1:]))
        return "\n".join(lineas)

    def pl_copiar_todas(tag):
        pl_copiar(pl_definiciones_todas(tag))

    # ======================================================================
    # Estado de la herramienta. Vive en el store (no en variables de screen)
    # para que el sub-screen pl_menu pueda leerlo/escribirlo vía SetDict.
    # ======================================================================

    pl_state = {
        "doki": "", "cuerpo": "", "outfit": "", "pose": 0,
        "cara": "", "trans": "t42", "fondo": "", "open": "",
    }
    pl_initialized = False

    def pl_ensure_init():
        """Inicializa la selección la primera vez que se abre la herramienta."""
        global pl_initialized
        if pl_initialized:
            return
        dokis = pl_personajes()
        fondos = pl_fondos()
        pl_state.update(
            doki=(dokis[0] if dokis else ""), cuerpo="", outfit="", pose=0,
            cara="", trans="t42", fondo=(fondos[0] if fondos else ""), open="")
        pl_initialized = True

    def pl_choose(name, value):
        return [SetDict(pl_state, name, value), SetDict(pl_state, "open", "")]

    def pl_choose_doki(value):
        return [SetDict(pl_state, k, v) for k, v in (
            ("doki", value), ("cuerpo", ""), ("outfit", ""), ("pose", 0),
            ("cara", ""), ("open", ""))]

    def pl_choose_cuerpo(value):
        return [SetDict(pl_state, "cuerpo", value), SetDict(pl_state, "open", "")]

    def pl_choose_outfit(value):
        return [SetDict(pl_state, "outfit", value), SetDict(pl_state, "pose", 0),
                SetDict(pl_state, "cara", ""), SetDict(pl_state, "open", "")]

    def pl_choose_pose(value):
        return [SetDict(pl_state, "pose", value), SetDict(pl_state, "cara", ""),
                SetDict(pl_state, "open", "")]

    def pl_copiar(texto):
        if not texto:
            return
        try:
            _pl_pygame.scrap.put(_pl_pygame.scrap.SCRAP_TEXT, texto.encode("utf-8"))
            renpy.notify("Copiado al portapapeles")
        except Exception:
            renpy.notify("No se pudo copiar")

    def pl_music_on():
        """Música propia de la herramienta (Ohayou Sayori!)."""
        renpy.music.play(audio.t2)

    def pl_music_off():
        """Restaura la música del menú principal al cerrar la herramienta."""
        renpy.music.play(config.main_menu_music)


# Dropdown limpio y reutilizable: título + botón de campo que despliega opciones.
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


# Escala el lienzo 1280x720 del preview para que ocupe su panel.
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

style pl_bad is pl_text:
    size 13
    color "#e07070"

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

    # Al mostrarse: inicializa la selección (primera vez) y pone la música
    # propia de la herramienta. Al cerrarla, restaura la del menú.
    on "show" action [Function(pl_ensure_init), Function(pl_music_on)]
    on "hide" action Function(pl_music_off)

    # --- Resolución de la selección efectiva (cascada) ---
    $ dokis = pl_personajes()
    $ doki = pl_state["doki"] if pl_state["doki"] in dokis else (dokis[0] if dokis else "")

    $ cuerpos = pl_cuerpos(doki)
    $ cuerpo = pl_state["cuerpo"] if pl_state["cuerpo"] in cuerpos else ""

    $ outfits = pl_outfits(doki)
    $ outfit = pl_state["outfit"] if pl_state["outfit"] in outfits else (outfits[0] if outfits else "")
    $ poses = pl_poses(doki, outfit)
    $ pose = pl_state["pose"] if pl_state["pose"] in poses else (poses[0] if poses else 0)
    $ caras = pl_caras(doki, outfit, pose)
    $ cara = pl_state["cara"] if pl_state["cara"] in caras else (caras[0] if caras else "")

    $ nombre = cuerpo or pl_nombre(doki, outfit, pose, cara)
    $ txt_show = pl_show(doki, nombre, pl_state["trans"])
    $ txt_def = pl_definicion(doki, nombre)
    $ hay_custom = pl_es_custom(doki)
    $ pl_fondo = pl_state["fondo"]

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

                    use pl_menu("Personaje", pl_label(doki) or "—", "doki", [
                        (pl_label(d), pl_choose_doki(d), d == doki) for d in dokis
                    ])

                    # Cuerpo completo (pose 5): sección aparte, opcional.
                    if cuerpos:
                        use pl_menu("Cuerpo completo", cuerpo or "— usar pose normal", "cuerpo", [
                            ("— usar pose normal", pl_choose_cuerpo(""), cuerpo == "")
                        ] + [
                            (c, pl_choose_cuerpo(c), c == cuerpo) for c in cuerpos
                        ])

                    if not cuerpo:
                        use pl_menu("Outfit", pl_outfit_label(outfit), "outfit", [
                            (pl_outfit_label(o), pl_choose_outfit(o), o == outfit) for o in outfits
                        ])

                        use pl_menu("Pose", str(pose) if pose else "—", "pose", [
                            (str(p), pl_choose_pose(p), p == pose) for p in poses
                        ])

                        use pl_menu("Cara", cara or "—", "cara", [
                            (c, pl_choose("cara", c), c == cara) for c in caras
                        ])

                    use pl_menu("Posicion (transform)", pl_state["trans"], "trans", [
                        (t, pl_choose("trans", t), t == pl_state["trans"]) for t in _PL_TRANSFORMS
                    ])

                    use pl_menu("Fondo", pl_fondo or "—", "fondo", [
                        (f, pl_choose("fondo", f), f == pl_fondo) for f in pl_fondos()
                    ])

                    textbutton "Cerrar":
                        style "pl_button"
                        action Hide("pose_lab")

        # ----- Preview + salida -----
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
                    add pl_preview(doki, nombre, pl_state["trans"], pl_fondo)

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

                    if hay_custom and txt_def:
                        vbox:
                            spacing 4
                            hbox:
                                spacing 8
                                text "image (pegar en sprites.rpy)" style "pl_caption"
                                textbutton "Copiar":
                                    style "pl_copy"
                                    action Function(pl_copiar, txt_def)
                                textbutton "Copiar todas":
                                    style "pl_copy"
                                    action Function(pl_copiar_todas, doki)
                            text "[txt_def]" style "pl_code" xmaximum 800

                    if not txt_show:
                        text "Elegi personaje, outfit, pose y cara." style "pl_hint"
