## pose_lab_ui.rpy
## PoseLab — Interfaz: estilos, dropdown reutilizable y las ventanas flotantes
## (arrastrables) de controles y de código.

# ---------------------------------------------------------------------------
# Estilos de la herramienta (limpios, oscuros, sin depender del template).
# ---------------------------------------------------------------------------

style pl_text is text:
    color "#cfd3da"
    size 15

style pl_title is pl_text:
    size 22
    bold True
    color "#ffffff"

style pl_caption is pl_text:
    size 13
    bold True
    color "#7fb0ff"

style pl_hint is pl_text:
    size 13
    color "#8a8f98"

style pl_code is text:
    size 15
    color "#e6e6e6"

style pl_panel is frame:
    background "#20232a"
    padding (14, 14)
    xfill True

style pl_field is button:
    background "#2c313a"
    hover_background "#3a4150"
    padding (12, 8)
    xfill True

style pl_field_text is pl_text:
    size 15
    color "#ffffff"
    text_align 0.0
    xalign 0.0

style pl_options is vbox:
    background "#1a1d23"
    padding (6, 6)
    spacing 2
    xfill True

style pl_option is button:
    background None
    hover_background "#2c313a"
    selected_background "#2f4d7a"
    selected_hover_background "#3a5d92"
    padding (10, 6)
    xfill True

style pl_option_text is pl_text:
    size 14
    text_align 0.0
    xalign 0.0

style pl_button is button:
    background "#3a5d92"
    hover_background "#4a72ad"
    padding (16, 8)

style pl_button_text is pl_text:
    size 15
    color "#ffffff"

style pl_copy is button:
    background "#2c313a"
    hover_background "#3a4150"
    padding (12, 6)

style pl_copy_text is pl_text:
    size 14
    color "#9fc3ff"

# Barra de título de las ventanas flotantes (zona para arrastrar).
style pl_window_bar is frame:
    background "#2b303a"
    xfill True
    padding (12, 8)

style pl_window_bar_text is pl_text:
    size 15
    bold True
    color "#ffffff"

# Cuerpo de la ventana.
style pl_window is frame:
    background "#20232ae6"
    xfill True


# Dropdown limpio y reutilizable: título + botón de campo que despliega opciones.
screen pl_menu(titulo, actual, clave, opciones):
    vbox:
        spacing 4
        text "[titulo]" style "pl_caption"
        textbutton "[actual]":
            style "pl_field"
            action ToggleDict(pl_state, "open", clave, "")
        if pl_state["open"] == clave:
            vbox:
                style "pl_options"
                for texto, accion, elegido in opciones:
                    textbutton "[texto]":
                        style "pl_option"
                        selected elegido
                        action accion


# Ventana flotante de controles (se arrastra por la barra de título).
screen pl_controls(r):
    frame:
        style "pl_window"
        xsize 340

        vbox:
            spacing 0

            frame:
                style "pl_window_bar"
                text "PoseLab" style "pl_window_bar_text"

            frame:
                background None
                padding (14, 14)
                xfill True

                viewport:
                    ysize 620
                    scrollbars "vertical"
                    mousewheel True
                    draggable True

                    vbox:
                        spacing 10

                        text "Arma una pose y copia el codigo para tu guion." style "pl_hint"

                        use pl_menu("Personaje", pl_label(r["doki"]) or "—", "doki", [
                            (pl_label(d), pl_choose_doki(d), d == r["doki"]) for d in pl_personajes()
                        ])

                        # Cuerpo completo (pose 5): sección aparte, opcional.
                        if r["cuerpos"]:
                            use pl_menu("Cuerpo completo", r["cuerpo"] or "— usar pose normal", "cuerpo", [
                                ("— usar pose normal", pl_choose_cuerpo(""), r["cuerpo"] == "")
                            ] + [
                                (c, pl_choose_cuerpo(c), c == r["cuerpo"]) for c in r["cuerpos"]
                            ])

                        if not r["cuerpo"]:
                            use pl_menu("Outfit", pl_outfit_label(r["outfit"]), "outfit", [
                                (pl_outfit_label(o), pl_choose_outfit(o), o == r["outfit"]) for o in r["outfits"]
                            ])

                            use pl_menu("Pose", str(r["pose"]) if r["pose"] else "—", "pose", [
                                (str(p), pl_choose_pose(p), p == r["pose"]) for p in r["poses"]
                            ])

                            use pl_menu("Cara", pl_cara_label(r["cara"]), "cara", [
                                (pl_cara_label(c), pl_choose("cara", c), c == r["cara"]) for c in r["caras"]
                            ])

                        # Transforms separados por categoría.
                        use pl_menu("Posición", pl_trans_actual(_PL_POS), "trans", [
                            (t, pl_choose("trans", t), t == pl_state["trans"]) for t in _PL_POS
                        ])

                        use pl_menu("Focus", pl_trans_actual(_PL_FOCUS), "trans", [
                            (t, pl_choose("trans", t), t == pl_state["trans"]) for t in _PL_FOCUS
                        ])

                        use pl_menu("Entrada lateral", pl_trans_actual(_PL_ENTRADAS), "trans", [
                            (t, pl_choose("trans", t), t == pl_state["trans"]) for t in _PL_ENTRADAS
                        ])

                        use pl_menu("Fondo", r["fondo"] or "—", "fondo", [
                            (f, pl_choose("fondo", f), f == r["fondo"]) for f in pl_fondos()
                        ])


# Ventana flotante del bloque de código (se arrastra por la barra de título).
screen pl_code(txt_show):
    frame:
        style "pl_window"
        xsize 470

        vbox:
            spacing 0

            frame:
                style "pl_window_bar"
                text "Código" style "pl_window_bar_text"

            frame:
                background None
                padding (14, 14)
                xfill True

                vbox:
                    spacing 8

                    if txt_show:
                        text "[txt_show]" style "pl_code" xmaximum 430
                        textbutton "Copiar":
                            style "pl_copy"
                            action Function(pl_copiar, txt_show)
                    else:
                        text "Elegi personaje, outfit, pose y cara." style "pl_hint"
