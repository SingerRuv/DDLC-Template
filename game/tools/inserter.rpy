## inserter.rpy
## Panel "Insertar en…" compartido: escribir un snippet dentro de un .rpy del
## guion sin romperlo.
##
## Lo usan los plugins que generan código para la historia (PoseLab, Diálogo).
## Cada plugin pasa su estado, el marcador que habilita un archivo como
## destino ("# poselab", "# dialogo"), el título del panel y su función de aviso.
##
## Reglas:
##   - Solo se escriben archivos físicos del proyecto (nada dentro de un .rpa).
##   - La sangría sale de la línea elegida: un define va al nivel superior y
##     una sentencia dentro de un label.
##   - Si el .rpy quedaría inválido, no se escribe nada.
##   - Se respeta el fin de línea del archivo (LF o CRLF).
##   - Antes de escribir se guarda un backup con el sufijo indicado.
##   - Al escribir se avisa al watcher (`add_auto`): si no, Ren'Py recarga el
##     script a los ~1,5 s y te saca de la herramienta.

init python:

    import io as _ins_io
    import os as _ins_os
    import re as _ins_re

    # Carpetas que no son destino: las herramientas y las traducciones.
    _INS_SALTAR = ("tools/", "tl/")

    def ins_ruta(rel):
        """Ruta física de un .rpy del proyecto (relativa a game/)."""
        return _ins_os.path.join(config.gamedir, rel.replace("/", _ins_os.sep))

    def _ins_escribir(ruta, texto):
        """Escribe `texto` en `ruta` sin que el autoreload recargue el script.

        Escribir un .rpy con el juego abierto cambia su mtime y a los ~1,5 s
        Ren'Py corre `reload_script()` (guarda y recarga la partida en curso:
        te tira al guion). `add_auto(force=True)` fija el mtime de referencia;
        es el mismo idiom que `renpy/scriptedit.py`. El lock evita que el hilo
        de vigilancia vea el archivo a mitad de la escritura."""
        with renpy.loader.auto_lock:
            with _ins_io.open(ruta, "w", encoding="utf-8", newline="") as fh:
                fh.write(texto)
            renpy.loader.add_auto(ruta, force=True)

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
            with _ins_io.open(ins_ruta(rel), encoding="utf-8", newline="") as fh:
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

    def ins_parsea(rel, texto):
        """True si el contenido sigue siendo un script válido de Ren'Py."""
        try:
            import renpy.parser
            del renpy.parser.parse_errors[:]
            ast = renpy.parser.parse(rel, filedata=texto)
            del renpy.parser.parse_errors[:]
            return ast is not None
        except Exception:
            return False

    def ins_insertar(rel, idx, texto, sufijo=".bak"):
        """Inserta `texto` tras la línea `idx` (0-based) del archivo `rel`.

        No escribe nada si el resultado no parsea: es preferible fallar a
        dejar el juego sin arrancar. Devuelve True si escribió.
        """
        ruta = ins_ruta(rel)
        try:
            with _ins_io.open(ruta, encoding="utf-8", newline="") as fh:
                original = fh.read()

            # Se respetan los finales de línea del archivo: un .rpy con
            # CRLF no se reescribe entero y el diff queda mínimo.
            sep = "\r\n" if "\r\n" in original else "\n"
            lineas = original.split(sep)

            sangria = ins_sangria(lineas, idx)

            # Una sentencia ($ ...) fuera de un label no se ejecuta nunca.
            if texto.lstrip().startswith("$") and not sangria:
                return False

            # La sangría va en todas las líneas: un snippet multilínea
            # sin sangría rompe el archivo con un error de indentación.
            # Los saltos del snippet usan el mismo fin de línea que el
            # archivo, así no quedan LF sueltos en un .rpy con CRLF.
            bloque = sep.join(
                (sangria + l) if l.strip() else l for l in texto.split("\n")
            ) if texto else ""
            lineas.insert(idx + 1, bloque)
            nuevo = sep.join(lineas)

            if not ins_parsea(rel, nuevo):
                return False

            with _ins_io.open(ruta + sufijo, "w", encoding="utf-8", newline="") as fh:
                fh.write(original)
            _ins_escribir(ruta, nuevo)
            return True
        except Exception:
            return False

    def ins_deshacer(rel, sufijo=".bak"):
        """Restaura el archivo desde su backup (un nivel), tal cual estaba."""
        ruta = ins_ruta(rel)
        bak = ruta + sufijo
        if not _ins_os.path.isfile(bak):
            return False
        try:
            with _ins_io.open(bak, encoding="utf-8", newline="") as fh:
                original = fh.read()
            _ins_escribir(ruta, original)
            return True
        except Exception:
            return False

    def ins_abrir_objetivo(rel, linea=0):
        """Abre el .rpy destino en el editor del sistema (best-effort)."""
        if rel:
            renpy.launch_editor([ins_ruta(rel)], line=linea + 1)

    # --- Estado del panel (el dict es el de cada plugin) -------------------

    def ins_destino_init(estado, texto, marcador):
        """Prepara el panel para un snippet."""
        objs = ins_objetivos(marcador)
        estado["destinos"] = objs
        estado["destino_archivo"] = objs[0] if objs else ""
        estado["destino_linea"] = 0
        estado["destino_texto"] = texto

    def ins_escribir_destino(estado, sufijo=".bak", aviso=None):
        """Escribe el snippet en el destino elegido."""
        rel = estado.get("destino_archivo")
        if not rel:
            return False
        idx = estado.get("destino_linea", 0)
        if ins_insertar(rel, idx, estado.get("destino_texto", ""), sufijo=sufijo):
            estado["destino_linea"] = idx + 1
            ok, mensaje = True, "Código insertado"
        else:
            ok, mensaje = False, "No se pudo escribir (revisá la línea elegida)"
        if aviso:
            aviso(mensaje)
        renpy.restart_interaction()
        return ok

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

    def ins_abrir_destino(estado):
        """Abre el archivo destino en el editor del sistema."""
        ins_abrir_objetivo(
            estado.get("destino_archivo"), estado.get("destino_linea", 0),
        )


# El panel: lista de archivos destino, preview del archivo con la línea
# elegida, el texto a pegar y la confirmación.
screen tool_destino(estado, texto, marcador, titulo, aviso, sufijo=".bak"):

    modal True
    zorder 250

    default confirmando = False

    on "show" action Function(ins_destino_init, estado, texto, marcador)

    key "K_ESCAPE" action Hide("tool_destino")

    frame:
        style "tool_panel"
        xalign 0.5
        yalign 0.5
        xsize 1000
        ysize 580

        vbox:
            spacing 10

            text titulo style "tool_title"
            text "La sangría sale de la línea elegida: un define va arriba del todo y las sentencias dentro de un label." style "tool_hint"

            $ _ins_objs = estado.get("destinos", [])

            if not _ins_objs:
                text "Agregá una línea `# " + marcador + "` al principio de un .rpy para que aparezca acá." style "tool_hint"

                textbutton "Cerrar":
                    style "tool_copy"
                    action Hide("tool_destino")
            else:
                $ _ins_rel = estado.get("destino_archivo")
                $ _ins_lineas = ins_leer(_ins_rel)

                hbox:
                    spacing 12

                    # Archivos destino (los que tienen el marcador).
                    frame:
                        style "tool_tray"
                        xsize 250
                        ysize 380

                        viewport:
                            ysize 364
                            scrollbars "vertical"
                            mousewheel True

                            vbox:
                                xfill True
                                spacing 2

                                for _ins_o in _ins_objs:
                                    textbutton "[_ins_o]":
                                        style "tool_line"
                                        selected _ins_o == _ins_rel
                                        action [SetDict(estado, "destino_archivo", _ins_o),
                                                SetDict(estado, "destino_linea", 0)]

                    # Preview del archivo: clic en una línea elige dónde insertar.
                    frame:
                        style "tool_tray"
                        xsize 700
                        ysize 380

                        viewport:
                            ysize 364
                            scrollbars "vertical"
                            mousewheel True

                            vbox:
                                xfill True
                                spacing 0

                                for _ins_i, _ins_linea in enumerate(_ins_lineas):
                                    # `{` se escapa porque los text tags se
                                    # procesan aunque no haya interpolación.
                                    $ _ins_etiqueta = ("%d  %s" % (_ins_i + 1, _ins_linea)).replace("{", "{{")
                                    textbutton _ins_etiqueta:
                                        substitute False
                                        style "tool_line"
                                        selected _ins_i == estado.get("destino_linea", 0)
                                        action SetDict(estado, "destino_linea", _ins_i)

                # Línea que se insertará (solo lectura).
                hbox:
                    spacing 8

                    text "Línea a pegar:" style "tool_caption" yalign 0.5

                    frame:
                        style "tool_tray"
                        xfill True

                        $ _ins_pegar = (estado.get("destino_texto") or "").replace("{", "{{")
                        text _ins_pegar style "tool_code" substitute False

                hbox:
                    spacing 8

                    if confirmando:
                        $ _ins_aviso = "Se insertará tras la línea %d de %s. Recargá scripts o reiniciá el juego para recompilar." % (estado.get("destino_linea", 0) + 1, _ins_rel)
                        text "[_ins_aviso]" style "tool_hint" yalign 0.5 xmaximum 520

                        textbutton "Sí, escribir":
                            style "tool_button"
                            action [Function(ins_escribir_destino, estado, sufijo, aviso),
                                    SetScreenVariable("confirmando", False)]

                        textbutton "Cancelar":
                            style "tool_copy"
                            action SetScreenVariable("confirmando", False)
                    else:
                        textbutton "Confirmar":
                            style "tool_button"
                            action SetScreenVariable("confirmando", True)

                        textbutton "Abrir archivo":
                            style "tool_copy"
                            action Function(ins_abrir_destino, estado)

                        textbutton "Deshacer":
                            style "tool_copy"
                            action Function(ins_deshacer_destino, estado, sufijo, aviso)

                        textbutton "Cerrar":
                            style "tool_copy"
                            action Hide("tool_destino")
