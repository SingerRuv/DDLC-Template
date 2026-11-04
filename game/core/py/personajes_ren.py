# personajes_ren.py
# Personajes en disco (.chr): restaurar y borrar archivos de `characters/`.
#
# La mecánica de DDLC de borrar a un personaje de la carpeta. El template NO
# incluye los .chr de DDLC (son datos oficiales): el modder los copia desde su
# instalación a `characters/` y, si quiere poder restaurarlos, a `game/chrs/`.
# Ver docs/01-historia.md.

import os

import renpy  # type: ignore

"""renpy
init -3 python:
"""


def get_characters_folder():
    """Carpeta `characters/` del proyecto, o None si no se puede saber."""
    if renpy.android:
        try:
            import jnius  # type: ignore
            activity = jnius.autoclass(
                "org.renpy.android.PythonSDLActivity")
            current = jnius.cast("android.app.Activity", activity.mActivity)
            base = current.getFilesDir().getAbsolutePath()
        except Exception:
            return None
        return os.path.join(base, "characters")
    return os.path.join(renpy.config.basedir, "characters").replace("\\", "/")


def restore_character(names):
    """Restaura los .chr que falten en `characters/` desde `game/chrs/`.

    No borra otros .chr que haya en la carpeta (a diferencia del template de
    Bronya): acá solo se recupera lo que falta."""
    folder = get_characters_folder()
    if not folder:
        return
    try:
        os.makedirs(folder, exist_ok=True)
    except OSError:
        return

    for name in names:
        destino = os.path.join(folder, "%s.chr" % name)
        if os.path.exists(destino):
            continue
        origen = "chrs/%s.chr" % name
        try:
            with renpy.open_file(origen) as fh:
                datos = fh.read()
            with open(destino, "wb") as fh:
                fh.write(datos)
        except Exception as e:
            print("personajes: falta %s (copialo desde tu DDLC): %s" % (origen, e))


def restore_characters():
    """Restaura los personajes según `persistent.playthrough`."""
    playthrough = renpy.store.persistent.playthrough
    if playthrough == 0:
        restore_character(["monika", "natsuki", "sayori", "yuri"])
    elif playthrough in (1, 2):
        restore_character(["monika", "natsuki", "yuri"])
    elif playthrough == 3:
        restore_character(["monika"])
    else:
        restore_character(["natsuki", "sayori", "yuri"])


def delete_character(name):
    """Borra `characters/<name>.chr` (si existe)."""
    folder = get_characters_folder()
    if not folder:
        return
    try:
        os.remove(os.path.join(folder, "%s.chr" % name))
    except OSError:
        pass


def initialize_characters_folder():
    """Crea `characters/` si falta y restaura lo que se pueda."""
    folder = get_characters_folder()
    if not folder:
        return
    try:
        os.makedirs(folder, exist_ok=True)
    except OSError as e:
        print("personajes: no se pudo crear la carpeta: %s" % e)
        return
    restore_characters()
