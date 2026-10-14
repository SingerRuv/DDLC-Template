## android_assets_ren.py
## Soporte Android: extracción de los assets de DDLC por el jugador.
##
## Adaptado del DDLC Mod Template 2.0 de Azariel "Bronya Rand" Del Carmen
## (bronya_rand). Ver las IP Guidelines de Team Salvato.
##
## Por las IP Guidelines, el mod NO incluye los assets de DDLC: en PC el jugador
## los copia a game/, pero en Android no puede (van dentro del APK). Por eso acá
## le pedimos que seleccione su APK/XAPK de DDLC (o el ZIP de PC) y extraemos los
## .rpa a la carpeta escribible del juego.
##
## No lo edites: si lo rompés, los mods Android no arrancan. Ver splash.rpy.

"""renpy
init -2 python:
"""

import errno
import os
import shutil
import threading
import zipfile
from contextlib import contextmanager

# ============================================================================
# Constantes
# ============================================================================

# Códigos de request para la Activity de Android.
REQUEST_CODE_PC = 2001
REQUEST_CODE_ANDROID = 2002
_REQUEST_MODES = {REQUEST_CODE_PC: "pc", REQUEST_CODE_ANDROID: "android"}

# Assets que el juego necesita para arrancar (PC y Android).
PC_RPAS = frozenset({"audio.rpa", "fonts.rpa", "images.rpa"})
ANDROID_PREFIXES = (
    "assets/game/images/",
    "assets/game/gui/",
    "assets/game/fonts/",
    "assets/game/bgm/",
    "assets/game/sfx/",
)
ANDROID_ASSET_ROOT = "assets/game/"

# Se escribe recién tras una extracción exitosa.
ASSET_MARKER = ".ddlc_assets_installed"

# Temporales de la extracción.
STAGING_DIR = ".ddlc_staging"
TEMP_IMPORT_NAME = "temp_import.archive"
NESTED_APK_NAME = ".ddlc_nested.apk"

COPY_CHUNK = 1024 * 1024  # 1 MiB

# ============================================================================
# Estado (lo lee la pantalla android_asset_setup)
# ============================================================================

asset_setup_status = ""
asset_setup_busy = False
asset_setup_complete = False
asset_setup_progress = 0.0  # 0.0..1.0, para la barra

_state_lock = threading.Lock()
_job_running = False
_cancel_requested = False

# Se incrementa en cada apertura del selector para que los pollers viejos salgan.
_picker_token = 0

PICKER_POLL_INTERVAL = 0.25  # segundos


class AssetSetupError(Exception):
    """Error controlado durante la extracción."""


class AssetSetupCancelled(Exception):
    """El jugador canceló la extracción."""


def _set_status(msg, busy=None, progress=None):
    global asset_setup_status, asset_setup_busy, asset_setup_progress
    asset_setup_status = msg
    if busy is not None:
        asset_setup_busy = busy
    if progress is not None:
        asset_setup_progress = progress


def _fail(msg):
    _set_status(msg, busy=False)


def _try_begin(status):
    """Intenta empezar la extracción. False si ya hay una en curso."""
    global asset_setup_busy, asset_setup_status, asset_setup_complete, asset_setup_progress
    with _state_lock:
        if asset_setup_busy:
            return False
        asset_setup_busy = True
        asset_setup_status = status
        asset_setup_complete = False
        asset_setup_progress = 0.0
    return True


def _check_cancel():
    if _cancel_requested:
        raise AssetSetupCancelled()


def _copy(src, dst):
    """Copia por chunks, chequeando cancelación (para archivos grandes)."""
    while True:
        _check_cancel()
        chunk = src.read(COPY_CHUNK)
        if not chunk:
            break
        dst.write(chunk)


def _fmt_size(n):
    """Formatea bytes en algo legible (B/KB/MB/GB)."""
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return "%.0f %s" % (n, unit) if unit == "B" else "%.1f %s" % (n, unit)
        n /= 1024.0


# ============================================================================
# Carpetas en Android
# ============================================================================

def _get_android_data_directory():
    """Carpeta de datos de la app en Android (vía jnius), o None."""
    if not renpy.android:
        return None
    import jnius  # type: ignore
    activity = jnius.autoclass("org.renpy.android.PythonSDLActivity")
    current_activity = jnius.cast("android.app.Activity", activity.mActivity)
    return current_activity.getFilesDir().getAbsolutePath()


def get_android_game_dir():
    """Carpeta 'game' escribible donde van los .rpa extraídos."""
    if renpy.android:
        return renpy.config.gamedir
    data_dir = _get_android_data_directory()
    if data_dir is None:
        return renpy.config.gamedir
    game_dir = os.path.join(data_dir, "game")
    if not os.path.exists(game_dir):
        os.makedirs(game_dir, 0o777)
    return game_dir


def _marker_path():
    return os.path.join(get_android_game_dir(), ASSET_MARKER)


def has_installed_ddlc_assets():
    """True si los assets de DDLC están instalados.

    El marcador se escribe recién al terminar toda la extracción, así que una
    instalación parcial no pasa."""
    if not renpy.android:
        return True
    if os.path.exists(_marker_path()):
        return True
    try:
        return all(renpy.loadable(name) for name in PC_RPAS)
    except Exception:
        return False


# ============================================================================
# Utilidades de extracción (seguridad)
# ============================================================================

def _safe_join(base, rel):
    """Une rel a base y rechaza lo que se escape de base (anti zip-slip)."""
    base_real = os.path.realpath(base)
    out = os.path.realpath(os.path.join(base_real, rel))
    if not out.startswith(base_real + os.sep):
        raise AssetSetupError(
            _("The selected file contains an unsafe path and was rejected.")
        )
    return out


def _check_free_space(path, needed):
    """Verifica que haya espacio libre (con 5% + 32 MiB de margen)."""
    if not hasattr(os, "statvfs"):
        return
    try:
        st = os.statvfs(path)
    except OSError:
        return
    free = st.f_bavail * st.f_frsize
    required = int(needed * 1.05) + 32 * 1024 * 1024
    if free < required:
        raise AssetSetupError(
            _("Not enough free storage. About %s is needed, but only %s is available.")
            % (_fmt_size(required), _fmt_size(free))
        )


def _mod_provides(rel, target_dir):
    """True si el mod ya provee esta ruta (no la pisamos).

    Un archivo ya presente en target_dir es de una extracción previa y se puede
    sobreescribir."""
    if os.path.exists(os.path.join(target_dir, rel)):
        return False
    try:
        return bool(renpy.loadable(rel))
    except Exception:
        return False


def _cleanup_stale():
    """Limpia restos de corridas interrumpidas."""
    try:
        game_dir = get_android_game_dir()
        shutil.rmtree(os.path.join(game_dir, STAGING_DIR), ignore_errors=True)
        for name in os.listdir(game_dir):
            if name.endswith(".part") or name in (TEMP_IMPORT_NAME, NESTED_APK_NAME):
                try:
                    os.remove(os.path.join(game_dir, name))
                except OSError:
                    pass
    except OSError:
        pass


def _commit(pairs):
    """Mueve los archivos preparados a su lugar y escribe el marcador al final.

    pairs: iterable de (staged_path, final_path). Mismo filesystem, así que
    os.replace es un rename barato."""
    marker = _marker_path()
    if os.path.exists(marker):
        os.remove(marker)  # "No instalado" mientras hacemos el commit.

    for src, dest in pairs:
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        os.replace(src, dest)

    with open(marker, "w") as f:
        f.write("1\n")


# ============================================================================
# Extracción desde el ZIP de PC
# ============================================================================

def extract_pc_zip(zip_source):
    """Extrae los assets de DDLC de un ZIP de PC a la carpeta del juego."""
    target_dir = get_android_game_dir()
    staged = {}

    try:
        with zipfile.ZipFile(zip_source, "r") as zf:
            wanted = {}
            for info in zf.infolist():
                if info.is_dir():
                    continue
                name = os.path.basename(info.filename).lower()
                if name in PC_RPAS and name not in wanted:
                    wanted[name] = info

            missing = PC_RPAS - set(wanted)
            if missing:
                raise AssetSetupError(
                    _("This ZIP is missing %s. Make sure it is the official DDLC PC download.")
                    % ", ".join(sorted(missing))
                )

            _check_free_space(target_dir, sum(i.file_size for i in wanted.values()))

            ordered = sorted(wanted)
            total = len(ordered)
            for n, name in enumerate(ordered, 1):
                _check_cancel()
                _set_status(_("Extracting %s...") % name, progress=(n - 1) / total)
                dest = os.path.join(target_dir, name)
                part = dest + ".part"
                with zf.open(wanted[name]) as src, open(part, "wb") as dst:
                    _copy(src, dst)  # CRC al cerrar
                staged[name] = (part, dest)

                with open(part, "rb") as f:
                    if f.read(4) != b"RPA-":
                        raise AssetSetupError(
                            _("%s in this ZIP appears to be corrupt.") % name
                        )

        _set_status(_("Installing assets..."), progress=1.0)
        _commit(staged.values())
    finally:
        for part, _ in staged.values():
            if os.path.exists(part):
                try:
                    os.remove(part)
                except OSError:
                    pass


# ============================================================================
# Extracción desde el APK/XAPK de Android
# ============================================================================

def _has_game_assets(apk_path):
    with zipfile.ZipFile(apk_path, "r") as z:
        return any(n.startswith(ANDROID_PREFIXES) for n in z.namelist())


def _unpack_apk(apk, staging, target_dir):
    wanted = []
    for info in apk.infolist():
        name = info.filename
        if info.is_dir():
            continue
        # Salteamos los scripts para no duplicar labels.
        if name.endswith((".rpy", ".rpyc")):
            continue
        if name.startswith(ANDROID_PREFIXES):
            wanted.append((info, name[len(ANDROID_ASSET_ROOT):]))

    if not wanted:
        raise AssetSetupError(
            _("No DDLC assets were found in this file. Make sure it is a downloaded DDLC Android APK/XAPK.")
        )

    _check_free_space(target_dir, sum(i.file_size for i, _ in wanted))

    total = len(wanted)
    done = 0
    for info, rel in wanted:
        _check_cancel()
        if _mod_provides(rel, target_dir):
            done += 1
            continue
        out = _safe_join(staging, rel)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with apk.open(info) as src, open(out, "wb") as dst:
            _copy(src, dst)
        done += 1
        _set_status(
            _("Extracting Android assets... (%d/%d)") % (done, total),
            progress=done / float(total),
        )


def extract_android_xapk(apk_source):
    """Extrae los assets de DDLC de un APK/XAPK a la carpeta del juego."""
    target_dir = get_android_game_dir()
    staging = os.path.join(target_dir, STAGING_DIR)
    nested_path = os.path.join(target_dir, NESTED_APK_NAME)

    shutil.rmtree(staging, ignore_errors=True)
    os.makedirs(staging)

    try:
        with zipfile.ZipFile(apk_source, "r") as outer:
            nested = [
                i for i in outer.infolist() if i.filename.lower().endswith(".apk")
            ]

            if nested:
                # XAPK/split APK: buscamos el APK interno que trae assets/game/.
                # Se pasa por disco (no BytesIO) para no tenerlo en RAM.
                found = False
                for info in nested:
                    _check_cancel()
                    _check_free_space(target_dir, info.file_size)
                    _set_status(_("Scanning the package..."))
                    with outer.open(info) as src, open(nested_path, "wb") as dst:
                        _copy(src, dst)
                    if _has_game_assets(nested_path):
                        found = True
                        break
                    os.remove(nested_path)

                if not found:
                    raise AssetSetupError(
                        _("No DDLC assets were found in this XAPK. Make sure it is the official DDLC Android package.")
                    )
                with zipfile.ZipFile(nested_path, "r") as apk:
                    _unpack_apk(apk, staging, target_dir)
            else:
                # APK suelto.
                _unpack_apk(outer, staging, target_dir)

        _set_status(_("Installing assets..."), progress=1.0)
        pairs = []
        for root, _dirs, files in os.walk(staging):
            for fname in files:
                src = os.path.join(root, fname)
                rel = os.path.relpath(src, staging)
                pairs.append((src, _safe_join(target_dir, rel)))
        _commit(pairs)
    finally:
        shutil.rmtree(staging, ignore_errors=True)
        if os.path.exists(nested_path):
            try:
                os.remove(nested_path)
            except OSError:
                pass


# ============================================================================
# Hilo de trabajo
# ============================================================================

def _finish_success():
    global asset_setup_complete
    _set_status(_("Extraction complete! Restarting..."), progress=1.0)
    asset_setup_complete = True
    renpy.invoke_in_main_thread(renpy.utter_restart)


def _run_job(mode, opener):
    """Cuerpo del hilo. opener() es un context manager que devuelve un archivo."""
    global _job_running, _cancel_requested
    _job_running = True
    _cancel_requested = False

    try:
        _set_status(_("Reading the selected file..."), busy=True)
        _cleanup_stale()

        with opener() as source:
            if mode == "pc":
                _set_status(_("Extracting PC assets..."))
                extract_pc_zip(source)
            else:
                _set_status(_("Extracting Android assets..."))
                extract_android_xapk(source)

        _finish_success()
    except AssetSetupCancelled:
        _set_status(_("Asset extraction canceled."), busy=False)
    except AssetSetupError as e:
        _fail(str(e))
    except zipfile.BadZipFile:
        _fail(_("That file isn't a valid ZIP/APK archive, or it is damaged. Try downloading it again."))
    except OSError as e:
        if e.errno == errno.ENOSPC:
            _fail(_("Not enough free storage to extract the DDLC assets."))
        else:
            _fail(_("File error during extraction: %s") % e)
    except Exception as e:
        _fail(_("Unexpected error during extraction: %s: %s") % (type(e).__name__, e))
    finally:
        _job_running = False
        _cleanup_stale()


def _start_job(mode, opener):
    threading.Thread(target=_run_job, args=(mode, opener), daemon=True).start()


def cancel_asset_setup():
    """Si hay una extracción corriendo, la cancela. Si no, resetea la UI (por si
    el selector nunca respondió, p. ej. si la Activity se cerró)."""
    global _picker_token, _cancel_requested
    if _job_running:
        _cancel_requested = True
        _set_status(_("Cancelling..."), busy=True)
        return
    _picker_token += 1  # Detiene cualquier poller pendiente.
    _set_status("", busy=False)


# ============================================================================
# Selector de archivos + acceso al URI (solo Android)
# ============================================================================

if renpy.android:
    import time

    from jnius import autoclass  # type: ignore

    PythonSDLActivity = autoclass("org.renpy.android.PythonSDLActivity")
    Intent = autoclass("android.content.Intent")
    Activity = autoclass("android.app.Activity")
    Files = autoclass("java.nio.file.Files")
    StandardCopyOption = autoclass("java.nio.file.StandardCopyOption")
    File = autoclass("java.io.File")

    def _handle_picker_result(request_code, result_code, data):
        mode = _REQUEST_MODES.get(request_code)
        if mode is None:
            return False  # No es nuestro; seguimos esperando.

        try:
            if result_code != Activity.RESULT_OK or data is None:
                _set_status(_("Asset extraction canceled."), busy=False)
                return True

            uri = data.getData()
            if uri is None:
                _fail(_("Error: No file selected."))
                return True

            _start_job(mode, lambda: _open_picked_uri(uri))
        except Exception as e:
            _fail(_("Error handling the selected file: %s") % e)
        return True

    def _poll_picker(token):
        """El PythonSDLActivity de RAPT no tiene listener de resultados: guarda
        el resultado en campos públicos pensados para pollearse desde Python."""
        activity = PythonSDLActivity.mActivity

        while token == _picker_token:
            time.sleep(PICKER_POLL_INTERVAL)
            try:
                request_code = activity.mActivityResultRequestCode
                if request_code == -1:
                    continue
                result_code = activity.mActivityResultResultCode
                data = activity.mActivityResultResultData
                activity.mActivityResultRequestCode = -1  # Consumir.
                if _handle_picker_result(request_code, result_code, data):
                    return
            except Exception as e:
                _fail(_("Error reading the file picker result: %s") % e)
                return

    @contextmanager
    def _open_picked_uri(uri):
        """Devuelve un archivo binario seekable para un URI de SAF."""
        resolver = PythonSDLActivity.mActivity.getContentResolver()
        temp_path = os.path.join(get_android_game_dir(), TEMP_IMPORT_NAME)
        f = None

        try:
            try:
                pfd = resolver.openFileDescriptor(uri, "r")
                f = os.fdopen(pfd.detachFd(), "rb")
            except Exception:
                f = None

            if f is not None and not f.seekable():
                _set_status(_("Copying the selected file..."))
                with open(temp_path, "wb") as out:
                    _copy(f, out)
                f.close()
                f = open(temp_path, "rb")
            elif f is None:
                _set_status(_("Copying the selected file..."))
                stream = resolver.openInputStream(uri)
                try:
                    Files.copy(
                        stream,
                        File(temp_path).toPath(),
                        StandardCopyOption.REPLACE_EXISTING,
                    )
                finally:
                    stream.close()
                f = open(temp_path, "rb")

            yield f
        finally:
            if f is not None:
                try:
                    f.close()
                except Exception:
                    pass
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except OSError:
                    pass

    def _launch_picker(request_code):
        global _picker_token
        activity = PythonSDLActivity.mActivity

        activity.mActivityResultRequestCode = -1
        activity.mActivityResultResultData = None

        intent = Intent(Intent.ACTION_OPEN_DOCUMENT)
        intent.addCategory(Intent.CATEGORY_OPENABLE)
        intent.setType("*/*")

        _picker_token += 1
        token = _picker_token
        activity.startActivityForResult(intent, request_code)
        threading.Thread(target=_poll_picker, args=(token,), daemon=True).start()


# ============================================================================
# Puntos de entrada (los llama la pantalla; siempre devuelven None)
# ============================================================================

def _prompt(request_code, status):
    if not renpy.android:
        return
    if not _try_begin(status):
        return  # Ya hay una en curso; ignoramos doble toque.

    try:
        _launch_picker(request_code)
    except Exception as e:
        _fail(_("Error opening the file picker: %s") % e)


def prompt_and_extract_pc():
    """Abre el gestor de archivos para elegir el ZIP de DDLC de PC."""
    _prompt(REQUEST_CODE_PC, _("Select a DDLC PC ZIP file..."))


def prompt_and_extract_android():
    """Abre el gestor de archivos para elegir el APK/XAPK de DDLC de Android."""
    _prompt(REQUEST_CODE_ANDROID, _("Select a DDLC Android APK/XAPK file..."))
