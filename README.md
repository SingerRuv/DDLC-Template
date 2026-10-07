<div align="center">

# DDLC DokifileModTemplate

**Un template de mods para Doki Doki Literature Club, hecho por Studio Dokifiles.**

Basado en el [DDLC Mod Template 2.0](https://github.com/Bronya-Rand/DDLCModTemplate2.0) de Azariel "Bronya Rand" Del Carmen (bronya_rand).

`Ren'Py 8.5.3` · `Python 3.12` · `Windows / macOS / Linux / Android`

</div>

---

> [!IMPORTANT]
> Este es un **proyecto de fans no oficial**. No está afiliado a Team Salvato ni a bronya_rand.
> Doki Doki Literature Club es propiedad de **Team Salvato**. Requiere tener el juego original instalado.
> Ver las [IP Guidelines](https://teamsalvato.com/ip-guidelines).

## Overview

DDLC DokifileModTemplate es una base lista para crear mods de DDLC con el look y
los sistemas del template original, pero con todo **organizado, configurable y
documentado** para el flujo de trabajo de Studio Dokifiles.

Incluye la interfaz de DDLC, el sistema de sprites estilo Bronya, transiciones,
efectos, menús configurables y un conjunto de ajustes para el jugador — todo con
valores por defecto sensatos que el modder puede cambiar sin tocar el motor.

- **Para quién:** quienes quieran empezar un mod con una base sólida y consistente.
- **Qué trae:** la interfaz de DDLC, el sistema de sprites (`im.Composite`),
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
4. Abrí el **Ren'Py Launcher** y seleccioná el proyecto **DDLC DokifileModTemplate**.
5. **Launch Project** para probarlo.

Para escribir tu historia, editá `game/script.rpy`.

## Estructura

```
game/
├── script.rpy            ← tu historia empieza acá (label start)
├── screens.rpy           ← pantallas base (diálogo, guardado, ajustes...)
├── gui.rpy               ← colores, fuentes y medidas de la interfaz
├── options.rpy           ← nombre, versión, configuración de build
├── definitions/
│   ├── definitions.rpy   ← fondos (bg), personajes y variables
│   ├── sprites.rpy       ← todos los sprites de las dokis (im.Composite)
│   ├── transforms.rpy    ← posiciones, animaciones y transiciones
│   ├── music.rpy         ← música y efectos de sonido
│   ├── effects.rpy       ← efectos visuales especiales
│   ├── menu_screens.rpy  ← menús configurables
│   ├── cgs.rpy           ← tus CGs (imágenes de evento)
│   ├── persistent.rpy    ← variables que se guardan entre partidas
│   └── splash.rpy        ← splash, aviso legal y anti-cheat
├── core/                 ← el motor del template (no tocar)
├── gui/                  ← interfaz, fuentes y logo del template
├── images/               ← sprites, fondos y CGs (desde images.rpa)
├── bgm/                  ← música (desde audio.rpa)
├── sfx/                  ← efectos de sonido (desde audio.rpa)
├── mod_assets/           ← tus assets propios (fondos, CGs, audio, sprites)
└── tl/                   ← traducciones (ej: tl/spanish)

docs/                     ← documentación para modders
```

> Las carpetas `images/`, `bgm/` y `sfx/` se llenan al colocar los `.rpa` de DDLC.
> Tus propios assets van en `mod_assets/` (ver `game/mod_assets/README.md`).

## Features

- **Sprites estilo Bronya** (`im.Composite`): ~100 poses por personaje con
  notación compacta, ej. `show sayori 2b at t41`.
- **Transforms de posición:** `t11`–`t44`, focus `f*`, entradas laterales `l*`/`r*`,
  animaciones `hop`/`dip`, salidas `lhide`/`rhide`.
- **Transiciones:** `dissolve`, `dissolve_cg`, `close_eyes`, `open_eyes`,
  `wipeleft_scene`, `wiperight_scene`, `trueblack` y más.
- **Audio:** temas `t1`–`t10` (y variantes) + efectos de sonido.
- **Efectos:** `invert`, `tear`, `dizzy`, glitch de texto.
- **Menús configurables:** principal, de pausa y quick menu; sprites, logo,
  partículas y animación hover editables desde `definitions/menu_screens.rpy`.
- **Ajustes del Template:** el jugador puede activar/desactivar quick menu,
  animaciones del menú y partículas, cambiar su nombre y borrar todos los datos.
- **Splash + anti-cheat:** aviso legal al primer arranque, autoload y chequeo de partidas.

## Documentación

- [`docs/IP-GUIDELINES.md`](docs/IP-GUIDELINES.md) — resumen de las IP Guidelines de Team Salvato.
- `game/README.md` — mapa de las carpetas del proyecto.

> Se planea ampliar `docs/` con guías detalladas para modders (empezar, personajes,
> escena, audio, menús, efectos, historia) en el futuro.

## Créditos y licencia

- **DDLC Mod Template:** Azariel "Bronya Rand" Del Carmen
  ([bronya_rand](https://github.com/Bronya-Rand/DDLCModTemplate2.0)). Crédito obligatorio:
  *"This mod was made possible by bronya_rand's DDLC Mod Template 2.0"*.
- **Doki Doki Literature Club:** propiedad de **Team Salvato**
  ([IP Guidelines](https://teamsalvato.com/ip-guidelines)).
- **Autor de este template:** Studio Dokifiles.

El código propio de Studio Dokifiles se distribuye bajo licencia **MIT**
(ver [`LICENSE`](LICENSE)). El código y los assets heredados pertenecen a sus
autores originales (bronya_rand / Team Salvato).
