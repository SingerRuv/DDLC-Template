## pose_lab_data.rpy
## PoseLab — Lógica (sin UI): parser de sprites, índices, consultas, estado,
## transforms disponibles, salida y utilidades (portapapeles, música).
##
## La interfaz vive en pose_lab_ui.rpy y el preview en pose_lab_preview.rpy.
## El screen raíz (pose_lab) en pose_lab.rpy.

init python:
    import re as _pl_re
    import os as _pl_os
    import pygame as _pl_pygame

    # Registro de todas las cachés de PoseLab (para poder limpiarlas con el
    # botón "Reescanear"). Ver `pl_limpiar_cache`.
    _PL_CACHES = []

    def _pl_cacheado(fn):
        """Cachea el resultado de `fn` por (nombre, argumentos).

        Las definiciones no cambian en runtime, así que se leen una sola vez.
        La caché se registra en `_PL_CACHES` para poder limpiarla."""
        cache = {}
        _PL_CACHES.append(cache)

        def wrapper(*args):
            key = (fn.__name__, args)
            if key not in cache:
                cache[key] = fn(*args)
            return cache[key]

        return wrapper

    # ======================================================================
    # Transforms del template ofrecidos para la salida `show ... at <t>`.
    # Se arman como familia (letra) + slot (11..44). Definidas en
    # definitions/transforms.rpy. La familia "Normal" = t11..t44.
    # ======================================================================

    _PL_SLOTS = ["11", "21", "22", "31", "32", "33", "41", "42", "43", "44"]

    # Familias: (etiqueta, prefijo). El transform es prefijo + slot.
    _PL_FAMILIAS = [
        ("Normal", "t"),
        ("Instantáneo", "i"),
        ("Focus", "f"),
        ("Hop", "h"),
        ("Dip", "d"),
        ("Sink", "s"),
        ("Hop-focus", "hf"),
        ("Entrada izq", "l"),
        ("Entrada der", "r"),
    ]

    def pl_prefijo(variante):
        for label, pref in _PL_FAMILIAS:
            if label == variante:
                return pref
        return "t"

    def pl_trans_de(variante, slot):
        return "%s%s" % (pl_prefijo(variante), slot)

    def pl_slot_de(trans):
        """Slot ('11'..'44') de un transform, o '' si no es una posición."""
        for label, pref in _PL_FAMILIAS:
            if trans.startswith(pref):
                resto = trans[len(pref):]
                if resto in _PL_SLOTS:
                    return resto
        return ""

    # Capas de la línea `show ... zorder N` (quién queda detrás/delante).
    _PL_ZORDERS = [0, 1, 2, 3, 4, 5]

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
    # Formato "cuerpo + expresión" (2 capas): cuerpo = pose (`1`, `2`, `1b`, `2b`),
    # expresión = `a`, `a1`, `i5`… (ver `_pl_capas_body_cara`).
    _PL_BODY_RE = _pl_re.compile(r"^\d+[a-z]*$")
    _PL_CARA2_RE = _pl_re.compile(r"^[a-z]\d*$")

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

    def _pl_capas_body_cara(capas):
        """(body, cara) si las capas son 'cuerpo + expresión' (2 capas); si no, None.

        Formato del pack MC: `Composite("1.png", "a.png")` → cuerpo `1` + expresión `a`."""
        body = cara = None
        for c in capas:
            if _PL_BODY_RE.fullmatch(c):
                body = c
            elif _PL_CARA2_RE.fullmatch(c):
                cara = c
        if body and cara:
            return body, cara
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
            if t:
                izq, der, cara = t
                outfit = _pl_outfit(izq)
                pose = 1 + 2 * (_pl_digitos(izq) - 1) + (_pl_digitos(der) - 1)
                res[(outfit, pose, cara)] = nombre
                continue

            # Formato "cuerpo + expresión" (2 capas), p.ej. `image mc 1a = Composite("1", "a")`.
            bc = _pl_capas_body_cara(capas)
            if bc:
                body, cara = bc
                res[(_pl_outfit(body), _pl_digitos(body), cara)] = nombre
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
        return ((tag in _pl_carpetas() or tag in _pl_carpetas_body_expr())
                and not pl_tiene_defs(tag))

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

    # --- Formato "cuerpo + expresión" por carpetas anidadas (sin definiciones):
    #     una subcarpeta con los cuerpos y otra con las expresiones. El
    #     personaje es la carpeta PADRE.

    @_pl_cacheado
    def _pl_carpetas_body_expr():
        """{tag: (dir_cuerpos, dir_expresiones)}."""
        por_dir = {}
        for f in renpy.list_files():
            if not f.lower().endswith(".png"):
                continue
            partes = f.split("/")
            if len(partes) < 2 or any(p in _PL_EXCLUIR for p in partes[:-1]):
                continue
            por_dir.setdefault("/".join(partes[:-1]), []).append(partes[-1][:-4])
        tipos = {}
        for d, nombres in por_dir.items():
            tiene_cuerpo = any(_PL_BODY_RE.fullmatch(n) for n in nombres)
            tiene_expr = any(_PL_CARA2_RE.fullmatch(n) for n in nombres)
            if tiene_cuerpo and not tiene_expr:
                tipos[d] = "cuerpos"
            elif tiene_expr and not tiene_cuerpo:
                tipos[d] = "exprs"
        res = {}
        for d in tipos:
            padre = d.rsplit("/", 1)[0] if "/" in d else ""
            if not padre or padre in res:
                continue
            hermanos = [dd for dd, tt in tipos.items()
                        if (dd.rsplit("/", 1)[0] if "/" in dd else "") == padre]
            dc = next((dd for dd in hermanos if tipos[dd] == "cuerpos"), None)
            de = next((dd for dd in hermanos if tipos[dd] == "exprs"), None)
            if dc and de:
                res[padre.split("/")[-1]] = (dc, de)
        return res

    def pl_es_body_expr(tag):
        return tag in _pl_carpetas_body_expr() and not pl_tiene_defs(tag)

    @_pl_cacheado
    def _pl_imgs_en(carpeta):
        """{nombre: ruta} de los .png directamente en `carpeta`."""
        res = {}
        pre = carpeta + "/"
        for f in renpy.list_files():
            if f.startswith(pre) and f.lower().endswith(".png"):
                resto = f[len(pre):]
                if "/" not in resto:
                    res[resto[:-4]] = f
        return res

    @_pl_cacheado
    def _pl_indice_body_expr(tag):
        """{(outfit, pose, cara): {nombre, body, expr}} (custom, 2 capas)."""
        dc = _pl_carpetas_body_expr().get(tag)
        if not dc:
            return {}
        cuerpos, exprs = _pl_imgs_en(dc[0]), _pl_imgs_en(dc[1])
        res = {}
        for body, body_path in cuerpos.items():
            if not _PL_BODY_RE.fullmatch(body):
                continue
            for expr, expr_path in exprs.items():
                if not _PL_CARA2_RE.fullmatch(expr):
                    continue
                res[(_pl_outfit(body), _pl_digitos(body), expr)] = {
                    "nombre": "%s%s" % (body, expr),
                    "body": body_path, "expr": expr_path}
        return res

    def _pl_paths_body_expr(tag, nombre):
        """(ruta_cuerpo, ruta_expr) del nombre dado, o (None, None)."""
        for v in _pl_indice_body_expr(tag).values():
            if v["nombre"] == nombre:
                return v["body"], v["expr"]
        return None, None

    def _pl_indice_tag(tag):
        """{(outfit, pose, cara): nombre}, según el modo del personaje."""
        if pl_tiene_defs(tag):
            return _pl_indice(tag)
        if tag in _pl_carpetas_body_expr():
            return {k: v["nombre"] for k, v in _pl_indice_body_expr(tag).items()}
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
        for t in _pl_carpetas_body_expr():
            if _pl_indice_body_expr(t):
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

    def pl_show(tag, nombre, trans, zorder=2):
        """Línea `show ...` para el guion ('' si no hay pose)."""
        if not nombre:
            return ""
        return "show %s %s at %s zorder %d" % (pl_tag(tag), nombre, trans, zorder)

    def pl_codigo(r):
        """Código para el botón "Código". En el modo "cuerpo + expresión" sin
        definiciones, incluye la definición `image ... = Composite(...)`
        (si no, un `show <tag> <pose>` daría error)."""
        if not r["nombre"]:
            return ""
        linea = pl_show(r["doki"], r["nombre"], r["trans"], r["zorder"])
        if pl_es_body_expr(r["doki"]):
            b, e = _pl_paths_body_expr(r["doki"], r["nombre"])
            if b and e:
                defn = ('image %s %s = Composite((960, 960), (0, 0), "%s", (0, 0), "%s")'
                        % (pl_tag(r["doki"]), r["nombre"], b, e))
                return defn + "\n" + linea
        return linea

    # ======================================================================
    # Estado de la herramienta. Vive en el store (no en variables de screen)
    # para que los sub-screens puedan leerlo/escribirlo vía SetDict.
    # ======================================================================

    pl_state = {
        "doki": "", "cuerpo": "", "outfit": "", "pose": 0,
        "cara": "", "trans": "t11", "variante": "Normal", "zorder": 2, "fondo": "class", "open": "",
        # "Copiar en…": archivo destino, línea elegida y texto a insertar.
        "destino_archivo": "", "destino_linea": 0, "destino_texto": "",
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
            cara="", trans="t11", variante="Normal",
            fondo=("class" if "class" in fondos else (fondos[0] if fondos else "")),
            open="")
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
            "trans": pl_state["trans"], "variante": pl_state["variante"], "zorder": pl_state["zorder"],
        }

    def pl_referencia(doki):
        """(tag, nombre) del primer personaje distinto a `doki`, con una pose
        por defecto. Sirve de referencia en el preview para ver el layering del
        zorder. None si no hay otro personaje."""
        for d in pl_personajes():
            if d == doki:
                continue
            cuerpos = pl_cuerpos(d)
            if cuerpos:
                return d, cuerpos[0]
            outfits = pl_outfits(d)
            if not outfits:
                continue
            outfit = outfits[0]
            poses = pl_poses(d, outfit)
            if not poses:
                continue
            pose = poses[0]
            caras = pl_caras(d, outfit, pose)
            nombre = pl_nombre(d, outfit, pose, caras[0] if caras else "")
            if nombre:
                return d, nombre
        return None

    def pl_choose(name, value):
        return [SetDict(pl_state, name, value), SetDict(pl_state, "open", "")]

    def pl_choose_variante(variante):
        # Cambia la familia conservando el slot actual (por defecto, 11).
        slot = pl_slot_de(pl_state["trans"]) or "11"
        return [SetDict(pl_state, "variante", variante),
                SetDict(pl_state, "trans", pl_trans_de(variante, slot)),
                SetDict(pl_state, "open", "")]

    def pl_choose_doki(value):
        return [SetDict(pl_state, k, v) for k, v in (
            ("doki", value), ("cuerpo", ""), ("outfit", ""), ("pose", 0),
            ("cara", ""), ("open", ""))]

    def pl_choose_cuerpo(value):
        # Al elegir cuerpo completo, si el transform no es una posición, resetealo.
        acciones = [SetDict(pl_state, "cuerpo", value), SetDict(pl_state, "open", "")]
        if value and not pl_slot_de(pl_state["trans"]):
            acciones.append(SetDict(pl_state, "trans", pl_trans_de(pl_state["variante"], "11")))
        return acciones

    def pl_choose_outfit(value):
        return [SetDict(pl_state, "outfit", value), SetDict(pl_state, "pose", 0),
                SetDict(pl_state, "cara", ""), SetDict(pl_state, "open", "")]

    def pl_choose_pose(value):
        return [SetDict(pl_state, "pose", value), SetDict(pl_state, "cara", ""),
                SetDict(pl_state, "open", "")]

    def pl_menus(r):
        """Menús de la ventana de controles: (título, valor, clave, opciones)."""
        menus = [
            ("Personaje", pl_label(r["doki"]) or "—", "doki", [
                (pl_label(d), pl_choose_doki(d), d == r["doki"])
                for d in pl_personajes()
            ]),
        ]
        # Cuerpo completo (pose 5): sección aparte, opcional.
        if r["cuerpos"]:
            menus.append(("Cuerpo completo", r["cuerpo"] or "— normal", "cuerpo", [
                ("— normal", pl_choose_cuerpo(""), r["cuerpo"] == ""),
            ] + [
                (c, pl_choose_cuerpo(c), c == r["cuerpo"]) for c in r["cuerpos"]
            ]))
        if not r["cuerpo"]:
            menus.append(("Outfit", pl_outfit_label(r["outfit"]), "outfit", [
                (pl_outfit_label(o), pl_choose_outfit(o), o == r["outfit"])
                for o in r["outfits"]
            ]))
            menus.append(("Pose", str(r["pose"]) if r["pose"] else "—", "pose", [
                (str(p), pl_choose_pose(p), p == r["pose"]) for p in r["poses"]
            ]))
            menus.append(("Cara", pl_cara_label(r["cara"]), "cara", [
                (pl_cara_label(c), pl_choose("cara", c), c == r["cara"])
                for c in r["caras"]
            ]))
        # Familia (letra) y posición (slot). El transform final es familia+slot.
        menus.append(("Variante", pl_state["variante"], "variante", [
            (label, pl_choose_variante(label), label == pl_state["variante"])
            for label, _pref in _PL_FAMILIAS
        ]))
        menus.append(("Posición", pl_state["trans"], "trans", [
            (pl_trans_de(pl_state["variante"], s), pl_choose("trans", pl_trans_de(pl_state["variante"], s)),
             pl_trans_de(pl_state["variante"], s) == pl_state["trans"]) for s in _PL_SLOTS
        ]))
        menus.append(("Fondo", r["fondo"] or "—", "fondo", [
            (f, pl_choose("fondo", f), f == r["fondo"]) for f in pl_fondos()
        ]))
        # Capa de la línea show (detrás/delante).
        menus.append(("Zorder", str(pl_state["zorder"]), "zorder", [
            (str(z), pl_choose("zorder", z), z == pl_state["zorder"])
            for z in _PL_ZORDERS
        ]))
        return menus

    # ======================================================================
    # Ventanas flotantes: posición y estado "fijada", persistentes entre
    # sesiones (global; no depende de los saves). Es dev-only.
    # ======================================================================

    _PL_VENTANAS = {"controls": (24, 24), "code": (790, 24)}

    def pl_ventana_pos(nombre):
        # `persistent` devuelve None para atributos no definidos (no AttributeError).
        pos = getattr(persistent, "pl_pos_" + nombre, None)
        return pos if pos is not None else _PL_VENTANAS[nombre]

    def pl_ventana_fija(nombre):
        return bool(getattr(persistent, "pl_fija_" + nombre, None))

    def pl_ventana_mover(nombre, x, y):
        setattr(persistent, "pl_pos_" + nombre, (int(x), int(y)))

    def pl_ventana_alternar_fija(nombre):
        setattr(persistent, "pl_fija_" + nombre, not pl_ventana_fija(nombre))

    def pl_drag_mover(nombre):
        """Callback para `dragged`: guarda dónde quedó la ventana al soltarla."""
        def cb(drags, drop):
            if drags:
                pl_ventana_mover(nombre, drags[0].x, drags[0].y)
        return cb

    def pl_ventana_reiniciar(nombre):
        """Devuelve la ventana a su posición por defecto (persistente + snap)."""
        x, y = _PL_VENTANAS[nombre]
        setattr(persistent, "pl_pos_" + nombre, (x, y))
        d = renpy.get_displayable("pose_lab", "pl_drag_" + nombre)
        if d is not None:
            d.snap(x, y, delay=0.2)

    # ======================================================================
    # Utilidades.
    # ======================================================================

    def pl_toast(mensaje):
        """Toast propio (animado) de la herramienta. Ver `screen pl_notify`."""
        renpy.hide_screen("pl_notify")
        renpy.show_screen("pl_notify", message=mensaje)

    def pl_limpiar_cache():
        """Limpia todas las cachés de lectura (definiciones de sprites/carpetas)."""
        for c in _PL_CACHES:
            c.clear()

    def pl_avisar_deteccion():
        """Toast al abrir: cuántos personajes hay y cuáles son nuevos."""
        tags = pl_personajes()
        vistos = persistent.pl_personajes_visto or []
        nuevos = [t for t in tags if t not in vistos]
        msg = "%d personaje%s" % (len(tags), "" if len(tags) == 1 else "s")
        if nuevos:
            msg += " · nuevo: " + ", ".join(nuevos)
        persistent.pl_personajes_visto = list(tags)
        pl_toast(msg)

    def pl_reescanear():
        """Vuelve a leer las definiciones/carpetas (limpia las cachés)."""
        pl_limpiar_cache()
        pl_resuelto()  # re-resuelve la selección con las listas nuevas
        tags = pl_personajes()
        pl_toast("Reescaneado: %d personaje%s"
                 % (len(tags), "" if len(tags) == 1 else "s"))

    def pl_copiar(texto):
        if not texto:
            return
        try:
            _pl_pygame.scrap.put(_pl_pygame.scrap.SCRAP_TEXT, texto.encode("utf-8"))
            pl_toast("¡Definición copiada!")
            renpy.restart_interaction()
        except Exception:
            pl_toast("No se pudo copiar")

    # ======================================================================
    # "Copiar en…": escribir la definición dentro de un .rpy del guion.
    #   Un .rpy es destino si tiene el marcador `# poselab` en una línea.
    #   Solo se escribe en archivos físicos (no dentro de un .rpa).
    # ======================================================================

    _PL_MARCADOR_RE = _pl_re.compile(r"^\s*#\s*poselab\b", _pl_re.MULTILINE)
    _PL_SALTAR = ("tools/", "tl/")

    def _pl_objetivo_abs(rel):
        """Ruta física de un .rpy del proyecto (relativa a game/)."""
        return _pl_os.path.join(config.gamedir, rel.replace("/", _pl_os.sep))

    def pl_objetivos():
        """Rutas (relativas, con '/') de los .rpy ofrecidos como destino.

        Deben contener el marcador `# poselab` y existir como archivo físico:
        los .rpy empaquetados dentro de un .rpa no se pueden escribir.
        No se cachea: Ren'Py predice el screen al arrancar (con la lista de
        archivos todavia incompleta) y ademas el modder puede agregar el
        marcador a otro .rpy durante la sesion."""
        res = []
        for f in renpy.list_files():
            if not f.endswith(".rpy") or f.startswith(_PL_SALTAR):
                continue
            if not _pl_os.path.isfile(_pl_objetivo_abs(f)):
                continue
            try:
                with renpy.file(f) as fh:
                    texto = fh.read().decode("utf-8")
            except Exception:
                continue
            if _PL_MARCADOR_RE.search(texto):
                res.append(f)
        return sorted(res)

    def pl_leer_objetivo(rel):
        """Líneas del archivo destino (se lee del disco en cada llamada, así el
        preview refleja lo escrito)."""
        if not rel:
            return []
        try:
            with open(_pl_objetivo_abs(rel), "r", encoding="utf-8") as fh:
                return fh.read().split("\n")
        except Exception:
            return []

    def pl_insertar(rel, idx, texto, sangria="    "):
        """Inserta `texto` con sangría de 4 espacios (columna 5) tras la línea
        `idx` (0-based). Guarda un backup antes de escribir."""
        ruta = _pl_objetivo_abs(rel)
        try:
            with open(ruta, "r", encoding="utf-8") as fh:
                original = fh.read()
            nl = "\r\n" if "\r\n" in original else "\n"
            lineas = original.split(nl)
            lineas.insert(idx + 1, (sangria + texto) if texto else "")
            with open(ruta + ".poselab.bak", "w", encoding="utf-8") as fh:
                fh.write(original)
            with open(ruta, "w", encoding="utf-8") as fh:
                fh.write(nl.join(lineas))
            return True
        except Exception:
            return False

    def pl_deshacer(rel):
        """Restaura el archivo desde su backup (un nivel)."""
        ruta = _pl_objetivo_abs(rel)
        bak = ruta + ".poselab.bak"
        if not _pl_os.path.isfile(bak):
            return False
        try:
            with open(bak, "r", encoding="utf-8") as fh:
                original = fh.read()
            with open(ruta, "w", encoding="utf-8") as fh:
                fh.write(original)
            return True
        except Exception:
            return False

    def pl_abrir_objetivo(rel, linea=0):
        """Abre el .rpy destino en el editor del sistema (best-effort)."""
        if rel:
            renpy.launch_editor([_pl_objetivo_abs(rel)], line=linea + 1)

    def pl_destino_init(texto):
        """Prepara el estado de "Copiar en…" al abrir el panel."""
        objs = pl_objetivos()
        pl_state["destino_archivo"] = objs[0] if objs else ""
        pl_state["destino_linea"] = 0
        pl_state["destino_texto"] = texto

    def pl_escribir_destino():
        rel = pl_state["destino_archivo"]
        if not rel:
            return
        idx = pl_state["destino_linea"]
        if pl_insertar(rel, idx, pl_state["destino_texto"]):
            pl_state["destino_linea"] = idx + 1
            pl_toast("Definición insertada")
        else:
            pl_toast("No se pudo escribir")
        renpy.restart_interaction()

    def pl_deshacer_destino():
        if pl_deshacer(pl_state["destino_archivo"]):
            pl_toast("Cambios deshechos")
        else:
            pl_toast("No hay nada que deshacer")
        renpy.restart_interaction()

    def pl_abrir_destino():
        pl_abrir_objetivo(pl_state["destino_archivo"], pl_state["destino_linea"])
