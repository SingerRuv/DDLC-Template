## pose_lab.rpy
## PoseLab: arma poses de los personajes leyendo las definiciones REALES de
## Composite de todos los .rpy del proyecto. No hay reglas fijas de nombres:
## lo que existe en sprites.rpy (o en cualquier .rpy) es lo que se puede armar.
## Esto funciona con los personajes del template y con personajes propios:
## basta con que definan `image <tag> <pose> = Composite(...)`.
##
## Es dev-only: se abre desde el hub "Herramientas" del menú principal.
## Salida: la línea `show <tag> <pose> at <transform> zorder 2` en un bloque.
##
## Organización: pose_lab_data.rpy (lógica), pose_lab_preview.rpy (lienzo),
## pose_lab_ui.rpy (estilos y ventanas). Este archivo solo compone la raíz.

screen pose_lab():
    tag menu
    modal True
    zorder 200

    # Al mostrarse: inicializa la selección (primera vez) y pone la música
    # propia de la herramienta. Al cerrarla, restaura la del menú.
    on "show" action [Function(pl_ensure_init), Function(pl_music_on)]
    on "hide" action Function(pl_music_off)

    # --- Resolución de la selección efectiva (cascada) ---
    $ r = pl_resuelto()
    $ txt_show = pl_show(r["doki"], r["nombre"], r["trans"])

    # Volver al hub de Herramientas.
    key "K_ESCAPE" action Show("complements")

    add Solid("#151515")

    # Preview a pantalla completa.
    add pl_preview(r["doki"], r["nombre"], r["trans"], r["fondo"])

    # Ventanas flotantes arrastrables.
    draggroup:
        drag:
            drag_name "pl_controls"
            draggable True
            drag_handle (0, 0, 1.0, 40)
            xpos 24
            ypos 24
            use pl_controls(r)

        drag:
            drag_name "pl_code"
            draggable True
            drag_handle (0, 0, 1.0, 40)
            xpos 790
            ypos 24
            use pl_code(txt_show)
