# console_ren.py
# Lógica de la consola de Monika (la "terminal" de DDLC).
#
# La pantalla vive en game/core/console.rpy. Para mostrarla:
#   $ console("entrada", "salida")
#   $ console.show_screen()
#
# Ver docs/01-historia.md.

import renpy  # type: ignore

"""renpy
init python:
"""


class Console(object):
    """Terminal falsa de DDLC: escribe la entrada, muestra la salida y
    guarda un historial corto."""

    def __init__(self, console_delay, console_cps, max_log_history=5):
        self.console_delay = console_delay
        self.console_cps = console_cps
        self.max_log_history = max_log_history
        self.console_history = {}

    def __call__(self, input_text, output_text, cps=None, delay=None):
        """Muestra `input_text` y después `output_text`, y los guarda."""
        if len(self.console_history) + 1 > self.max_log_history:
            self.console_history.pop(min(self.console_history.keys()))

        if renpy.get_screen("console_screen"):
            renpy.hide_screen("console_screen")
        renpy.call_screen("console_screen", console=self,
                          input_text=input_text, output_text=output_text,
                          cps=cps, delay=delay)

        self.console_history[input_text] = output_text
        self.show_screen()
        renpy.restart_interaction()

    def clear_history(self):
        """Borra el historial de la consola."""
        self.console_history.clear()

    def show_screen(self):
        """Muestra la consola con el historial actual."""
        renpy.show_screen("console_screen", console=self)
