# Contenido de `game/`

Mapa de la carpeta. Para el flujo de trabajo, ver [`docs/`](../docs/README.md).

## Carpetas

| Carpeta | Qué contiene |
|---|---|
| `core/` | El motor del template: imports tempranos, funciones de ayuda y Discord RPC. No tocar (ver `core/README.md`) |
| `definitions/` | Definiciones: imágenes, sprites, música, efectos, transforms, menús, splash y variables persistentes (ver `definitions/README.md`) |
| `mod_assets/` | **Tus** assets: imágenes, CGs y audio (ver `mod_assets/README.md`) |
| `tools/` | Hub de Plugins (dev-only) y herramientas: PoseLab, Shaders Lab, Diálogo (ver `tools/README.md`) |
| `migracion/` | Sistema de migración de assets entre versiones del template (ver `migracion/README.md`) |
| `tl/` | Traducciones; viene con español (ver `tl/README.md`) |
| `python-packages/` | Librerías de Python de terceros (hoy solo `pypresence` 4.2.1, MIT). Ren'Py agrega la carpeta al `sys.path` sola |
| `gui/` | Solo los assets **propios** del template (`gui/buttons/btn_example_*`). El resto de la interfaz se resuelve desde `images.rpa` y `fonts.rpa` |
| `saves/` | Partidas locales y persistentes. No se versiona |

## Archivos de la raíz de `game/`

| Archivo | Qué hace |
|---|---|
| `script.rpy` | Punto de entrada: `label start` y `label endgame` |
| `screens.rpy` | Pantallas base: diálogo, guardado, ajustes, historial, confirmaciones, NVL, selector de idioma y Android |
| `gui.rpy` | Colores, fuentes, tamaños y medidas de la interfaz |
| `options.rpy` | Nombre, versión, música del menú, carpeta de guardado y configuración del build |
| `*.rpa` | Assets oficiales de DDLC que aporta cada modder/jugador (`images`, `fonts`, `audio`). No se versionan |

## Assets de DDLC

Los `.rpa` de DDLC no se incluyen en el repo (IP Guidelines). Al colocarlos en
`game/`, Ren'Py resuelve `images/…`, `bgm/…`, `sfx/…` y `gui/…` desde ahí.

Prioridad de resolución de un asset:

1. Archivo suelto en `game/`.
2. Archivo suelto en `mod_assets/` (agregado al searchpath en `core/0imports.rpy`).
3. Archivo dentro de un `.rpa`.

Por eso podés pisar un asset oficial poniendo un archivo con la misma ruta en
`mod_assets/` (por ejemplo `mod_assets/gui/window_icon.png`).

## Reglas del proyecto

- Los `.rpy` van en **UTF-8 sin BOM** y saltos **LF**.
- Tu historia y tus assets van en `game/` y `mod_assets/`; el motor no se toca.
- Si agregás una herramienta, va como plugin en `tools/plugins/` (ver
  `tools/plugins/README.md`).
