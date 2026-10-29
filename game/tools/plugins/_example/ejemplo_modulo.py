## ejemplo_modulo.py
## Módulo Python del plugin de ejemplo.
##
## El hub lo importa cuando el plugin declara `"modulo": "ejemplo_modulo"` en
## su tool.json, y llama los hooks de abajo si existen. Es la forma de meter
## lógica en Python sin escribir un .rpy.
##
## Copiá este archivo junto a tu plugin y renombralo (el nombre sin extensión
## es el que va en "modulo").
##
## Ojo: dentro de un módulo, `open` es el de Ren'Py y acepta un solo
## argumento. Para leer o escribir archivos, usá `io.open`.

import renpy

ESTADO = {"veces_abierto": 0}


def metadata():
    """Campos cosméticos del manifiesto que sobreescriben el tool.json."""
    return {
        "categoria": "Ejemplos",
        "palabras_clave": ["ejemplo", "plantilla", "modulo"],
    }


def setup(tool):
    """Se llama una vez, al iniciar el juego."""
    print("ejemplo: setup del plugin %r" % (tool.get("id"),))


def open(tool):
    """Se llama al abrir la herramienta desde el hub."""
    ESTADO["veces_abierto"] += 1
    renpy.store.ejemplo_veces = ESTADO["veces_abierto"]
    print("ejemplo: abierto %d vez(es)" % ESTADO["veces_abierto"])


def close(tool):
    """Se llama al cerrar la herramienta."""
    print("ejemplo: cerrado")
