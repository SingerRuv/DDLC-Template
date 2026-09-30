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
  "capturas": ["capturas/1.png"]
}
```

| Campo         | Obligatorio | Descripción                                                        |
|---------------|-------------|--------------------------------------------------------------------|
| `id`          | No          | Identificador. Por defecto, el nombre de la carpeta.               |
| `titulo`      | No*         | Nombre visible en el hub. Por defecto, el nombre de la carpeta.     |
| `descripcion` | No          | Texto del panel derecho.                                           |
| `autor`       | No          | Se muestra junto a la versión.                                     |
| `version`     | No          | Se muestra como `v1.0`.                                            |
| `screen`      | **Sí**      | Nombre del screen que abre la herramienta.                         |
| `capturas`    | No          | Rutas de PNG **relativas a la carpeta** del plugin.                |

\* Si `tool.json` está roto, falta, o `screen` no existe, el plugin se salta
(el hub avisa en `log.txt` pero no falla).

## El screen

En tu `.rpy` define el screen que pusiste en `"screen"`:

```renpy
screen mi_herramienta():
    tag menu
    modal True
    zorder 200

    key "K_ESCAPE" action Show("complements")   # volver al hub
    add gui.main_menu_background                # mismo fondo del menú

    frame:
        style "complements_detail"
        xalign 0.5
        yalign 0.5
        xsize 640

        vbox:
            spacing 14
            text "Mi Herramienta" style "complements_detail_title"
            text "Contenido..." style "complements_detail_desc"
            textbutton "Volver":
                style "complements_open"
                text_style "main_navigation_button_text"
                action Show("complements")
                at nav_button_anim
```

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

Si tu herramienta quiere música propia, ponla en `on "show"` y restáurala en
`on "hide"` del screen:

```renpy
screen mi_herramienta():
    on "show" action Play("music", "bgm/2.ogg")
    on "hide" action Function(renpy.music.play, config.main_menu_music)
```

## Probar

1. Copiá `_example/`, renombrala y editá su `tool.json`.
2. Arrancá el template y abrí **Herramientas** en el menú principal.
3. Tu herramienta aparece en la lista; el panel derecho muestra sus datos y
   capturas.
