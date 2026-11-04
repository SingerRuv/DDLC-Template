## creditos.rpy
## Pantalla de créditos del template.
##
## Es propia (no es la secuencia de créditos de DDLC): acredita al autor del
## template, al template base de bronya_rand y a ChromaGlitch.
## Ver docs/05-creditos.md.

style creditos_titulo is gui_text:
    size 38
    bold True
    color "#ffffff"
    outlines [(3, "#000000aa", 0, 0)]

style creditos_texto is gui_text:
    size 20
    color "#ffffff"
    outlines [(2, "#000000aa", 0, 0)]

style creditos_url is creditos_texto:
    size 17
    color "#ffe1ef"


screen creditos():
    tag menu

    use game_menu(_("Credits"), scroll="viewport"):

        vbox:
            xoffset 50
            xsize 900
            spacing 14

            text "Ryu MaGucci Mod Template" style "creditos_titulo"
            text _("Versión [config.version]") style "creditos_texto"

            null height 10

            text _("Hecho por Ryu MaGucci.") style "creditos_texto"

            text _("Basado en el DDLC Mod Template 2.0 de Azariel \"Bronya Rand\" Del Carmen (bronya_rand):"):
                style "creditos_texto"
            text "https://github.com/Bronya-Rand/DDLCModTemplate2.0" style "creditos_url"

            text _("Efectos de glitch por franjas: ChromaGlitch de Gouvernathor."):
                style "creditos_texto"
            text "https://github.com/Gouvernathor/renpy-ChromaGlitch" style "creditos_url"

            null height 10

            text _("Motor: Ren'Py [renpy.version_only].") style "creditos_texto"
            text _("Proyecto de fans no oficial, sin relación con Team Salvato."):
                style "creditos_texto"
            text _("Los assets de DDLC no se distribuyen con el template: los aporta cada modder desde su instalación."):
                style "creditos_texto"

            null height 10

            text _("Repositorio del template:") style "creditos_texto"
            text "https://github.com/SingerRuv/DDLC-Template" style "creditos_url"
