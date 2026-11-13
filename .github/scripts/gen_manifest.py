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
##   python3 .github/scripts/gen_manifest.py <raiz> --version 1.2.0 [--repo owner/repo]
##   python3 .github/scripts/gen_manifest.py --selftest

import hashlib
import json
import os
import subprocess
import sys
import tempfile

# Mismas reglas de exclusión que game/migracion/migrar.py.
IGNORAR_EXT = (".rpa", ".rpyc", ".rpyb", ".pyc", ".log", ".tmp")
IGNORAR_DIRS = ("saves", "cache", "__pycache__", "backup")
IGNORAR_FILES = ("log.txt", "errors.txt", "traceback.txt",
                 "manifest.json", "reporte.json", ".job.json",
                 ".template.zip", "manual.zip")
IGNORAR_RAIZ = (".git", ".github", ".vscode", ".idea", ".vs", "dist", "ZIPs",
                "tools", "migracion_backup", "plugin_backups")

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


def _recorrer(raiz):
    """Recorre el árbol y devuelve rutas relativas (modo sin git)."""
    rels = []
    raiz_abs = os.path.abspath(raiz)
    for dirpath, dirnames, filenames in os.walk(raiz):
        # IGNORAR_RAIZ solo aplica en la raíz: si se aplicara en todo el árbol,
        # `tools` excluiría también `game/plugins/` (el hub de Plugins + PoseLab).
        en_raiz = os.path.abspath(dirpath) == raiz_abs
        dirnames[:] = [d for d in dirnames
                       if d not in IGNORAR_DIRS
                       and not (en_raiz and d in IGNORAR_RAIZ)]
        for nombre in filenames:
            rels.append(os.path.relpath(os.path.join(dirpath, nombre), raiz).replace("\\", "/"))
    return rels


def _rels_git(raiz):
    """Archivos versionados según git (excluye lo gitignored). None si falla."""
    try:
        res = subprocess.run(["git", "-C", raiz, "ls-files", "-z"],
                             capture_output=True, check=True)
    except Exception:
        return None
    salida = res.stdout.decode("utf-8", "surrogateescape")
    return [r for r in salida.split("\0") if r]


def _export_ignorados(raiz):
    """Patrones con export-ignore en .gitattributes (lo que no va en el ZIP)."""
    patrones = []
    try:
        with open(os.path.join(raiz, ".gitattributes"), "r", encoding="utf-8") as f:
            for linea in f:
                linea = linea.split("#", 1)[0].strip()
                if not linea or "export-ignore" not in linea:
                    continue
                patron = linea.split()[0].strip("/")
                if patron:
                    patrones.append(patron)
    except Exception:
        pass
    return patrones


def _export_ignorado(rel, patrones):
    rel = rel.replace("\\", "/")
    for p in patrones:
        if rel == p or rel.startswith(p + "/"):
            return True
    return False


def generar(raiz, version, repo):
    files = {}
    raiz_abs = os.path.abspath(raiz)

    # Con .git/ se listan los archivos versionados (git ls-files), así el
    # manifest coincide con lo que arma `git archive` en el release. Sin git
    # (p. ej. el árbol ya extraído en CI) se recorre el directorio.
    rels = None
    if os.path.isdir(os.path.join(raiz_abs, ".git")):
        rels = _rels_git(raiz_abs)
    if rels is None:
        rels = _recorrer(raiz_abs)

    exportados = _export_ignorados(raiz_abs)
    for rel in rels:
        if _ignorar(rel) or _export_ignorado(rel, exportados):
            continue
        files[rel] = _sha256(os.path.join(raiz_abs, rel))
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
        ("game/plugins/x/tool.json", "{}"),  # SÍ se lista (game/plugins)
        ("tools/gen_manifest.py", "x"),      # ignorado (tools de la raíz)
        (".gitattributes",
         ".gitattributes export-ignore\nCHANGELOG.md export-ignore\ndocs/ export-ignore\n"),
        ("CHANGELOG.md", "no va en el ZIP"),   # export-ignore
        ("docs/guia.md", "no va en el ZIP"),   # export-ignore (carpeta)
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
    assert "game/plugins/x/tool.json" in man["files"], "incluye game/plugins"
    assert "tools/gen_manifest.py" not in man["files"], "ignora tools de la raíz"
    assert "CHANGELOG.md" not in man["files"], "respeta export-ignore (archivo)"
    assert "docs/guia.md" not in man["files"], "respeta export-ignore (carpeta)"
    assert ".gitattributes" not in man["files"], "respeta export-ignore (él mismo)"
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
