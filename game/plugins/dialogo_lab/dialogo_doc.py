## dialogo_doc.py
## Datos para `tools/gen_docs.py`. No lo carga Ren'Py: es solo la fuente de la
## referencia `docs/referencia/dialogo.md`. Se mantiene como literal Python para
## poder leerlo con `ast.literal_eval`.

DIALOGO_DOC = {
    "efectos": [
        ["negrita", "Engruesa la frase (negrita sintética: no hace falta otra fuente).", "{b}…{/b}", "No"],
        ["italica", "Inclina la frase (itálica sintética).", "{i}…{/i}", "No"],
        ["subrayado", "Subraya la frase.", "{u}…{/u}", "No"],
        ["tachado", "Tacha la frase.", "{s}…{/s}", "No"],
        ["color", "Pinta la frase del color elegido (paleta o hexadecimal).", "{color=#ff8acc}…{/color}", "Sin cambio"],
        ["tamano", "Cambia el tamaño de la frase: pasos de ±2 y ±4 sobre los 24 px del estilo.", "{size=+2}…{/size}", "Normal"],
    ],
    "campos": [
        ["Texto del diálogo", "La línea que se arma. Va sin comillas: las agrega la herramienta."],
        ["Frase a resaltar", "Parte de la línea a la que se aplican los efectos. Si se repite, se resaltan todas las apariciones. Vacío = toda la línea."],
        ["Personaje", "Variable del Character que antecede a la línea (`s`, `m`, `n`, `y` o `narrator`)."],
        ["Incluir personaje", "Apagado, la salida es solo el texto (sin comillas), para pegarlo dentro de las tuyas."],
    ],
    "tags": [
        ["{b}…{/b}", "Negrita."],
        ["{i}…{/i}", "Itálica."],
        ["{u}…{/u}", "Subrayado."],
        ["{s}…{/s}", "Tachado."],
        ["{color=#ff8acc}…{/color}", "Color (hexadecimal o nombre)."],
        ["{size=+2}…{/size}", "Tamaño relativo al estilo; `+2` suma, `-2` resta."],
    ],
}
