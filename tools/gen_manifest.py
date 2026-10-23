#!/usr/bin/env python3
## gen_manifest.py
## Genera game/migracion/manifest.json para una release del template.
##
## El manifest lista el hash sha256 de cada archivo que trae el template. El
## sistema de migración (game/migracion/) lo usa para saber, al comparar el
## manifest viejo con el nuevo, qué archivos tocó el modder y cuáles cambió el
## template. Se corre en el workflow de release (ver .github/workflows/).
##
## Uso:
##   python3 tools/gen_manifest.py <raiz> --version 1.2.0 [--repo owner/repo]
##   python3 tools/gen_manifest.py --selftest

import hashlib
import json
import os
import sys
import tempfile

# Mismas reglas de exclusión que game/migracion/migrar.py.
IGNORAR_EXT = (".rpa", ".rpyc", ".rpyb", ".pyc")
IGNORAR_DIRS = ("saves", "cache", "__pycache__", "backup")
IGNORAR_FILES = ("log.txt", "errors.txt", "traceback.txt",
                 "manifest.json", "reporte.json", ".job.json",
                 ".template.zip", "manual.zip")
IGNORAR_RAIZ = (".git", ".github", ".vscode", "dist", "ZIPs", "tools")

REPO_DEF = "SingerRuv/DDLC-Template"
RUTA_MANIFEST = os.path.join("game", "migracion", "manifest.json")


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def _ignorar(rel):
    rel = rel.replace("\\", "/")
    partes = rel.split("/")
    if partes[0] in IGNORAR_RAIZ:
        return True
    if partes[-1] in IGNORAR_FILES or rel.endswith(IGNORAR_EXT):
        return True
    for d in IGNORAR_DIRS:
        if d in partes:
            return True
    # El propio manifest no se lista a sí mismo.
    if rel == RUTA_MANIFEST.replace("\\", "/"):
        return True
    return False


def _version_de_options(raiz):
    ruta = os.path.join(raiz, "game", "options.rpy")
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            for linea in f:
                if "config.version" in linea and "=" in linea:
                    return linea.split("=", 1)[1].strip().strip('"').strip("'")
    except Exception:
        pass
    return "0.0.0"


def generar(raiz, version, repo):
    files = {}
    raiz_abs = os.path.abspath(raiz)
    for dirpath, dirnames, filenames in os.walk(raiz):
        # IGNORAR_RAIZ solo aplica en la raíz: si se aplicara en todo el árbol,
        # `tools` excluiría también `game/tools/` (el hub de Plugins + PoseLab).
        en_raiz = os.path.abspath(dirpath) == raiz_abs
        dirnames[:] = [d for d in dirnames
                       if d not in IGNORAR_DIRS
                       and not (en_raiz and d in IGNORAR_RAIZ)]
        for nombre in filenames:
            abs_ = os.path.join(dirpath, nombre)
            rel = os.path.relpath(abs_, raiz).replace("\\", "/")
            if _ignorar(rel):
                continue
            files[rel] = _sha256(abs_)
    manifest = {
        "template_version": version,
        "repo": repo,
        "files": dict(sorted(files.items())),
    }
    destino = os.path.join(raiz, RUTA_MANIFEST)
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    with open(destino, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    return destino, len(files)


def selftest():
    tmp = tempfile.mkdtemp(prefix="genman-test-")
    for rel, contenido in (
        ("game/core/a.rpy", "A"),
        ("game/definitions/def.rpy", "DEF"),
        ("README.md", "readme"),
        ("game/saves/save1.save", "x"),      # ignorado
        ("game/migracion/manifest.json", "{}"),  # no se lista
        ("game/tools/plugins/x/tool.json", "{}"),  # SÍ se lista (game/tools)
        ("tools/gen_manifest.py", "x"),      # ignorado (tools de la raíz)
    ):
        p = os.path.join(tmp, rel.replace("/", os.sep))
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            f.write(contenido)

    destino, n = generar(tmp, "1.2.0", "o/r")
    assert os.path.isfile(destino), "debería crear el manifest"
    with open(destino, encoding="utf-8") as f:
        man = json.load(f)
    assert man["template_version"] == "1.2.0", "versión"
    assert man["repo"] == "o/r", "repo"
    assert "game/core/a.rpy" in man["files"], "incluye archivos de game/"
    assert "README.md" in man["files"], "incluye archivos de la raíz"
    assert "game/saves/save1.save" not in man["files"], "ignora saves/"
    assert "game/tools/plugins/x/tool.json" in man["files"], "incluye game/tools"
    assert "tools/gen_manifest.py" not in man["files"], "ignora tools de la raíz"
    assert RUTA_MANIFEST.replace("\\", "/") not in man["files"], "no se lista a sí mismo"
    print("gen_manifest selftest OK")


def main(argv):
    if "--selftest" in argv:
        selftest()
        return 0
    raiz = argv[1] if len(argv) > 1 and not argv[1].startswith("-") else "."
    version = argv[argv.index("--version") + 1] if "--version" in argv else None
    repo = argv[argv.index("--repo") + 1] if "--repo" in argv else REPO_DEF
    if not version:
        version = _version_de_options(raiz)
    destino, n = generar(raiz, version, repo)
    print("manifest: %s (%d archivos, v%s)" % (destino, n, version))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
