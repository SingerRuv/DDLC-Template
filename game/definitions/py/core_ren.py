# Este archivo contiene la configuracion base de Python para el Mod Template.
# Define `persistent` y `store` muy temprano (init -3) para que los modulos
# _ren.py puedan acceder al objeto persistente de Ren'Py.

"""renpy
init -3 python:
"""
# Se usan para que los IDEs no reporten errores y el codigo Python pueda acceder al store y persistent de Ren'Py.
persistent = renpy.store.persistent
store = renpy.store
