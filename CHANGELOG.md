# Changelog

Todas las versiones notables de **DDLC BrokenDreamsModTemplate**.
El formato sigue [Keep a Changelog](https://keepachangelog.com/es/1.1.0/)
y el versionado [SemVer](https://semver.org/lang/es/).

## [Unreleased]

## [1.3.0] - 2026-10-28

### Añadido
- **Hub de Plugins:** barra de herramientas compartida (Copiar, Copiar en…,
  Reiniciar, Abrir carpeta, Volver) para todas las herramientas.
- **Copiar en…:** panel que escribe el snippet en un `.rpy` del guion, con copia
  de seguridad y deshacer.
- **Shaders Lab (plugin):** vista previa de los shaders de fondo (scanlines,
  aberración cromática, viñeta, glitch y CRT), con glitch por franjas y cuadrados
  estilo DDLC.
- **Diálogo (plugin):** arma líneas de diálogo con énfasis (negrita, itálica,
  subrayado, tachado, color y tamaño) sobre la frase que marques, con vista previa
  del textbox del juego y la línea lista para copiar o insertar en el guion.
- **Text shaders:** `ts_glitch` para diálogo glitcheado, junto con los text shaders
  que trae Ren'Py (wave, jitter, dissolve, typewriter…).
- **Estilos:** catálogo global `tool_*` compartido por el hub y los plugins.
- **Plugins:** pueden traer lógica en Python (módulos con hooks `setup`, `open`
  y `close`) además de sus screens.
- **Docs:** guías reorganizadas y referencia generada desde el código
  (`docs/referencia/`), con `python tools/gen_docs.py --check` para validarla.

### Corregido
- **Diálogo:** el texto del `say` lleva un contorno, así se lee sobre cualquier
  fondo.
- **Interfaz:** se traducen al español los mensajes de error del motor.
- **Migración:** los avisos se muestran en la consola (antes solo iban al log).
- **Personaje MC:** se quita el personaje `mc` del template.

## [1.2.3] - 2026-10-22

### Corregido
- **Migración:** el `manifest.json` de las releases no incluía `game/tools/**`
  (hub de Plugins + PoseLab), así que al actualizar desde una versión anterior
  esas herramientas no se reemplazaban. Ahora se listan y se copian.
- **Migración:** al aplicar un `.rpy` actualizado se borra su `.rpyc` viejo,
  para que Ren'Py recompile en vez de seguir ejecutando el código anterior.

## [1.2.2] - 2026-10-22

### Añadido
- **Migración:** modo `--dry-run` para ver qué haría sin tocar nada, y registro
  de pasos en `game/migracion/migracion.log`.
- **PoseLab:** el panel "Código" muestra la línea con colores, se copia con
  Ctrl+C y las ventanas se pueden mover y fijar.

### Corregido
- **Migración:** si algo falla a mitad, revierte los archivos ya reemplazados y
  deja reporte; el juego se relanza siempre. Respeta los archivos que borraste,
  valida el ZIP (rutas y tamaño) y no cierra el juego si no hay ZIP o URL. La
  caché de versiones ya no se escribe desde un hilo.
- **PoseLab:** escribe los `.rpy` en LF (sin CRLF), con backup obligatorio y
  escritura atómica; el parser entiende `Composite` multilínea, comillas
  simples y archivos con BOM; el preview de líneas muestra `[` literal y las
  poses Focus se ven con su posición y zoom reales.
- **Android:** el botón Cancelar funciona durante la extracción y cancelar (o
  abrir en iOS) ya no muestra un traceback.
- **Sprites:** eliminadas definiciones duplicadas de Natsuki (`12b`/`42b`).
- **Efectos:** `Tear` usa el delta real de tiempo y `ParticleBurst` ya no
  modifica la lista mientras la recorre.
- **Aviso legal:** está en inglés (idioma base) con traducción al español.

### Cambiado
- Documentación: `im.Composite` → `Composite`; README del hub de Plugins.
- `options.rpy`: `config.check_conflicting_properties` y nota sobre
  `config.save_directory` en mods publicados.
- El hub de Plugins valida los tipos de `metadata()`.
- Codificación: todos los `.rpy` en UTF-8 sin BOM y LF.

## [1.2.1] - 2026-10-21

### Añadido
- **PoseLab:** soporte de sprites "cuerpo + expresión" (2 capas), tanto con
  definiciones `Composite` como con carpetas `Poses/` + `Expressions/`; aviso
  de personajes detectados y botón "Reescanear".
- **Sprites:** variantes de cara de Yuri (`a2`–`e2`, `y1`–`y7`) y de Natsuki
  (manga casual `12b`/`42b`, `scream`), en todas sus poses.

### Corregido
- El menú principal ya no re-anima (logo, fondo, sprites) al cambiar de idioma;
  solo cambia el texto y el fondo mantiene su paneo.

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
- El **ZIP de release** vuelve a incluir `game/tools/` (hub de **Plugins** + PoseLab):
  el patrón `tools/` del `export-ignore` lo excluía por error (el botón *Plugins*
  fallaba con `ScreenNotFound: 'complements'`).

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

[Unreleased]: https://github.com/SingerRuv/DDLC-Template/compare/1.2.3...HEAD
[1.2.3]: https://github.com/SingerRuv/DDLC-Template/compare/1.2.2...1.2.3
[1.2.2]: https://github.com/SingerRuv/DDLC-Template/compare/1.2.1...1.2.2
[1.2.1]: https://github.com/SingerRuv/DDLC-Template/compare/1.2.0...1.2.1
[1.2.0]: https://github.com/SingerRuv/DDLC-Template/compare/1.1.0...1.2.0
[1.1.0]: https://github.com/SingerRuv/DDLC-Template/compare/1.0.0...1.1.0
[1.0.0]: https://github.com/SingerRuv/DDLC-Template/releases/tag/1.0.0
