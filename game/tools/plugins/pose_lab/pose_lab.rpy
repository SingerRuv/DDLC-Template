## pose_lab.rpy
## PoseLab: arma poses de los personajes leyendo las definiciones REALES de
## Composite de todos los .rpy del proyecto. No hay reglas fijas de nombres:
## lo que existe en sprites.rpy (o en cualquier .rpy) es lo que se puede armar.
## Esto funciona con los personajes del template y con personajes propios:
## basta con que definan `image <tag> <pose> = Composite(...)`.
##
## Es dev-only: se abre desde el hub de Plugins del menú principal.
## Salida: la línea `show <tag> <pose> at <transform> zorder 2` en un bloque.
##
## Organización: pose_lab_data.rpy (lógica), pose_lab_preview.rpy (lienzo),
## pose_lab_ui.rpy (estilos y ventanas). Este archivo solo compone la raíz.

screen pose_lab():
    tag menu
    modal True
    zorder 200

    # Al mostrarse: inicializa la selección (primera vez) y avisa cuántos
    # personajes detectó (y si hay alguno nuevo respecto a la sesión anterior).
    # Un timer en vez de `on "show"`: el hub (mismo `tag menu`) reemplaza la
    # pantalla y el evento "show" no se dispara.
    timer 0.15 action [Function(pl_ensure_init), Function(pl_avisar_deteccion), Function(pl_ofrecer_definiciones)]

    # --- Resolución de la selección efectiva (cascada) ---
    $ r = pl_resuelto()
    $ txt_show = pl_codigo(r)

    # Volver al hub de plugins.
    key "K_ESCAPE" action Show("complements")

    # Copiar el código con Ctrl+C.
    key "ctrl_K_c" action Function(tool_copiar, txt_show)

    add Solid("#151515")

    # Preview a pantalla completa.
    use pl_preview(r["doki"], r["nombre"], r["trans"], r["fondo"], r["zorder"])

    # Ventanas flotantes arrastrables.
    draggroup:
        if pl_state.get("panel", True):
            drag:
                id "pl_drag_controls"
                drag_name "pl_controls"
                draggable (not tool_ventana_fija("controls", PL_PREFIJO))
                drag_handle (0, 0, 1.0, 40)
                xpos tool_ventana_pos("controls", PL_PREFIJO)[0]
                ypos tool_ventana_pos("controls", PL_PREFIJO)[1]
                dragged tool_drag_mover("controls", PL_PREFIJO)
                use pl_controls(r)

        drag:
            id "pl_drag_code"
            drag_name "pl_code"
            draggable (not tool_ventana_fija("code", PL_PREFIJO))
            drag_handle (0, 0, 1.0, 40)
            xpos tool_ventana_pos("code", PL_PREFIJO)[0]
            ypos tool_ventana_pos("code", PL_PREFIJO)[1]
            dragged tool_drag_mover("code", PL_PREFIJO)
            use pl_code(txt_show)

    # Barra de herramientas (al final: queda por encima de las ventanas).
    use tool_toolbar(
        titulo="PoseLab",
        texto=txt_show,
        estado=pl_state,
        marcador="poselab",
        sufijo=".poselab.bak",
        acciones=[
            ("Ocultar panel" if pl_state.get("panel", True) else "Mostrar panel",
             Function(pl_alternar_panel)),
            ("Reiniciar", Function(pl_reset)),
        ])
