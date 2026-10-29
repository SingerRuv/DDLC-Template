#!/usr/bin/env python3
## gen_docs.py
## Genera la referencia de `docs/referencia/` a partir del código del template:
## sprites, transforms, audio, efectos, shaders, text shaders y plugins del hub.
##
## La referencia va commiteada (se distribuye en el release) y el generador es
## dev-only (`/tools/` está en export-ignore), así que se corre a mano:
##
##     python tools/gen_docs.py            # regenera los .md
##     python tools/gen_docs.py --check    # no escribe: falla si hay diferencias
##
## Con `--check` también valida que los enlaces relativos de todos los .md del
## repo apunten a algo que exista. Pensado para el checklist de release.

import argparse
import ast
import io
import json
import os
import re
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SALIDA = "docs/referencia"


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------

def leer(rel):
    with io.open(os.path.join(RAIZ, rel), encoding="utf-8-sig") as f:
        return f.read()


def escribir(rel, texto):
    ruta = os.path.join(RAIZ, rel)
    carpeta = os.path.dirname(ruta)
    if carpeta and not os.path.isdir(carpeta):
        os.makedirs(carpeta)
    with io.open(ruta, "w", encoding="utf-8", newline="\n") as f:
        f.write(texto)


def tabla(cabeceras, filas):
    out = ["| " + " | ".join(cabeceras) + " |"]
    out.append("|" + "|".join("---" for _ in cabeceras) + "|")
    for fila in filas:
        out.append("| " + " | ".join(fila) + " |")
    return "\n".join(out)


def sin_parentesis(texto):
    """Quita solo el paréntesis externo: "(a=(1, 2))" -> "a=(1, 2)"."""
    texto = (texto or "").strip()
    if texto.startswith("(") and texto.endswith(")"):
        return texto[1:-1]
    return texto


def final(texto):
    """Normaliza el resultado: como máximo una línea en blanco entre bloques."""
    return re.sub(r"\n{3,}", "\n\n", texto).strip("\n") + "\n"


def cabecera(titulo, fuente):
    return (
        "# Referencia — %s\n\n"
        "> Generado por `tools/gen_docs.py` desde `%s`.\n"
        "> **No editar a mano**: corré `python tools/gen_docs.py` después de tocar el código.\n"
        % (titulo, fuente)
    )


def orden_natural(nombre):
    """Ordena 't2' antes que 't11'."""
    return [int(p) if p.isdigit() else p for p in re.split(r"(\d+)", nombre)]


def primera_linea_docstring(texto, desde):
    """Primer párrafo del docstring de una def/clase que empieza en `desde`."""
    lineas = texto.splitlines()
    for i in range(desde, min(desde + 6, len(lineas))):
        m = re.match(r'\s*(?:"""|\'\'\')\s*(.+?)\s*(?:"""|\'\'\')?\s*$', lineas[i])
        if m:
            return m.group(1).rstrip('"').rstrip("'").strip()
        if re.match(r'\s*(?:"""|\'\'\')', lineas[i]):
            # Docstring multilínea: unimos las líneas hasta el cierre o un
            # renglón en blanco (el primer párrafo).
            partes = []
            for j in range(i + 1, min(i + 12, len(lineas))):
                t = lineas[j].strip()
                if not t:
                    if partes:
                        break
                    continue
                if t.endswith(('"""', "'''")):
                    t = t.rstrip('"').rstrip("'").strip()
                    if t:
                        partes.append(t)
                    break
                partes.append(t)
            if partes:
                return " ".join(partes)
    return ""


# ---------------------------------------------------------------------------
# Sprites
# ---------------------------------------------------------------------------

NOMBRES_TAG = {
    "sayori": "Sayori",
    "natsuki": "Natsuki",
    "yuri": "Yuri",
    "monika": "Monika",
    "mc": "MC",
}


def _versionados():
    """Rutas versionadas según git, o None si no hay repo (p. ej. en el ZIP)."""
    try:
        salida = subprocess.run(
            ["git", "-C", RAIZ, "ls-files", "-z"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
        if salida.returncode == 0:
            return set(p.replace("\\", "/") for p in salida.stdout.decode("utf-8").split("\0") if p)
    except Exception:
        pass
    return None


def _sprite_publicado(linea, versionados):
    """False si el sprite depende SOLO de assets propios sin commitear.

    Los assets de DDLC viven en los `.rpa` (no están en el repo), así que solo
    se filtran las rutas `mod_assets/…`: el set propio de un modder que no está
    versionado no debe aparecer en la referencia del template.
    """
    if versionados is None:
        return True
    rutas = re.findall(r'"(mod_assets/[^"]+)"', linea)
    return not rutas or any(r in versionados for r in rutas)


def gen_sprites():
    texto = leer("game/definitions/sprites.rpy")
    versionados = _versionados()
    imagenes = []
    for linea in texto.splitlines():
        m = re.match(r"^image\s+(\w+)\s+(\S+)\s*=", linea)
        if m and _sprite_publicado(linea, versionados):
            imagenes.append((m.group(1), m.group(2)))

    por_tag = {}
    for tag, nombre in imagenes:
        por_tag.setdefault(tag, []).append(nombre)

    tags = sorted(
        por_tag,
        key=lambda t: (list(NOMBRES_TAG).index(t) if t in NOMBRES_TAG else 99, t),
    )

    partes = [cabecera("Sprites", "game/definitions/sprites.rpy")]
    partes.append(
        "Total: **%d** variantes en %d personajes.\n" % (len(imagenes), len(tags))
    )
    partes.append(
        "La notación es `<tag> <pose><variante>`. En las poses `b` el sufijo "
        "**no es una expresión**: `1b`, `2b`, … son poses propias (uniforme "
        "casual). Ver la guía [`02-referencia.md`](../02-referencia.md).\n"
    )
    partes.append(
        "Solo se listan los sprites con assets versionados: si agregás assets "
        "propios sin commitear, no aparecen acá.\n"
    )

    resumen = []
    for tag in tags:
        nombres = por_tag[tag]
        mostrar = NOMBRES_TAG.get(tag, tag.capitalize())
        grupos = _agrupar_poses(nombres)
        resumen.append(["`%s`" % tag, mostrar, str(len(nombres)), str(len(grupos))])

    partes.append("## Resumen\n")
    partes.append(tabla(["Tag", "Personaje", "Variantes", "Poses"], resumen))

    for tag in tags:
        nombres = por_tag[tag]
        mostrar = NOMBRES_TAG.get(tag, tag.capitalize())
        grupos = _agrupar_poses(nombres)
        partes.append(
            "\n## %s (`%s`) — %d variantes\n" % (mostrar, tag, len(nombres))
        )
        filas = []
        for pose in sorted(grupos, key=orden_natural):
            variantes = sorted(grupos[pose], key=lambda v: (v != "", orden_natural(v)))
            etiquetas = ["`(base)`" if v == "" else "`%s`" % v for v in variantes]
            filas.append(["`%s`" % pose, ", ".join(etiquetas)])
        partes.append(tabla(["Pose", "Variantes"], filas))

    return {"docs/referencia/sprites.md": final("\n".join(partes))}


def _poses_conocidas(nombres):
    """Poses = nombres base (`1`, `1b`, `12`…) + los dígitos iniciales de todo."""
    candidatas = {n for n in nombres if re.fullmatch(r"\d+b?", n)}
    for n in nombres:
        m = re.match(r"\d+", n)
        if m:
            candidatas.add(m.group(0))
    # Más largas primero: así `1ba` cae en la pose `1b` y no en `1`.
    return sorted(candidatas, key=lambda p: (-len(p), p))


def _agrupar_poses(nombres):
    poses = _poses_conocidas(nombres)
    grupos = {}
    for n in nombres:
        pose = next((p for p in poses if n.startswith(p)), n)
        grupos.setdefault(pose, []).append(n[len(pose):])
    return grupos


# ---------------------------------------------------------------------------
# Transforms y transiciones
# ---------------------------------------------------------------------------

FAMILIAS_TRANSFORMS = [
    ("Base", lambda n: n in ("tcommon", "tinstant", "t_focus")),
    ("Posición (`t##`)", lambda n: re.fullmatch(r"t\d\d", n)),
    ("Focus (`f##`)", lambda n: re.fullmatch(r"f\d\d", n)),
    ("Instantáneo (`i##`)", lambda n: re.fullmatch(r"i\d\d", n)),
    ("Hop (`h##`)", lambda n: re.fullmatch(r"h\d\d", n)),
    ("Hop + focus (`hf##`)", lambda n: re.fullmatch(r"hf\d\d", n)),
    ("Dip (`d##`)", lambda n: re.fullmatch(r"d\d\d?", n)),
    ("Sink (`s##`)", lambda n: re.fullmatch(r"s\d\d", n)),
    ("Entrada desde la izquierda (`l##`)", lambda n: re.fullmatch(r"l\d\d", n)),
    ("Entrada desde la derecha (`r##`)", lambda n: re.fullmatch(r"r\d\d", n)),
    ("Entradas especiales", lambda n: n in ("leftin", "rightin")),
    ("Salidas", lambda n: n in ("lhide", "rhide", "thide")),
    ("Otras animaciones", lambda n: n in ("hop", "hopfocus", "dip", "sink", "musica_slide_in")),
]


def gen_transforms():
    texto = leer("game/definitions/transforms.rpy")

    transforms = []
    for m in re.finditer(r"^transform\s+(\w+)\s*(\([^)]*\))?\s*:", texto, re.M):
        transforms.append((m.group(1), (m.group(2) or "").strip()))
    nombres = [n for n, _ in transforms]

    usados = set()
    filas = []
    for titulo, coincide in FAMILIAS_TRANSFORMS:
        miembros = [n for n in nombres if n not in usados and coincide(n)]
        usados.update(miembros)
        if miembros:
            filas.append(
                [
                    titulo,
                    str(len(miembros)),
                    ", ".join("`%s`" % n for n in sorted(miembros, key=orden_natural)),
                ]
            )
    resto = [n for n in nombres if n not in usados]
    if resto:
        filas.append(
            [
                "Otros",
                str(len(resto)),
                ", ".join("`%s`" % n for n in sorted(resto, key=orden_natural)),
            ]
        )

    base = [(n, p) for n, p in transforms if n in ("tcommon", "tinstant", "t_focus")]

    transiciones = []
    for m in re.finditer(r"^define\s+(\w+)\s*=\s*(.+?)\s*$", texto, re.M):
        valor = m.group(2)
        if valor.startswith("MultipleTransition"):
            valor = "MultipleTransition (compuesta)"
        elif len(valor) > 90:
            valor = valor[:87] + "..."
        transiciones.append(["`%s`" % m.group(1), "`%s`" % valor])

    partes = [cabecera("Transforms y transiciones", "game/definitions/transforms.rpy")]
    partes.append(
        "Se usan con `at`: `show yuri 2b at t22`. Se pueden encadenar "
        "(`at t22, hop`).\n"
    )

    partes.append("## Transforms base\n")
    partes.append(
        tabla(
            ["Transform", "Parámetros"],
            [["`%s`" % n, "`%s`" % (sin_parentesis(p) or "—")] for n, p in base],
        )
    )

    partes.append("\n## Familias\n")
    partes.append(
        "La nomenclatura `##` es `nº de personajes` + `slot`: `t21` es el "
        "primero de dos, `t42` el segundo de cuatro.\n"
    )
    partes.append(tabla(["Familia", "Cantidad", "Nombres"], filas))

    partes.append("\n## Transiciones (`with …`)\n")
    partes.append(tabla(["Nombre", "Definición"], transiciones))

    return {"docs/referencia/transforms.md": final("\n".join(partes))}


# ---------------------------------------------------------------------------
# Audio
# ---------------------------------------------------------------------------

def gen_audio():
    texto = leer("game/definitions/music.rpy")
    musica, efectos = [], []
    patron = re.compile(
        r'^define\s+audio\.(\w+)\s*=\s*"([^"]*)"(?:\s*#\s*(.*))?$', re.M
    )
    for m in patron.finditer(texto):
        nombre, ruta, comentario = m.group(1), m.group(2), (m.group(3) or "").strip()
        fila = ["`audio.%s`" % nombre, "`%s`" % ruta, comentario or "—"]
        (efectos if ruta.startswith("sfx/") else musica).append(fila)

    partes = [
        cabecera("Audio", "game/definitions/music.rpy"),
        "Se usan con `play music audio.t1` / `play sound audio.slap`, o "
        "`$ renpy.music.play(audio.t1)`.\n",
        "\n## Música (`bgm/`)\n",
        tabla(["Nombre", "Archivo", "Descripción"], musica),
        "\n## Efectos de sonido (`sfx/`)\n",
        tabla(["Nombre", "Archivo", "Descripción"], efectos),
    ]
    return {"docs/referencia/audio.md": final("\n".join(partes))}


# ---------------------------------------------------------------------------
# Efectos
# ---------------------------------------------------------------------------

def gen_efectos():
    texto = leer("game/definitions/effects.rpy")
    lineas = texto.splitlines()

    clases = []
    for m in re.finditer(r"^(\s+)class\s+(\w+)\s*(\([^)]*\))?\s*:", texto, re.M):
        nlinea = texto[: m.start()].count("\n")
        doc = primera_linea_docstring(texto, nlinea)
        clases.append(["`%s`" % m.group(2), doc or "—"])

    screens = []
    for m in re.finditer(r"^screen\s+(\w+)\s*(\([^)]*\))?\s*:", texto, re.M):
        screens.append(
            ["`%s`" % m.group(1), "`%s`" % (sin_parentesis(m.group(2)) or "—")]
        )

    animaciones = []
    for m in re.finditer(r"^transform\s+(\w+)\s*(\([^)]*\))?\s*:", texto, re.M):
        nlinea = texto[: m.start()].count("\n")
        doc = ""
        for j in range(nlinea - 1, max(nlinea - 4, -1), -1):
            t = lineas[j].strip()
            if t.startswith("#"):
                doc = t.lstrip("# ").strip()
                break
            if t:
                break
        animaciones.append(
            ["`%s`" % m.group(1), "`%s`" % (sin_parentesis(m.group(2)) or "—"), doc or "—"]
        )

    funciones = []
    for m in re.finditer(r"^\s{4}def\s+(\w+)\s*(\([^)]*\))\s*:", texto, re.M):
        nlinea = texto[: m.start()].count("\n")
        doc = primera_linea_docstring(texto, nlinea)
        funciones.append(["`%s()`" % m.group(1), doc or "—"])

    partes = [
        cabecera("Efectos", "game/definitions/effects.rpy"),
        "Los efectos se invocan desde el guion: `show screen invert(0.5)` o "
        "`show screen tear(10)`; las animaciones, con `at`.\n",
        "\n## Displayables\n",
        tabla(["Clase", "Qué hace"], clases),
        "\n## Screens\n",
        tabla(["Screen", "Parámetros"], screens),
        "\n## Animaciones\n",
        tabla(["Transform", "Parámetros", "Qué hace"], animaciones),
        "\n## Funciones auxiliares\n",
        tabla(["Función", "Qué hace"], funciones),
    ]
    return {"docs/referencia/efectos.md": final("\n".join(partes))}


# ---------------------------------------------------------------------------
# Shaders
# ---------------------------------------------------------------------------

# Parámetros con paréntesis anidados (`color=(1.0, 1.0, 1.0, 1.0)`).
RE_TRANSFORM_CON_PARAMS = r"^transform\s+(\w+)\s*((?:\((?:[^()]|\([^()]*\))*\))?)\s*:"


def gen_shaders():
    rel = "game/tools/plugins/shaders_lab/shaders_lab_data.rpy"
    texto = leer(rel)

    # Solo las llamadas reales (indentadas en `init python`), no los ejemplos
    # de los comentarios (`##   1. renpy.register_shader(...)`).
    registrados = re.findall(r'^\s+renpy\.register_shader\("([\w.]+)"', texto, re.M)

    transforms = []
    for m in re.finditer(RE_TRANSFORM_CON_PARAMS, texto, re.M):
        nombre = m.group(1)
        params = sin_parentesis(m.group(2))
        bloque = texto[m.end():]
        siguiente = re.search(r"^transform\s", bloque, re.M)
        bloque = bloque[: siguiente.start()] if siguiente else bloque
        usados = re.findall(r'shader\s+"([\w.]+)"', bloque)
        uniforms = re.findall(r"^\s{4}(u_\w+)\s+(.+?)\s*$", bloque, re.M)
        transforms.append(
            [
                "`%s`" % nombre,
                "`%s`" % params if params else "—",
                ", ".join("`%s`" % s for s in usados) or "—",
                ", ".join("`%s`" % u for u, _ in uniforms) or "—",
            ]
        )

    listas = []
    for m in re.finditer(r"^\s{4}(_SHL_\w+)\s*=\s*\[(.*?)\]", texto, re.S | re.M):
        valores = re.findall(r'"([^"]*)"', m.group(2))
        listas.append(["`%s`" % m.group(1), ", ".join(valores)])

    combinar = ""
    m = re.search(r"^\s{4}def\s+sh_combinar\s*\((.*?)\):", texto, re.M)
    if m:
        doc = primera_linea_docstring(texto, texto[: m.start()].count("\n"))
        combinar = "`sh_combinar(%s)` — %s" % (m.group(1), doc or "")

    partes = [
        cabecera("Shaders", rel),
        "\n## Transforms listos (`sh_*`)\n",
        tabla(["Transform", "Parámetros", "Shader", "Uniforms"], transforms),
        "\n## Shaders registrados\n",
        ", ".join("`%s`" % s for s in registrados),
        "\n\n## Combinar\n",
        combinar or "—",
        "\n\n## Listas de la demo\n",
        tabla(["Lista", "Valores"], listas),
    ]
    return {"docs/referencia/shaders.md": final("\n".join(partes))}


# ---------------------------------------------------------------------------
# Text shaders
# ---------------------------------------------------------------------------

def gen_textshaders():
    rel = "game/definitions/textshaders.rpy"
    texto = leer(rel)

    filas = []
    for m in re.finditer(r'renpy\.register_textshader\(\s*"(\w+)"', texto):
        bloque = texto[m.end():]
        fin = re.search(r"\n\s*\)", bloque)
        bloque = bloque[: fin.start()] if fin else bloque

        uniforms = []
        for nombre in re.findall(r"uniform\s+\w+\s+(u__\w+)\s*;", bloque):
            default = re.search(r"\b%s\s*=\s*([^,\n]+)" % re.escape(nombre), bloque)
            if default:
                valor = default.group(1).strip().rstrip(")").strip()
                uniforms.append("`%s` = `%s`" % (nombre, valor))
            else:
                uniforms.append("`%s`" % nombre)

        doc = ""
        md = re.search(r'doc\s*=\s*"""(.*?)"""', bloque, re.S)
        if md:
            lineas = [l.strip() for l in md.group(1).strip().splitlines() if l.strip()]
            doc = " ".join(lineas[:2])

        filas.append(["`%s`" % m.group(1), ", ".join(uniforms) or "—", doc or "—"])

    partes = [
        cabecera("Text shaders", rel),
        "Text shaders propios del template. Los que trae Ren'Py (dissolve, flip, "
        "jitter, linetexture, offset, slowalpha, texture, typewriter, wave, zoom) "
        "se usan igual y están explicados en la guía "
        "[`02-referencia.md`](../02-referencia.md).\n",
        tabla(["Text shader", "Uniforms", "Qué hace"], filas),
    ]
    return {"docs/referencia/textshaders.md": final("\n".join(partes))}


# ---------------------------------------------------------------------------
# Diálogo (plugin)
# ---------------------------------------------------------------------------

def gen_dialogo():
    rel = "game/tools/plugins/dialogo_lab/dialogo_doc.py"
    datos = None
    for nodo in ast.parse(leer(rel)).body:
        if not isinstance(nodo, ast.Assign):
            continue
        for destino in nodo.targets:
            if isinstance(destino, ast.Name) and destino.id == "DIALOGO_DOC":
                datos = ast.literal_eval(nodo.value)
    if datos is None:
        raise RuntimeError("No se encontró DIALOGO_DOC en %s" % rel)

    partes = [
        cabecera("Estilo de diálogo (Diálogo)", rel),
        "Plugin **Diálogo** (`game/tools/plugins/dialogo_lab/`). Arma líneas de "
        "diálogo con énfasis (negrita, itálica, subrayado, tachado, color y "
        "tamaño) sobre la frase que marques, y deja la línea lista para copiar o "
        "insertar en el guion.\n\nNo hay motor: el efecto se aplica con los tags "
        "de Ren'Py, que son markup nativo. Ver "
        "[`03-herramientas.md`](../03-herramientas.md).\n",
        "## Efectos\n",
        tabla(["Efecto", "Qué hace", "Tag", "Default"], datos["efectos"]),
        "\n## Campos\n",
        tabla(["Campo", "Qué hace"], datos["campos"]),
        "\n## Tags de Ren'Py\n",
        tabla(["Tag", "Qué hace"], datos["tags"]),
    ]
    return {"docs/referencia/dialogo.md": final("\n".join(partes))}


# ---------------------------------------------------------------------------
# Plugins del hub
# ---------------------------------------------------------------------------

def gen_plugins():
    base = os.path.join(RAIZ, "game", "tools", "plugins")
    filas = []
    for nombre in sorted(os.listdir(base)):
        ruta = os.path.join(base, nombre)
        tool = os.path.join(ruta, "tool.json")
        if not os.path.isdir(ruta) or not os.path.isfile(tool):
            continue
        try:
            with io.open(tool, encoding="utf-8-sig") as f:
                datos = json.load(f)
        except Exception:
            filas.append(["`%s`" % nombre, "—", "—", "**tool.json inválido**"])
            continue
        autor = datos.get("autor") or "—"
        version = datos.get("version")
        autor = "%s%s" % (autor, (" v%s" % version) if version else "")
        desc = datos.get("descripcion") or "—"
        if nombre.startswith("_"):
            desc += " _(ejemplo)_"
        filas.append(
            [
                "`%s`" % (datos.get("id") or nombre),
                datos.get("titulo") or nombre,
                datos.get("categoria") or "General",
                "%s — %s" % (autor, desc),
            ]
        )

    texto = leer("game/tools/complements_data.rpy")
    m = re.search(r'tools_api_version\s*=\s*"([^"]+)"', texto)
    api = m.group(1) if m else "—"

    partes = [
        cabecera("Plugins del hub", "game/tools/plugins/*/tool.json"),
        "API de plugins: **%s** (`tools_api_version` en "
        "`game/tools/complements_data.rpy`).\n" % api,
        tabla(["ID", "Título", "Categoría", "Autor / descripción"], filas),
    ]
    return {"docs/referencia/plugins.md": final("\n".join(partes))}


# ---------------------------------------------------------------------------
# Verificación
# ---------------------------------------------------------------------------

RE_ENLACE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")


def validar_enlaces():
    """Devuelve [(archivo, linea, destino)] con enlaces relativos rotos."""
    rotos = []
    for dirpath, dirnames, filenames in os.walk(RAIZ):
        dirnames[:] = [
            d for d in dirnames if d not in (".git", "cache", "saves", "__pycache__", "lib")
        ]
        for nombre in filenames:
            if not nombre.endswith(".md"):
                continue
            ruta = os.path.join(dirpath, nombre)
            rel = os.path.relpath(ruta, RAIZ).replace("\\", "/")
            with io.open(ruta, encoding="utf-8-sig") as f:
                for i, linea in enumerate(f, 1):
                    for destino in RE_ENLACE.findall(linea):
                        if re.match(r"(?:https?:|mailto:|#)", destino):
                            continue
                        objetivo = destino.split("#")[0].split("?")[0]
                        if not objetivo:
                            continue
                        abs_ = os.path.normpath(os.path.join(dirpath, objetivo))
                        if not os.path.exists(abs_):
                            rotos.append((rel, i, destino))
    return rotos


def main(argv):
    parser = argparse.ArgumentParser(
        description="Genera docs/referencia/ y valida enlaces de la documentación."
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="no escribe: falla si la referencia está desactualizada o hay enlaces rotos",
    )
    args = parser.parse_args(argv)

    # (generador, fuentes que tienen que existir). Si falta alguna fuente, la
    # sección no se documenta: así la misma herramienta sirve en `dev` y en
    # `main` (donde el plugin Shaders Lab todavía no vive).
    generadores = (
        (gen_sprites, []),
        (gen_transforms, []),
        (gen_audio, []),
        (gen_efectos, []),
        (gen_shaders, ["game/tools/plugins/shaders_lab/shaders_lab_data.rpy"]),
        (gen_textshaders, ["game/definitions/textshaders.rpy"]),
        (gen_dialogo, ["game/tools/plugins/dialogo_lab/dialogo_doc.py"]),
        (gen_plugins, []),
    )

    generados = {}
    for generador, fuentes in generadores:
        if any(not os.path.isfile(os.path.join(RAIZ, f)) for f in fuentes):
            continue
        generados.update(generador())

    problemas = 0

    # Referencia generada que ya no corresponde (por ejemplo, un plugin que no
    # está en esta rama): se borra al regenerar y se reporta con --check.
    carpeta = os.path.join(RAIZ, SALIDA)
    sobrantes = []
    if os.path.isdir(carpeta):
        for nombre in sorted(os.listdir(carpeta)):
            if not nombre.endswith(".md"):
                continue
            rel = "%s/%s" % (SALIDA, nombre)
            if rel in generados:
                continue
            with io.open(os.path.join(carpeta, nombre), encoding="utf-8-sig") as f:
                if "Generado por `tools/gen_docs.py`" not in f.read(300):
                    continue  # escrito a mano: no se toca
            sobrantes.append(rel)

    for rel in sobrantes:
        if args.check:
            print("sobra      %s" % rel)
            problemas += 1
        else:
            os.remove(os.path.join(RAIZ, rel))
            print("borrado    %s" % rel)

    for rel, texto in generados.items():
        ruta = os.path.join(RAIZ, rel)
        actual = ""
        if os.path.isfile(ruta):
            with io.open(ruta, encoding="utf-8-sig") as f:
                actual = f.read()
        if actual == texto:
            print("ok        %s" % rel)
            continue
        if args.check:
            print("desactualizado %s" % rel)
            problemas += 1
        else:
            escribir(rel, texto)
            print("escrito   %s" % rel)

    rotos = validar_enlaces()
    for rel, linea, destino in rotos:
        print("enlace roto %s:%d -> %s" % (rel, linea, destino))
    problemas += len(rotos)

    if problemas:
        print("\n%d problema(s)." % problemas)
        return 1
    print("\nDocumentación al día.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
