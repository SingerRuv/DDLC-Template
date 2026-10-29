# Plugins

Este hub permite crear **plugins propios** para el template sin tocar su
código. Cada plugin es una carpeta autocontenida dentro de
`game/tools/plugins/`, y el hub lo descubre y muestra automáticamente.

> Dev-only: el botón **Plugins** del menú principal solo aparece con
> `config.developer = True` (se oculta solo al publicar el juego).

## Estructura

```
game/tools/plugins/
  mi_plugin/          <- tu carpeta (el nombre que quieras)
    tool.json         <- metadatos (obligatorio)
    mi_plugin.rpy     <- tu screen (el que nombra tool.json)
    capturas/         <- opcional: PNG para el hub
      1.png
```

## `tool.json`

```json
{
  "id": "mi_plugin",
  "titulo": "Mi Plugin",
  "descripcion": "Qué hace, en una línea.",
  "autor": "Tu nombre",
  "version": "1.0",
  "screen": "mi_plugin",
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
| `descripcion`    | No          | Texto de la tarjeta.                                                |
| `autor`          | No          | Se muestra junto a la versión.                                       |
| `version`        | No          | Se muestra como `v1.0`.                                              |
| `screen`         | **Sí**      | Nombre del screen que abre el plugin.                                |
| `categoria`      | No          | Agrupa plugins en el hub (`"General"` por defecto).                  |
| `orden`          | No          | Entero; ordena la lista (menor primero), luego por título.           |
| `icono`          | No          | PNG **relativo a la carpeta**; se valida que exista.                 |
| `palabras_clave` | No          | Lista de strings para la búsqueda del hub.                           |
| `capturas`       | No          | Rutas de PNG **relativas a la carpeta** del plugin.                  |
| `args`           | No          | Objeto con kwargs que se pasan al `Show(screen)` al abrir.           |
| `modulo`         | No          | Nombre del módulo Python del plugin (ver abajo).                     |
| `min_version`    | No          | Versión mínima de la API de plugins (hoy `"1.0"`; ver `tools_api_version` en `game/tools/complements_data.rpy`) |

\* Si `tool.json` está roto o falta, o el `screen` no existe, el plugin **no**
se muestra como plugin pero **sí** aparece en el panel **Diagnóstico** del
hub, con el motivo. Nunca se descarta en silencio.

### Capturas

`icono` y `capturas` son rutas **relativas a la carpeta** del plugin y se validan
(se avisa en Diagnóstico si no se pueden cargar). La tarjeta usa `icono`; si no
hay, usa **la primera captura**. La miniatura se encuadra en 80×80 (`contain`),
así que una captura 16:9 se ve con barras. No hay límite de tamaño, pero PNG de
menos de 500 KB mantienen el hub ágil.

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
    """Una vez, al init. `tool` es el dict del plugin."""

def open(tool):
    """Al abrir el plugin (desde el hub)."""

def close(tool):
    """Al cerrarlo (el hub lo detecta)."""
```

El módulo puede importar otros `.py` de su propia carpeta (p. ej.
`import mi_helper`). Todos los errores de import/hook van a `log.txt` y **no**
rompen el hub.

> Nota: dentro de un módulo `.py`, el `open` global está tomado por Ren'Py y
> acepta un solo argumento. Si necesitas leer/escribir archivos, usa `io.open`.

El plugin **`_example/`** usa esta API completa (`ejemplo_modulo.py`): es a la
vez la plantilla para copiar y el test de que los hooks funcionan.

### `.py` o `*_ren.py`

- `mi_modulo.py` es un **módulo**: solo se ejecuta cuando el hub lo importa.
- `mi_modulo_ren.py` es un módulo **y** un script de Ren'Py: su cabecera
  `"""renpy\ninit -N python:\n"""` hace que Ren'Py ejecute ese bloque al cargar.
  Usalo si tu plugin necesita registrar algo al arrancar (shaders, transforms,
  canales de audio) y no solo al abrirlo.

En los dos casos, el nombre del archivo (sin extensión) es el que va en
`"modulo"`. Si el archivo se llama `mi_modulo_ren.py`, el módulo se importa como
`mi_modulo_ren`.

## El screen

En tu `.rpy` define el screen que pusiste en `"screen"`. Lo más simple es usar
el shell reutilizable `tool_shell` (definido en `game/tools/complements_ui.rpy`),
que aporta el fondo del menú, el título, ESC y el botón "Volver" al hub:

```renpy
screen mi_plugin():
    tag menu
    modal True
    zorder 200

    use tool_shell("Mi Plugin"):
        text "Contenido..." style "complements_detail_desc"
```

> Las propiedades del screen (`tag menu`, `modal True`, `zorder 200`) van en TU
> screen: no se transfieren al usar `tool_shell`.


### Estilos reutilizables

El catálogo **global** está en `game/tools/ui_styles.rpy` (namespace `tool_*`):
textos, paneles, botones, inputs, barras, código y el dropdown. Heredá de ahí
para que tu plugin se vea igual que el resto:

```renpy
style mi_boton is tool_button
style mi_titulo is tool_title
```

El shell `tool_shell` y el dropdown `tool_dropdown` también viven en
`game/tools/` (ver `game/tools/README.md`). Los estilos `complements_*` (tarjeta
blanca del hub) siguen en `complements_ui.rpy`:

- `complements_detail` — tarjeta blanca semi-opaca (panel).
- `complements_detail_title` — título grande rosa.
- `complements_meta` — línea de autor/versión.
- `complements_detail_desc` — texto de descripción.
- `complements_section` — subtítulo de sección.
- `complements_open` — botón (como los del menú).

Y el fondo del juego: `gui.main_menu_background`.

## Música (opcional)

Los eventos `on "show"`/`on "hide"` de un screen con `tag menu` no se disparan
de forma confiable. Si tu plugin necesita música, manéjala desde el módulo
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
2. Arranca el template y abre **Plugins** en el menú principal.
3. Tu plugin aparece como una tarjeta en el hub (con búsqueda y filtro por
   categoría).
