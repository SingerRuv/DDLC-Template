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
##   python migrar.py --zip <zip> --project <dir> [--dry-run]   # modo manual

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
    "game/migracion/migracion.log",
)

RUTA_MANIFEST = os.path.join("game", "migracion", "manifest.json")
RUTA_REPORTE = os.path.join("game", "migracion", "reporte.json")
RUTA_LOG = os.path.join("game", "migracion", "migracion.log")

# Tope de tamano descomprimido del ZIP del template (defensa ante zip-bombs).
LIMITE_ZIP = 500 * 1024 * 1024


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


_DRY = [False]  # en --dry-run no se escribe nada en el proyecto, ni el log


def _log(project, mensaje):
    """Registra un paso en game/migracion/migracion.log (el juego no tiene consola)."""
    if _DRY[0]:
        return
    try:
        ruta = os.path.join(project, RUTA_LOG.replace("/", os.sep))
        os.makedirs(os.path.dirname(ruta), exist_ok=True)
        with open(ruta, "a", encoding="utf-8", newline="\n") as f:
            f.write("%s %s\n" % (time.strftime("%Y-%m-%d %H:%M:%S"), mensaje))
    except Exception:
        pass


def _ver(txt):
    """(1, 2, 0) a partir de '1.2' / 'v1.2.0'. None si no se puede."""
    try:
        partes = str(txt).strip().lstrip("vV").split(".")
        nums = [int(p) for p in partes[:3]]
        while len(nums) < 3:
            nums.append(0)
        return tuple(nums)
    except Exception:
        return None


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

def planificar(project, man_old, man_new):
    """Calcula que hacer con cada archivo.

    Devuelve un dict con:
      copiar    -> archivos del template nuevo a copiar (sobreescribir/crear)
      conservar -> {rel: motivo} archivos del modder que se dejan como estan
      conflictos-> sublista de conservar donde tambien cambio el template
      nuevos    -> archivos que trae el template nuevo y no existian
      borrados  -> archivos que el template viejo tenia y el nuevo ya no
      agregados -> archivos que el modder agrego (para respaldar)
      ausentes  -> archivos del template viejo que el modder borro
    """
    viejos = man_old.get("files", {})
    nuevos = man_new.get("files", {})

    copiar = []
    conservar = {}
    conflictos = []
    nuevos_files = []
    borrados = []
    agregados = []
    ausentes = set()

    # 1) Archivos del template: ¿los toco el modder? ¿los cambio el template?
    for rel, hash_viejo in viejos.items():
        abs_ = os.path.join(project, rel)
        if not os.path.isfile(abs_):
            ausentes.add(rel)  # lo borro el modder: no se vuelve a crear
            continue
        if _sha256(abs_) != hash_viejo:
            conservar[rel] = "editado por el modder"
            if rel in nuevos and nuevos[rel] != hash_viejo:
                conflictos.append(rel)

    # 2) Archivos que agrega el template nuevo.
    for rel in nuevos:
        if rel not in viejos:
            nuevos_files.append(rel)

    # 3) Archivos que el template nuevo ya no trae (se dejan, solo se reportan).
    for rel in viejos:
        if rel not in nuevos:
            borrados.append(rel)

    # 4) Archivos que agrego el modder (incluye colisiones con el template nuevo).
    for rel in _listar(project, "game"):
        if rel in viejos or rel in ARCHIVOS_SISTEMA or rel.endswith(IGNORAR_EXT):
            continue
        if rel in nuevos:
            if rel.startswith("game/tools/"):
                # Bug de las releases <=1.2.2: el manifest no listaba game/tools,
                # así que estos archivos del template parecían "del modder". Se
                # respaldan y se reemplazan por los del template nuevo.
                agregados.append(rel)
                continue
            conservar[rel] = "agregado por el modder (colisiona con el template)"
            conflictos.append(rel)
        else:
            agregados.append(rel)

    # 5) A copiar: todo el template nuevo menos lo que se conserva del modder y
    #    lo que el modder habia borrado.
    for rel in nuevos:
        if rel in ausentes or rel in conservar:
            continue
        copiar.append(rel)

    return {
        "copiar": sorted(copiar),
        "conservar": conservar,
        "conflictos": sorted(conflictos),
        "nuevos": sorted(nuevos_files),
        "borrados": sorted(borrados),
        "agregados": sorted(agregados),
        "ausentes": sorted(ausentes),
    }


def respaldar(project, plan, desde, cuando):
    """Copia SOLO los archivos del modder a migracion_backup/<desde>-<cuando>/.

    Va en la RAÍZ del proyecto (hermano de game/), nunca dentro de game/, para
    que Ren'Py no escanee los .rpy respaldados (darían labels duplicados).
    Incluye los que editó (conservar) y los que agregó (agregados)."""
    destino = os.path.join(project, "migracion_backup",
                           "%s-%s" % (desde or "0.0.0", cuando))
    rels = set(plan["conservar"].keys()) | set(plan.get("agregados", []))
    copiados = 0
    for rel in sorted(rels):
        origen = os.path.join(project, rel.replace("/", os.sep))
        if not os.path.isfile(origen):
            continue
        dst = os.path.join(destino, rel.replace("/", os.sep))
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(origen, dst)
        copiados += 1
    return destino, copiados


def _dir_previos(backup):
    return os.path.join(backup, "_previos")


def respaldar_previos(project, plan, backup):
    """Copia el estado actual de los archivos que se van a sobrescribir.

    Es la red de seguridad para poder revertir si `aplicar()` falla a mitad.
    Se borra al terminar bien."""
    base = _dir_previos(backup)
    rels = list(plan["copiar"])
    if os.path.isfile(os.path.join(project, RUTA_MANIFEST.replace("/", os.sep))):
        rels.append(_norm(RUTA_MANIFEST))
    copiados = 0
    for rel in rels:
        origen = os.path.join(project, rel.replace("/", os.sep))
        if not os.path.isfile(origen):
            continue
        dst = os.path.join(base, rel.replace("/", os.sep))
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(origen, dst)
        copiados += 1
    return copiados


def restaurar_previos(project, backup):
    """Devuelve el proyecto al estado previo a la migración. Devuelve cuántos."""
    base = _dir_previos(backup)
    if not os.path.isdir(base):
        return 0
    restaurados = 0
    for dirpath, _dirnames, filenames in os.walk(base):
        for nombre in filenames:
            abs_ = os.path.join(dirpath, nombre)
            rel = _norm(os.path.relpath(abs_, base))
            dst = os.path.join(project, rel.replace("/", os.sep))
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            tmp = dst + ".tmp"
            shutil.copy2(abs_, tmp)
            os.replace(tmp, dst)
            restaurados += 1
    return restaurados


def _escribir_atomico(origen_abs, dst_abs):
    """Copia a un temporal y reemplaza, para no dejar archivos a medias."""
    os.makedirs(os.path.dirname(dst_abs), exist_ok=True)
    tmp = dst_abs + ".tmp"
    shutil.copy2(origen_abs, tmp)
    os.replace(tmp, dst_abs)


def aplicar(project, staging, plan, man_new):
    """Copia el template nuevo (atómico por archivo) y deja el manifest."""
    escritos = 0
    for rel in plan["copiar"]:
        origen = os.path.join(staging, rel.replace("/", os.sep))
        dst = os.path.join(project, rel.replace("/", os.sep))
        if not os.path.isfile(origen):
            continue
        _escribir_atomico(origen, dst)
        escritos += 1
        # Borra el bytecode viejo: si el .rpyc sobrevive, Ren'Py puede seguir
        # ejecutando el código anterior aunque el .rpy ya esté actualizado.
        if rel.endswith(".rpy"):
            for sufijo in (".rpyc", ".rpyb"):
                try:
                    if os.path.isfile(dst + sufijo):
                        os.remove(dst + sufijo)
                except Exception:
                    pass
    # El manifest nuevo se instala siempre (es la fuente de verdad de la version).
    origen_man = os.path.join(staging, RUTA_MANIFEST.replace("/", os.sep))
    if os.path.isfile(origen_man):
        _escribir_atomico(origen_man,
                          os.path.join(project, RUTA_MANIFEST.replace("/", os.sep)))
    return escritos


def _imprimir_plan(plan, desde, hasta):
    print("Migracion %s -> %s" % (desde or "?", hasta or "?"))
    for clave in ("copiar", "conservar", "conflictos", "nuevos", "borrados",
                  "agregados", "ausentes"):
        valor = plan.get(clave)
        print("%-11s %d" % (clave + ":", len(valor or [])))
    for rel in plan["copiar"]:
        print("  + %s" % rel)


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
    """True si el PID exacto sigue vivo (evita falsos positivos tipo 123/1234)."""
    try:
        if os.name == "nt":
            out = subprocess.run(
                ["tasklist", "/FI", "PID eq %d" % pid, "/FO", "CSV", "/NH"],
                capture_output=True, text=True).stdout or ""
            primera = out.strip().splitlines()[0] if out.strip() else ""
            if not primera.startswith('"'):
                return False
            campos = primera.split('","')
            return len(campos) > 1 and campos[1].strip('"').strip() == str(pid)
        os.kill(pid, 0)
        return True
    except Exception:
        return False


def esperar_cierre(pid, timeout=300):
    """Espera a que el proceso del juego termine. True si ya no corre."""
    if not pid:
        return True
    fin = time.time() + timeout
    time.sleep(0.5)
    while time.time() < fin:
        if not _proceso_vivo(pid):
            return True
        time.sleep(0.5)
    return not _proceso_vivo(pid)


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
    """Valida y extrae el ZIP. Devuelve la carpeta que contiene `game/`."""
    if not zipfile.is_zipfile(zip_path):
        raise RuntimeError("el archivo no es un ZIP valido: %s" % zip_path)
    with zipfile.ZipFile(zip_path) as z:
        total = 0
        for info in z.infolist():
            nombre = _norm(info.filename)
            if nombre.startswith("/") or ".." in nombre.split("/"):
                raise RuntimeError("el ZIP contiene una ruta no permitida: %s"
                                   % info.filename)
            if ((info.external_attr >> 16) & 0o170000) == 0o120000:
                raise RuntimeError("el ZIP contiene un enlace simbolico: %s"
                                   % info.filename)
            total += info.file_size
            if total > LIMITE_ZIP:
                raise RuntimeError("el ZIP supera el limite de %d MB"
                                   % (LIMITE_ZIP // (1024 * 1024)))
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

def migrar(job, dry_run=False):
    project = job["project"]
    tmp = tempfile.mkdtemp(prefix="bdmigrar-")
    desde = job.get("from_version")
    hasta = job.get("to_version")
    plan = None
    backup = None
    _DRY[0] = dry_run
    try:
        man_old = _leer_manifest(project)
        if man_old is None:
            _log(project, "sin manifest: no se puede migrar")
            escribir_reporte(project, desde, job.get("to_version"), None, None, 0,
                             ok=False,
                             error="El proyecto no tiene manifest; no se puede migrar.")
            return False
        desde = man_old.get("template_version") or desde

        # 1) Esperar a que el juego cierre; si sigue vivo, no se toca nada.
        if not esperar_cierre(job.get("pid")):
            raise RuntimeError("el juego no se cerro a tiempo; no se modifico nada")

        # 2) Obtener y validar el ZIP del template nuevo.
        zip_path = job.get("zip")
        if not zip_path:
            url = job.get("download_url")
            if not url:
                raise RuntimeError("la actualizacion no trae ZIP ni URL de descarga")
            zip_path = os.path.join(tmp, "template.zip")
            _log(project, "descargando %s" % url)
            descargar(url, zip_path)
        if not os.path.isfile(zip_path):
            raise RuntimeError("no se encontro el ZIP: %s" % zip_path)
        staging = extraer(zip_path, os.path.join(tmp, "x"))

        man_new = _leer_manifest(staging)
        if man_new is None:
            raise RuntimeError("el template nuevo no trae manifest")
        hasta = man_new.get("template_version") or job.get("to_version")
        v_new, v_old = _ver(hasta), _ver(desde)
        if v_new and v_old and v_new < v_old:
            raise RuntimeError("el ZIP es mas viejo (%s) que el instalado (%s)"
                               % (hasta, desde))

        # 3) Planificar.
        plan = planificar(project, man_old, man_new)
        _log(project, "plan: %d copiar, %d conservar, %d conflictos, %d ausentes"
             % (len(plan["copiar"]), len(plan["conservar"]),
                len(plan["conflictos"]), len(plan["ausentes"])))

        if dry_run:
            _imprimir_plan(plan, desde, hasta)
            return True

        # 4) Respaldar (modder + estado previo) y aplicar.
        cuando = time.strftime("%Y%m%d-%H%M%S")
        backup, _n = respaldar(project, plan, desde, cuando)
        respaldar_previos(project, plan, backup)
        escritos = aplicar(project, staging, plan, man_new)

        escribir_reporte(project, desde, hasta, plan, backup, escritos)
        shutil.rmtree(_dir_previos(backup), ignore_errors=True)
        _log(project, "migracion OK: %d archivos" % escritos)
        return True
    except Exception as e:
        _log(project, "ERROR: %s" % e)
        if backup:
            n = restaurar_previos(project, backup)
            _log(project, "rollback: %d archivos restaurados" % n)
        escribir_reporte(project, desde, hasta, plan, backup, 0,
                         ok=False, error=str(e))
        return False
    finally:
        _DRY[0] = False
        shutil.rmtree(tmp, ignore_errors=True)
        if not dry_run:
            relanzar(job)


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
    escribir(project, "game/core/borrado.rpy", "BORRADO v1")  # el modder lo borra
    escribir(project, "game/migracion/manifest.json", "{}")  # se regenera abajo
    man_old = manifest_de(project, "1.0.0")
    os.remove(os.path.join(project, "game", "core", "borrado.rpy"))

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
    escribir(staging, "game/core/borrado.rpy", "BORRADO v2")    # el modder lo borro: no vuelve
    escribir(staging, "README.md", "readme v2")                 # cambia -> copiar
    man_new = manifest_de(staging, "2.0.0")

    # El template nuevo tambien incluye mod_assets vacio (no debe pisar al modder).
    escribir(staging, "game/migracion/manifest.json", "{}")

    plan = planificar(project, man_old, man_new)

    assert "game/core/a.rpy" in plan["copiar"], "a.rpy deberia copiarse"
    assert "game/definitions/def.rpy" in plan["conservar"], "def.rpy editado se conserva"
    assert "game/definitions/def.rpy" in plan["conflictos"], "def.rpy es conflicto"
    assert "game/gui.rpy" in plan["conservar"], "gui.rpy editado se conserva"
    assert "game/gui.rpy" not in plan["conflictos"], "gui.rpy no es conflicto (template igual)"
    assert "game/core/b.rpy" in plan["nuevos"], "b.rpy es nuevo"
    assert "README.md" in plan["copiar"], "README.md se copia"
    assert "game/core/borrado.rpy" in plan["ausentes"], "borrado.rpy figura como ausente"
    assert "game/core/borrado.rpy" not in plan["copiar"], "no se re-crea un archivo borrado"

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
    assert not os.path.isfile(os.path.join(project, "game", "core", "borrado.rpy")), \
        "el archivo borrado por el modder no debe reaparecer"
    man_final = _leer_manifest(project)
    assert man_final["template_version"] == "2.0.0", "el manifest debe quedar en 2.0.0"

    # --- Rollback: restaurar _previos devuelve el estado anterior ---
    backup2 = os.path.join(tmp, "backup2")
    os.makedirs(backup2)
    respaldar_previos(project, {"copiar": ["game/core/a.rpy"]}, backup2)
    escribir(project, "game/core/a.rpy", "A ROTO")
    assert restaurar_previos(project, backup2) >= 1, "deberia restaurar al menos un archivo"
    with open(os.path.join(project, "game", "core", "a.rpy")) as f:
        assert f.read() == "A v2", "el rollback debe devolver el contenido previo"

    # --- ZIP con ruta no permitida se rechaza ---
    malo = os.path.join(tmp, "malo.zip")
    with zipfile.ZipFile(malo, "w") as z:
        z.writestr("../evil.txt", "x")
    try:
        extraer(malo, os.path.join(tmp, "x2"))
        raise AssertionError("deberia rechazar rutas con ..")
    except RuntimeError:
        pass

    shutil.rmtree(tmp, ignore_errors=True)
    print("selftest OK")


def _usage():
    print(__doc__.strip())


def main(argv):
    if "--selftest" in argv:
        selftest()
        return 0
    dry = "--dry-run" in argv
    # Modo manual: --zip <zip> --project <dir> [--version X.Y.Z]
    if "--zip" in argv and "--project" in argv:
        z = argv[argv.index("--zip") + 1]
        p = argv[argv.index("--project") + 1]
        ver = argv[argv.index("--version") + 1] if "--version" in argv else ""
        return 0 if migrar({"project": p, "zip": z, "to_version": ver}, dry_run=dry) else 1
    # Flujo normal: un job.json.
    jobs = [a for a in argv[1:] if not a.startswith("-")]
    if not jobs:
        _usage()
        return 2
    return 0 if migrar(cargar_job(jobs[0]), dry_run=dry) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
