## _example.rpy
## Plugin de ejemplo para el hub de Plugins.
##
## Copia la carpeta _example/, renómbrala (p. ej. mi_plugin/), edita su
## tool.json y reescribe este screen. El hub la descubre solo.
##
## Este ejemplo usa el shell reutilizable `tool_shell` (definido en
## game/tools/complements_ui.rpy), que aporta fondo, título, ESC y el botón
## "Volver" al hub. Tu screen solo define tag/modal/zorder y el contenido.
##
## La lógica en Python va en un módulo aparte (ejemplo_modulo.py), que el hub
## importa y llama con los hooks setup/open/close. Ver
## game/tools/plugins/README.md.
##
## Ver game/tools/plugins/README.md.

## El módulo escribe acá cuando se abre la herramienta.
default ejemplo_veces = 0


screen example_tool():
    tag menu
    modal True
    zorder 200

    use tool_shell("Ejemplo"):
        text "Esta es una herramienta de ejemplo. Reemplaza este contenido por el tuyo." style "complements_detail_desc"
        text "El módulo la abrió [ejemplo_veces] vez(es)." style "complements_detail_desc"
