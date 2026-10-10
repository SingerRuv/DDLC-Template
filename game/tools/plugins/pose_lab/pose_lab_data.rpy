## pose_lab_data.rpy
## PoseLab — Lógica (sin UI): parser de sprites, índices, consultas, estado,
## transforms disponibles, salida y utilidades (portapapeles, música).
##
## La interfaz vive en pose_lab_ui.rpy y el preview en pose_lab_preview.rpy.
## El screen raíz (pose_lab) en pose_lab.rpy.

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
    # Transforms del template ofrecidos para la salida `show ... at <t>`.
    #   Posición: t11..t44 | Focus: f11..f44 | Entradas: l*/r* (2+ personajes)
    # ======================================================================

    _PL_POS = ["t11", "t21", "t22", "t31", "t32", "t33", "t41", "t42", "t43", "t44"]
    _PL_FOCUS = ["f11", "f21", "f22", "f31", "f32", "f33", "f41", "f42", "f43", "f44"]
    _PL_ENTRADAS = [
        "l21", "l22", "l31", "l32", "l33", "l41", "l42", "l43", "l44",
        "r21", "r22", "r31", "r32", "r33", "r41", "r42", "r43", "r44",
    ]

    def pl_trans_actual(grupo):
        """Transform actual si pertenece al grupo dado; si no, '—'."""
        actual = pl_state["trans"]
        if actual in grupo:
            return actual
        return "—"

    # ======================================================================
    # Parser de sprites: lee todos los `image <tag> <nombre> = ...` de los .rpy
    # del proyecto (excluye traducciones y la propia carpeta tools/) y guarda
    # las capas. Es la fuente de verdad; nada se adivina.
    # ======================================================================

    _PL_LINEA_RE = _pl_re.compile(r'^\s*image\s+(\w+)\s+(\w+)\s*=\s*(.+)$')
    _PL_IZQ_RE = _pl_re.compile(r"^\d+[a-z]*l$")
    _PL_DER_RE = _pl_re.compile(r"^\d+[a-z]*r$")
    _PL_CARA_RE = _pl_re.compile(r"^[a-z]$")
    # Poses especiales de Natsuki: 12/42 (cabeza 2t*) — la cara va como `2t[letra]`.
    _PL_ESPECIAL_RE = _pl_re.compile(r"^(12|42)([a-z]?)$")

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
                # sirve tanto para Composite(...) como para = "ruta.png"
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
        """{(outfit, pose, cara): nombre} de las poses del tag (incl. especiales)."""
        res = {}
        for nombre, capas in _pl_sprites().get(tag, {}).items():
            if nombre.startswith("5"):
                continue  # pose 5 = cuerpo completo, va en su propia sección

            # Poses especiales (p. ej. natsuki 12/42): el nombre manda.
            esp = _PL_ESPECIAL_RE.match(nombre)
            if esp:
                res[("", int(esp.group(1)), esp.group(2) or "")] = nombre
                continue

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
    # tienen definiciones Composite. Siguen el patrón DDLC (960x960, (0,0)).
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
        return sorted(f.split("/")[-1][:-4] for f in renpy.list_files()
                      if f.startswith(carpeta + "/") and f.lower().endswith(".png"))

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

    def pl_cara_label(cara):
        """Etiqueta de cara. Vacío solo ocurre en poses especiales (sprite base)."""
        return cara if cara else "(base)"

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
    # Salida para el guion.
    # ======================================================================

    def pl_show(tag, nombre, trans):
        """Línea `show ...` para el guion ('' si no hay pose)."""
        if not nombre:
            return ""
        return "show %s %s at %s zorder 2" % (pl_tag(tag), nombre, trans)

    # ======================================================================
    # Estado de la herramienta. Vive en el store (no en variables de screen)
    # para que los sub-screens puedan leerlo/escribirlo vía SetDict.
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

    def pl_resuelto():
        """Resuelve la selección efectiva (cascada) y devuelve un dict con la
        selección + las listas disponibles. Fuente común para UI y preview."""
        dokis = pl_personajes()
        doki = pl_state["doki"] if pl_state["doki"] in dokis else (dokis[0] if dokis else "")

        cuerpos = pl_cuerpos(doki)
        cuerpo = pl_state["cuerpo"] if pl_state["cuerpo"] in cuerpos else ""

        outfits = pl_outfits(doki)
        outfit = pl_state["outfit"] if pl_state["outfit"] in outfits else (outfits[0] if outfits else "")
        poses = pl_poses(doki, outfit)
        pose = pl_state["pose"] if pl_state["pose"] in poses else (poses[0] if poses else 0)
        caras = pl_caras(doki, outfit, pose)
        cara = pl_state["cara"] if pl_state["cara"] in caras else (caras[0] if caras else "")

        nombre = cuerpo or pl_nombre(doki, outfit, pose, cara)
        return {
            "doki": doki, "cuerpos": cuerpos, "cuerpo": cuerpo,
            "outfits": outfits, "outfit": outfit,
            "poses": poses, "pose": pose,
            "caras": caras, "cara": cara,
            "nombre": nombre, "fondo": pl_state["fondo"],
            "trans": pl_state["trans"],
        }

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

    # ======================================================================
    # Utilidades.
    # ======================================================================

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
