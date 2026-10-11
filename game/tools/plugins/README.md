# Herramientas (plugins)

Este hub permite crear **herramientas propias** para el template sin tocar su
código. Cada herramienta es una carpeta autocontenida dentro de
`game/tools/plugins/`, y el hub la descubre y muestra automáticamente.

> Dev-only: el botón **Herramientas** del menú principal solo aparece con
> `config.developer = True` (se oculta solo al publicar el juego).

## Estructura

```
game/tools/plugins/
  mi_herramienta/          <- tu carpeta (el nombre que quieras)
    tool.json              <- metadatos (obligatorio)
    mi_herramienta.rpy     <- tu screen (el que nombra tool.json)
    capturas/              <- opcional: PNG para el hub
      1.png
```

## `tool.json`

```json
{
  "id": "mi_herramienta",
  "titulo": "Mi Herramienta",
  "descripcion": "Qué hace, en una línea.",
  "autor": "Tu nombre",
  "version": "1.0",
  "screen": "mi_herramienta",
  "categoria": "Utilidades",
  "orden": 10,
  "icono": "icono.png",
  "palabras_clave": ["poses", "sprites"],
  "capturas": ["capturas/1.png"]
}
```

| Campo            | Obligatorio | Descripción                                                          |
|------------------|-------------|----------------------------------------------------------------------|
| `id`             | No          | Clave única. Por defecto, el nombre de la carpeta. Duplicados → diagnóstico. |
| `titulo`         | No          | Nombre visible en el hub. Por defecto, el nombre de la carpeta.       |
| `descripcion`    | No          | Texto del panel derecho.                                             |
| `autor`          | No          | Se muestra junto a la versión.                                       |
| `version`        | No          | Se muestra como `v1.0`.                                              |
| `screen`         | **Sí**      | Nombre del screen que abre la herramienta.                           |
| `categoria`      | No          | Agrupa herramientas en el hub (`"General"` por defecto).             |
| `orden`          | No          | Entero; ordena la lista (menor primero), luego por título.           |
| `icono`          | No          | PNG **relativo a la carpeta**; se valida que exista.                 |
| `palabras_clave` | No          | Lista de strings para la búsqueda del hub.                           |
| `capturas`       | No          | Rutas de PNG **relativas a la carpeta** del plugin.                  |
| `args`           | No          | Objeto con kwargs que se pasan al `Show(screen)` al abrir.           |
| `modulo`         | No          | Nombre del módulo Python del plugin (ver abajo).                     |
| `min_version`    | No          | Versión mínima de la API de plugins (`tools_api_version`).           |

\* Si `tool.json` está roto o falta, o el `screen` no existe, el plugin **no**
se muestra como herramienta pero **sí** aparece en el panel **Diagnóstico** del
hub, con el motivo. Nunca se descarta en silencio.

## Plugin en Python (`.py`)

Además del `.rpy` del screen, un plugin puede incluir lógica en Python. Declaras
el módulo en el manifiesto:

```json
{ "modulo": "mi_modulo" }
```

y pones `mi_modulo.py` dentro de la carpeta del plugin (la carpeta se agrega al
import path automáticamente). El hub lo importa y llama, **si existen**, estos
hooks opcionales:

```python
def metadata():
    """Dict opcional: sobreescribe campos cosméticos del manifiesto
    (titulo, descripcion, autor, version, categoria, palabras_clave, orden)."""
    return {"categoria": "Sprites"}

def setup(tool):
    """Una vez, al init. `tool` es el dict de la herramienta."""

def open(tool):
    """Al abrir la herramienta (desde el hub)."""

def close(tool):
    """Al cerrarla (el hub lo detecta)."""
```

El módulo puede importar otros `.py` de su propia carpeta (p. ej.
`import mi_helper`). Todos los errores de import/hook van a `log.txt` y **no**
rompen el hub.

> Nota: dentro de un módulo `.py`, el `open` global está tomado por Ren'Py y
> acepta un solo argumento. Si necesitas leer/escribir archivos, usa `io.open`.

## El screen

En tu `.rpy` define el screen que pusiste en `"screen"`. Lo más simple es usar
el shell reutilizable `tool_shell` (definido en `game/tools/complements.rpy`),
que aporta el fondo del menú, el título, ESC y el botón "Volver" al hub:

```renpy
screen mi_herramienta():
    tag menu
    modal True
    zorder 200

    use tool_shell("Mi Herramienta"):
        text "Contenido..." style "complements_detail_desc"
```

> Las propiedades del screen (`tag menu`, `modal True`, `zorder 200`) van en TU
> screen: no se transfieren al usar `tool_shell`.


### Estilos reutilizables

Para que tu herramienta se vea integrada, reutiliza estos estilos definidos en
`game/tools/complements.rpy`:

- `complements_detail` — tarjeta blanca semi-opaca (panel).
- `complements_detail_title` — título grande rosa.
- `complements_meta` — línea de autor/versión.
- `complements_detail_desc` — texto de descripción.
- `complements_section` — subtítulo de sección.
- `complements_open` / `complements_open_text` — botón (como los del menú).

Y el fondo del juego: `gui.main_menu_background`.

## Música (opcional)

Los eventos `on "show"`/`on "hide"` de un screen con `tag menu` no se disparan
de forma confiable. Si tu herramienta necesita música, manéjala desde el módulo
`.py` (hooks `open`/`close`):

```python
import renpy

def open(tool):
    renpy.music.play("bgm/2.ogg")

def close(tool):
    renpy.music.play(renpy.config.main_menu_music)
```

## Probar

1. Copia `_example/`, renómbrala y edita su `tool.json`.
2. Arranca el template y abre **Herramientas** en el menú principal.
3. Tu herramienta aparece como una tarjeta en el hub (con búsqueda, categorías
   y un botón para ocultarla o mostrarla).
