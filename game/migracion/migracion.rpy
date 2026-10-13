## migracion.rpy
## Sistema de migración de assets del template.
##
## Detecta si hay una versión nueva del template en GitHub, avisa al modder con
## una ventana y, si acepta, prepara todo para que un script EXTERNO
## (migracion/migrar.py) haga el reemplazo al cerrar el juego (Ren'Py no puede
## reemplazar su propio código mientras corre).
##
## La versión del template y el hash de cada archivo salen de
## `migracion/manifest.json` (generado en cada release). La UI vive en
## migracion_ui.rpy. Ver migracion/README.md.

init -1 python:
    import builtins as _mg_builtins
    import io as _mg_io
    import json as _mg_json
    import os as _mg_os
    import sys as _mg_sys
    import subprocess as _mg_sub
    import threading as _mg_threading
    import time as _mg_time

    _MG_MANIFEST = "migracion/manifest.json"
    _MG_DIRNAME = "migracion"
    _MG_REPO_DEF = "SingerRuv/DDLC-Template"
    _MG_CACHE_SEG = 24 * 3600  # 24 h

    # ---- Manifest y versión del template ------------------------------------

    def mg_manifest():
        """Lee migracion/manifest.json (suelto o desde el .rpa). {} si falta."""
        try:
            with renpy.file(_MG_MANIFEST) as fh:
                datos = _mg_json.loads(fh.read().decode("utf-8"))
            if isinstance(datos, _mg_builtins.dict):
                return datos
        except Exception:
            pass
        return {}

    def mg_hay_manifest():
        """True si el proyecto trae migracion/manifest.json (viene de un release).

        El repo fuente del template NO tiene manifest, así que todo el sistema
        de migración queda inerte ahí (solo aplica a proyectos de mod)."""
        return bool(mg_manifest())

    def mg_version():
        """Versión del template del manifest, o None si no hay manifest."""
        v = mg_manifest().get("template_version")
        return str(v) if v else None

    def mg_repo():
        return str(mg_manifest().get("repo") or _MG_REPO_DEF)

    def _mg_ver(v):
        try:
            return tuple(int(x) for x in str(v).split("."))
        except Exception:
            return None

    def mg_nueva(v):
        """True si `v` es más nueva que la versión instalada."""
        a, b = _mg_ver(v), _mg_ver(mg_version())
        return bool(a and b and a > b)

    # ---- Chequeo de la última release en GitHub -----------------------------

    _MG_LOCK = _mg_threading.Lock()
    _MG_ESTADO = {"listo": False, "en_curso": False, "version": "", "url": "",
                  "error": "", "manual": False}
    _MG_AVISADO = {"version": ""}  # versión ya avisada en esta sesión

    def _mg_consultar():
        """Consulta la última release. Devuelve (version, url_del_zip)."""
        import requests
        url = "https://api.github.com/repos/%s/releases/latest" % mg_repo()
        req = {"User-Agent": "DDLC-BrokenDreamsModTemplate",
               "Accept": "application/vnd.github+json"}
        try:
            proxies = renpy.exports.proxies
        except Exception:
            proxies = None
        resp = requests.get(url, headers=req, proxies=proxies, timeout=8)
        resp.raise_for_status()
        datos = resp.json()
        version = str(datos.get("tag_name") or "").lstrip("v")
        zip_url = ""
        for a in (datos.get("assets") or []):
            if str(a.get("name", "")).lower().endswith(".zip"):
                zip_url = a.get("browser_download_url") or ""
                break
        return version, zip_url

    def _mg_descargar(url, destino):
        """Descarga un archivo con requests (Ren'Py ya trae certifi)."""
        import requests
        try:
            proxies = renpy.exports.proxies
        except Exception:
            proxies = None
        with requests.get(url, headers={"User-Agent": "DDLC-BrokenDreamsModTemplate"},
                          proxies=proxies, timeout=60, stream=True) as resp:
            resp.raise_for_status()
            with _mg_io.open(destino, "wb") as f:
                for chunk in resp.iter_content(65536):
                    if chunk:
                        f.write(chunk)
        return destino

    def _mg_chequear():
        try:
            version, zip_url = _mg_consultar()
            with _MG_LOCK:
                _MG_ESTADO.update({"listo": True, "en_curso": False,
                                   "version": version, "url": zip_url, "error": ""})
            persistent.mg_cache = {"ts": int(_mg_time.time()),
                                   "version": version, "url": zip_url}
        except Exception as e:
            with _MG_LOCK:
                _MG_ESTADO.update({"listo": True, "en_curso": False,
                                   "version": "", "url": "", "error": str(e)})

    def mg_iniciar(ignorar_cache=False, manual=False):
        """Arranca (o resuelve desde caché) el chequeo de versión."""
        if not mg_hay_manifest():
            return
        cache = persistent.mg_cache
        fresco = (not ignorar_cache and isinstance(cache, _mg_builtins.dict)
                  and _mg_time.time() - cache.get("ts", 0) < _MG_CACHE_SEG)
        with _MG_LOCK:
            if _MG_ESTADO.get("en_curso"):
                return
            if fresco:
                _MG_ESTADO.update({"listo": True, "en_curso": False,
                                   "version": cache.get("version", ""),
                                   "url": cache.get("url", ""),
                                   "error": "", "manual": manual})
                return
            _MG_ESTADO.update({"listo": False, "en_curso": True, "version": "",
                               "url": "", "error": "", "manual": manual})
        _mg_threading.Thread(target=_mg_chequear, daemon=True).start()

    def mg_buscar_manual():
        """Fuerza un chequeo (botón de Ajustes). El resultado lo muestra el vigilante."""
        if not mg_hay_manifest():
            return
        mg_iniciar(ignorar_cache=True, manual=True)

    # ---- Vigilante (se ejecuta como periodic callback) ----------------------

    def mg_vigilar():
        """Si el chequeo terminó, muestra la ventana correspondiente (una vez)."""
        if not config.developer or not mg_hay_manifest():
            return
        if renpy.get_screen("migracion_aviso") or \
           renpy.get_screen("migracion_confirmar") or \
           renpy.get_screen("migracion_al_dia"):
            return
        with _MG_LOCK:
            estado = dict(_MG_ESTADO)
        if not estado.get("listo") or estado.get("en_curso"):
            return
        manual = estado.get("manual")
        version = estado.get("version")
        # Consume el resultado para no repetir.
        with _MG_LOCK:
            _MG_ESTADO["listo"] = False
            _MG_ESTADO["manual"] = False

        if not version:
            if manual:
                renpy.show_screen("migracion_al_dia", error=estado.get("error", ""))
            return
        if mg_nueva(version) and version != persistent.mg_ignorar:
            if not manual and version == _MG_AVISADO["version"]:
                return  # ya se avisó en esta sesión
            _MG_AVISADO["version"] = version
            renpy.show_screen("migracion_aviso", version=version, url=estado.get("url", ""))
        elif manual:
            renpy.show_screen("migracion_al_dia")

    # ---- Preparar y lanzar el script externo --------------------------------

    def mg_preparar(version, url):
        """Descarga el ZIP y lanza migrar.py detached. True si pudo."""
        dir_mig = _mg_os.path.join(config.gamedir, _MG_DIRNAME)
        script = _mg_os.path.join(dir_mig, "migrar.py")
        job_path = _mg_os.path.join(dir_mig, ".job.json")
        zip_path = _mg_os.path.join(dir_mig, ".template.zip")
        zip_manual = _mg_os.path.join(dir_mig, "manual.zip")
        if not _mg_os.path.isfile(script):
            renpy.log("migracion: no existe %s" % script)
            return False
        job = {
            "pid": _mg_os.getpid(),
            "project": config.basedir,
            "from_version": mg_version(),
            "to_version": version,
            "download_url": url,
            "python": _mg_sys.executable,
            "argv": list(_mg_sys.argv),
        }
        try:
            if _mg_os.path.isfile(zip_manual):
                # Modo offline: se usa el ZIP puesto a mano (ver migracion/README.md).
                job["zip"] = zip_manual
            elif url:
                _mg_descargar(url, zip_path)
                job["zip"] = zip_path
        except Exception as e:
            renpy.log("migracion: no se pudo descargar el template: %s" % e)
            return False
        try:
            with _mg_io.open(job_path, "w", encoding="utf-8") as f:
                _mg_json.dump(job, f, ensure_ascii=False, indent=2)
            kwargs = {}
            if renpy.windows:
                kwargs["creationflags"] = 0x00000008 | 0x00000200  # DETACHED | NEW_GROUP
            else:
                kwargs["start_new_session"] = True
            _mg_sub.Popen([_mg_sys.executable, script, job_path],
                          close_fds=True, **kwargs)
        except Exception as e:
            renpy.log("migracion: no se pudo lanzar el migrador: %s" % e)
            return False
        return True

    def mg_migrar_y_salir(version, url):
        """Acción del botón 'Migrar ahora': lanza el migrador y cierra el juego."""
        if mg_preparar(version, url):
            renpy.quit(relaunch=False)
        else:
            renpy.hide_screen("migracion_confirmar")
            renpy.notify("No se pudo iniciar la migración. Revisá game/migracion/.")

    # ---- Post-migración (reporte) -------------------------------------------

    def mg_reporte_pendiente():
        """Devuelve el reporte de la última migración si no se mostró aún."""
        ruta = _mg_os.path.join(config.gamedir, _MG_DIRNAME, "reporte.json")
        try:
            if not _mg_os.path.isfile(ruta):
                return None
            with _mg_io.open(ruta, "r", encoding="utf-8") as f:
                reporte = _mg_json.load(f)
        except Exception:
            return None
        if reporte.get("cuando") == persistent.mg_ultimo_reporte:
            return None
        return reporte

    def mg_marcar_reporte(reporte):
        persistent.mg_ultimo_reporte = reporte.get("cuando")

    # ---- Registro del vigilante --------------------------------------------

    def _mg_registrar():
        if mg_vigilar not in config.periodic_callbacks:
            config.periodic_callbacks.append(mg_vigilar)


init 999 python:
    _mg_registrar()
