# Traducciones (`tl/`)

Ren'Py guarda las traducciones en `game/tl/<idioma>/`. Este template viene con
**español** (`game/tl/spanish/`), que traduce las pantallas y los textos base.

```
game/tl/spanish/
  common.rpy            textos comunes de Ren'Py
  screens.rpy           pantallas del template
  definitions/
    menu_screens.rpy    menús principal/pausa
    splash.rpy          splash y avisos
  core/
    discord_rpc.rpy     estados del Rich Presence
  migracion/
    migracion_ui.rpy    ventanas de migración (dev; entradas identidad)
  tools/
    complements.rpy     hub de Plugins (dev; entradas identidad)
    complements_ui.rpy  shell de Plugins (dev; entradas identidad)
```

El jugador cambia de idioma desde **Ajustes → Language** (screen
`choose_language` en `screens.rpy`).

## Cómo funciona

- Todo texto envuelto en `_("...")` es traducible. Ren'Py extrae esos textos y
  los empareja con el `old`/`new` de cada `.rpy` de `tl/`.
- El idioma activo queda en las preferencias del jugador
  (`_preferences.language`); no hace falta tocar nada en el guion.
- Los `.rpyc` de `tl/` son bytecode: se regeneran solos, no se editan.

## Agregar un idioma

1. En el launcher de Ren'Py: **Generate Translations** → elegí el proyecto y el
   nombre del idioma (por ejemplo `french`). Crea `game/tl/french/` con los
   archivos vacíos.
2. Traducí los bloques `old` / `new`.
3. El idioma aparece solo en el selector: el screen `choose_language` arma la
   lista desde las carpetas de `tl/`.

## Actualizar las traducciones

Cuando cambiás textos del template, los `old` viejos quedan huérfanos. Volvé a
correr **Generate Translations** (o **Update Translations** en el launcher) para
sincronizar. Las entradas sin `old` vigente se ignoran, no rompen nada.

## Textos de plugins y herramientas

Las pantallas de `game/tools/` son **dev-only** y no se traducen (no se
distribuyen). Si un plugin tuyo muestra texto al jugador, envolvelo en `_()`
igual que el resto y agregalo a tu idioma.

## Reglas

- Los `.rpy` de `tl/` van en **UTF-8 sin BOM** y saltos LF, como todo el
  proyecto.
- No traduzcas los `id` ni los nombres de variables, solo el texto de `new`.
- No dupliques entradas con el mismo `old`: Ren'Py usa la primera y avisa en
  `lint`.
