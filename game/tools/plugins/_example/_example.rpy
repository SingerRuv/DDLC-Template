## _example.rpy
## Herramienta de ejemplo para el hub de Herramientas.
##
## Copia la carpeta _example/, renombrala (p. ej. mi_herramienta/), edita su
## tool.json y reescribe este screen. El hub lo descubre solo.
##
## El screen debe llevar `tag menu` y, al cerrarse, volver al hub con
## Show("complements") — usando el mismo fondo y frame del menú para verse
## integrado.

screen example_tool():
    tag menu
    modal True
    zorder 200

    # ESC vuelve al hub de Herramientas.
    key "K_ESCAPE" action Show("complements")

    add gui.main_menu_background

    frame:
        style "complements_detail"
        xalign 0.5
        yalign 0.5
        xsize 640

        vbox:
            spacing 14

            text "Ejemplo" style "complements_detail_title"
            text "Esta es una herramienta de ejemplo. Reemplaza este contenido por el tuyo." style "complements_detail_desc"

            textbutton "Volver":
                style "complements_open"
                text_style "main_navigation_button_text"
                action Show("complements")
                at nav_button_anim
