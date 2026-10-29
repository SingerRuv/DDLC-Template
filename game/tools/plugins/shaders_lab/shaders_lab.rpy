## shaders_lab.rpy
## Shaders Lab: demo del sistema de shaders del template. Se abre desde el hub
## de Plugins del menú principal (solo en modo dev) y no requiere assets: usa
## el fondo `bg class` como referencia.
##
## Salida: los transforms `sh_*` están disponibles para usarlos en cualquier
## historia, sin abrir esta herramienta (ver shaders_lab_data.rpy).
##
## Los efectos de TEXTO viven en el plugin Diálogo (`dialogo_lab`):
## énfasis del diálogo (negrita, itálica, color, tamaño).
##
## Organización: shaders_lab_data.rpy (registro y estado), shaders_lab_preview.rpy
## (lienzo), shaders_lab_ui.rpy (estilos y controles). Este archivo solo compone
## la raíz.
##
## Los efectos de franjas/cuadrados están vendorizados de "renpy-ChromaGlitch"
## de Gouvernathor (https://github.com/Gouvernathor/renpy-ChromaGlitch); ver
## glitch_slices_ren.py.

screen shaders_lab():

    tag menu
    modal True
    zorder 200

    # Volver al hub de Plugins.
    key "K_ESCAPE" action Show("complements")

    # Copiar el código del efecto elegido con Ctrl+C.
    key "ctrl_K_c" action Function(tool_copiar, shl_snippet())

    use shl_preview()

    # Ventanas flotantes arrastrables (la de controles y la del código).
    draggroup:
        if shl_state.get("panel", True):
            drag:
                id "shl_drag_controls"
                drag_name "shl_controls"
                draggable (not tool_ventana_fija("controls", SHL_PREFIJO))
                drag_handle (0, 0, 1.0, 40)
                xpos tool_ventana_pos("controls", SHL_PREFIJO)[0]
                ypos tool_ventana_pos("controls", SHL_PREFIJO)[1]
                dragged tool_drag_mover("controls", SHL_PREFIJO)
                use shl_controles()

        drag:
            id "shl_drag_code"
            drag_name "shl_code"
            draggable (not tool_ventana_fija("code", SHL_PREFIJO))
            drag_handle (0, 0, 1.0, 40)
            xpos tool_ventana_pos("code", SHL_PREFIJO)[0]
            ypos tool_ventana_pos("code", SHL_PREFIJO)[1]
            dragged tool_drag_mover("code", SHL_PREFIJO)
            use shl_code(shl_snippet())

    # Barra de herramientas (al final: queda por encima de las ventanas).
    use tool_toolbar(
        titulo="Shaders Lab",
        texto=shl_snippet(),
        estado=shl_state,
        marcador="shaders",
        sufijo=".shaders.bak",
        acciones=[
            ("Ocultar panel" if shl_state.get("panel", True) else "Mostrar panel",
             Function(shl_alternar_panel)),
            ("Reiniciar", Function(shl_reset)),
        ])
