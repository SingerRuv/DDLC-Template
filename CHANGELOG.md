# Changelog

Todas las versiones notables de **DDLC BrokenDreamsModTemplate**.
El formato sigue [Keep a Changelog](https://keepachangelog.com/es/1.1.0/)
y el versionado [SemVer](https://semver.org/lang/es/).

## [Unreleased] — 1.1.0

### Añadido
- `mod_assets/` ahora forma parte del searchpath de Ren'Py (`core/0imports.rpy`):
  tus assets propios se pueden referenciar con nombre corto
  (`"images/bg/mi_cuarto.png"`) igual que los de DDLC, además de con la ruta
  completa `"mod_assets/..."`.

### Corregido
- La pestaña **Template Settings** (y su contenido) ya no aparece al publicar:
  solo se muestra con `config.developer = True`.

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

[Unreleased]: https://github.com/SingerRuv/DDLC-Template/compare/1.0.0...HEAD
[1.0.0]: https://github.com/SingerRuv/DDLC-Template/releases/tag/1.0.0
