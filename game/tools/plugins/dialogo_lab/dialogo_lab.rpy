## dialogo_lab.rpy
## Diálogo — editor de estilo de diálogo del template.
##
## Es un plugin del hub (dev): arma una línea de diálogo con énfasis
## (negrita, itálica, subrayado, tachado, color y tamaño) sobre la frase que
## el modder marque, y la deja lista para copiar o insertar en el guion.
##
## No hay motor ni assets: el efecto se aplica con tags de Ren'Py, que son
## markup nativo. Lo que sale de la herramienta se pega en el guion y funciona.
##
## Organización: dialogo_lab_data.rpy (estado y construcción de la línea),
## dialogo_lab_ui.rpy (controles), dialogo_lab_preview.rpy (vista previa).
## Este archivo solo compone la raíz.

screen dialogo_lab():

    tag menu
    modal True
    zorder 200

    # Volver al hub de Plugins.
    key "K_ESCAPE" action Show("complements")

    # Copiar la línea con Ctrl+C.
    key "ctrl_K_c" action Function(tool_copiar, dlg_linea())

    # Fondo de la herramienta: el del menú principal, con su paneo en loop.
    # La tool reemplaza la screen del menú (tag menu), así que sin esto el
    # fondo del juego se queda negro.
    add "gui/menu_bg.png" at menu_bg_loop

    # Ventanas flotantes arrastrables (controles y vista previa).
    draggroup:
        if dlg_state.get("controles", True):
            drag:
                id "dlg_drag_controls"
                drag_name "dlg_controls"
                draggable (not tool_ventana_fija("controls", DLG_PREFIJO))
                drag_handle (0, 0, 1.0, 40)
                xpos tool_ventana_pos("controls", DLG_PREFIJO)[0]
                ypos tool_ventana_pos("controls", DLG_PREFIJO)[1]
                dragged tool_drag_mover("controls", DLG_PREFIJO)
                use dlg_controles()

        drag:
            id "dlg_drag_preview"
            drag_name "dlg_preview"
            draggable (not tool_ventana_fija("preview", DLG_PREFIJO))
            drag_handle (0, 0, 1.0, 40)
            xpos tool_ventana_pos("preview", DLG_PREFIJO)[0]
            ypos tool_ventana_pos("preview", DLG_PREFIJO)[1]
            dragged tool_drag_mover("preview", DLG_PREFIJO)
            use dlg_preview()

    # Barra de herramientas (al final: queda por encima de las ventanas).
    use tool_toolbar(
        titulo="Diálogo",
        texto=dlg_linea(),
        estado=dlg_state,
        marcador="dialogo",
        sufijo=".dialogo.bak",
        acciones=[
            ("Ocultar controles" if dlg_state.get("controles", True) else "Mostrar controles",
             Function(dlg_alternar_controles)),
            ("Reiniciar", Function(dlg_reset)),
        ])
