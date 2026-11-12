## inserter.rpy
## Panel "Copiar en…" compartido por los plugins que generan código para la
## historia (PoseLab, Shaders Lab, Diálogo): escribir un snippet dentro de un
## .rpy del guion sin romperlo.
##
## Cada plugin pasa su estado, el marcador que habilita un archivo como destino
## ("# poselab", "# dialogo", "# shaders"), el título del panel y su función de
## aviso.
##
## Reglas:
##   - Solo se escriben archivos físicos del proyecto (nada dentro de un .rpa).
##   - La sangría sale de la línea elegida: un define va al nivel superior y
##     una sentencia dentro de un label.
##   - Si el .rpy quedaría inválido, no se escribe nada.
##   - Se respeta el fin de línea del archivo (LF o CRLF).
##   - Antes de escribir se guarda un backup con el sufijo indicado.
##   - Escribir NO reinicia el juego.

init python:

    import io as _ins_io
    import os as _ins_os
    import re as _ins_re
    import subprocess as _ins_subprocess
    import time as _ins_time

    # Carpetas que no son destino: las herramientas y las traducciones.
    _INS_SALTAR = ("plugins/", "tl/")

    # Última escritura del panel: la usa el filtro de autoreload.
    _INS_RECIENTE = {"ruta": "", "ts": 0.0}

    # Caché de la validación (parsear el archivo entero en cada frame es caro).
    _INS_VALIDA = {"clave": None, "ok": True, "msg": ""}

    def ins_ruta(rel):
        """Ruta física de un .rpy del proyecto (relativa a game/)."""
        return _ins_os.path.join(config.gamedir, rel.replace("/", _ins_os.sep))

    def _ins_redo(sufijo):
        """Sufijo del snapshot de rehacer (`.poselab.bak` -> `.poselab.redo`)."""
        return sufijo[:-4] + ".redo" if sufijo.endswith(".bak") else sufijo + ".redo"

    def _ins_borrar(ruta):
        try:
            _ins_os.remove(ruta)
        except OSError:
            pass

    def _ins_normal(ruta):
        """Normaliza una ruta como clave del watcher (absoluta con /)."""
        return _ins_os.path.abspath(ruta).replace("\\", "/")

    def _ins_refrescar_watcher(ruta):
        """Fija el mtime de referencia del archivo en el watcher de autoreload.

        El loader registra cada .rpy al arrancar con su propia clave
        (`script.py`: dir + "/" + fn + ".rpy"). Si `add_auto` usa otra clave,
        queda una vieja con el mtime anterior y Ren'Py recarga el script a los
        ~1,5 s (en el menú eso reinicia el juego). Por eso se refrescan todas
        las claves que resuelvan al mismo archivo, no solo la nuestra."""
        try:
            clave = _ins_normal(ruta)
            mtimes = renpy.loader.auto_mtimes
            with renpy.loader.auto_lock:
                for k in list(mtimes):
                    if not isinstance(k, str):
                        continue
                    if mtimes[k] is renpy.loader.auto_blacklisted:
                        continue
                    if _ins_normal(k) == clave:
                        mtimes[k] = renpy.loader.auto_mtime(k)
                        renpy.loader.needs_autoreload.discard(k)
                renpy.loader.needs_autoreload.discard(clave)
            renpy.loader.add_auto(ruta, force=True)
            _INS_RECIENTE["ruta"] = clave
            _INS_RECIENTE["ts"] = _ins_time.time()
        except Exception as e:
            print("plugins.inserter: no se pudo refrescar el watcher: %s" % e)

    def _ins_escribir(ruta, texto):
        """Escribe `texto` en `ruta` sin que el autoreload recargue el script."""
        with renpy.loader.auto_lock:
            with _ins_io.open(ruta, "w", encoding="utf-8", newline="") as fh:
                fh.write(texto)
        _ins_refrescar_watcher(ruta)

    def _ins_autoreload(fn):
        """Filtro de `config.autoreload_functions`.

        Red de seguridad: si el watcher igual marca el archivo que el panel
        acaba de escribir, se ignora. Cualquier otro .rpy recarga como siempre.
        `fn` llega relativo a game/."""
        if _INS_RECIENTE["ruta"]:
            ruta = _ins_normal(_ins_os.path.join(config.gamedir, fn))
            if ruta == _INS_RECIENTE["ruta"] \
                    and _ins_time.time() - _INS_RECIENTE["ts"] < 3.0:
                print("plugins.inserter: autoreload ignorado para %s" % fn)
                return
        renpy.exports.reload_script()

    if _ins_autoreload not in [f for _r, f in config.autoreload_functions]:
        config.autoreload_functions.append((r"\.rpy$", _ins_autoreload))

    def ins_marcador(marcador):
        """Regex de las líneas que habilitan un archivo como destino."""
        return _ins_re.compile(
            r"^\s*#\s*%s\b" % _ins_re.escape(marcador), _ins_re.MULTILINE,
        )

    def ins_objetivos(marcador):
        """Archivos .rpy del proyecto que tienen el marcador dado."""
        regex = ins_marcador(marcador)
        res = []
        for f in renpy.list_files():
            if not f.endswith(".rpy") or f.startswith(_INS_SALTAR):
                continue
            ruta = ins_ruta(f)
            if not _ins_os.path.isfile(ruta):
                continue
            try:
                with _ins_io.open(ruta, encoding="utf-8-sig") as fh:
                    if not regex.search(fh.read()):
                        continue
            except Exception:
                continue
            res.append(f)
        return sorted(res)

    def ins_leer(rel):
        """Líneas del archivo destino (se releen en cada llamada, así el
        preview refleja lo escrito)."""
        if not rel:
            return []
        try:
            with _ins_io.open(ins_ruta(rel), encoding="utf-8-sig", newline="") as fh:
                texto = fh.read()
            return texto.replace("\r\n", "\n").replace("\r", "\n").split("\n")
        except Exception:
            return []

    def ins_indent(linea):
        """La sangría de una línea."""
        return linea[:len(linea) - len(linea.lstrip())]

    def ins_sangria(lineas, idx):
        """Sangría del código que se inserta después de la línea `idx`.

        La línea elegida manda; si es un encabezado de bloque, el código
        entra adentro del bloque. Así un define cae arriba del todo y una
        sentencia dentro de un label, sin que el modder lo piense.
        """
        for i in range(max(idx, 0), len(lineas)):
            if not lineas[i].strip():
                continue
            if not lineas[i].rstrip().endswith(":"):
                return ins_indent(lineas[i])
            for j in range(i + 1, len(lineas)):
                if lineas[j].strip():
                    return ins_indent(lineas[j])
            return ins_indent(lineas[i]) + "    "
        return ""

    def ins_bloque(lineas, idx):
        """Encabezado del bloque que contiene la línea (p. ej. "label starter")."""
        if not lineas:
            return ""
        i = max(0, min(idx, len(lineas) - 1))
        while i < len(lineas) and not lineas[i].strip():
            i += 1
        if i >= len(lineas):
            return ""
        if lineas[i].rstrip().endswith(":"):
            return lineas[i].strip().rstrip(":")
        base = len(ins_indent(lineas[i]))
        j = i - 1
        while j >= 0:
            if lineas[j].strip():
                if len(ins_indent(lineas[j])) < base:
                    txt = lineas[j].strip()
                    return txt.rstrip(":") if txt.endswith(":") else ""
            j -= 1
        return ""

    def _ins_componer(lineas, ancla, texto, reemplazar=False):
        """(líneas nuevas, sangría, líneas del snippet, posición).

        `ancla` es el índice después del cual se inserta; -1 = arriba del todo.
        Si `reemplazar`, el snippet ocupa la línea `ancla` (una línea vacía).
        Lo usan el preview y la escritura para no divergir nunca."""
        if reemplazar:
            pos = max(0, min(ancla, len(lineas) - 1))
            sangria = ins_sangria(lineas, pos)
        elif ancla < 0:
            sangria, pos = "", 0
        else:
            pos = min(ancla + 1, len(lineas))
            sangria = ins_sangria(lineas, ancla)

        bloque = [(sangria + l) if l.strip() else l
                  for l in (texto.split("\n") if texto else [])]
        nuevas = list(lineas)
        if reemplazar:
            nuevas[pos:pos + 1] = bloque
        else:
            nuevas[pos:pos] = bloque
        return nuevas, sangria, bloque, pos

    def ins_valida(rel, texto):
        """(válido, mensaje de error) del script resultante."""
        try:
            import renpy.parser as _ins_parser
            del _ins_parser.parse_errors[:]
            ast = _ins_parser.parse(rel, filedata=texto)
            errores = list(_ins_parser.parse_errors)
            del _ins_parser.parse_errors[:]
            if ast is None:
                return False, (str(errores[0]) if errores else "Error de sintaxis.")
            return True, ""
        except Exception as e:
            return False, str(e)

    def ins_preview(rel, idx, texto):
        """Todo lo que la pantalla necesita para dibujar el preview.

        No escribe nada. Valida el resultado con caché por (archivo, mtime,
        línea, snippet) para no parsear el archivo en cada frame."""
        lineas = ins_leer(rel)
        if not lineas:
            return {"lineas": [], "pos": 0, "sangria": "", "bloque": "",
                    "ghost": [], "valido": False,
                    "error": "No se pudo leer el archivo destino."}

        idx = max(0, min(idx, len(lineas) - 1))
        ancla = idx
        reemplazar = not lineas[idx].strip()
        nuevas, sangria, ghost, pos = _ins_componer(lineas, ancla, texto,
                                                    reemplazar)

        # El código de estos paneles es de historia: fuera de un label no
        # se ejecuta (aunque el parser lo acepte).
        if not sangria:
            return {
                "lineas": lineas,
                "pos": pos,
                "reemplazar": reemplazar,
                "sangria": sangria,
                "bloque": ins_bloque(lineas, idx),
                "ghost": ghost,
                "valido": False,
                "error": "El código tiene que ir dentro de un label.",
            }

        ruta = ins_ruta(rel)
        try:
            mtime = _ins_os.path.getmtime(ruta)
        except Exception:
            mtime = 0.0
        clave = (rel, mtime, idx, texto)
        if _INS_VALIDA["clave"] != clave:
            ok, msg = ins_valida(rel, "\n".join(nuevas))
            _INS_VALIDA.update({"clave": clave, "ok": ok, "msg": msg})

        return {
            "lineas": lineas,
            "pos": pos,
            "reemplazar": reemplazar,
            "sangria": sangria,
            "bloque": ins_bloque(lineas, idx),
            "ghost": ghost,
            "valido": _INS_VALIDA["ok"],
            "error": _INS_VALIDA["msg"],
        }

    def ins_ventana(n, idx, alto=140):
        """(inicio, fin) de las líneas que se dibujan: una ventana alrededor
        de la elegida en vez de miles de botones."""
        if n <= alto:
            return 0, n
        ini = max(0, min(idx - alto // 2, n - alto))
        return ini, ini + alto

    def ins_filas(lineas, pos, ini, fin, reemplazar=False):
        """Filas del preview intercalando la fila fantasma del snippet."""
        filas = []
        for i in range(ini, fin):
            if i == pos:
                filas.append(("fantasma", pos))
                if reemplazar:
                    continue
            filas.append(("linea", i))
        if pos >= fin:
            filas.append(("fantasma", pos))
        return filas

    def ins_insertar(rel, idx, texto, sufijo=".bak"):
        """Inserta `texto` en el archivo `rel`. Devuelve la línea nueva (0-based)
        o None si no escribió.

        No escribe nada si el resultado no parsea: es preferible fallar a
        dejar el juego sin arrancar."""
        ruta = ins_ruta(rel)
        try:
            with _ins_io.open(ruta, encoding="utf-8-sig", newline="") as fh:
                original = fh.read()

            # Se respetan los finales de línea del archivo: un .rpy con CRLF
            # no se reescribe entero y el diff queda mínimo.
            sep = "\r\n" if "\r\n" in original else "\n"
            lineas = original.split(sep)

            idx = max(0, min(idx, len(lineas) - 1))
            ancla = idx
            reemplazar = not lineas[idx].strip()
            nuevas, sangria, _ghost, pos = _ins_componer(lineas, ancla, texto,
                                                         reemplazar)

            # Fuera de un label el código no se ejecuta: no escribir.
            if not sangria:
                return None

            nuevo = sep.join(nuevas)
            if not ins_valida(rel, nuevo)[0]:
                return None

            with _ins_io.open(ruta + sufijo, "w", encoding="utf-8", newline="") as fh:
                fh.write(original)
            _ins_escribir(ruta, nuevo)
            _ins_borrar(ruta + _ins_redo(sufijo))
            return pos
        except Exception:
            return None

    def ins_deshacer(rel, sufijo=".bak"):
        """Restaura el backup y guarda el estado actual para Rehacer."""
        ruta = ins_ruta(rel)
        bak = ruta + sufijo
        if not _ins_os.path.isfile(bak):
            return False
        try:
            with _ins_io.open(ruta, encoding="utf-8-sig", newline="") as fh:
                actual = fh.read()
            with _ins_io.open(bak, encoding="utf-8-sig", newline="") as fh:
                original = fh.read()
            if actual == original:
                _ins_borrar(bak)
                return False
            with _ins_io.open(ruta + _ins_redo(sufijo), "w",
                               encoding="utf-8", newline="") as fh:
                fh.write(actual)
            _ins_escribir(ruta, original)
            _ins_borrar(bak)
            return True
        except Exception:
            return False

    def ins_rehacer(rel, sufijo=".bak"):
        """Vuelve a aplicar el último cambio deshecho."""
        ruta = ins_ruta(rel)
        redo = ruta + _ins_redo(sufijo)
        if not _ins_os.path.isfile(redo):
            return False
        try:
            with _ins_io.open(ruta, encoding="utf-8-sig", newline="") as fh:
                actual = fh.read()
            with _ins_io.open(redo, encoding="utf-8-sig", newline="") as fh:
                nuevo = fh.read()
            if actual == nuevo:
                _ins_borrar(redo)
                return False
            with _ins_io.open(ruta + sufijo, "w",
                              encoding="utf-8", newline="") as fh:
                fh.write(actual)
            _ins_escribir(ruta, nuevo)
            _ins_borrar(redo)
            return True
        except Exception:
            return False

    def ins_eliminar(rel, idx, sufijo=".bak"):
        """Elimina la línea `idx`; no escribe si rompe el script."""
        ruta = ins_ruta(rel)
        try:
            with _ins_io.open(ruta, encoding="utf-8-sig", newline="") as fh:
                original = fh.read()
            sep = "\r\n" if "\r\n" in original else "\n"
            lineas = original.split(sep)
            if idx < 0 or idx >= len(lineas):
                return False
            nuevo = sep.join(lineas[:idx] + lineas[idx + 1:])
            if not ins_valida(rel, nuevo)[0]:
                return False
            with _ins_io.open(ruta + sufijo, "w", encoding="utf-8", newline="") as fh:
                fh.write(original)
            _ins_escribir(ruta, nuevo)
            _ins_borrar(ruta + _ins_redo(sufijo))
            return True
        except Exception:
            return False

    def ins_puede_deshacer(rel, sufijo=".bak"):
        """True si hay backup para Deshacer."""
        if not rel:
            return False
        return _ins_os.path.isfile(ins_ruta(rel) + sufijo)

    def ins_puede_rehacer(rel, sufijo=".bak"):
        """True si hay snapshot para Rehacer."""
        if not rel:
            return False
        return _ins_os.path.isfile(ins_ruta(rel) + _ins_redo(sufijo))

    def ins_abrir_objetivo(rel):
        """Abre el .rpy destino con el programa asociado del sistema."""
        if not rel:
            return
        ruta = ins_ruta(rel)
        try:
            if renpy.windows:
                _ins_os.startfile(ruta)
            elif renpy.macintosh:
                _ins_subprocess.Popen(["open", ruta])
            else:
                _ins_subprocess.Popen(["xdg-open", ruta])
            tool_toast("Abriendo %s" % rel)
        except Exception:
            tool_toast("No se pudo abrir el archivo")
        renpy.restart_interaction()

    def ins_mover(estado, delta):
        """Mueve la línea elegida (teclado)."""
        n = len(ins_leer(estado.get("destino_archivo")))
        if not n:
            return
        i = estado.get("destino_linea", 0) + delta
        estado["destino_linea"] = max(0, min(n - 1, i))

    # --- Estado del panel (el dict es el de cada plugin) -------------------

    def ins_linea_inicial(rel):
        """Primera línea de un label; 0 si el archivo no tiene labels."""
        for i, l in enumerate(ins_leer(rel)):
            if _ins_re.match(r"^\s*label\s+\w+", l):
                return i
        return 0

    def ins_elegir_archivo(estado, rel):
        estado["destino_archivo"] = rel
        estado["destino_linea"] = ins_linea_inicial(rel)

    def ins_destino_init(estado, texto, marcador):
        """Prepara el panel para un snippet."""
        objs = ins_objetivos(marcador)
        estado["destinos"] = objs
        estado["destino_archivo"] = objs[0] if objs else ""
        estado["destino_linea"] = ins_linea_inicial(estado["destino_archivo"])
        estado["destino_texto"] = texto

    def ins_escribir_destino(estado, sufijo=".bak", aviso=None):
        """Escribe el snippet en el destino elegido."""
        rel = estado.get("destino_archivo")
        if not rel:
            return
        pos = ins_insertar(rel, estado.get("destino_linea", 0),
                           estado.get("destino_texto", ""), sufijo=sufijo)
        if pos is not None:
            estado["destino_linea"] = min(pos, max(0, len(ins_leer(rel)) - 1))
            mensaje = "Código insertado."
        else:
            mensaje = "No se pudo escribir (revisá la línea elegida)"
        if aviso:
            aviso(mensaje)
        renpy.restart_interaction()
        # No devolver nada: un `Function` con retorno corta la interacción
        # (en el menú principal eso puede arrancar la partida).

    def ins_deshacer_destino(estado, sufijo=".bak", aviso=None):
        """Restaura el archivo destino desde su backup."""
        rel = estado.get("destino_archivo")
        if rel and ins_deshacer(rel, sufijo):
            mensaje = "Cambios deshechos"
        else:
            mensaje = "No hay nada que deshacer"
        if aviso:
            aviso(mensaje)
        renpy.restart_interaction()

    def ins_rehacer_destino(estado, sufijo=".bak", aviso=None):
        """Vuelve a aplicar el último cambio deshecho."""
        rel = estado.get("destino_archivo")
        if rel and ins_rehacer(rel, sufijo):
            mensaje = "Cambios rehechos"
        else:
            mensaje = "No hay nada que rehacer"
        if aviso:
            aviso(mensaje)
        renpy.restart_interaction()

    def ins_eliminar_destino(estado, sufijo=".bak", aviso=None):
        """Elimina la línea seleccionada del archivo destino."""
        rel = estado.get("destino_archivo")
        if rel and ins_eliminar(rel, estado.get("destino_linea", 0), sufijo):
            mensaje = "Línea eliminada."
        else:
            mensaje = "No se pudo eliminar (dejaría el script inválido)."
        if rel:
            estado["destino_linea"] = max(
                0, min(estado.get("destino_linea", 0), len(ins_leer(rel)) - 1))
        if aviso:
            aviso(mensaje)
        renpy.restart_interaction()

    def ins_abrir_destino(estado):
        """Abre el archivo destino en el editor del sistema."""
        ins_abrir_objetivo(estado.get("destino_archivo"))


# ---------------------------------------------------------------------------
# Estilos del panel. Se definen acá con propiedades explícitas: heredan de los
# `tool_*` y no arrastran outlines.
# ---------------------------------------------------------------------------

style ins_gutter is text:
    size 13
    color "#6f7783"
    outlines []

# Las filas del código usan su propio estilo: la selección es un fondo suave,
# no la barra azul de las listas.
style ins_line is tool_line:
    selected_background "#232935"
    selected_hover_background "#2a3140"

# Misma altura que las filas (`gui.button_height`): así la fila fantasma y las
# líneas quedan como bandas contiguas, sin huecos.
style ins_ghost is frame:
    background "#152a1d"
    padding (4, 0)
    ysize 36
    xfill True

style ins_marker is text:
    size 13
    color "#7ee0a0"
    font "DejaVuSans.ttf"
    outlines []

style ins_guide is text:
    size 13
    color "#4d7a5f"
    outlines []

style ins_ghost_line is text:
    size 15
    color "#a8e6bf"
    outlines []

style ins_ghost_tag is text:
    size 10
    bold True
    color "#7ee0a0"
    outlines []

style ins_ok is text:
    size 14
    bold True
    color "#7ee0a0"
    outlines []

style ins_bad is text:
    size 14
    bold True
    color "#ff8f8f"
    outlines []


screen tool_destino(estado, texto, marcador, titulo, aviso, sufijo=".bak"):

    modal True
    zorder 250

    on "show" action Function(ins_destino_init, estado, texto, marcador)

    key "K_ESCAPE" action Hide("tool_destino")
    key "K_UP" action Function(ins_mover, estado, -1)
    key "K_DOWN" action Function(ins_mover, estado, 1)
    key "K_PAGEUP" action Function(ins_mover, estado, -20)
    key "K_PAGEDOWN" action Function(ins_mover, estado, 20)

    $ _ins_objs = estado.get("destinos", [])
    $ _ins_rel = estado.get("destino_archivo")
    $ _ins_prev = ins_preview(_ins_rel, estado.get("destino_linea", 0),
                              estado.get("destino_texto", ""))
    $ _ins_valido = _ins_prev["valido"]
    $ _ins_puede_insertar = _ins_valido and bool(estado.get("destino_texto"))
    $ _ins_puede = ins_puede_deshacer(_ins_rel, sufijo)
    $ _ins_puede_r = ins_puede_rehacer(_ins_rel, sufijo)

    key "K_RETURN" action If(_ins_puede_insertar,
                             true=Function(ins_escribir_destino, estado, sufijo, aviso),
                             false=NullAction())

    frame:
        style "tool_panel"
        xalign 0.5
        yalign 0.5
        xsize 1040
        ysize 620

        vbox:
            spacing 8

            # Título + estado.
            hbox:
                spacing 12
                text titulo style "tool_title"
                null width 10
                if _ins_prev["lineas"]:
                    if _ins_valido:
                        text "✓ válido" style "ins_ok" yalign 0.5
                    else:
                        text "✗ rompería el script" style "ins_bad" yalign 0.5

            if not _ins_objs:
                text "Agregá una línea `# " + marcador + "` al principio de un .rpy para que aparezca acá." style "tool_hint"

                textbutton "Cerrar":
                    style "tool_copy"
                    action Hide("tool_destino")
            else:
                # Breadcrumb de lo que va a pasar.
                $ _ins_donde = _ins_prev["bloque"] or "nivel superior"
                $ _ins_sang = len(_ins_prev["sangria"])
                $ _ins_lado = "en" if _ins_prev.get("reemplazar") else "después de"
                text "[_ins_rel] › [_ins_donde] › [_ins_lado] la línea [estado.get('destino_linea', 0) + 1] · [_ins_sang] espacios":
                    style "tool_hint"

                hbox:
                    spacing 12

                    # Columna izquierda: archivos y código.
                    hbox:
                        spacing 12

                        # Archivos destino.
                        frame:
                            style "tool_tray"
                            xsize 210
                            ysize 440

                            viewport:
                                ysize 424
                                scrollbars "vertical"
                                mousewheel True

                                vbox:
                                    xfill True
                                    spacing 2

                                    for _ins_o in _ins_objs:
                                        textbutton "[_ins_o]":
                                            style "tool_line"
                                            selected _ins_o == _ins_rel
                                            action Function(ins_elegir_archivo, estado, _ins_o)

                        # Preview con gutter y fila fantasma.
                        frame:
                            style "tool_tray"
                            xsize 490
                            ysize 440

                            viewport:
                                ysize 424
                                mousewheel True
                                scrollbars "vertical"

                                vbox:
                                    xfill True
                                    spacing 0

                                    $ _ins_ini, _ins_fin = ins_ventana(len(_ins_prev["lineas"]), estado.get("destino_linea", 0))
                                    $ _ins_filas = ins_filas(_ins_prev["lineas"], _ins_prev["pos"], _ins_ini, _ins_fin, _ins_prev.get("reemplazar", False))

                                    if _ins_ini > 0:
                                        text "… [ _ins_ini ] líneas más arriba" style "tool_hint"

                                    for _ins_tipo, _ins_i in _ins_filas:
                                        if _ins_tipo == "fantasma":
                                            frame:
                                                style "ins_ghost"
                                                hbox:
                                                    spacing 8
                                                    yalign 0.5
                                                    fixed:
                                                        xsize 36
                                                        ysize 18
                                                        text ("%d" % (_ins_prev["pos"] + 1) if _ins_prev.get("reemplazar") else "▸"):
                                                            style "ins_marker"
                                                            xalign 1.0
                                                            yalign 0.5
                                                    vbox:
                                                        spacing 0
                                                        text "A PEGAR" style "ins_ghost_tag"
                                                        for _ins_gl in _ins_prev["ghost"]:
                                                            $ _ins_gl_sang = len(_ins_gl) - len(_ins_gl.lstrip(" "))
                                                            $ _ins_gl_txt = _ins_gl.lstrip(" ").replace("{", "{{")
                                                            hbox:
                                                                spacing 0
                                                                if _ins_gl_sang:
                                                                    text ("·" * _ins_gl_sang) style "ins_guide"
                                                                text _ins_gl_txt style "ins_ghost_line" substitute False
                                        else:
                                            $ _ins_l = _ins_prev["lineas"][_ins_i]
                                            $ _ins_l_txt = _ins_l.replace("{", "{{")
                                            $ _ins_sel = _ins_i == estado.get("destino_linea", 0)
                                            button:
                                                style "ins_line"
                                                selected _ins_sel
                                                action SetDict(estado, "destino_linea", _ins_i)
                                                hbox:
                                                    spacing 8
                                                    fixed:
                                                        xsize 36
                                                        ysize 18
                                                        text "%d" % (_ins_i + 1):
                                                            style "ins_gutter"
                                                            xalign 1.0
                                                            yalign 0.5
                                                            color ("#f4a6c8" if _ins_sel else "#6f7783")
                                                    text _ins_l_txt:
                                                        style "tool_code"
                                                        color ("#ffffff" if _ins_sel else "#cfd3da")
                                                        substitute False

                                    if _ins_fin < len(_ins_prev["lineas"]):
                                        text "… [ len(_ins_prev['lineas']) - _ins_fin ] líneas más abajo" style "tool_hint"

                    # Columna derecha: snippet y acciones.
                    vbox:
                        xsize 280
                        spacing 6

                        text "Línea a pegar:" style "tool_caption"

                        frame:
                            style "tool_tray"
                            xfill True
                            ysize 130

                            viewport:
                                ysize 114
                                mousewheel True
                                scrollbars "vertical"

                                vbox:
                                    spacing 0
                                    for _ins_sl in (estado.get("destino_texto") or "").split("\n"):
                                        $ _ins_sl_rich = tool_codigo_rico(_ins_sl)
                                        text _ins_sl_rich style "tool_code" substitute False

                        text "Clic en una línea dentro del label." style "tool_hint"

                        textbutton "Abrir archivo":
                            style "tool_copy"
                            xfill True
                            action Function(ins_abrir_destino, estado)

                        textbutton "Deshacer":
                            style "tool_copy"
                            xfill True
                            sensitive _ins_puede
                            action Function(ins_deshacer_destino, estado, sufijo, aviso)

                        textbutton "Rehacer":
                            style "tool_copy"
                            xfill True
                            sensitive _ins_puede_r
                            action Function(ins_rehacer_destino, estado, sufijo, aviso)

                        textbutton "Eliminar línea":
                            style "tool_copy"
                            xfill True
                            action Function(ins_eliminar_destino, estado, sufijo, aviso)

                        null height 4

                        textbutton "Cerrar":
                            style "tool_copy"
                            xfill True
                            action Hide("tool_destino")

                        textbutton "Insertar":
                            style "tool_button"
                            xfill True
                            sensitive _ins_puede_insertar
                            action Function(ins_escribir_destino, estado, sufijo, aviso)

                        if not _ins_valido and _ins_prev["error"]:
                            $ _ins_err = _ins_prev["error"].replace("{", "{{")
                            text "[_ins_err]" style "ins_bad" substitute False size 12
