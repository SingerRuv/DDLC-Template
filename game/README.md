# Contenido

### <u>gui</u>

Esta carpeta contiene las imágenes de la interfaz (botones, textbox, ventanas, menú, etc.),
las fuentes, el logo del template y los assets base (splash/avisos).

### <u>core</u>

Esta carpeta contiene los archivos necesarios para que el template funcione. (Imports y funciones helper)

### <u>definitions</u>

Esta carpeta contiene los archivos de definición de imágenes, sprites, música, etc. (CGs, Definiciones, Efectos, Splash, Transforms)

### <u>images</u>

Assets del juego: sprites de las dokis (`images/<doki>/`), fondos (`images/bg/`), CGs
(`images/cg/`) y transiciones (`images/menu/`). **No se incluyen:** provienen de los
archivos `.rpa` de tu copia de DDLC (ver el README raíz y `docs/IP-GUIDELINES.md`).

### <u>bgm</u> y <u>sfx</u>

Música (`bgm/`) y efectos de sonido (`sfx/`). **No se incluyen:** provienen de
`audio.rpa` de tu copia de DDLC.

### <u>mod_assets</u>

Carpeta para **tus assets propios** (los oficiales de DDLC salen de los `.rpa`).
Contiene `images/bg`, `images/cg`, `images/<personaje>` y `audio/bgm`, `audio/sfx`.
Se referencian con la ruta completa `"mod_assets/..."` o con nombre corto
(`"images/bg/mi_cuarto.png"`), porque `mod_assets` se agrega al searchpath en
`core/0imports.rpy`. Ver `mod_assets/README.md`.

### gui.rpy y screens.rpy — el look del template

`gui.rpy`, `screens.rpy` y la carpeta `gui/` definen el look del menú y la
interfaz. Los assets `gui/…` (menú, botones, marcos, fuentes, sonidos de la
interfaz) **no se versionan:** se resuelven del `.rpa` del jugador
(`images.rpa`, `fonts.rpa`, `audio.rpa`). Solo quedan versionados los assets
propios del template (`gui/buttons/btn_example_*`).

Para reemplazar cualquier asset de la interfaz por uno propio, poné el archivo
en `mod_assets/` con la **misma ruta** (`gui/…`): los archivos sueltos tienen
prioridad sobre el `.rpa`. La prioridad de resolución es: archivo suelto en
`game/` > archivo suelto en `mod_assets/` > `.rpa`.

Notas:
- El `screens.rpy` se adaptó para template genérico: se limpió la lógica
  específica de DDLC (playthrough, autoload, extras, etc.) pero se mantuvieron
  las características del mod original: modo uncensored y nombre del jugador.

Para personalizar colores de la interfaz, edita `gui.rpy` (variables
`gui.accent_color`, `gui.hover_color`, etc.).

### options.rpy

Este archivo define información sobre tu juego y contiene el código necesario para compilarlo.

### script.rpy

Este archivo es el script principal que Ren'Py llama para iniciar la historia de tu juego.

### Definición de la estructura (resumen del sistema original de DDLC)

- Los **personajes** se declaran en `definitions/definitions.rpy` con `DynamicCharacter` y su nombre se define en `script.rpy` (`$ s_name = "???"`). Los sprites viven en `definitions/sprites.rpy` con `im.Composite` (sistema Bronya).
- La **música** y **fondos** se declaran en `definitions/definitions.rpy` con `define audio.x` e `image bg x`.
- Las **transiciones y animaciones** viven en `definitions/transforms.rpy`.
- La **historia** se organiza en archivos de script por capítulos, llamados desde `script.rpy` con `call capituloX`.
- El **código Python** se separa de los `.rpy` guardándolo en carpetas `py/` con archivos `*_ren.py`.
- Cada subcarpeta tiene un `README.md` que documenta qué hacía cada archivo en el template original.
