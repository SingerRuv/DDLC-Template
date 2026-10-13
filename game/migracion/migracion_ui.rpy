## migracion_ui.rpy
## Ventanas del sistema de migración de assets.
## La lógica vive en migracion.rpy. Reusa los estilos de menú del template.

init -1 python:
    def mg_ignorar_version(version):
        persistent.mg_ignorar = version

    def mg_resumen(reporte):
        """Arma las líneas del reporte de migración para mostrar en pantalla."""
        lineas = []
        if not reporte:
            return lineas
        lineas.append(_("Template: v%s a v%s") % (reporte.get("desde", "?"), reporte.get("hasta", "?")))
        if reporte.get("ok"):
            lineas.append(_("Se actualizaron %d archivos del template.") % reporte.get("copiados", 0))
            if reporte.get("conservados"):
                lineas.append(_("Se conservaron %d archivos tuyos.") % len(reporte["conservados"]))
            if reporte.get("conflictos"):
                lineas.append(_("¡Atención! Estos archivos tuyos también cambiaron en el template (se conservó tu versión):"))
                for r in reporte["conflictos"]:
                    lineas.append("    • " + r)
            if reporte.get("backup"):
                lineas.append(_("Respaldo de tus archivos: %s") % reporte["backup"])
        else:
            lineas.append(_("No se pudo migrar: %s") % reporte.get("error", ""))
        return lineas


screen migracion_panel():

    frame:
        style "migracion_borde"

        frame:
            style "migracion_frame"

            transclude


screen migracion_aviso(version, url):

    zorder 300
    modal True
    style_prefix "migracion"

    use migracion_panel:

        vbox:
            spacing 24

            text _("Actualización del template disponible"):
                style "migracion_titulo"

            text _("Hay una versión nueva del template (v[version]).\n¿Querés migrar tus assets a la nueva versión ahora?"):
                style "migracion_texto"

            hbox:
                spacing 22
                xalign 0.5

                textbutton _("Migrar ahora"):
                    style "navigation_button"
                    text_style "navigation_button_text"
                    action [Hide("migracion_aviso"), Show("migracion_confirmar", version=version, url=url)]

                textbutton _("Más tarde"):
                    style "navigation_button"
                    text_style "navigation_button_text"
                    action Hide("migracion_aviso")

                textbutton _("No volver a preguntar\npor esta versión"):
                    style "navigation_button"
                    text_style "navigation_button_text"
                    action [Function(mg_ignorar_version, version), Hide("migracion_aviso")]


screen migracion_confirmar(version, url):

    zorder 300
    modal True
    style_prefix "migracion"

    use migracion_panel:

        vbox:
            spacing 24

            text _("Migrar a la versión v[version]"):
                style "migracion_titulo"

            text _("Se respaldarán tus archivos, se actualizará el template y\ntus assets se conservarán.\n\nEl juego se cerrará y se volverá a abrir al terminar."):
                style "migracion_texto"

            hbox:
                spacing 24
                xalign 0.5

                textbutton _("Sí, migrar y cerrar"):
                    style "navigation_button"
                    text_style "navigation_button_text"
                    action Function(mg_migrar_y_salir, version, url)

                textbutton _("Cancelar"):
                    style "navigation_button"
                    text_style "navigation_button_text"
                    action Hide("migracion_confirmar")


screen migracion_al_dia(error=""):

    zorder 300
    modal True
    style_prefix "migracion"

    use migracion_panel:

        vbox:
            spacing 24

            if error:
                text _("No se pudo comprobar si hay actualizaciones."):
                    style "migracion_titulo"
                text "[error]":
                    style "migracion_texto"
            else:
                text _("Estás en la última versión del template."):
                    style "migracion_texto"

            textbutton _("Cerrar"):
                style "navigation_button"
                text_style "navigation_button_text"
                xalign 0.5
                action Hide("migracion_al_dia")


screen migracion_reporte(reporte):

    zorder 300
    modal True
    style_prefix "migracion"

    use migracion_panel:

        vbox:
            spacing 16

            text _("Migración de assets completada"):
                style "migracion_titulo"

            for linea in mg_resumen(reporte):
                text "[linea]":
                    style "migracion_texto"

            textbutton _("Entendido"):
                style "navigation_button"
                text_style "navigation_button_text"
                xalign 0.5
                action Return()


# ============================================================================
# ESTILOS
# ============================================================================

style migracion_borde is frame:
    xalign 0.5
    yalign 0.5
    padding (6, 6)
    background "#ec72a7"

style migracion_frame is frame:
    xpadding 44
    ypadding 32
    xmaximum 980
    background "#ffacd0"

style migracion_titulo is text:
    font "gui/font/RifficFree-Bold.ttf"
    size 34
    color "#fff"
    outlines [(3, text_outline_color, 0, 0), (2, text_outline_color, 1, 1)]

style migracion_texto is text:
    size 24
    color "#eaeaea"
