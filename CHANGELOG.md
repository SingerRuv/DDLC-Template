# Changelog

Todas las versiones notables de **DDLC BrokenDreamsModTemplate**.
El formato sigue [Keep a Changelog](https://keepachangelog.com/es/1.1.0/)
y el versionado [SemVer](https://semver.org/lang/es/).

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

[1.0.0]: https://github.com/SingerRuv/DDLC-Template/releases/tag/1.0.0
