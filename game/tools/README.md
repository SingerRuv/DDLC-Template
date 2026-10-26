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
| `ui_styles.rpy` | Catálogo **global** `tool_*` (textos, paneles, botones, inputs, barras) y los componentes `tool_dropdown` / `tool_shell` |
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
    despues=[Function(shl_reset_efecto)])  # acciones extra al elegir (opcional)
)
```

El estado vive en `tool_dd_state`, en el store, así funciona también dentro de
un `use` (no usa `SetScreenVariable`).

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
- `docs/03-herramientas.md` — guía de uso del hub y PoseLab.
