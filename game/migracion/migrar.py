#!/usr/bin/env python3
## migrar.py
## Migrador de assets del template (script externo, sin Ren'Py).
##
## Ren'Py no puede reemplazar su propio codigo mientras esta en ejecucion, asi
## que el juego lanza este script "detached" cuando el modder acepta migrar.
## Aca:
##   1. esperamos a que el juego cierre,
##   2. descargamos (o usamos) el ZIP del template nuevo,
##   3. respaldamos SOLO los archivos del modder,
##   4. aplicamos el update conservando lo suyo,
##   5. relanzamos el juego y dejamos un reporte.
##
## El algoritmo se apoya en `game/migracion/manifest.json`, que lista el hash
## sha256 de cada archivo del template. Comparando con el manifest viejo se
## sabe que archivos toco el modder y que archivos cambio el template.
##
## Uso:
##   python migrar.py <job.json>          # flujo normal (lo lanza el juego)
##   python migrar.py --selftest          # autotest del algoritmo de mezcla
##   python migrar.py --zip <zip> --project <dir>   # modo manual (sin job)

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import zipfile

# ---- Reglas de que NO se toca nunca -------------------------------------------------

# Extensiones que jamas se migran ni respaldan (bytecode, assets de DDLC, etc.).
IGNORAR_EXT = (".rpa", ".rpyc", ".rpyb", ".pyc")
# Carpetas que se ignoran al escanear el proyecto.
IGNORAR_DIRS = ("saves", "cache", "__pycache__", "backup")
# Archivos sueltos que se ignoran siempre.
IGNORAR_FILES = ("log.txt", "errors.txt", "traceback.txt")
# Archivos propios del sistema de migracion (no son parte del template).
ARCHIVOS_SISTEMA = (
    "game/migracion/manifest.json",
    "game/migracion/.job.json",
    "game/migracion/.template.zip",
    "game/migracion/manual.zip",
    "game/migracion/reporte.json",
)

RUTA_MANIFEST = os.path.join("game", "migracion", "manifest.json")
RUTA_REPORTE = os.path.join("game", "migracion", "reporte.json")


def _norm(rel):
    return rel.replace("\\", "/")


def _ignorar(rel):
    """True si la ruta (relativa, con /) no debe migrarse ni respaldarse."""
    rel = _norm(rel)
    partes = rel.split("/")
    if partes[-1] in IGNORAR_FILES:
        return True
    if rel.endswith(IGNORAR_EXT):
        return True
    for d in IGNORAR_DIRS:
        if d in partes:
            return True
    return False


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def _listar(raiz, sub):
    """Devuelve las rutas relativas (posix) de los archivos bajo raiz/sub."""
    base = os.path.join(raiz, sub) if sub else raiz
    resultado = []
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames[:] = [d for d in dirnames if d not in IGNORAR_DIRS]
        for nombre in filenames:
            abs_ = os.path.join(dirpath, nombre)
            rel = _norm(os.path.relpath(abs_, raiz))
            if not _ignorar(rel):
                resultado.append(rel)
    return sorted(resultado)


def _leer_manifest(raiz):
    """Lee game/migracion/manifest.json bajo `raiz`. Devuelve dict o None."""
    ruta = os.path.join(raiz, RUTA_MANIFEST)
    if not os.path.isfile(ruta):
        return None
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        sys.stderr.write("manifest ilegible (%s): %s\n" % (ruta, e))
        return None


# ---- Plan de migracion --------------------------------------------------------------

def planificar(project, staging, man_old, man_new):
    """Calcula que hacer con cada archivo.

    Devuelve un dict con:
      copiar    -> archivos del template nuevo a copiar (sobreescribir/crear)
      conservar -> {rel: motivo} archivos del modder que se dejan como estan
      conflictos-> sublista de conservar donde tambien cambio el template
      nuevos    -> archivos que trae el template nuevo y no existian
      borrados  -> archivos que el template viejo tenia y el nuevo ya no
      agregados -> archivos que el modder agrego (para respaldar)
    """
    viejos = man_old.get("files", {})
    nuevos = man_new.get("files", {})

    copiar = []
    conservar = {}
    conflictos = []
    nuevos_files = []
    borrados = []
    agregados = []

    # 1) Archivos del template: ¿los toco el modder? ¿los cambio el template?
    for rel, hash_viejo in viejos.items():
        abs_ = os.path.join(project, rel)
        if not os.path.isfile(abs_):
            continue  # lo borro el modder: se respeta (no se re-copia)
        if _sha256(abs_) != hash_viejo:
            conservar[rel] = "editado por el modder"
            if rel in nuevos and nuevos[rel] != hash_viejo:
                conflictos.append(rel)

    # 2) Archivos que agrega el template nuevo.
    for rel in nuevos:
        if rel not in viejos:
            nuevos_files.append(rel)

    # 3) Archivos que el template nuevo ya no trae (dejados en el proyecto).
    for rel in viejos:
        if rel not in nuevos:
            borrados.append(rel)

    # 4) Archivos que agrego el modder (incluye colisiones con el template nuevo).
    for rel in _listar(project, "game"):
        if rel in viejos or rel in ARCHIVOS_SISTEMA or rel.endswith(IGNORAR_EXT):
            continue
        if rel in nuevos:
            conservar[rel] = "agregado por el modder (colisiona con el template)"
            conflictos.append(rel)
        else:
            agregados.append(rel)

    # 5) A copiar: todo el template nuevo menos lo que se conserva del modder.
    for rel in nuevos:
        if rel not in conservar:
            copiar.append(rel)

    return {
        "copiar": sorted(copiar),
        "conservar": conservar,
        "conflictos": sorted(conflictos),
        "nuevos": sorted(nuevos_files),
        "borrados": sorted(borrados),
        "agregados": sorted(agregados),
    }


def respaldar(project, plan, desde, cuando):
    """Copia SOLO los archivos del modder a migracion_backup/<desde>-<cuando>/.

    Va en la RAÍZ del proyecto (hermano de game/), nunca dentro de game/, para
    que Ren'Py no escanee los .rpy respaldados (darían labels duplicados).
    Incluye los que editó (conservar) y los que agregó (agregados)."""
    destino = os.path.join(project, "migracion_backup",
                           "%s-%s" % (desde or "0.0.0", cuando))
    rels = set(plan["conservar"].keys()) | set(plan.get("agregados", []))
    for rel in rels:
        origen = os.path.join(project, rel.replace("/", os.sep))
        if not os.path.isfile(origen):
            continue
        dst = os.path.join(destino, rel.replace("/", os.sep))
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(origen, dst)
    return destino, len(rels)


def aplicar(project, staging, plan, man_new):
    """Copia el template nuevo y deja el manifest actualizado."""
    escritos = 0
    for rel in plan["copiar"]:
        origen = os.path.join(staging, rel.replace("/", os.sep))
        if not os.path.isfile(origen):
            continue
        dst = os.path.join(project, rel.replace("/", os.sep))
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(origen, dst)
        escritos += 1
    # El manifest nuevo se instala siempre (es la fuente de verdad de la version).
    origen_man = os.path.join(staging, RUTA_MANIFEST.replace("/", os.sep))
    if os.path.isfile(origen_man):
        dst_man = os.path.join(project, RUTA_MANIFEST.replace("/", os.sep))
        os.makedirs(os.path.dirname(dst_man), exist_ok=True)
        shutil.copy2(origen_man, dst_man)
    return escritos


def escribir_reporte(project, desde, hasta, plan, backup, escritos, ok=True, error=""):
    reporte = {
        "cuando": time.strftime("%Y-%m-%d %H:%M:%S"),
        "desde": desde or "0.0.0",
        "hasta": hasta or "0.0.0",
        "ok": bool(ok),
        "error": error,
        "backup": _norm(os.path.relpath(backup, project)) if backup else "",
        "copiados": escritos,
        "conservados": sorted(plan["conservar"].keys()) if plan else [],
        "conflictos": plan["conflictos"] if plan else [],
        "nuevos": plan["nuevos"] if plan else [],
        "borrados": plan["borrados"] if plan else [],
    }
    ruta = os.path.join(project, RUTA_REPORTE)
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(reporte, f, ensure_ascii=False, indent=2)
    return ruta


# ---- Procesos, descarga y extraccion ------------------------------------------------

def _proceso_vivo(pid):
    try:
        if os.name == "nt":
            out = subprocess.run(
                ["tasklist", "/FI", "PID eq %d" % pid],
                capture_output=True, text=True).stdout
            return str(pid) in (out or "")
        os.kill(pid, 0)
        return True
    except Exception:
        return False


def esperar_cierre(pid, timeout=300):
    """Espera a que el proceso del juego termine (o el timeout)."""
    if not pid:
        return
    fin = time.time() + timeout
    time.sleep(0.5)
    while time.time() < fin and _proceso_vivo(pid):
        time.sleep(0.5)


def descargar(url, destino):
    import ssl
    import urllib.request
    contexto = None
    try:
        import certifi
        contexto = ssl.create_default_context(cafile=certifi.where())
    except Exception:
        contexto = None
    req = urllib.request.Request(url, headers={"User-Agent": "DDLC-BDMigrator"})
    with urllib.request.urlopen(req, timeout=60, context=contexto) as resp, open(destino, "wb") as f:
        shutil.copyfileobj(resp, f)
    return destino


def extraer(zip_path, destino):
    """Extrae el ZIP y devuelve la carpeta que contiene `game/` (sin el prefijo)."""
    with zipfile.ZipFile(zip_path) as z:
        z.extractall(destino)
    for nombre in sorted(os.listdir(destino)):
        candidato = os.path.join(destino, nombre)
        if os.path.isdir(candidato) and os.path.isdir(os.path.join(candidato, "game")):
            return candidato
    if os.path.isdir(os.path.join(destino, "game")):
        return destino
    raise RuntimeError("el ZIP no contiene una carpeta game/")


def relanzar(job):
    """Reabre el juego tal como se lanzo."""
    exe = job.get("python") or sys.executable
    argv = job.get("argv") or []
    if not argv:
        return False
    try:
        subprocess.Popen([exe] + list(argv), close_fds=True)
        return True
    except Exception as e:
        sys.stderr.write("no se pudo relanzar el juego: %s\n" % e)
        return False


# ---- Flujo principal ----------------------------------------------------------------

def migrar(job):
    project = job["project"]
    tmp = tempfile.mkdtemp(prefix="bdmigrar-")

    man_old = _leer_manifest(project)
    if man_old is None:
        escribir_reporte(project, job.get("from_version"), job.get("to_version"),
                         None, None, 0, ok=False,
                         error="El proyecto no tiene manifest; no se puede migrar.")
        return False
    desde = man_old.get("template_version") or job.get("from_version")

    # 1) Esperar a que el juego cierre.
    esperar_cierre(job.get("pid"))

    # 2) Obtener el ZIP del template nuevo.
    try:
        zip_path = job.get("zip")
        if not zip_path:
            zip_path = os.path.join(tmp, "template.zip")
            descargar(job["download_url"], zip_path)
        staging = extraer(zip_path, os.path.join(tmp, "x"))
    except Exception as e:
        escribir_reporte(project, desde, job.get("to_version"), None, None, 0, ok=False,
                         error="No se pudo obtener/extraer el template: %s" % e)
        shutil.rmtree(tmp, ignore_errors=True)
        return False

    man_new = _leer_manifest(staging)
    if man_new is None:
        escribir_reporte(project, desde, job.get("to_version"), None, None, 0, ok=False,
                         error="El template nuevo no trae manifest.")
        shutil.rmtree(tmp, ignore_errors=True)
        return False
    hasta = man_new.get("template_version") or job.get("to_version")

    # 3) Planificar, respaldar y aplicar.
    plan = planificar(project, staging, man_old, man_new)
    cuando = time.strftime("%Y%m%d-%H%M%S")
    backup, _n = respaldar(project, plan, desde, cuando)
    escritos = aplicar(project, staging, plan, man_new)
    reporte = escribir_reporte(project, desde, hasta, plan, backup, escritos)

    shutil.rmtree(tmp, ignore_errors=True)

    # 4) Relanzar el juego.
    relanzar(job)
    return reporte


def cargar_job(ruta):
    with open(ruta, "r", encoding="utf-8") as f:
        return json.load(f)


# ---- Autotest -----------------------------------------------------------------------

def selftest():
    """Verifica el algoritmo de mezcla con dos arboles sinteticos."""
    tmp = tempfile.mkdtemp(prefix="bdmigrar-test-")
    project = os.path.join(tmp, "proj")
    staging = os.path.join(tmp, "nuevo")

    def escribir(raiz, rel, contenido):
        p = os.path.join(raiz, rel.replace("/", os.sep))
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            f.write(contenido)
        return p

    def manifest_de(raiz, version):
        files = {}
        for rel in _listar(raiz, None):
            if rel in ARCHIVOS_SISTEMA:
                continue
            files[rel] = _sha256(os.path.join(raiz, rel.replace("/", os.sep)))
        return {"template_version": version, "files": files}

    # --- Template viejo (1.0.0) ---
    escribir(project, "game/core/a.rpy", "A v1")
    escribir(project, "game/definitions/def.rpy", "DEF v1")
    escribir(project, "game/gui.rpy", "GUI v1")
    escribir(project, "README.md", "readme v1")
    escribir(project, "game/migracion/manifest.json", "{}")  # se regenera abajo
    man_old = manifest_de(project, "1.0.0")

    # --- El modder toca cosas ---
    escribir(project, "game/definitions/def.rpy", "DEF v1 + MI CAMBIO")  # editado (conflicto)
    escribir(project, "game/gui.rpy", "GUI v1 + MI TEMA")                # editado (sin conflicto)
    escribir(project, "game/mod_assets/images/bg/mi_bg.png", "PNG")      # agregado
    escribir(project, "game/script.rpy", "MI HISTORIA")                  # agregado

    # --- Template nuevo (2.0.0) ---
    escribir(staging, "game/core/a.rpy", "A v2")                # cambia sin edicion -> copiar
    escribir(staging, "game/definitions/def.rpy", "DEF v2")     # cambia + editado -> conflicto
    escribir(staging, "game/gui.rpy", "GUI v1")                  # igual -> copiar (no pisa?)
    escribir(staging, "game/core/b.rpy", "B v2")                # nuevo -> copiar
    escribir(staging, "README.md", "readme v2")                 # cambia -> copiar
    man_new = manifest_de(staging, "2.0.0")

    # El template nuevo tambien incluye mod_assets vacio (no debe pisar al modder).
    escribir(staging, "game/migracion/manifest.json", "{}")

    plan = planificar(project, staging, man_old, man_new)

    assert "game/core/a.rpy" in plan["copiar"], "a.rpy deberia copiarse"
    assert "game/definitions/def.rpy" in plan["conservar"], "def.rpy editado se conserva"
    assert "game/definitions/def.rpy" in plan["conflictos"], "def.rpy es conflicto"
    assert "game/gui.rpy" in plan["conservar"], "gui.rpy editado se conserva"
    assert "game/gui.rpy" not in plan["conflictos"], "gui.rpy no es conflicto (template igual)"
    assert "game/core/b.rpy" in plan["nuevos"], "b.rpy es nuevo"
    assert "README.md" in plan["copiar"], "README.md se copia"

    backup, n = respaldar(project, plan, "1.0.0", "test")
    assert n >= 3, "deberia respaldar def.rpy, gui.rpy y los agregados"
    assert os.path.isfile(os.path.join(backup, "game", "definitions", "def.rpy")), "backup de def.rpy"

    escribir(staging, "game/migracion/manifest.json", json.dumps(man_new))
    escribir(project, "game/migracion/manifest.json", json.dumps(man_old))
    aplicar(project, staging, plan, man_new)

    # a.rpy actualizado, def.rpy conservado, mod_assets intacto, script.rpy intacto.
    with open(os.path.join(project, "game", "core", "a.rpy")) as f:
        assert f.read() == "A v2", "a.rpy deberia quedar en v2"
    with open(os.path.join(project, "game", "definitions", "def.rpy")) as f:
        assert "MI CAMBIO" in f.read(), "def.rpy deberia conservar la edicion del modder"
    assert os.path.isfile(os.path.join(project, "game", "mod_assets", "images", "bg", "mi_bg.png")), \
        "mod_assets no debe tocarse"
    with open(os.path.join(project, "game", "script.rpy")) as f:
        assert f.read() == "MI HISTORIA", "script.rpy no debe tocarse"
    man_final = _leer_manifest(project)
    assert man_final["template_version"] == "2.0.0", "el manifest debe quedar en 2.0.0"

    shutil.rmtree(tmp, ignore_errors=True)
    print("selftest OK")


def _usage():
    print(__doc__.strip())


def main(argv):
    if "--selftest" in argv:
        selftest()
        return 0
    # Modo manual: --zip <zip> --project <dir> [--version X.Y.Z]
    if "--zip" in argv and "--project" in argv:
        z = argv[argv.index("--zip") + 1]
        p = argv[argv.index("--project") + 1]
        ver = argv[argv.index("--version") + 1] if "--version" in argv else ""
        return 0 if migrar({"project": p, "zip": z, "to_version": ver}) else 1
    # Flujo normal: un job.json.
    jobs = [a for a in argv[1:] if not a.startswith("-")]
    if not jobs:
        _usage()
        return 2
    return 0 if migrar(cargar_job(jobs[0])) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
