## discord_rpc.rpy
## Motor del Rich Presence de Discord (pypresence 4.2.1).
##
## La configuración va en `game/definitions/discord.rpy` y la UI en
## Ajustes › Discord RPC (`screens.rpy`), que usa `RPC.rpc_connected`,
## `RPC.connect()` y `RPC.disconnect()`.
##
## Todo el diálogo con Discord corre en un hilo aparte: el hilo principal solo
## encola operaciones y aplica los resultados en `poll()`, así que un Discord
## colgado (o cerrado a mitad de partida) nunca congela el juego.

init -1 python in discord_rpc:

    import json
    import queue
    import threading
    import time

    import renpy
    import store

    try:
        import asyncio
        import pypresence
    except Exception:
        asyncio = None
        pypresence = None


    def _hash(actividad):
        """Firma de una actividad, para no reenviar lo que ya está puesto."""
        return hash(json.dumps(actividad, sort_keys=True))


    class _Worker(object):
        """Hilo daemon que ejecuta una operación de Discord a la vez."""

        def __init__(self):
            self._entrada = queue.Queue()
            self._salida = queue.Queue()
            self._hilo = threading.Thread(target=self._correr, name="discord_rpc", daemon=True)
            self._hilo.start()

        def encolar(self, funcion, callback):
            self._entrada.put((funcion, callback))

        def poll(self):
            """Corre en el hilo principal los callbacks de las operaciones listas."""
            while True:
                try:
                    callback, resultado, error = self._salida.get_nowait()
                except queue.Empty:
                    return
                callback(resultado, error)

        def esperar(self, tiempo):
            self._hilo.join(tiempo)

        def _correr(self):
            # pypresence pide el event loop con asyncio.get_event_loop(), que en
            # un hilo secundario no existe (Python 3.12): lo creamos acá.
            asyncio.set_event_loop(asyncio.new_event_loop())
            while True:
                funcion, callback = self._entrada.get()
                try:
                    resultado, error = funcion(), None
                except Exception as e:
                    resultado, error = None, e
                self._salida.put((callback, resultado, error))


    class DiscordRPC(store.NoRollback):
        """Estado del Rich Presence. `NoRollback` lo mantiene fuera de rollback
        y de los saves (nunca se reasigna el `define RPC`)."""

        def __init__(self):
            self.rpc_connected = False   # lo lee la UI de Ajustes
            self.last_error = ""
            self.start = int(time.time())  # contador "hace X" de Discord

            self._worker = _Worker()
            self._cliente = None
            self._epoch = 0              # invalida resultados de una sesión vieja
            self._abriendo = False
            self._encolado = False       # hay un update encolado
            self._ultimo_poll = 0.0
            self._ultimo_intento = 0.0
            self._ultimo_envio = 0.0
            self._hash_enviado = None
            self._error_impreso = ""

        # ---- API que usa la UI ---------------------------------------------

        def connect(self):
            if self._cliente is not None or self._abriendo or not self._habilitado():
                return

            self._abriendo = True
            self._ultimo_intento = time.time()
            epoch, client_id = self._epoch, store.discord_client_id
            actividad = store.discord_activity()
            self._worker.encolar(
                lambda: self._abrir(client_id, actividad),
                lambda cliente, error: self._abierto(epoch, actividad, cliente, error),
            )

        def disconnect(self):
            self._epoch += 1
            self._abriendo = False
            self._encolado = False
            self.rpc_connected = False
            self._hash_enviado = None
            self._ultimo_envio = 0.0

            cliente, self._cliente = self._cliente, None
            if cliente is not None:
                self._worker.encolar(lambda: self._cerrar(cliente), lambda *a: None)
            renpy.exports.restart_interaction()

        def update(self, force=False):
            """Manda la actividad actual si cambió (o si toca refrescarla)."""
            if self._cliente is None or self._encolado or self._abriendo:
                return

            actividad = store.discord_activity()
            firma = _hash(actividad)
            ahora = time.time()
            if not force:
                if (firma == self._hash_enviado and
                        ahora - self._ultimo_envio < store.discord_refresh_interval):
                    return
                if ahora - self._ultimo_envio < store.discord_update_interval:
                    return  # el poll lo reintenta apenas venza el intervalo

            self._encolado = True
            epoch, cliente = self._epoch, self._cliente
            self._worker.encolar(
                lambda: self._enviar(cliente, actividad),
                lambda _, error: self._enviado(epoch, firma, error),
            )

        def poll(self):
            """Procesa resultados y mantiene la presencia al día (1 vez por segundo)."""
            self._worker.poll()

            ahora = time.time()
            if ahora - self._ultimo_poll < 1.0:
                return
            self._ultimo_poll = ahora

            if not self._habilitado():
                return

            if self.rpc_connected:
                self.update()
            elif not self._abriendo and ahora - self._ultimo_intento >= store.discord_retry_interval:
                self.connect()

        def shutdown(self):
            """Cierra la conexión al salir del juego."""
            self._epoch += 1
            self.rpc_connected = False
            cliente, self._cliente = self._cliente, None
            if cliente is not None:
                self._worker.encolar(lambda: self._cerrar(cliente), lambda *a: None)
                self._worker.esperar(1.0)

        # ---- Interno --------------------------------------------------------

        def _habilitado(self):
            if pypresence is None or renpy.android:
                return False
            return bool(store.persistent.enable_discord and store.discord_client_id)

        def _abrir(self, client_id, actividad):
            """(hilo) Conecta y publica la primera actividad."""
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            cliente = None
            try:
                cliente = pypresence.Presence(client_id)
                cliente.connect()
                cliente.update(**actividad)
                return cliente
            except Exception:
                if cliente is not None:
                    self._cerrar(cliente)
                raise

        def _enviar(self, cliente, actividad):
            """(hilo) Actualiza la actividad de una conexión abierta."""
            cliente.update(**actividad)

        def _cerrar(self, cliente):
            """(hilo) Cierra la conexión sin propagar errores."""
            try:
                cliente.close()
            except Exception:
                pass

        def _abierto(self, epoch, actividad, cliente, error):
            self._abriendo = False

            if epoch != self._epoch:
                # Se desconectó mientras conectaba: cerramos lo que llegó tarde.
                if cliente is not None:
                    self._worker.encolar(lambda: self._cerrar(cliente), lambda *a: None)
                return

            if error is not None:
                self._fallo(error)
                return

            self._cliente = cliente
            self.rpc_connected = True
            self._hash_enviado = _hash(actividad)
            self._ultimo_envio = time.time()
            renpy.exports.restart_interaction()

        def _enviado(self, epoch, firma, error):
            self._encolado = False
            if epoch != self._epoch:
                return
            if error is not None:
                self._fallo(error)
                return

            self._hash_enviado = firma
            self._ultimo_envio = time.time()

        def _fallo(self, error):
            """Anota el error y descarta la conexión; el poll reintenta después."""
            self.last_error = str(error)
            if self.last_error != self._error_impreso:
                self._error_impreso = self.last_error
                print("discord_rpc:", self.last_error)
            self.disconnect()


    controller = DiscordRPC()


init python:

    def discord_activity():
        """Actividad de Discord según el estado actual del juego.

        Las imágenes son las subidas a tu application (ver
        `game/definitions/discord.rpy`); las que falten se omiten."""
        if store.main_menu:
            estado = _("In the main menu")
        else:
            estado = _("Chapter %d") % int(getattr(store, "chapter", 0) or 0)

        actividad = {
            "details": config.name,
            "state": estado,
            "large_image": store.discord_image_logo,
            "large_text": config.name,
            "small_image": store.discord_image_icon,
            "small_text": "v" + config.version,
            "start": RPC.start,
        }
        return {k: v for k, v in actividad.items() if v not in (None, "")}

    def _discord_poll():
        RPC.poll()

    def _discord_quit():
        RPC.shutdown()

    if _discord_poll not in config.periodic_callbacks:
        config.periodic_callbacks.append(_discord_poll)

    if _discord_quit not in config.quit_callbacks:
        config.quit_callbacks.append(_discord_quit)


# Objeto que espera la UI (screens.rpy). Nunca se reasigna: no entra en los saves.
define RPC = store.discord_rpc.controller
