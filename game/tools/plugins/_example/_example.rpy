## _example.rpy
## Herramienta de ejemplo para el hub "Herramientas".
##
## Copia la carpeta _example/, renómbrala (p. ej. mi_herramienta/), edita su
## tool.json y reescribe este screen. El hub la descubre solo.
##
## Este ejemplo usa el shell reutilizable `tool_shell` (definido en
## game/tools/complements.rpy), que aporta fondo, título, ESC y el botón
## "Volver" al hub. Tu screen solo define tag/modal/zorder y el contenido.
##
## Ver game/tools/plugins/README.md.

screen example_tool():
    tag menu
    modal True
    zorder 200

    use tool_shell("Ejemplo"):
        text "Esta es una herramienta de ejemplo. Reemplaza este contenido por el tuyo." style "complements_detail_desc"
