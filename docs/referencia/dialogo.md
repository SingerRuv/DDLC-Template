# Referencia — Estilo de diálogo (Diálogo)

> Generado por `tools/gen_docs.py` desde `game/tools/plugins/dialogo_lab/dialogo_doc.py`.
> **No editar a mano**: corré `python tools/gen_docs.py` después de tocar el código.

Plugin **Diálogo** (`game/tools/plugins/dialogo_lab/`). Arma líneas de diálogo con énfasis (negrita, itálica, subrayado, tachado, color y tamaño) sobre la frase que marques, y deja la línea lista para copiar o insertar en el guion.

No hay motor: el efecto se aplica con los tags de Ren'Py, que son markup nativo. Ver [`03-herramientas.md`](../03-herramientas.md).

## Efectos

| Efecto | Qué hace | Tag | Default |
|---|---|---|---|
| negrita | Engruesa la frase (negrita sintética: no hace falta otra fuente). | {b}…{/b} | No |
| italica | Inclina la frase (itálica sintética). | {i}…{/i} | No |
| subrayado | Subraya la frase. | {u}…{/u} | No |
| tachado | Tacha la frase. | {s}…{/s} | No |
| color | Pinta la frase del color elegido (paleta o hexadecimal). | {color=#ff8acc}…{/color} | Sin cambio |
| tamano | Cambia el tamaño de la frase: pasos de ±2 y ±4 sobre los 24 px del estilo. | {size=+2}…{/size} | Normal |

## Campos

| Campo | Qué hace |
|---|---|
| Texto del diálogo | La línea que se arma. Va sin comillas: las agrega la herramienta. |
| Frase a resaltar | Parte de la línea a la que se aplican los efectos. Si se repite, se resaltan todas las apariciones. Vacío = toda la línea. |
| Personaje | Variable del Character que antecede a la línea (`s`, `m`, `n`, `y` o `narrator`). |
| Incluir personaje | Apagado, la salida es solo el texto (sin comillas), para pegarlo dentro de las tuyas. |

## Tags de Ren'Py

| Tag | Qué hace |
|---|---|
| {b}…{/b} | Negrita. |
| {i}…{/i} | Itálica. |
| {u}…{/u} | Subrayado. |
| {s}…{/s} | Tachado. |
| {color=#ff8acc}…{/color} | Color (hexadecimal o nombre). |
| {size=+2}…{/size} | Tamaño relativo al estilo; `+2` suma, `-2` resta. |
