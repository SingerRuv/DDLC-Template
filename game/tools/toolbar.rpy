## toolbar.rpy
## Barra de herramientas compartida por las herramientas dev (PoseLab,
## Shaders Lab, Diálogo). Fija arriba y siempre visible.
##
## Cada herramienta pasa su código (lo que se copia) y sus acciones propias;
## la barra aporta las comunes: Abrir carpeta y Volver.
##
## Reusa los estilos del catálogo global (`tool_panel`, `tool_button`,
## `tool_title`): la barra no define estilos propios.
##
## Es dev-only (la usan solo las herramientas del hub).
##
## Ver game/tools/README.md.

init python:

    import os as _tb_os

    # ======================================================================
    # Carpeta del proyecto.
    # ======================================================================

    def tool_abrir_carpeta():
        """Abre la carpeta del proyecto en el explorador del sistema."""
        ruta = renpy.config.basedir
        try:
            if renpy.windows:
                _tb_os.startfile(ruta)
            elif renpy.macintosh:
                import subprocess as _tb_sp
                _tb_sp.Popen(["open", ruta])
            else:
                import subprocess as _tb_sp
                _tb_sp.Popen(["xdg-open", ruta])
        except Exception:
            tool_toast("No se pudo abrir la carpeta")
            renpy.restart_interaction()
            return False
        tool_toast("Carpeta: %s" % ruta)
        renpy.restart_interaction()
        return True


# ---------------------------------------------------------------------------
# La barra.
#
# texto:   el código que copian "Copiar" y "Copiar en…".
# estado:  dict de la herramienta (lo usa el panel "Copiar en…").
# marcador/sufijo: los que el panel "Copiar en…" necesita para saber dónde
#           escribir y cómo nombrar el backup.
# acciones: pares (etiqueta, acción) propios de cada herramienta.
# ---------------------------------------------------------------------------

screen tool_toolbar(titulo="", texto="", estado=None, marcador="", sufijo=".bak",
                    acciones=()):

    # Reusa el catálogo global (`tool_panel`, `tool_button`, `tool_title`): la
    # barra se ve como el resto de las herramientas sin estilos nuevos.
    frame:
        style "tool_panel"
        padding (12, 4)
        xalign 0.5
        ypos 0

        hbox:
            spacing 6

            if titulo:
                text titulo style "tool_title" size 15 yalign 0.5

            if texto:
                textbutton "Copiar":
                    style "tool_button"
                    action Function(tool_copiar, texto)

                textbutton "Copiar en…":
                    style "tool_button"
                    action Show("tool_destino",
                                estado=estado,
                                texto=texto,
                                marcador=marcador,
                                titulo="Copiar en…",
                                aviso=tool_toast,
                                sufijo=sufijo)

            for etiqueta, accion in acciones:
                textbutton etiqueta:
                    style "tool_button"
                    action accion

            null width 14

            textbutton "Abrir carpeta":
                style "tool_button"
                action Function(tool_abrir_carpeta)

            textbutton "Volver":
                style "tool_button"
                action Show("complements")
