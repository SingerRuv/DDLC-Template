## functions.rpy
# Funciones de ayuda usadas en todo el juego.
# La mayoria son utilidades Python que envuelven la funcionalidad de Ren'Py en una API mas simple.

init python:
    import os
    import subprocess
    import platform

    # ----- Archivos de personajes (.chr) --------------------------------------------

    def get_characters_folder():
        """
        Devuelve la ruta a la carpeta de personajes.
        """
        return os.path.join(config.basedir, "characters").replace("\\", "/")

    def restore_character(characters):
        """
        Restaura los personajes indicados en la carpeta 'characters'
        y elimina cualquier archivo de personaje que no este en la lista.
        """
        characters_folder = get_characters_folder()
        if not os.path.exists(characters_folder):
            os.makedirs(characters_folder)
        for existing_file in list(os.listdir(characters_folder)):
            if existing_file.endswith(".chr"):
                character_name = os.path.splitext(existing_file)[0]
                if character_name not in characters:
                    try:
                        os.remove(os.path.join(characters_folder, existing_file))
                    except OSError:
                        pass
        for character in characters:
            character_file_path = os.path.join(characters_folder, character + ".chr")
            if not os.path.exists(character_file_path):
                src_path = os.path.join("chrs", character + ".chr").replace("\\", "/")
                try:
                    with renpy.open_file(src_path) as src_file:
                        data = src_file.read()
                    with open(character_file_path, "wb") as char_file:
                        char_file.write(data)
                except Exception:
                    pass

    def restore_characters():
        """
        Restaura todos los personajes segun el playthrough actual.
        """
        if persistent.playthrough == 0:
            restore_character(["monika", "natsuki", "sayori", "yuri"])
        elif persistent.playthrough in (1, 2):
            restore_character(["monika", "natsuki", "yuri"])
        elif persistent.playthrough == 3:
            restore_character(["monika"])
        else:
            restore_character(["natsuki", "sayori", "yuri"])

    def initialize_characters_folder():
        """
        Inicializa la carpeta de personajes creandola si no existe.
        """
        characters_folder = get_characters_folder()
        if not os.path.exists(characters_folder):
            os.makedirs(characters_folder)
        restore_characters()

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
