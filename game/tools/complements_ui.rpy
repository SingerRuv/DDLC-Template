## complements_ui.rpy
## Hub "Herramientas" — Interfaz reutilizable: estilos, la tarjeta de la grilla
## (pl_card) y el shell para herramientas simples (tool_shell).
##
## La lógica vive en complements_data.rpy y el screen raíz del hub en
## complements.rpy.

# ---------------------------------------------------------------------------
# Estilos del hub.
# ---------------------------------------------------------------------------

style complements_detail is frame:
    background "#ffffffcc"
    padding (28, 24)

style complements_detail_title is text:
    size 34
    bold True
    color "#cc6699"
    outlines []

style complements_meta is text:
    size 15
    color "#999999"
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

style complements_hint is text:
    size 14
    color "#888888"
    outlines []

# --- Hub: búsqueda, chips y tarjetas ---

transform pl_thumb:
    fit "contain"
    xysize (80, 80)

style pl_search_border is frame:
    background "#d9a9c2"
    padding (2, 2)

style pl_search_frame is frame:
    background "#ffffff"
    padding (10, 6)
    xsize 400

style pl_search is input:
    color "#333333"
    size 18
    outlines []

style pl_search_hint is text:
    color "#999999"
    size 18
    outlines []

style pl_hub_title is text:
    size 26
    bold True
    color "#5a1a3a"
    outlines []

style pl_dropdown is button:
    background "#ffffff"
    hover_background "#ffeef5"
    padding (12, 6)
    xsize 220

style pl_dropdown_text is text:
    size 17
    color "#7a3355"
    outlines []

style pl_dropdown_arrow is text:
    font "DejaVuSans.ttf"
    size 14
    color "#7a3355"
    outlines []

style pl_dropdown_item is button:
    background "#ffffff"
    hover_background "#ffeef5"
    selected_background "#f4a6c8"
    selected_hover_background "#ef94bd"
    padding (12, 4)
    xsize 220

style pl_dropdown_item_text is text:
    size 15
    color "#7a3355"
    outlines []

# La tarjeta es un button con borde (background) que envuelve un frame blanco.
style pl_card is button:
    background "#d9a9c2"
    hover_background "#c07fa3"
    padding (2, 2)
    xsize 425
    ysize 128

style pl_card_inner is frame:
    background "#ffffff"
    padding (14, 10)
    xfill True
    yfill True

style pl_card_thumb is frame:
    background "#f3e7ee"
    xysize (80, 80)
    padding (0, 0)
    xalign 0.0
    yalign 0.5

style pl_card_title is text:
    size 26
    bold True
    color "#cc6699"
    outlines []

style pl_card_desc is text:
    size 15
    color "#444444"
    outlines []

style pl_card_cat is text:
    size 13
    color "#aa7799"
    outlines []

style pl_card_open is text:
    size 18
    bold True
    color "#cc6699"
    outlines []


# ---------------------------------------------------------------------------
# Tarjeta de una herramienta en la grilla del hub. Toda la tarjeta es clickeable.
# ---------------------------------------------------------------------------

screen pl_card(t):
    $ _img = t["icono"] or (t["capturas"][0] if t["capturas"] else "")

    button:
        style "pl_card"
        action Function(pl_abrir, t)

        frame:
            style "pl_card_inner"

            fixed:
                xfill True
                yfill True

                hbox:
                    spacing 12
                    yalign 0.5

                    frame:
                        style "pl_card_thumb"
                        if _img:
                            add _img at pl_thumb

                    vbox:
                        spacing 2
                        yalign 0.5
                        text _(t["titulo"]) style "pl_card_title"
                        text _(pl_corto(t["descripcion"], 90)) style "pl_card_desc" xmaximum 230
                        text _(t["categoria"]) style "pl_card_cat"

                text _("Abrir →") style "pl_card_open" xalign 0.98 yalign 0.98


# ---------------------------------------------------------------------------
# Shell reutilizable para herramientas simples: fondo del menú, título, ESC y
# botón "Volver" al hub, y el frame de tarjeta. Tu screen define tag/modal/zorder
# (las propiedades de screen NO se transfieren con `use`) y aporta el contenido:
#
#   screen mi_herramienta():
#       tag menu
#       modal True
#       zorder 200
#       use tool_shell("Mi Herramienta"):
#           text "Contenido..." style "complements_detail_desc"
# ---------------------------------------------------------------------------

screen tool_shell(titulo):
    key "K_ESCAPE" action Show("complements")

    add gui.main_menu_background

    frame:
        style "complements_detail"
        xalign 0.5
        yalign 0.5
        xsize 800

        vbox:
            spacing 14

            text "[titulo]" style "complements_detail_title"

            transclude

            textbutton _("Volver"):
                style "complements_open"
                text_style "main_navigation_button_text"
                action Show("complements")
                at nav_button_anim
