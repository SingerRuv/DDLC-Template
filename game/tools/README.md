# Herramientas (hub de Plugins)

El hub es la pantalla **Plugins** del menú principal: un catálogo de herramientas
de desarrollo, autocontenidas, que el template descubre solo.

> Es **dev-only**: el botón aparece solo con `config.developer = True` (true al
> correr desde el launcher, false en un build publicado). Ver
> `game/definitions/menu_screens.rpy`.

## Archivos

| Archivo | Rol |
|---|---|
| `complements.rpy` | Screen raíz del hub (`complements`): grilla de tarjetas, búsqueda, filtro y panel de diagnóstico |
| `complements_data.rpy` | Lógica sin UI: descubre plugins, lee y valida `tool.json`, busca, y carga los módulos `.py` con sus hooks |
| `complements_ui.rpy` | Piezas visuales del hub: la tarjeta (`pl_card`), el shell `tool_shell` y los estilos `complements_*`/`pl_*` |
| `inserter.rpy` | Panel **Insertar en…** compartido: escribe un snippet en un `.rpy` del guion (lo usan PoseLab y Diálogo) |
| `toolbar.rpy` | **Barra de herramientas** compartida por las herramientas dev: Copiar/Copiar en…, Reiniciar, Abrir carpeta y Volver |
| `ui_styles.rpy` | Catálogo **global** `tool_*` (textos, paneles, botones, inputs, barras) y los componentes `tool_dropdown` / `tool_barra` / `tool_shell` |
| `plugins/` | Un directorio por plugin (ver `plugins/README.md`) |

## Cómo descubre los plugins

Recorre `game/tools/plugins/<carpeta>/` y busca `tool.json`. El único campo
obligatorio es `"screen"`; el resto tiene valores por defecto (id y título =
nombre de la carpeta, categoría `General`, orden al final).

Si algo está mal (JSON roto, `screen` inexistente, `min_version` mayor que la
API), el plugin **no** se lista pero aparece en el panel **Diagnóstico** con el
motivo. Nunca se descarta en silencio.

Versión de la API: `tools_api_version = "1.0"` en `complements_data.rpy`. Un
plugin puede exigir una mínima con `"min_version"`.

Para escribir uno: `game/tools/plugins/README.md`.

## Refrescar sin reiniciar

`renpy.list_files()` es una foto del arranque: una carpeta nueva no aparece y
una borrada sigue estando. `tool_refrescar()` (en `complements_data.rpy`) vuelve
a listar los archivos con `renpy.loader.index_files()` y limpia las cachés de
`loadable` y de imágenes. Con eso, un plugin que lee archivos ve los cambios sin
cerrar la herramienta ni reiniciar el juego.

Un plugin se engancha con dos listas:

- `TOOL_REFRESCO_FNS` — funciones sin argumentos que limpian sus cachés
  (PoseLab registra `pl_limpiar_cache`).
- `TOOL_DIAG_FNS` — funciones que devuelven una lista de
  `{"id", "ruta", "motivo", "fatal"}` para el **Diagnóstico** del hub
  (PoseLab avisa ahí de definiciones que apuntan a `.png` borrados).

```python
init 10 python:
    TOOL_REFRESCO_FNS.append(mi_limpiar_cache)
    TOOL_DIAG_FNS.append(mi_diagnostico)
```

Escribir un `.rpy` es otro caso: el archivo cambia de fecha y el autoreload de
Ren'Py corre `reload_script()` a los ~1,5 s (guarda y recarga la partida). Por
eso `inserter.rpy` (y las definiciones de PoseLab) escriben con `auto_lock` +
`renpy.loader.add_auto(ruta, force=True)`, el mismo idiom de
`renpy/scriptedit.py`: el watcher toma ese mtime como referencia y no recarga.

Solo PoseLab necesita el *Reescanear* del disco. Shaders Lab lee
`renpy.list_images()` (imágenes ya registradas) y Diálogo usa sus propias
tablas: refrescarles el disco no mostraría nada nuevo.

## Estilos globales (`ui_styles.rpy`)

Namespace `tool_*`, pensado para que el hub y los plugins se vean igual sin
repetir propiedades. Las herramientas del juego (menús de DDLC, diálogo) **no**
se tocan.

| Grupo | Estilos |
|---|---|
| Textos | `tool_text`, `tool_title`, `tool_caption`, `tool_hint`, `tool_keyhint` |
| Ventanas | `tool_panel`, `tool_window`, `tool_window_bar`, `tool_window_title`, `tool_pin` |
| Botones | `tool_button`, `tool_button_small`, `tool_copy`, `tool_chip` |
| Listas | `tool_tray`, `tool_option`, `tool_line`, `tool_separator` |
| Código | `tool_code`, `tool_code_box` |
| Inputs | `tool_input_frame`, `tool_input`, `tool_hint` |
| Feedback | `tool_toast`, `tool_toast_text` |
| Barras | `tool_bar`, `tool_slider` |
| Dropdown | `tool_dropdown_header`, `tool_dropdown_header_text`, `tool_dropdown_value`, `tool_dropdown_item`, `tool_dropdown_item_text` |

Un plugin puede heredar de cualquiera:

```renpy
style mi_boton is tool_button
style mi_titulo is tool_title
```

### `tool_dropdown`

Acordeón inline: un encabezado clickeable (título arriba, valor en blanco
debajo) y las opciones debajo, cada una en su propio recuadro.

```renpy
use tool_dropdown(
    "sujeto",                          # id único (estado abierto/cerrado)
    "Aplicar a",                       # título del apartado
    shl_state["sujeto"],               # valor actual
    [("Fondo", "Fondo"), ("Personaje", "Personaje")],  # (valor, etiqueta)
    shl_state,                         # dict donde se guarda el valor
    "sujeto",                          # clave dentro del dict
    despues=[Function(shl_reset_efecto)],  # acciones extra al elegir (opcional)
    columnas=1)                        # cómo se acomodan las opciones (opcional)
)
```

`columnas` decide cómo se listan las opciones: `1` (default) una por fila, `2`
en dos columnas, `0` todas en una sola fila.

El estado vive en `tool_dd_state`, en el store, así funciona también dentro de
un `use` (no usa `SetScreenVariable`).

### `tool_toast` / `tool_copiar`

Aviso flotante (arriba, 2 segundos) y copia al portapapeles del sistema. Los
dos están en `ui_styles.rpy`, así ningún plugin reimplementa el toast:

```python
tool_toast("Código insertado")
tool_copiar("texto a copiar")           # avisa solo
```

### `tool_codigo_rico`

Resaltado de código para **mostrar** (no para copiar): devuelve el código con
tags de color de Ren'Py. El texto que se copia va plano.

```renpy
text "[tool_codigo_rico(txt)]" style "tool_code"
```

Colorea palabras clave (`show`, `at`, `as`, `expression`…), nombres, funciones,
números y cadenas. Si el código trae `[` o `]`, el `text` va con
`substitute False` y se pasa el string ya coloreado.

### `tool_barra` + ventanas flotantes

Barra de título reutilizable (zona para arrastrar + "Fijar" / "Restablecer") y
helpers de posición persistente. Cada plugin usa su prefijo para no chocar en
`persistent` y registra sus ventanas con `tool_ventanas_defecto`.

```python
# en el init del plugin (init 10: corre después de los bloques normales)
SHL_PREFIJO = "shl"
tool_ventanas_defecto({"code": (24, 400)}, SHL_PREFIJO)
```

```renpy
use tool_barra("Código", "code", SHL_PREFIJO, "shaders_lab")

draggroup:
    drag:
        id "shl_drag_code"              # convención: <prefijo>_drag_<nombre>
        drag_name "shl_code"
        draggable (not tool_ventana_fija("code", SHL_PREFIJO))
        drag_handle (0, 0, 1.0, 40)
        xpos tool_ventana_pos("code", SHL_PREFIJO)[0]
        ypos tool_ventana_pos("code", SHL_PREFIJO)[1]
        dragged tool_drag_mover("code", SHL_PREFIJO)
        use shl_code(txt)
```

La posición se guarda en `persistent.<prefijo>_pos_<nombre>` y sobrevive entre
sesiones. `Restablecer` la devuelve a la posición por defecto.

### `tool_toolbar`

Barra fija arriba, siempre visible, que comparten las herramientas dev
(PoseLab, Shaders Lab, Diálogo). Reusa los estilos del catálogo (`tool_panel`,
`tool_button`, `tool_title`): no define estilos propios.

```renpy
use tool_toolbar(
    titulo="PoseLab",              # nombre de la herramienta
    texto=txt_show,                # el código que copian "Copiar"/"Copiar en…"
    estado=pl_state,               # dict de la herramienta (lo usa "Copiar en…")
    marcador="poselab",            # línea que habilita un .rpy como destino
    sufijo=".poselab.bak",         # nombre del backup
    acciones=[                     # acciones propias de la herramienta
        ("Ocultar panel", Function(pl_alternar_panel)),
        ("Reiniciar", Function(pl_reset)),
    ])
```

Aporta además **Abrir carpeta** (abre la carpeta del proyecto en el
explorador del sistema).

### `tool_shell`

Shell para plugins simples: fondo del menú, título, ESC y botón "Volver" al hub.

```renpy
screen mi_plugin():
    tag menu
    modal True
    zorder 200

    use tool_shell("Mi Plugin"):
        text "Contenido..." style "complements_detail_desc"
```

Las propiedades del screen (`tag`, `modal`, `zorder`) van en **tu** screen: no se
transfieren con `use`.

## Documentación relacionada

- `game/tools/plugins/README.md` — manifiesto, hooks, música y estilos.
- `docs/03-herramientas.md` — guía de uso del hub, PoseLab y Shaders Lab.
