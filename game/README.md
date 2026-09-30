# Contenido

### <u>gui</u>

Esta carpeta contiene las imágenes de la interfaz (botones, textbox, ventanas, menú, etc.) del template original de DDLC.

### <u>core</u>

Esta carpeta contiene los archivos necesarios para que el template funcione. (Imports y funciones helper)

### <u>definitions</u>

Esta carpeta contiene los archivos de definición de imágenes, sprites, música, etc. (CGs, Definiciones, Efectos, Splash, Transforms)

### <u>mod_assets</u>

Esta carpeta almacena todas tus imágenes, música/sfx y más relacionadas con tu juego. (Incluye el logo y la música del menú del template original.)

### <u>chrs</u>

Esta carpeta contiene los archivos de personajes (`.chr`) — easter egg del template original. El sistema `restore_characters()` los copia a la carpeta `characters/` según el playthrough.

### gui.rpy y screens.rpy — INCLUIDOS (look del template original)

`gui.rpy`, `screens.rpy` y la carpeta `gui/` (con las imágenes de la interfaz del
template original de DDLC, extraídas de sus archivos RPA) replican el look del
menú y la interfaz del mod template original.

Notas:
- El `screens.rpy` se adaptó para template genérico: se limpió la lógica
  específica de DDLC (playthrough, autoload, extras, etc.) pero se mantuvieron
  las características del mod original: modo uncensored, nombre del jugador y
  Discord RPC (opcional).
- La música del menú (audio/1.ogg, audio/m1.ogg) proviene del template original.

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
