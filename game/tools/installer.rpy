## installer.rpy
## Instalador de plugins desde ZIP local: pantalla del hub.
##
## La lógica (validación, extracción atómica, instalar/actualizar/desinstalar)
## vive en installer_data.rpy.
##
## Se llega desde el botón "Instalar…" del hub (`complements.rpy`). Después de
## instalar o desinstalar hay que reiniciar: Ren'Py compila los .rpy al
## arrancar, así que un plugin nuevo no se puede mostrar en caliente.

style pl_ins_panel is tool_panel:
    background "#ffffff"
    padding (14, 10)

style pl_ins_row_title is tool_title:
    size 20
    bold True
    color "#cc6699"
    outlines []

style pl_ins_row_text is tool_text:
    size 14
    color "#444444"
    outlines []

style pl_ins_button is tool_button:
    background "#f4e3ec"
    hover_background "#f9d6e7"
    padding (12, 5)

style pl_ins_button_text is tool_button_text:
    size 15
    color "#7a3355"
    hover_color "#cc6699"
    outlines []


screen plugins_installer():
    tag menu
    modal True
    zorder 200

    # Volver al hub.
    key "K_ESCAPE" action Show("complements")

    # La acción pedida se procesa en el frame siguiente, para que el toast
    # ("Instalando…") llegue a pintarse antes de la extracción.
    if _pi_solicitud["archivo"] or _pi_solicitud["desinstalar"] is not None:
        timer 0.05 action Function(_pi_procesar)

    add gui.main_menu_background

    $ pendientes = _pi_listar()
    $ instalados = pl_plugins()[0]

    # ----- Panel izquierdo: título y accesos -----
    frame:
        style "main_menu_frame"

        vbox:
            xpos gui.navigation_xpos
            xoffset -50
            yoffset 24
            spacing 10

            text _("Instalador") style "pl_hub_title"
            text _("Dejá los .zip en _incoming y volvé a esta pantalla."):
                style "pl_ins_row_text"
                size 14
                xmaximum 220

            textbutton _("Abrir _incoming"):
                style "pl_dropdown"
                action Function(_pi_abrir_incoming)

            textbutton _("Reescanear"):
                style "pl_dropdown"
                action Function(tool_refrescar)

    # ----- Columna derecha: pendientes e instalados -----
    vbox:
        xpos 340
        ypos 24
        xsize 900
        spacing 8

        frame:
            style "pl_ins_panel"
            xsize 900
            ysize 540

            viewport:
                mousewheel True
                scrollbars "vertical"

                vbox:
                    xsize 830
                    spacing 12

                    if pendientes:
                        text _("Pendientes") style "complements_section"
                    else:
                        text _("No hay ZIPs en _incoming.") style "complements_detail_desc"

                    for item in pendientes:
                        hbox:
                            spacing 10

                            vbox:
                                xsize 620
                                spacing 2
                                text "[item['archivo']]" style "pl_ins_row_title"
                                if item["meta"]:
                                    text "[item['meta']['titulo']] · v[item['meta']['version']] · [max(1, item['bytes'] // 1024)] KB":
                                        style "pl_ins_row_text"
                                if item["aviso"]:
                                    text "[item['aviso']]":
                                        style "pl_ins_row_text"
                                        color "#a9791c"
                                if item["motivo"]:
                                    text "[item['motivo']]":
                                        style "pl_ins_row_text"
                                        color "#cc3333"

                            if item["meta"] and item["estado"] != "conflicto":
                                button:
                                    style "pl_ins_button"
                                    yalign 0.5
                                    action Function(_pi_pedir_instalar, item["archivo"])
                                    text "[item['etiqueta']]" style "pl_ins_button_text"

                    if instalados:
                        text _("Instalados") style "complements_section"

                    for t in instalados:
                        hbox:
                            spacing 10

                            vbox:
                                xsize 620
                                spacing 2
                                text "[t['titulo']]" style "pl_ins_row_title"
                                text "tools/plugins/[t['dir']] · v[t['version']]":
                                    style "pl_ins_row_text"

                            button:
                                style "pl_ins_button"
                                yalign 0.5
                                action Show("confirm",
                                            message="¿Borrar tools/plugins/%s? No hay vuelta atrás." % t["dir"],
                                            yes_action=[Function(_pi_pedir_desinstalar, t),
                                                        Hide("confirm")],
                                            no_action=Hide("confirm"))
                                text _("Desinstalar") style "pl_ins_button_text"

        # Resultado de la última acción.
        hbox:
            spacing 10
            if _pi_msg["texto"]:
                text "[_pi_msg['texto']]":
                    style "pl_ins_row_text"
                    size 15
                    xmaximum 720
                    color ("#3c7a3c" if _pi_msg["ok"] else "#cc3333")
            if _pi_msg["pendiente"]:
                button:
                    style "pl_ins_button"
                    action Function(_pi_reiniciar)
                    text _("Reiniciar ahora") style "pl_ins_button_text"

    # Volver al hub (esquina inferior derecha).
    textbutton _("Back"):
        style "main_navigation_button"
        text_style "main_navigation_button_text"
        xalign 1.0
        yalign 1.0
        xoffset -30
        yoffset -18
        action Show("complements")
