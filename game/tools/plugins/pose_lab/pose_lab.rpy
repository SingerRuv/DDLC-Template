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

    # Al mostrarse: inicializa la selección (primera vez).
    on "show" action Function(pl_ensure_init)

    # --- Resolución de la selección efectiva (cascada) ---
    $ r = pl_resuelto()
    $ txt_show = pl_show(r["doki"], r["nombre"], r["trans"], r["zorder"])

    # Volver al hub de plugins.
    key "K_ESCAPE" action Show("complements")

    add Solid("#151515")

    # Preview a pantalla completa.
    use pl_preview(r["doki"], r["nombre"], r["trans"], r["fondo"], r["zorder"])

    # Ventanas flotantes arrastrables.
    draggroup:
        drag:
            id "pl_drag_controls"
            drag_name "pl_controls"
            draggable (not pl_ventana_fija("controls"))
            drag_handle (0, 0, 1.0, 40)
            xpos pl_ventana_pos("controls")[0]
            ypos pl_ventana_pos("controls")[1]
            dragged pl_drag_mover("controls")
            use pl_controls(r)

        drag:
            id "pl_drag_code"
            drag_name "pl_code"
            draggable (not pl_ventana_fija("code"))
            drag_handle (0, 0, 1.0, 40)
            xpos pl_ventana_pos("code")[0]
            ypos pl_ventana_pos("code")[1]
            dragged pl_drag_mover("code")
            use pl_code(txt_show)
