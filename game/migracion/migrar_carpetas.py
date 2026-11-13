#!/usr/bin/env python3
## migrar_carpetas.py
## Migrador externo de una carpeta de proyecto a otra.
##
## Lo lanza el juego desde un temporal. Espera el cierre del proceso, copia
## solo los archivos propios del origen, respalda el destino, arranca el
## destino y elimina la carpeta vieja cuando el arranque fue correcto.

import io
import json
import os
import shutil
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import migrar as base

IGNORAR_DIRS = set(base.IGNORAR_DIRS) | {"migracion_backup"}
RUTA_REPORTE = os.path.join("game", "migracion", "reporte.json")
RUTA_LOG = os.path.join("game", "migracion", "migracion.log")

# El script principal siempre lo aporta la plantilla destino. La historia del
# origen va en otros .rpy y no se pierde.
ARCHIVOS_PLANTILLA = ("game/script.rpy",)


def _marcar_destino(dest, source):
    """Marca la carpeta como destino para no volver a ofrecerla."""
    try:
        with io.open(os.path.join(dest, ".migracion_destino"), "w",
                     encoding="utf-8", newline="\n") as fh:
            fh.write("origen=%s\n" % source)
    except Exception:
        pass


def _limpiar_boot(boot_rpy):
    """Borra el .rpy temporal y su .rpyc compilado."""
    for ruta in (boot_rpy, boot_rpy + "c"):
        try:
            os.remove(ruta)
        except OSError:
            pass


def _rel(raiz, ruta):
    return base._norm(os.path.relpath(ruta, raiz))


def _ignorar(rel):
    rel = base._norm(rel)
    if base._ignorar(rel):
        return True
    return any(d in IGNORAR_DIRS for d in rel.split("/"))


def _sha(ruta):
    return base._sha256(ruta)


def _copiar(origen, destino):
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    if os.path.isfile(destino):
        tmp = destino + ".migracion-tmp"
        shutil.copy2(origen, tmp)
        os.replace(tmp, destino)
    else:
        shutil.copy2(origen, destino)


def _leer_job(ruta):
    with io.open(ruta, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _log(project, mensaje):
    try:
        ruta = os.path.join(project, RUTA_LOG)
        os.makedirs(os.path.dirname(ruta), exist_ok=True)
        with io.open(ruta, "a", encoding="utf-8") as fh:
            fh.write("%s %s\n" % (time.strftime("%Y-%m-%d %H:%M:%S"), mensaje))
    except Exception:
        pass


def _reporte(project, source, dest, desde, hasta, ok, error, plan=None,
             backup=None, copiados=0, borrada=False, extra=None):
    plan = plan or {}
    reporte = {
        "cuando": time.strftime("%Y-%m-%d %H:%M:%S"),
        "modo": "carpetas",
        "desde": desde or "?",
        "hasta": hasta or "?",
        "ok": bool(ok),
        "error": error,
        "backup": _rel(project, backup) if backup else "",
        "copiados": copiados,
        "conservados": [],
        "conflictos": plan.get("conflictos", []),
        "nuevos": plan.get("nuevos", []),
        "borrados": [],
        "origen": source,
        "origen_nombre": os.path.basename(os.path.normpath(source)),
        "destino": dest,
        "destino_nombre": os.path.basename(os.path.normpath(dest)),
        "carpeta_vieja": source,
        "carpeta_vieja_borrada": bool(borrada),
    }
    if extra:
        reporte.update(extra)
    ruta = os.path.join(project, RUTA_REPORTE)
    try:
        os.makedirs(os.path.dirname(ruta), exist_ok=True)
        with io.open(ruta, "w", encoding="utf-8") as fh:
            json.dump(reporte, fh, ensure_ascii=False, indent=2)
    except Exception:
        pass
    return reporte


def _archivos_origen(source, man):
    """Archivos propios: cambiados respecto del manifest o agregados."""
    propios = []
    ignorados = set(base.ARCHIVOS_SISTEMA)
    files = man.get("files", {}) if man else {}
    raiz_abs = os.path.abspath(source)
    for dirpath, dirnames, filenames in os.walk(source):
        en_raiz = os.path.abspath(dirpath) == raiz_abs
        dirnames[:] = [d for d in dirnames
                       if d not in IGNORAR_DIRS
                       and not (en_raiz and d in base.IGNORAR_RAIZ)]
        for nombre in filenames:
            ruta = os.path.join(dirpath, nombre)
            rel = _rel(source, ruta)
            if _ignorar(rel) or rel in ignorados or rel in ARCHIVOS_PLANTILLA:
                continue
            if rel in files:
                try:
                    if _sha(ruta) == files[rel]:
                        continue
                except Exception:
                    continue
            propios.append((rel, ruta))
    return propios


def _copiar_saves(source, dest, backup):
    origen = os.path.join(source, "game", "saves")
    destino = os.path.join(dest, "game", "saves")
    if not os.path.isdir(origen):
        return 0, False
    tiene_destino = os.path.isdir(destino) and any(
        os.scandir(destino)) if os.path.isdir(destino) else False
    if not tiene_destino:
        shutil.copytree(origen, destino, dirs_exist_ok=True)
        return 1, True
    # No pisar las saves del destino: guardar las del origen aparte.
    _copiar_arbol(origen, os.path.join(backup, "saves_origen"))
    return 0, False


def _copiar_arbol(origen, destino):
    if not os.path.isdir(origen):
        return
    for dirpath, _dirnames, filenames in os.walk(origen):
        rel = os.path.relpath(dirpath, origen)
        dst_dir = os.path.join(destino, rel) if rel != "." else destino
        os.makedirs(dst_dir, exist_ok=True)
        for nombre in filenames:
            shutil.copy2(os.path.join(dirpath, nombre),
                         os.path.join(dst_dir, nombre))


def _copiar_rpa(source, dest):
    nuevos = []
    for dirpath, dirnames, filenames in os.walk(source):
        dirnames[:] = [d for d in dirnames if d not in IGNORAR_DIRS]
        for nombre in filenames:
            if not nombre.lower().endswith(".rpa"):
                continue
            ruta = os.path.join(dirpath, nombre)
            rel = _rel(source, ruta)
            destino = os.path.join(dest, rel)
            if os.path.exists(destino):
                continue
            _copiar(ruta, destino)
            nuevos.append(rel)
    return nuevos


def _backup_destino(dest, rel, backup):
    ruta = os.path.join(dest, rel.replace("/", os.sep))
    if not os.path.isfile(ruta):
        return False
    dst = os.path.join(backup, rel.replace("/", os.sep))
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(ruta, dst)
    return True


def _restaurar_backup(dest, backup, creados, rpa_nuevos, saves_copiadas):
    if os.path.isdir(backup):
        for dirpath, _dirnames, filenames in os.walk(backup):
            for nombre in filenames:
                ruta = os.path.join(dirpath, nombre)
                rel = os.path.relpath(ruta, backup)
                if rel.startswith("saves_origen" + os.sep):
                    continue
                dst = os.path.join(dest, rel)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(ruta, dst)
    for rel in creados:
        try:
            os.remove(os.path.join(dest, rel.replace("/", os.sep)))
        except OSError:
            pass
    for rel in rpa_nuevos:
        try:
            os.remove(os.path.join(dest, rel.replace("/", os.sep)))
        except OSError:
            pass
    if saves_copiadas:
        shutil.rmtree(os.path.join(dest, "game", "saves"), ignore_errors=True)


def _boot_rpy(dest, pid):
    ruta = os.path.join(dest, "game", "zz_migracion_boot_%s.rpy" % pid)
    with io.open(ruta, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("init 1000 python:\n")
        fh.write("    import os\n")
        fh.write("    try:\n")
        fh.write("        open(os.path.join(config.basedir, \".migracion_boot_ok\"), \"w\").close()\n")
        fh.write("    except Exception:\n")
        fh.write("        pass\n")
    return ruta


def _lanzar(job):
    exe = job.get("python") or sys.executable
    argv = list(job.get("argv") or [])
    if not argv:
        return None
    try:
        return subprocess.Popen([exe] + argv, close_fds=True)
    except Exception:
        return None


def migrar(job):
    source = os.path.abspath(job["source"])
    dest = os.path.abspath(job["dest"])
    man_src = base._leer_manifest(source)
    man_dst = base._leer_manifest(dest)
    if man_src is None or man_dst is None:
        raise RuntimeError("las dos carpetas deben tener manifest")
    desde = man_src.get("template_version") or job.get("source_version")
    hasta = man_dst.get("template_version") or job.get("dest_version")
    v_src, v_dst = base._ver(desde), base._ver(hasta)
    if v_src and v_dst and v_src > v_dst:
        raise RuntimeError("el destino es más viejo que el origen")
    if not base.esperar_cierre(job.get("pid")):
        raise RuntimeError("el juego no se cerró a tiempo; no se modificó nada")

    ops = []
    if v_dst and v_dst >= (2, 0, 0) and v_src and v_src < (2, 0, 0):
        ops = base._estructura_v2(source)
        base._renombrar_man(man_src)

    propios = _archivos_origen(source, man_src)
    cuando = time.strftime("%Y%m%d-%H%M%S")
    backup = os.path.join(dest, "migracion_backup", "carpetas-" + cuando)
    os.makedirs(backup, exist_ok=True)

    plan = {"conflictos": [], "nuevos": []}
    creados = []
    rpa_nuevos = []
    saves_flag = False
    boot_rpy = None
    try:
        for rel, ruta in propios:
            dst = os.path.join(dest, rel.replace("/", os.sep))
            if os.path.isfile(dst):
                if _sha(dst) == _sha(ruta):
                    continue
                _backup_destino(dest, rel, backup)
                plan["conflictos"].append(rel)
            else:
                creados.append(rel)
            _copiar(ruta, dst)

        rpa_nuevos = _copiar_rpa(source, dest)
        try:
            _saves_count, saves_flag = _copiar_saves(source, dest, backup)
        except Exception as e:
            _log(dest, "saves: %s" % e)

        boot_marker = os.path.join(dest, ".migracion_boot_ok")
        try:
            os.remove(boot_marker)
        except OSError:
            pass
        boot_rpy = _boot_rpy(dest, os.getpid())
        proc = _lanzar(job)
        if proc is None:
            raise RuntimeError("no se pudo lanzar la carpeta destino")

        arranco = False
        for _ in range(120):
            if os.path.isfile(boot_marker):
                arranco = True
                break
            if proc.poll() is not None:
                break
            time.sleep(1)
        try:
            _limpiar_boot(boot_rpy)
        except Exception:
            pass
        try:
            os.remove(boot_marker)
        except OSError:
            pass
        if not arranco:
            raise RuntimeError("el destino no confirmó el arranque")

        borrada = False
        try:
            shutil.rmtree(source)
            borrada = True
        except Exception as e:
            _log(dest, "no se pudo borrar la carpeta vieja: %s" % e)

        _marcar_destino(dest, source)
        _reporte(dest, source, dest, desde, hasta, True, "", plan, backup,
                 len(propios), borrada,
                 {"rpa": rpa_nuevos, "saves": bool(saves_flag)})
        _log(dest, "migracion entre carpetas OK: %d archivos" % len(propios))
        return True
    except Exception as e:
        if boot_rpy:
            try:
                _limpiar_boot(boot_rpy)
            except Exception:
                pass
        try:
            os.remove(os.path.join(dest, ".migracion_boot_ok"))
        except OSError:
            pass
        _restaurar_backup(dest, backup, creados, rpa_nuevos, saves_flag)
        if ops:
            base._revertir_estructura(ops)
        _reporte(dest, source, dest, desde, hasta, False, str(e), plan,
                 backup, len(propios), False)
        _reporte(source, source, dest, desde, hasta, False, str(e), plan,
                 backup, len(propios), False)
        _log(source, "ERROR migracion entre carpetas: %s" % e)
        return False


def main():
    if len(sys.argv) < 2:
        sys.stderr.write("uso: migrar_carpetas.py <job.json>\n")
        return 2
    job = _leer_job(sys.argv[1])
    return 0 if migrar(job) else 1


if __name__ == "__main__":
    sys.exit(main())
