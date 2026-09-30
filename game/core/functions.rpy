## functions.rpy
# Funciones de ayuda usadas en todo el juego.
# La mayoria son utilidades Python que envuelven la funcionalidad de Ren'Py en una API mas simple.

init python:
    import subprocess

    def delete_all_saves():
        """
        Borra todos los archivos de guardado del juego.
        """
        for savegame in renpy.list_saved_games(fast=True):
            renpy.unlink_save(savegame)
        try:
            renpy.loadsave.location.unlink_persistent()
        except Exception:
            pass
        renpy.persistent.should_save_persistent = False

    # ----- Deteccion de streaming ----------------------------------------------

    def get_process_list():
        """
        Obtiene el conjunto de nombres de procesos en ejecucion.
        """
        process_list = set()
        if renpy.windows:
            try:
                output = subprocess.run(
                    "powershell (Get-Process).ProcessName",
                    shell=True, capture_output=True, text=True,
                ).stdout
                for process in output.splitlines():
                    process_list.add(process.strip().lower() + ".exe")
            except Exception:
                pass
        else:
            try:
                output = subprocess.run(
                    "ps -eo comm=", shell=True, capture_output=True, text=True,
                ).stdout
                for process in output.splitlines():
                    process = process.strip().split()[0]
                    if process:
                        process_list.add(process.lower())
            except Exception:
                pass
        return process_list

    def process_check(stream_list):
        """
        Comprueba si alguno de los procesos de streaming indicados esta en ejecucion.
        """
        process_list = get_process_list()
        for process in stream_list:
            for running_process in process_list:
                if running_process == process or running_process.startswith(process + "/"):
                    return True
        return False

    def is_user_streaming():
        """
        Devuelve True si alguna aplicacion conocida de streaming/grabacion esta en ejecucion.
        """
        streaming_apps = [
            "obs.exe", "obs64.exe", "streamlabsobs.exe",
            "xsplit.core.exe", "xsplit.broadcaster.exe",
            "twitchstudio.exe", "elgato.streamdeck.exe",
            "nvidia.share.exe", "amd.raptr.exe",
            "zoom.exe", "teams.exe",
        ]
        return process_check(streaming_apps)
