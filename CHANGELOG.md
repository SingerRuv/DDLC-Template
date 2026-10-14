# Changelog

Todas las versiones notables de **DDLC BrokenDreamsModTemplate**.
El formato sigue [Keep a Changelog](https://keepachangelog.com/es/1.1.0/)
y el versionado [SemVer](https://semver.org/lang/es/).

## [Unreleased]

## [1.2.0] - 2026-10-14

### Añadido
- **Migración de assets:** cuando sale una versión nueva del template, el juego
  avisa y actualiza el template **conservando tus assets** (`mod_assets`, tu
  historia, tus `definitions` y `gui`). El reemplazo lo hace un script externo
  (`game/migracion/migrar.py`) al cerrar el juego. Solo se activa en proyectos
  derivados de un release (con `game/migracion/manifest.json`).
- **Controles táctiles + accesibilidad:** gestos (deslizar) para Atrás/Historial/
  Menú, quick menu escalado en pantallas táctiles, y acceso a la pantalla de
  accesibilidad de Ren'Py (self-voicing y opciones de texto). Se configuran desde
  Ajustes; en táctil arrancan activados.
- **Soporte Android:** en el primer arranque, el jugador extrae los assets de DDLC
  desde su APK/XAPK (o el ZIP de PC) a la carpeta del juego, con barra de progreso
  y cancelación, según las IP Guidelines de Team Salvato.
- **PoseLab:** ahora se elige la **familia** del transform (Normal / Instantáneo /
  Focus / Hop / Dip / Sink / Hop-focus / Entrada izq / Entrada der) además de la
  posición (slot 11..44).
- **Nuevos transforms** en `definitions/transforms.rpy`: `sink` + `s*`, `hopfocus`
  + `hf*`, `h*`, `d*`, `l11`/`r11` y `thide`.

### Corregido
- Codificación (mojibake) de `definitions/splash.rpy`.
- El sistema de migración no molesta en el repositorio fuente del template
  (no tiene manifest → queda inerte).

### Cambiado
- `screens.rpy`: la pantalla `choice` ya no usa la API obsoleta
  `im.MatrixColor`/`im.matrix` (migrada a `Transform(matrixcolor=…)`).
- `options.rpy`: el build incluye el target `android` y los permisos de
  almacenamiento.

### Limpieza
- Código muerto eliminado (~190 líneas): el bloque comentado *"Display
  Resolutions"*, `viewframe_options` y sus estilos, `screen rigged_choice`,
  `screen fake_skip_indicator`, `class RectCluster`, `pl_tool_por_id` y
  `style pl_panel`.

### Documentación
- `README.md`: secciones de controles táctiles/accesibilidad y de Android.
- `game/migracion/README.md`: guía del sistema de migración.

## [1.1.0] - 2026-10-11

### Añadido
- `mod_assets/` ahora forma parte del searchpath de Ren'Py (`core/0imports.rpy`):
  tus assets propios se pueden referenciar con nombre corto
  (`"images/bg/mi_cuarto.png"`) igual que los de DDLC, además de con la ruta
  completa `"mod_assets/..."`.

### Corregido
- La pestaña **Template Settings** (y su contenido) ya no aparece al publicar:
  solo se muestra con `config.developer = True`.
- `effects.rpy`: `recolorize()` ya no usa el manipulador de imagen obsoleto
  `im.MatrixColor` (migrado a `Transform(matrixcolor=…)`).

### Cambiado
- Limpieza interna: textos unificados («Plugins»), comentarios e indentación;
  se quitaron estilos y funciones sin uso.

### Documentación
- `README.md` y `mod_assets/README.md`: criterio unificado de `mod_assets`,
  prioridad de resolución de assets (`game/` suelto > `mod_assets/` suelto >
  `.rpa`) y eliminación de una referencia rota a `mod_assets/ejemplo.rpy`.

## [1.0.0] - 2026-10-07

Primera versión estable. Plantilla para crear mods de DDLC sobre Ren'Py 8,
con el look del DDLC Mod Template y sistemas listos para usar.

### Incluye
- Sistema de sprites estilo Bronya (`im.Composite`): poses de las 4 dokis
  (uniforme, casual y cuerpo completo), expandidas a todas las expresiones.
- Interfaz y menús del template (principal, pausa y quick menu) configurables
  desde `definitions/menu_screens.rpy`.
- Transforms, transiciones y efectos visuales.
- `mod_assets/`: carpeta para tus assets propios (fondos, CG, audio y sprites),
  con guía en `mod_assets/README.md`.
- Nombres de personaje ocultos al estilo de la plantilla original
  (`"???"` / `Chica 3/2/1`), para revelarlos en tu historia.
- Música del menú de pausa configurable con una línea (`config.game_menu_music`).
- Documentación para modders (`README.md`, `docs/IP-GUIDELINES.md`).

### Assets
- **No incluye** assets oficiales de DDLC: copiá `audio.rpa`, `fonts.rpa` e
  `images.rpa` de tu copia de DDLC a la carpeta `game/` (ver el README).
  Esto cumple las IP Guidelines de Team Salvato.

### Notas
- Requiere **Ren'Py 8.5.x**.
- Desarrollo y herramientas dev viven en la rama `dev`.

[Unreleased]: https://github.com/SingerRuv/DDLC-Template/compare/1.2.0...HEAD
[1.2.0]: https://github.com/SingerRuv/DDLC-Template/compare/1.1.0...1.2.0
[1.1.0]: https://github.com/SingerRuv/DDLC-Template/compare/1.0.0...1.1.0
[1.0.0]: https://github.com/SingerRuv/DDLC-Template/releases/tag/1.0.0
