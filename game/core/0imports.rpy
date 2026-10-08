# 0imports.rpy
# Este archivo importa ciertos modulos Python en tiempo de ejecucion para funciones del juego.
# El nombre '0imports' garantiza que se cargue antes que otros scripts.

# En el template original, este archivo importaba los módulos de Achievements y
# Gallery (extras opcionales). Si no tienes esos extras, deja este archivo vacío
# o agrega tus propios imports aquí.

init -2 python:
    # Ejemplo:
    #   from store.mi_modulo import MiClase
    pass

init -2 python:
    # Añade la carpeta 'mod_assets' (dentro de game/) a la lista de búsqueda
    # de Ren'Py, para poder referenciar tus assets con nombres cortos
    # ("images/bg/mi_cuarto.png") igual que los de DDLC.
    mod_assets = config.gamedir + "/mod_assets"
    if mod_assets not in config.searchpath:
        config.searchpath.append(mod_assets)
