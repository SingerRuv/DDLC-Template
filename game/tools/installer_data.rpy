## installer_data.rpy
## Instalador de plugins desde ZIP local — lógica sin UI.
##
## El usuario deja uno o más .zip en game/tools/plugins/_incoming/ y la
## pantalla `plugins_installer` (installer.rpy) los lista. Un ZIP contiene
## UN plugin: `tool.json` en la raíz o dentro de una única carpeta raíz.
##
## Reglas de seguridad (el ZIP viene de afuera, así que se valida todo):
##   - Solo se escribe dentro de game/tools/plugins/<carpeta>/.
##   - Se rechazan rutas absolutas, `..`, unidades (C:) y symlinks.
##   - Allowlist de extensiones, tope de tamaño y de cantidad de archivos.
##   - La instalación es atómica: se descomprime en _tmp, se valida y recién
##     ahí se mueve a destino. Si algo falla no queda nada a medias.
##
## Actualizar aparta la versión anterior a _incoming/_backups/.
## El ZIP usado se archiva en _incoming/instalados/.
##
## Un plugin nuevo no se puede cargar en caliente (Ren'Py compila los .rpy al
## arrancar): después de instalar se pide reiniciar.

init python:
    import os as _pi_os
    import io as _pi_io
    import re as _pi_re
    import json as _pi_json
    import shutil as _pi_shutil
    import time as _pi_time
    import uuid as _pi_uuid
    import zipfile as _pi_zip
    import builtins as _pi_builtins

    _PI_INCOMING = "tools/plugins/_incoming"
    _PI_INSTALADOS = "tools/plugins/_incoming/instalados"
    _PI_BACKUPS = "tools/plugins/_incoming/_backups"
    _PI_TMP = "tools/plugins/_incoming/_tmp"

    # ponytail: topes fijos, holgados para un plugin. Si algún día un plugin
    # legítimo los pasa, se suben acá.
    _PI_MAX_BYTES = 100 * 1024 * 1024
    _PI_MAX_FILES = 2000
    _PI_MAX_TOOL = 1024 * 1024

    # Extensiones permitidas: nada ejecutable ni bytecode.
    _PI_EXT = {
        "", ".rpy", ".py", ".json", ".md", ".txt", ".ini", ".csv",
        ".png", ".jpg", ".jpeg", ".webp", ".gif", ".ico",
        ".ogg", ".opus", ".wav", ".mp3", ".flac",
        ".ttf", ".otf", ".glsl", ".vert", ".frag",
    }

    # Resultado de la última acción (la pantalla lo muestra).
    _pi_msg = {"texto": "", "ok": True, "pendiente": False}

    # ------------------------------------------------------------------
    # Rutas y helpers.
    # ------------------------------------------------------------------

    def _pi_ruta(rel):
        """Ruta absoluta dentro de game/ (usa config.gamedir)."""
        return ins_ruta(rel)

    def _pi_asegurar(rel):
        ruta = _pi_ruta(rel)
        _pi_os.makedirs(ruta, exist_ok=True)
        return ruta

    def _pi_dentro(base, ruta):
        """True si `ruta` queda dentro de `base` (resolviendo symlinks)."""
        base = _pi_os.path.realpath(base)
        ruta = _pi_os.path.realpath(ruta)
        return ruta == base or ruta.startswith(base + _pi_os.sep)

    def _pi_sanea(nombre):
        """Nombre de carpeta seguro: [a-z0-9_-], sin puntos al borde."""
        s = str(nombre or "").strip().lower()
        s = _pi_re.sub(r"[^a-z0-9_-]+", "_", s)
        return s.strip("_-. ")[:64]

    def _pi_fuera(texto, n=3):
        return " · ".join(texto[:n])

    # ------------------------------------------------------------------
    # Validación de un ZIP (sin extraer).
    # ------------------------------------------------------------------

    def _pi_leer_zip(ruta):
        """Valida el ZIP y devuelve (meta, motivos).

        meta es None si no se puede instalar; motivos explica por qué.
        No escribe nada en disco."""

        try:
            zf = _pi_zip.ZipFile(ruta)
        except Exception as e:
            return None, ["No es un ZIP válido: %s" % e]

        with zf:
            infos = [i for i in zf.infolist() if not i.is_dir()]

            if not infos:
                return None, ["El ZIP está vacío."]
            if len(infos) > _PI_MAX_FILES:
                return None, ["Tiene %d archivos (máximo %d)."
                              % (len(infos), _PI_MAX_FILES)]

            total = sum(i.file_size for i in infos)
            if total > _PI_MAX_BYTES:
                return None, ["Pesa %d MB (máximo %d MB)."
                              % (total // (1024 * 1024), _PI_MAX_BYTES // (1024 * 1024))]

            motivos = []
            entradas = []

            for info in infos:
                nombre = info.filename.replace("\\", "/")

                if nombre.startswith("/") or _pi_re.match(r"^[A-Za-z]:", nombre):
                    motivos.append("Ruta absoluta no permitida: %s" % info.filename)
                    continue

                partes = nombre.split("/")
                if any(p in ("", ".", "..") for p in partes):
                    motivos.append("Ruta insegura: %s" % info.filename)
                    continue

                # Symlink (modo del archivo dentro del ZIP).
                if (info.external_attr >> 16) & 0o170000 == 0o120000:
                    motivos.append("Symlink no permitido: %s" % info.filename)
                    continue

                ext = _pi_os.path.splitext(partes[-1])[1].lower()
                if ext not in _PI_EXT:
                    motivos.append("Extensión no permitida: %s" % info.filename)
                    continue

                entradas.append((info, "/".join(partes)))

            if motivos:
                return None, motivos

            # ¿Dónde está tool.json? En la raíz o en una única carpeta raíz.
            candidatos = [p for _, p in entradas
                          if p == "tool.json" or p.endswith("/tool.json")]
            if not candidatos:
                return None, ["No incluye tool.json."]

            raiz = ""
            if "tool.json" not in candidatos:
                raices = {p[:-len("tool.json")].rstrip("/") for p in candidatos}
                if len(raices) > 1:
                    return None, ["Contiene más de un plugin (varios tool.json)."]
                raiz = raices.pop()

            fuera = [p for _, p in entradas
                     if raiz and p != raiz and not p.startswith(raiz + "/")]
            if fuera:
                return None, ["Tiene archivos fuera de la carpeta del plugin."]

            ruta_tool = (raiz + "/tool.json") if raiz else "tool.json"
            info_tool = next(i for i, p in entradas if p == ruta_tool)

            if info_tool.file_size > _PI_MAX_TOOL:
                return None, ["tool.json es demasiado grande."]

            # Misma validación de manifiesto que el hub (complements_data.rpy).
            carpeta = raiz.split("/")[-1] if raiz else _pi_os.path.splitext(
                _pi_os.path.basename(ruta))[0]
            e, motivos = pl_manifiesto_bytes(zf.read(info_tool), carpeta)
            if e is None:
                return None, [texto for texto, _fatal in motivos]

            # Un plugin sin .rpy no puede definir su screen (los .rpyc están
            # fuera del allowlist), así que se rechaza antes de escribir.
            if not any(p.endswith(".rpy") for _, p in entradas):
                return None, ["No incluye ningún .rpy: no podría definir su screen."]

            dir_ = _pi_sanea(e["id"]) or _pi_sanea(carpeta)
            if not dir_:
                return None, ["No se pudo deducir el nombre de la carpeta."]

            return dict(e, dir=dir_, raiz=raiz, entradas=entradas, bytes=total), []

    # ------------------------------------------------------------------
    # Listado de pendientes.
    # ------------------------------------------------------------------

    def _pi_estado(meta, actual):
        """(estado, etiqueta del botón) contra el plugin instalado (o None)."""
        if not actual:
            return "instalar", "Instalar"

        a = _pl_ver(actual.get("version"))
        n = _pl_ver(meta["version"])
        if n and a and n > a:
            return "actualizar", "Actualizar a v%s" % meta["version"]
        if n and a and n < a:
            return "bajar", "Bajar a v%s" % meta["version"]
        return "reinstalar", "Reinstalar"

    def _pi_instalado_de(dir_):
        """Lee el tool.json de una carpeta instalada, aunque el hub todavía no
        la liste (un .rpy recién instalado necesita reinicio para cargar).

        Devuelve {dir, id, version} o None."""
        ruta = _pi_ruta("tools/plugins/" + dir_ + "/tool.json")
        try:
            with _pi_io.open(ruta, encoding="utf-8-sig") as fh:
                datos = _pi_json.load(fh)
            if not isinstance(datos, _pi_builtins.dict):
                return None
            return {"dir": dir_,
                    "id": str(datos.get("id") or dir_),
                    "version": str(datos.get("version") or "")}
        except Exception:
            return None

    def _pi_listar():
        """ZIPs de _incoming ya validados.

        Cada item: archivo, ruta, bytes, meta, motivo, estado, etiqueta,
        instalado (el plugin activo que reemplazaría, o None).

        Lee cada ZIP en cada llamada: con unos pocos archivos es barato y así
        la pantalla nunca muestra datos viejos."""

        base = _pi_asegurar(_PI_INCOMING)
        plugins = pl_plugins()[0]
        por_dir = {t["dir"]: t for t in plugins}
        por_id = {t["id"]: t for t in plugins}

        try:
            nombres = sorted(
                n for n in _pi_os.listdir(base)
                if n.lower().endswith(".zip")
                and _pi_os.path.isfile(_pi_os.path.join(base, n)))
        except OSError:
            nombres = []

        salida = []
        for nombre in nombres:
            ruta = _pi_os.path.join(base, nombre)
            meta, motivos = _pi_leer_zip(ruta)
            item = {
                "archivo": nombre,
                "ruta": ruta,
                "bytes": _pi_os.path.getsize(ruta),
                "meta": meta,
                "motivo": _pi_fuera(motivos),
                "aviso": "",
                "estado": "",
                "etiqueta": "",
                "instalado": None,
            }
            if meta:
                actual = por_dir.get(meta["dir"]) or por_id.get(meta["id"])
                if not actual:
                    actual = _pi_instalado_de(meta["dir"])
                item["instalado"] = actual

                # Mismo id en OTRA carpeta: si se instalara, reemplazaría al
                # otro plugin (y su backup sería el de él). Se frena acá.
                if actual and actual["dir"] != meta["dir"]:
                    item["estado"] = "conflicto"
                    item["motivo"] = ("Ya hay un plugin con el id '%s' en "
                                      "tools/plugins/%s."
                                      % (meta["id"], actual["dir"]))
                else:
                    item["estado"], item["etiqueta"] = _pi_estado(meta, actual)

                v_req = _pl_ver(meta.get("min_version"))
                v_api = _pl_ver(tools_api_version)
                if v_req and v_api and v_req > v_api:
                    item["aviso"] = ("Requiere API %s (actual %s)."
                                     % (meta["min_version"], tools_api_version))
            salida.append(item)

        return salida

    # ------------------------------------------------------------------
    # Instalar / desinstalar.
    # ------------------------------------------------------------------

    def _pi_archivar_zip(ruta_zip):
        """Mueve el ZIP usado a _incoming/instalados/ (no aborta si falla)."""
        try:
            destino_dir = _pi_asegurar(_PI_INSTALADOS)
            nombre = _pi_os.path.basename(ruta_zip)
            base, ext = _pi_os.path.splitext(nombre)
            destino = _pi_os.path.join(destino_dir, nombre)
            n = 2
            while _pi_os.path.exists(destino):
                destino = _pi_os.path.join(destino_dir, "%s-%d%s" % (base, n, ext))
                n += 1
            _pi_shutil.move(ruta_zip, destino)
        except Exception as e:
            print("tools.plugins: no se pudo archivar %s: %s" % (ruta_zip, e))

    def _pi_instalar(archivo):
        """Instala o actualiza el ZIP `archivo` (nombre dentro de _incoming).

        Devuelve (carpeta, motivos). Si hay motivos no se tocó nada."""

        ruta_zip = _pi_os.path.join(_pi_asegurar(_PI_INCOMING), archivo)
        if not _pi_os.path.isfile(ruta_zip):
            return None, ["El ZIP ya no está en _incoming."]

        meta, motivos = _pi_leer_zip(ruta_zip)
        if not meta:
            return None, motivos

        # Mismo id en otra carpeta: no es una actualización, es otro plugin.
        # ponytail: no ve un plugin instalado que el hub todavía no lista y
        # tenga otro dir; ese caso ya lo frena la pantalla al listar.
        for t in pl_plugins()[0]:
            if t["id"] == meta["id"] and t["dir"] != meta["dir"]:
                return None, ["Ya hay un plugin con el id '%s' en "
                              "tools/plugins/%s." % (meta["id"], t["dir"])]

        plugins_dir = _pi_asegurar("tools/plugins")
        destino = _pi_os.path.join(plugins_dir, meta["dir"])
        if not _pi_dentro(plugins_dir, destino):
            return None, ["Destino no válido."]

        # 1. Descomprimir en _tmp (nada visible todavía).
        tmp = _pi_os.path.join(_pi_asegurar(_PI_TMP), _pi_uuid.uuid4().hex)
        _pi_os.makedirs(tmp, exist_ok=True)
        escritos = 0
        try:
            with _pi_zip.ZipFile(ruta_zip) as zf:
                for info, rel in meta["entradas"]:
                    sub = rel[len(meta["raiz"]) + 1:] if meta["raiz"] else rel
                    if not sub:
                        continue
                    dst = _pi_os.path.join(tmp, *sub.split("/"))
                    _pi_os.makedirs(_pi_os.path.dirname(dst), exist_ok=True)
                    with zf.open(info) as src, _pi_io.open(dst, "wb") as out:
                        while True:
                            trozo = src.read(65536)
                            if not trozo:
                                break
                            escritos += len(trozo)
                            if escritos > _PI_MAX_BYTES:
                                raise ValueError("el contenido supera el tope")
                            out.write(trozo)
        except Exception as e:
            _pi_shutil.rmtree(tmp, ignore_errors=True)
            return None, ["No se pudo extraer: %s" % e]

        # 2. Apartar la versión anterior (actualización), con backup.
        backup = None
        if _pi_os.path.isdir(destino):
            try:
                bdir = _pi_asegurar(_PI_BACKUPS)
                marca = _pi_time.strftime("%Y%m%d-%H%M%S", _pi_time.localtime())
                backup = _pi_os.path.join(bdir, "%s-%s" % (meta["dir"], marca))
                n = 2
                while _pi_os.path.exists(backup):
                    backup = _pi_os.path.join(
                        bdir, "%s-%s-%d" % (meta["dir"], marca, n))
                    n += 1
                _pi_shutil.move(destino, backup)
            except Exception as e:
                _pi_shutil.rmtree(tmp, ignore_errors=True)
                return None, ["No se pudo apartar la versión anterior: %s" % e]

        # 3. Poner la nueva en su lugar (o restaurar la anterior si falla).
        try:
            _pi_shutil.move(tmp, destino)
        except Exception as e:
            if backup:
                try:
                    _pi_shutil.move(backup, destino)
                except Exception:
                    pass
            _pi_shutil.rmtree(tmp, ignore_errors=True)
            return None, ["No se pudo instalar: %s" % e]

        _pi_archivar_zip(ruta_zip)
        tool_refrescar()
        return meta["dir"], []

    def _pi_desinstalar(tool):
        """Borra la carpeta del plugin. Devuelve (ok, motivo)."""

        plugins_dir = _pi_asegurar("tools/plugins")
        dir_ = str(tool.get("dir") or "")
        if not dir_ or "/" in dir_ or "\\" in dir_ or dir_ in (".", ".."):
            return False, "Carpeta no válida."

        ruta = _pi_os.path.join(plugins_dir, dir_)
        if not _pi_dentro(plugins_dir, ruta) or not _pi_os.path.isdir(ruta):
            return False, "La carpeta ya no existe."

        try:
            _pi_shutil.rmtree(ruta)
        except Exception as e:
            return False, "No se pudo borrar: %s" % e

        tool_refrescar()
        return True, ""

    # ------------------------------------------------------------------
    # Acciones para la pantalla (dejan el resultado en _pi_msg).
    #
    # Instalar y desinstalar son sincrónicos: para que el aviso llegue a
    # pintarse antes del freeze, la pantalla pide la acción, muestra el toast y
    # recién en el siguiente frame la procesa (_pi_procesar).
    # ------------------------------------------------------------------

    _pi_solicitud = {"archivo": None, "desinstalar": None}

    def _pi_pedir_instalar(archivo):
        _pi_solicitud["archivo"] = archivo
        _pi_solicitud["desinstalar"] = None
        tool_toast("Instalando %s…" % archivo)

    def _pi_pedir_desinstalar(tool):
        _pi_solicitud["desinstalar"] = tool
        _pi_solicitud["archivo"] = None
        tool_toast("Desinstalando %s…" % tool["dir"])

    def _pi_procesar():
        archivo = _pi_solicitud["archivo"]
        tool = _pi_solicitud["desinstalar"]
        _pi_solicitud["archivo"] = None
        _pi_solicitud["desinstalar"] = None
        if archivo:
            _pi_instalar_ui(archivo)
        elif tool is not None:
            _pi_desinstalar_ui(tool)

    def _pi_instalar_ui(archivo):
        carpeta, motivos = _pi_instalar(archivo)
        if carpeta:
            _pi_msg["ok"] = True
            _pi_msg["pendiente"] = True
            _pi_msg["texto"] = ("Instalado en tools/plugins/%s. Reiniciá; "
                                "si no aparece, mirá Diagnóstico." % carpeta)
        else:
            _pi_msg["ok"] = False
            _pi_msg["pendiente"] = False
            _pi_msg["texto"] = _pi_fuera(motivos)

    def _pi_desinstalar_ui(tool):
        ok, motivo = _pi_desinstalar(tool)
        _pi_msg["ok"] = ok
        _pi_msg["pendiente"] = ok
        if ok:
            _pi_msg["texto"] = ("Desinstalado %s. Reiniciá para que "
                                "desaparezca del hub." % tool["dir"])
        else:
            _pi_msg["texto"] = motivo

    def _pi_abrir_incoming():
        _pi_asegurar(_PI_INCOMING)
        tool_abrir_carpeta(_PI_INCOMING)

    def _pi_reiniciar():
        # `full_restart` NO vuelve a leer los .rpy (reusa el script cargado);
        # `utter_restart` sí. El splash se salta con la bandera de sesión.
        if config.developer:
            renpy.session["_pi_reinicio"] = True
            renpy.utter_restart()
