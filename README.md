<div align="center">

# DDLC BrokenDreamsModTemplate

**Un template de mods para Doki Doki Literature Club, hecho por Broken Dreams Studio.**

Basado en el [DDLC Mod Template 2.0](https://github.com/Bronya-Rand/DDLCModTemplate2.0) de Azariel "Bronya Rand" Del Carmen (bronya_rand).

`Ren'Py 8.5.3` · `Python 3.12` · `Windows / macOS / Linux / Android`

</div>

---

> [!IMPORTANT]
> Este es un **proyecto de fans no oficial**. No está afiliado a Team Salvato ni a bronya_rand.
> Doki Doki Literature Club es propiedad de **Team Salvato**. Requiere tener el juego original instalado.
> Ver las [IP Guidelines](https://teamsalvato.com/ip-guidelines).

## Overview

DDLC BrokenDreamsModTemplate es una base lista para crear mods de DDLC con el look y
los sistemas del template original, pero con todo **organizado, configurable y
documentado** para el flujo de trabajo de Broken Dreams Studio.

Incluye la interfaz de DDLC, el sistema de sprites estilo Bronya, transiciones,
efectos, menús configurables y un conjunto de ajustes para el jugador — todo con
valores por defecto sensatos que el modder puede cambiar sin tocar el motor.

- **Para quién:** quienes quieran empezar un mod con una base sólida y consistente.
- **Qué trae:** la interfaz de DDLC, el sistema de sprites (`Composite`),
  transforms, transiciones, efectos, menús configurables y ajustes del jugador.
- **Qué NO trae:** los **assets oficiales de DDLC** (sprites, fondos, música,
  fuentes **y la interfaz `gui/…`**) — se aportan desde tu copia del juego (ver
  abajo) — ni una historia escrita (cada mod pone la suya en `script.rpy`).

## Assets oficiales (IMPORTANTE)

Por las **[IP Guidelines de Team Salvato](https://teamsalvato.com/ip-guidelines)**,
este template **no incluye** los assets oficiales de Doki Doki Literature Club
(arte, música, fuentes). Debés aportarlos desde **tu propia copia de DDLC**.

Copiá estos archivos de tu instalación de DDLC a la carpeta `game/` del proyecto:

```
audio.rpa
fonts.rpa
images.rpa
```

Con eso, Ren'Py resolverá las rutas `images/…`, `bgm/…`, `sfx/…` y **`gui/…`**
(interfaz, menú, botones y fuentes). Sin ellos, el juego arranca pero **no se
verán sprites, fondos, interfaz ni sonará la música**.

### Android

En Android no se pueden copiar los `.rpa` a `game/` (van dentro del APK), así que
en el **primer arranque** el juego le pide al jugador **seleccionar su APK/XAPK de
DDLC (o el ZIP de PC)** y **extrae los assets solo** a la carpeta escribible
(IP Guidelines). No hace falta hacer nada: el flujo está en
`definitions/py/android_assets_ren.py` y la pantalla en `screens.rpy`.
Requiere los permisos de almacenamiento (ya configurados en `options.rpy`).

> **Ícono en Android:** si compilás para Android y falla el ícono de la ventana,
> agregá tu propio `game/gui/window_icon.png` (tu ícono/logo). Ojo: ese archivo
> **pisa** al del `.rpa`, así que también pasa a ser el logo del menú principal.

## Requisitos

- **[Ren'Py 8.5.x](https://www.renpy.org/latest.html)** (probado en 8.5.3).
- **[Doki Doki Literature Club](https://ddlc.moe/)** (PC), para los assets oficiales.

> [!WARNING]
> No pongas la carpeta de Ren'Py ni del proyecto en servicios de nube
> (Google Drive, OneDrive, etc.): causa problemas al testear el mod.

## Instalación

1. Instalá **Ren'Py 8.5.x**.
2. Copiá esta carpeta dentro de `renpy-8.5.x-sdk/Proyectos/` (o donde tengas tus proyectos).
3. **Aportá los assets** de tu copia de DDLC (`audio.rpa`, `fonts.rpa`, `images.rpa`)
   a la carpeta `game/` (ver sección "Assets oficiales").
4. Abrí el **Ren'Py Launcher** y seleccioná el proyecto **DDLC BrokenDreamsModTemplate**.
5. **Launch Project** para probarlo.

Para escribir tu historia podés empezar en `game/script.rpy` (`label start`) o
usar un archivo por capítulo en `game/` (ver
[`docs/00-empezar.md`](docs/00-empezar.md)).

## Estructura

```
game/
├── script.rpy            ← punto de entrada (label start / endgame)
├── screens.rpy           ← pantallas base (diálogo, guardado, ajustes...)
├── gui.rpy               ← colores, fuentes y medidas de la interfaz
├── options.rpy           ← nombre, versión, configuración de build
├── definitions/          ← sprites, transforms, audio, efectos, menús, splash
├── core/                 ← el motor del template (no tocar)
├── tools/                ← hub de Plugins (dev): PoseLab, Shaders Lab, Diálogo
├── migracion/            ← sistema de migración de assets entre versiones
├── mod_assets/           ← tus assets propios (imágenes, CGs, audio)
├── tl/                   ← traducciones (viene con español)
├── gui/                  ← solo los assets propios del template
└── *.rpa                 ← assets oficiales de DDLC (los aportás vos)

docs/                     ← guías para modders (empezá por docs/README.md)
tools/                    ← scripts de mantenimiento (no se distribuyen)
```

> Las carpetas `images/`, `bgm/`, `sfx/` y casi todo `gui/` **no están en el
> repo**: se resuelven desde los `.rpa` de DDLC. Tus propios assets van en
> `mod_assets/` (ver `game/mod_assets/README.md`).

## Features

- **Sprites estilo Bronya** (`Composite`): cientos de variantes por doki (más de
  700 en total) con notación compacta, ej. `show sayori 2b at t41`. Tabla
  completa en [`docs/referencia/sprites.md`](docs/referencia/sprites.md).
- **Transforms de posición:** `t11`–`t44`, focus `f*`, entradas laterales `l*`/`r*`,
  animaciones `hop`/`dip`, salidas `lhide`/`rhide`.
- **Transiciones:** `dissolve`, `dissolve_cg`, `close_eyes`, `open_eyes`,
  `wipeleft_scene`, `wiperight_scene`, `trueblack` y más.
- **Audio:** temas `t1`–`t10` (y variantes) + efectos de sonido.
- **Efectos:** `invert`, `tear`, `dizzy`, `recolorize` y partículas.
- **Shaders (plugin):** scanlines, aberración cromática, glitch, viñeta y CRT
  combinado, más glitch por **franjas y cuadrados** estilo DDLC, vendorizado de
  [ChromaGlitch](https://github.com/Gouvernathor/renpy-ChromaGlitch) de Gouvernathor.
  Se usan como transforms (`show bg class at sh_scanlines`) y hay una demo en el
  hub de Plugins. Ver `game/tools/plugins/shaders_lab/`.
- **Text shaders (dev):** `ts_glitch` para diálogo glitcheado (sacudida por glifo
  + separación RGB), más los text shaders incluidos en Ren'Py (wave, jitter,
  dissolve, typewriter…). Se aplican con `what_textshader` o `textshader`.
  Ver `game/definitions/textshaders.rpy`.
- **Diálogo (plugin):** arma líneas de diálogo con énfasis (negrita, itálica,
  subrayado, tachado, color y tamaño) sobre la frase que marques, con vista
  previa del textbox del juego y la línea lista para copiar o insertar en el
  guion. Se apoya en los tags de Ren'Py, sin motor propio. Ver
  `game/tools/plugins/dialogo_lab/` y `docs/referencia/dialogo.md`.
- **Hub de Plugins (dev):** catálogo de herramientas autocontenidas con búsqueda,
  categorías y diagnóstico; viene con **PoseLab** (arma poses leyendo los
  sprites reales y devuelve el `show` listo), **Shaders Lab** (vista previa de
  shaders de fondo) y **Diálogo** (énfasis en el texto del diálogo).
  Ver `game/tools/README.md`.
- **Menús configurables:** principal, de pausa y quick menu; sprites, logo,
  partículas y animación hover editables desde `definitions/menu_screens.rpy`.
- **Ajustes del Template:** el jugador puede activar/desactivar quick menu,
  animaciones del menú y partículas, cambiar su nombre y borrar todos los datos.
- **Traducciones:** español incluido; el jugador cambia de idioma desde Ajustes.
  Ver `game/tl/README.md`.
- **Splash + anti-cheat:** aviso legal al primer arranque, autoload y chequeo de partidas.
- **Controles táctiles + accesibilidad:** gestos (deslizar) para Atrás/Historial/Menú,
  quick menu agrandado y reposicionable en móvil, y acceso a la pantalla de
  accesibilidad de Ren'Py. Se configuran desde Ajustes (default: ON en táctil).
  Ver `game/definitions/touch.rpy`.
- **Android:** en el primer arranque, el jugador extrae los assets de DDLC desde su
  APK/XAPK (o el ZIP de PC) a la carpeta del juego (IP Guidelines). Ver
  `game/definitions/py/android_assets_ren.py`.
- **Migración de assets:** cuando sale una versión nueva del template, el juego te
  avisa y actualiza el template **conservando tus assets** (mod_assets, tu historia,
  tus `definitions` y `gui`). Ver `game/migracion/README.md`.
- **Discord Rich Presence:** muestra en tu perfil de Discord que estás jugando,
  con el capítulo actual y el tiempo jugado. Apagado por defecto; se activa en
  Ajustes › Discord RPC y se configura en `game/definitions/discord.rpy`. Ver
  [`docs/03-herramientas.md`](docs/03-herramientas.md).

## Documentación

- [`docs/README.md`](docs/README.md) — índice: empezar, historia, referencia,
  herramientas, publicar y créditos.
- [`docs/referencia/`](docs/referencia/) — tablas de sprites, transforms, audio,
  efectos, shaders, text shaders, efectos de diálogo (Diálogo) y plugins
  (generadas desde el código).
- [`docs/IP-GUIDELINES.md`](docs/IP-GUIDELINES.md) — resumen de las IP Guidelines de Team Salvato.
- `game/README.md` — mapa de las carpetas del proyecto.

## Créditos y licencia

- **DDLC Mod Template:** Azariel "Bronya Rand" Del Carmen
  ([bronya_rand](https://github.com/Bronya-Rand/DDLCModTemplate2.0)). Crédito obligatorio:
  *"This mod was made possible by bronya_rand's DDLC Mod Template 2.0"*.
- **Doki Doki Literature Club:** propiedad de **Team Salvato**
  ([IP Guidelines](https://teamsalvato.com/ip-guidelines)).
- **Autor de este template:** Broken Dreams Studio.

El código propio de Broken Dreams Studio se distribuye bajo licencia **MIT**
(ver [`LICENSE`](LICENSE)). El código y los assets heredados pertenecen a sus
autores originales (bronya_rand / Team Salvato).
