## shaders_lab.rpy
## Shaders Lab: demo del sistema de shaders del template. Se abre desde el hub
## de Plugins del menú principal (solo en modo dev) y no requiere assets: usa
## el fondo `bg class` y el sprite `yuri 1a` como referencia.
##
## Salida: los transforms `sh_*` están disponibles para usarlos en cualquier
## historia, sin abrir esta herramienta (ver shaders_lab_data.rpy).
##
## Organización: shaders_lab_data.rpy (registro y estado), shaders_lab_preview.rpy
## (lienzo), shaders_lab_ui.rpy (estilos y controles). Este archivo solo compone
## la raíz.

screen shaders_lab():

    tag menu
    modal True
    zorder 200

    # Volver al hub de Plugins.
    key "K_ESCAPE" action Show("complements")

    use shl_preview()

    use shl_controles()
