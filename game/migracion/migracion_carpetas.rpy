## migracion_carpetas.rpy
## Migración entre dos carpetas: siempre se copia de la versión menor a la
## mayor. La carpeta actual puede ser origen o destino; las versiones iguales
## se preguntan.
##
## El juego solo detecta, muestra la oferta y lanza el script externo.
## La copia, el respaldo y el borrado los hace `migrar_carpetas.py`.

init python:
    import io as _mc_io
    import json as _mc_json
    import os as _mc_os
    import shutil as _mc_shutil
    import subprocess as _mc_sub
    import sys as _mc_sys
    import tempfile as _mc_tempfile

    _MC_DIR = "migracion"
    _MC_MANIFEST = "game/migracion/manifest.json"

    def _mc_ver(txt):
        try:
            partes = str(txt).strip().lstrip("vV").split(".")
            nums = [int(p) for p in partes[:3]]
            while len(nums) < 3:
                nums.append(0)
            return tuple(nums)
        except Exception:
            return None

    def _mc_manifest(ruta):
        try:
            with _mc_io.open(ruta, "r", encoding="utf-8") as fh:
                datos = _mc_json.loads(fh.read())
            if hasattr(datos, "get"):
                return datos
        except Exception:
            pass
        return None

    def mc_buscar():
        """Candidatas hermanas con manifest, en cualquier dirección de versión.

        Siempre se copia de la versión menor a la mayor. Si la carpeta nueva
        inicia la migración, importa la vieja; si la vieja inicia, migra hacia
        la nueva. Las versiones iguales se preguntan."""
        if not config.developer or not mg_hay_manifest():
            return []
        actual = mg_version()
        v_actual = _mc_ver(actual)
        if not v_actual:
            return []

        base = _mc_os.path.abspath(config.basedir)
        padre = _mc_os.path.dirname(base)
        candidatas = []
        try:
            nombres = _mc_os.listdir(padre)
        except Exception:
            return []

        for nombre in nombres:
            if nombre.startswith("."):
                continue
            ruta = _mc_os.path.join(padre, nombre)
            if not _mc_os.path.isdir(ruta):
                continue
            if _mc_os.path.abspath(ruta) == base:
                continue
            if not _mc_os.path.isdir(_mc_os.path.join(ruta, "game")):
                continue
            man = _mc_manifest(_mc_os.path.join(ruta, _MC_MANIFEST))
            if not man:
                continue
            version = str(man.get("template_version") or "")
            v = _mc_ver(version)
            if not v:
                continue
            if v > v_actual:
                sentido = "actual_origen"
            elif v < v_actual:
                sentido = "otra_origen"
            else:
                sentido = ""
            candidatas.append({
                "ruta": ruta,
                "nombre": nombre,
                "version": version,
                "igual": v == v_actual,
                "sentido": sentido,
                "recomendada": False,
            })

        candidatas.sort(key=lambda c: _mc_ver(c["version"]) or (0, 0, 0),
                        reverse=True)
        for c in candidatas:
            if not c["igual"]:
                c["recomendada"] = True
                break
        return candidatas

    def _mc_lanzar(source, dest):
        """Copia los helpers a un temporal, escribe el job y lanza el script."""
        script = _mc_os.path.join(config.gamedir, _MC_DIR, "migrar_carpetas.py")
        base_script = _mc_os.path.join(config.gamedir, _MC_DIR, "migrar.py")
        if not _mc_os.path.isfile(script) or not _mc_os.path.isfile(base_script):
            return False
        if not _mc_os.path.isdir(source) or not _mc_os.path.isdir(dest):
            return False
        if _mc_os.path.abspath(source) == _mc_os.path.abspath(dest):
            return False

        tmp = _mc_tempfile.mkdtemp(prefix="bdmcarpetas-")
        try:
            _mc_shutil.copy2(script, _mc_os.path.join(tmp, "migrar_carpetas.py"))
            _mc_shutil.copy2(base_script, _mc_os.path.join(tmp, "migrar.py"))
            argv = []
            for arg in _mc_sys.argv:
                if _mc_os.path.abspath(arg) == _mc_os.path.abspath(source):
                    argv.append(dest)
                else:
                    argv.append(arg)
            if not any(_mc_os.path.abspath(a) == _mc_os.path.abspath(dest)
                       for a in argv):
                argv.append(dest)
            job = {
                "pid": _mc_os.getpid(),
                "source": source,
                "dest": dest,
                "source_version": mg_version(),
                "dest_version": (_mc_manifest(_mc_os.path.join(
                    dest, _MC_MANIFEST)) or {}).get("template_version", ""),
                "python": _mc_sys.executable,
                "argv": argv,
            }
            job_path = _mc_os.path.join(tmp, "job.json")
            with _mc_io.open(job_path, "w", encoding="utf-8") as fh:
                _mc_json.dump(job, fh, ensure_ascii=False, indent=2)
            kwargs = {}
            if renpy.windows:
                kwargs["creationflags"] = 0x00000008 | 0x00000200
            else:
                kwargs["start_new_session"] = True
            _mc_sub.Popen([_mc_sys.executable,
                           _mc_os.path.join(tmp, "migrar_carpetas.py"),
                           job_path], close_fds=True, **kwargs)
            return True
        except Exception as e:
            print("migracion_carpetas: no se pudo lanzar: %s" % e)
            _mc_shutil.rmtree(tmp, ignore_errors=True)
            return False

    def mc_migrar_y_salir(destino, version, sentido="actual_origen"):
        """sentido: actual_origen = esta carpeta hacia la otra;
        otra_origen = la otra hacia esta (para versiones iguales/corruptas)."""
        actual = config.basedir
        if sentido == "otra_origen":
            source, target = destino, actual
        else:
            source, target = actual, destino
        if _mc_lanzar(source, target):
            renpy.quit(relaunch=False)
            return True
        renpy.notify("No se pudo iniciar la migración entre carpetas.")
        return False


screen mc_oferta(candidatas):
    zorder 300
    modal True
    style_prefix "migracion"

    use migracion_panel:

        vbox:
            spacing 18

            text _("Otra carpeta del template encontrada"):
                style "migracion_titulo"

            text _("Podés migrar tus archivos propios a otra carpeta y eliminar "
                   "la actual cuando el destino arranque bien."):
                style "migracion_texto"

            for c in candidatas:
                $ _mc_nom = c.get("nombre", "")
                $ _mc_ver_txt = c.get("version", "")
                $ _mc_ruta = c.get("ruta", "")
                $ _mc_rec = " (recomendada)" if c.get("recomendada") else ""
                vbox:
                    spacing 4
                    text "[_mc_nom] — v[_mc_ver_txt][_mc_rec]":
                        style "migracion_texto"
                    text "[_mc_ruta]":
                        style "migracion_texto"
                        size 14
                    if c.get("igual"):
                        text _("Misma versión: puede ser una carpeta corrupta. "
                               "Elegí cuál usar como origen."):
                            style "migracion_texto"
                            size 14
                        hbox:
                            spacing 14
                            textbutton _("Migrar esta a la otra"):
                                style "navigation_button"
                                text_style "navigation_button_text"
                                action Return((_mc_ruta, _mc_ver_txt,
                                               "actual_origen"))
                            textbutton _("Migrar la otra a esta"):
                                style "navigation_button"
                                text_style "navigation_button_text"
                                action Return((_mc_ruta, _mc_ver_txt,
                                               "otra_origen"))
                    elif c.get("sentido") == "otra_origen":
                        textbutton _("Importar esta carpeta vieja"):
                            style "navigation_button"
                            text_style "navigation_button_text"
                            action Return((_mc_ruta, _mc_ver_txt,
                                           "otra_origen"))
                    else:
                        textbutton _("Migrar a esta carpeta"):
                            style "navigation_button"
                            text_style "navigation_button_text"
                            action Return((_mc_ruta, _mc_ver_txt,
                                           "actual_origen"))

            textbutton _("Ahora no"):
                style "navigation_button"
                text_style "navigation_button_text"
                action Return(())
