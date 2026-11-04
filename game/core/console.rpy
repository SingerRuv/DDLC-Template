## console.rpy
## Consola de Monika (la "terminal" de DDLC).
##
## Uso desde el guion:
##   $ console("sayori", "Just Monika.")   # escribe entrada y salida
##   $ console.show_screen()               # muestra el historial
##
## La lógica está en game/core/py/console_ren.py.
## Ver docs/01-historia.md.

init -1:
    default console = Console(console_delay=0.5, console_cps=30,
                              max_log_history=5)


screen console_screen(console, input_text=None, output_text=None, cps=None,
                      delay=None):
    """Terminal falsa: la entrada se escribe letra a letra y después
    aparece la salida."""

    style_prefix "console_screen"

    default finish_actions = [SetScreenVariable("in_progress", False), Return()]

    python:
        used_cps = cps if isinstance(cps, int) else console.console_cps
        used_delay = delay if isinstance(delay, float) else console.console_delay

    # Entrada que se está mostrando (se conserva entre re-renders).
    default new_input_code = "_"
    default in_progress = False

    if not in_progress:
        $ new_input_code = "_"
        if input_text:
            $ in_progress = True
            $ new_input_code = input_text

    if in_progress:
        timer ((float(len(renpy.filter_text_tags(new_input_code, deny=[])))
                / float(used_cps)) + used_delay) action finish_actions

    frame:
        vbox:
            hbox:
                text ">" xpos 5 ypos 10
                text new_input_code xpos 15 ypos 10:
                    slow_cps 30
                    xmaximum 460

            vbox:
                xpos 26 ypos 30
                spacing 5

                for output in console.console_history.values():
                    text output


style console_screen_frame:
    background Frame(Transform(Solid("#333"), alpha=0.75))
    xsize 480
    ysize 180

# Fuente de la terminal de DDLC (viene de fonts.rpa).
style console_screen_text:
    font "gui/font/F25_Bank_Printer.ttf"
    color "#fff"
    size 18
    outlines []
