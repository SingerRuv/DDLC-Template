## discord.rpy
## Configuración del Rich Presence de Discord.
##
## El motor vive en `game/core/discord_rpc.rpy` y la librería (pypresence 4.2.1,
## MIT) en `game/python-packages/pypresence/`.
##
## Para activarlo:
##   1. Creá una application en https://discord.com/developers/applications
##   2. Subí tus imágenes en "Rich Presence › Art Assets" y anotá sus nombres.
##   3. Pegá el Application ID en `discord_client_id` y los nombres acá abajo.
##
## Con `discord_client_id` vacío el módulo queda inerte: no se conecta a nada y
## la sección de Ajustes muestra "Deshabilitado". El jugador igual tiene que
## activarlo a mano (Ajustes › Discord RPC), porque por defecto está apagado.

define discord_client_id = ""

# Nombres de las imágenes (tal cual figuran en Art Assets de tu application).
define discord_image_logo = "mod_logo"
define discord_image_icon = "mod_icon"

## Ritmo de los envíos, en segundos.
# Discord acepta ~5 actualizaciones por 20 s: separamos los envíos.
define discord_update_interval = 15.0
# Reenvío de la misma actividad para detectar que Discord se cerró.
define discord_refresh_interval = 60.0
# Reintento de conexión cuando está habilitado y no hay conexión.
define discord_retry_interval = 30.0
