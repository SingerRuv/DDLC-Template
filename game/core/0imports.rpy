# 0imports.rpy
# Este archivo importa ciertos modulos Python en tiempo de ejecucion para funciones del juego.
# El nombre '0imports' garantiza que se cargue antes que otros scripts.

# Agregá acá tus propios imports de arranque (si no necesitás ninguno, no hace
# falta tocar nada: el único bloque real es el del searchpath).

init -2 python:
    # Añade la carpeta 'mod_assets' (dentro de game/) a la lista de búsqueda
    # de Ren'Py, para poder referenciar tus assets con nombres cortos
    # ("images/bg/mi_cuarto.png") igual que los de DDLC.
    # Ejemplo de import propio:
    #   from store.mi_modulo import MiClase
    mod_assets = config.gamedir + "/mod_assets"
    if mod_assets not in config.searchpath:
        config.searchpath.append(mod_assets)
