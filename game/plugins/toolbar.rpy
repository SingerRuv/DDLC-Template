## toolbar.rpy
## Barra de herramientas y botones de copia compartidos por las herramientas
## dev (PoseLab, Shaders Lab, Diálogo).
##
## La barra (`tool_toolbar`) aporta Abrir carpeta y Volver; los botones de
## copia (`tool_copiar_barra`) van dentro de la sección de código.
##
## Reusa los estilos del catálogo global (`tool_panel`, `tool_button`,
## `tool_title`): no define estilos propios.
##
## Es dev-only (la usan solo las herramientas del hub).
##
## Ver game/plugins/README.md.

init python:

    import os as _tb_os

    # ======================================================================
    # Carpeta del proyecto.
    # ======================================================================

    def tool_abrir_carpeta(rel=None):
        """Abre una carpeta del proyecto en el explorador del sistema.

        Sin argumentos abre la raíz del proyecto; con `rel` (p. ej.
        "plugins/_incoming") abre esa carpeta dentro de game/."""
        if rel:
            ruta = ins_ruta(rel)
            try:
                _tb_os.makedirs(ruta, exist_ok=True)
            except Exception:
                pass
        else:
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
            return
        tool_toast("Carpeta: %s" % ruta)
        renpy.restart_interaction()


# ---------------------------------------------------------------------------
# Barra de herramientas de la ventana.
#
# Aporta "Abrir carpeta" y "Volver". Las acciones de copia viven en
# `tool_copiar_barra`, dentro de la sección de código de cada herramienta.
# `acciones`: pares (etiqueta, acción) propios de cada herramienta.
# ---------------------------------------------------------------------------

screen tool_toolbar(titulo="", acciones=()):

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


# Botones de copia de la sección de código, compartidos por las herramientas.
# `acciones` permite sumar botones propios.
screen tool_copiar_barra(texto, estado=None, marcador="", sufijo=".bak", acciones=()):

    hbox:
        spacing 6

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
