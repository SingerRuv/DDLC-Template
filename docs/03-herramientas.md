# Herramientas

Todas las herramientas de desarrollo se abren desde el **hub de Plugins**, en el
menú principal. El botón **Plugins** (arriba a la derecha) solo aparece con
`config.developer = True`, es decir: cuando corrés el proyecto desde el launcher
y no en un build publicado.

## Hub de Plugins

- Buscador y filtro por categoría.
- Una tarjeta por plugin, con título, descripción, autor/versión y capturas.
- Panel **Diagnóstico**: si un `tool.json` está roto, falta el screen o la versión
  de la API no alcanza, el plugin no se lista pero **sí** aparece ahí con el
  motivo. Nunca se descarta en silencio.

Cada plugin es una carpeta en `game/tools/plugins/<carpeta>/` con:

```
mi_plugin/
  tool.json      metadatos (obligatorio: "screen")
  mi_plugin.rpy  screen que abre el plugin
  capturas/      PNG opcionales para la tarjeta
```

Para escribir uno (manifiesto, hooks de Python, estilos `tool_*`, música), seguí
`game/tools/plugins/README.md`. La API actual es **1.0**
(`tools_api_version` en `game/tools/complements_data.rpy`) y un plugin puede
pedir una mínima con `"min_version"` en su `tool.json`.

La arquitectura del hub y los estilos globales están en `game/tools/README.md`;
la lista de plugins instalados se genera en
[`referencia/plugins.md`](referencia/plugins.md).

## PoseLab

Arma poses leyendo las definiciones **reales** de sprites del proyecto. No hay
reglas fijas de nombres: lo que exista como `image <tag> <nombre> = ...` y
referencie un `.png` se puede armar. Funciona con los personajes del template y
con personajes propios.

Campos:

| Campo | Qué elige |
|---|---|
| Personaje | Tag del sprite (`sayori`, `natsuki`, …) |
| Cuerpo completo | Poses de una sola capa (pose 5), si existen |
| Outfit | Variante de uniforme (`1`, `1b`, …) |
| Pose | Número de pose |
| Cara | Expresión |
| Variante | Familia de transform (`Normal`, `Focus`, `Hop`, …) |
| Posición | Slot `11`–`44` |
| Fondo | Fondo del preview (no cambia el código generado) |
| Zorder | Orden de dibujado (`zorder N`) |

Devuelve el código listo para pegar en el guion (el `zorder` también):

```renpy
show sayori 1a at t21 zorder 2
```

Botones útiles: **Copiar** (portapapeles), **Copiar en…** (inserta la línea en
un `.rpy` del proyecto, con backup y deshacer), **Reescanear** (si agregaste
sprites nuevos) y **Fijar** (deja la ventana de controles abierta).

Si encuentra carpetas de sprites propias **sin** definiciones (`image … =
Composite(…)`), ofrece crearlas: las escribe en `definitions/sprites.rpy` con
backup y avisa que se aplican al reiniciar el juego.

> El preview aplica el transform **real**, así que ves la misma animación y
> posición que en el juego.

## Shaders Lab

Vista previa de los shaders del template. No requiere assets: usa `bg class` y
un sprite de referencia.

- **Aplicar a:** `Fondo` o `Personaje` (y qué doki).
- **Efecto:** scanlines, aberración cromática, viñeta, glitch, CRT, contorno,
  silueta, palidez, flash y los glitches de ChromaGlitch (franjas, cuadrados).
- **Intensidad:** suave, media o fuerte (en los efectos que la admiten).

Abajo muestra el código para tu historia, por ejemplo:

```renpy
show yuri 1a at sh_contorno
show bg class at sh_crt
```

Los transforms `sh_*` están disponibles **sin abrir la herramienta** (ver
[`02-referencia.md`](02-referencia.md) y
[`referencia/shaders.md`](referencia/shaders.md)).

### Crear un shader propio

1. Registralo en un `init python` (como en
   `game/tools/plugins/shaders_lab/shaders_lab_data.rpy`):
   `renpy.register_shader("mi.nombre", variables=…, fragment_300=… )`.
   En `variables` declarás los `uniform` que vas a usar; después se pueden
   animar desde ATL (`linear 1.0 u_x 1.0`).
2. Creá un transform que lo aplique:

   ```renpy
   transform sh_mio(fuerza=0.5):
       mesh True
       shader "mi.nombre"
       u_fuerza fuerza
   ```

3. Cuidado con el **alpha premultiplicado**: multiplicá el RGB por el alpha o
   las zonas transparentes se pintan como un rectángulo.
4. Prioridades de los shaders de Ren'Py: `renpy.texture` = 200,
   `renpy.matrixcolor` = 400, `renpy.alpha` = 500. El código propio va en
   `fragment_300` para quedar entre textura y matriz de color.

## Apéndice: Discord RPC (planificado)

Todavía **no está implementado**; esto es el diseño acordado para cuando se
haga. La interfaz ya existe en `screens.rpy` (Ajustes → Discord RPC: estado,
Enable/Disable, Reconnect) y las traducciones también; falta el motor.

Qué se va a agregar:

- `game/python-packages/pypresence/` (versión 4.2.1, licencia MIT) + su LICENSE.
- `game/core/discord.rpy` con la clase `DiscordRPC` (hereda de `NoRollback`, así
  no se guarda en los saves) y el objeto global `RPC` que espera la UI.
- `define discord_client_id = ""`: vacío = módulo inerte. Cada mod debe crear su
  propia *application* en el Developer Portal de Discord, subir las imágenes y
  poner ahí su ID.
- Actualizaciones con **throttle de 15 s** (límite de Discord) y todo envuelto en
  `try/except`: sin librería, sin Discord abierto o con Discord cerrado a mitad
  de partida, la UI queda "Desconectado" sin traceback.
- **Apagado por defecto** (`persistent.enable_discord = False`) y sin datos
  personales: solo textos del mod y arte subido a la aplicación.
- En Android la sección no se muestra.

Pendiente al implementarlo: elegir las imágenes del *presence* y decidir si el
estado cambia solo por capítulo o solo mediante un helper que llame el guion.
