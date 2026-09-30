## complements.rpy
## Hub "Herramientas": punto de entrada a las herramientas dev del template.
##
## Es dev-only: el botón aparece en el menú principal solo si
## config.developer = True. Los estilos pl_* y las funciones de cada
## herramienta viven en tools/pose_lab.rpy (misma unidad).
##
## Usa el mismo fondo y el mismo frame rosa de navegación que el menú
## principal, para que se sienta parte de él.
##
## Para sumar una herramienta: agregar una entrada a pl_herramientas().
## Para mostrar capturas, poner los PNG en game/tools/capturas/ y listar
## sus rutas (relativas a game/) en el campo `capturas` de la entrada.

init python:
    def pl_herramientas():
        """Lista de herramientas: (titulo, descripcion, capturas, action).

        `capturas` es una lista de rutas de PNG (relativas a game/) que se
        muestran en el panel derecho. Se construye al abrir el hub (no en
        init) para no depender del orden de carga de los archivos .rpy."""
        return [
            ("PoseLab",
             "Arma poses de los personajes y genera el codigo show/image "
             "listo para pegar en tu guion y en definitions/sprites.rpy.",
             [
                 # "tools/capturas/poselab_1.png",
             ],
             [Function(pl_ensure_init), Show("pose_lab")]),
        ]


screen complements():
    tag menu
    modal True
    zorder 200

    default sel = 0

    # Volver al menú principal (el hub se abre desde allí).
    key "K_ESCAPE" action ShowMenu("main_menu")

    # Mismo fondo animado que el menú principal.
    add gui.main_menu_background

    $ herramientas = pl_herramientas()

    # ----- Panel izquierdo: lista de herramientas -----
    frame:
        style "main_menu_frame"

        vbox:
            style_prefix "main_navigation"
            xpos gui.navigation_xpos
            xoffset -50
            yalign 0.0
            yoffset 40
            spacing gui.navigation_spacing

            text _("Herramientas") style "complements_title"

            for i, (titulo, desc, capturas, action) in enumerate(herramientas):
                textbutton "[titulo]":
                    style "main_navigation_button"
                    text_style "main_navigation_button_text"
                    selected sel == i
                    action SetScreenVariable("sel", i)

            textbutton _("Back"):
                style "main_navigation_button"
                text_style "main_navigation_button_text"
                action ShowMenu("main_menu")

    # ----- Panel derecho: detalle de la herramienta elegida -----
    if herramientas:
        $ sel_titulo, sel_desc, sel_capturas, sel_action = herramientas[sel]

        frame:
            style "complements_detail"
            xpos 360
            ypos 60
            xsize 880

            vbox:
                spacing 14

                text "[sel_titulo]" style "complements_detail_title"
                text "[sel_desc]" style "complements_detail_desc"

                text _("Capturas de pantalla") style "complements_section"

                if sel_capturas:
                    hbox:
                        spacing 12
                        for cap in sel_capturas:
                            add cap zoom 0.4
                else:
                    frame:
                        style "complements_shot_frame"
                        text _("Sin capturas todavía.") style "complements_shot_empty"

                textbutton "Abrir [sel_titulo]":
                    style "complements_open"
                    text_style "main_navigation_button_text"
                    action sel_action
                    at nav_button_anim


style complements_detail is frame:
    background "#ffffffcc"
    padding (28, 24)

style complements_detail_title is text:
    size 34
    bold True
    color "#cc6699"
    outlines []

style complements_detail_desc is text:
    size 18
    color "#333333"
    outlines []

style complements_section is text:
    size 18
    bold True
    color "#666666"
    outlines []

style complements_shot_frame is frame:
    background "#e6e6e6"
    padding (20, 30)
    xsize 620

style complements_shot_empty is text:
    size 16
    color "#888888"
    outlines []

# Botón "Abrir": mismo diseño que los textbuttons de navegación del menú,
# sin el size_group (para no atar su ancho a los de la izquierda).
style complements_open is main_navigation_button:
    size_group None

style complements_title is text:
    size 26
    color "#ffffff"
    outlines [(4, text_outline_color, 0, 0), (2, text_outline_color, 2, 2)]
