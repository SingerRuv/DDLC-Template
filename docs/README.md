# Documentación

Guías para modders que usan **DDLC BrokenDreamsModTemplate**. Todo está en
español y asume Ren'Py 8.5.x.

## Por dónde empezar

| Quiero… | Leé |
|---|---|
| Instalar el template y ver algo en pantalla | [`00-empezar.md`](00-empezar.md) |
| Escribir la historia: labels, capítulos, personajes | [`01-historia.md`](01-historia.md) |
| Saber qué sprite/transform/audio/efecto usar | [`02-referencia.md`](02-referencia.md) |
| Usar el hub de Plugins y PoseLab | [`03-herramientas.md`](03-herramientas.md) |
| Publicar una versión del template (mantenedores) | [`04-publicar.md`](04-publicar.md) |
| Ver créditos, licencias y qué acreditar en tu mod | [`05-creditos.md`](05-creditos.md) |
| Cumplir las IP Guidelines de Team Salvato | [`IP-GUIDELINES.md`](IP-GUIDELINES.md) |

También hay documentación pegada al código, en cada carpeta:

- `game/README.md` — mapa completo de `game/`.
- `game/tools/README.md` — cómo funciona el hub de Plugins y sus estilos.
- `game/tools/plugins/README.md` — cómo escribir un plugin.
- `game/story/README.md` — convención para organizar la historia.
- `game/tl/README.md` — traducciones.
- `game/migracion/README.md` — sistema de migración de assets entre versiones.
- `tools/README.md` — scripts de mantenimiento (release y referencia).

## Referencia generada

Las tablas de sprites, transforms, audio, efectos y plugins **no se
escriben a mano**: las genera `tools/gen_docs.py` leyendo el código.

```
docs/referencia/
  sprites.md      variantes por personaje (pose → expresiones)
  transforms.md   familias de transforms y transiciones
  audio.md        música y efectos de sonido
  efectos.md      displayables, screens y animaciones
  plugins.md      plugins que descubre el hub
```

Para regenerarlas después de tocar el código:

```
python tools/gen_docs.py
python tools/gen_docs.py --check   # no escribe: falla si están desactualizadas
```

`--check` también valida que los enlaces relativos de toda la documentación
apunten a archivos que existan.

## Estado

- El **Discord RPC** está planificado pero todavía no implementado. El diseño y
  los requisitos están en el apéndice de [`03-herramientas.md`](03-herramientas.md).
