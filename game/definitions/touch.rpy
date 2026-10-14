## touch.rpy
## Controles táctiles (gestos + quick menu) y acceso a la accesibilidad.
## Pensado mobile-first. Todo configurable por el modder desde acá.
##
## Cómo funciona: Ren'Py reconoce "gestos" (trazos largos, en 8 direcciones) y
## `config.gestures` mapea cada gesto a un EVENTO; un `renpy.Keymap` (que
## agregamos abajo) mapea el evento a una acción. Los eventos `rollback` y
## `game_menu` ya existen; `touch_history` es nuestro.

# ============================================================================
# CONFIG DEL MODDER
# ============================================================================

# ¿Los gestos táctiles arrancan activados en dispositivos táctiles?
#   True  -> en móvil ON por defecto (y en PC OFF).
#   False -> OFF por defecto siempre (el jugador los prende en Ajustes).
define touch_gestures_auto = True

# Mapeo gesto -> acción. Direcciones: n = arriba, s = abajo, e = derecha,
# w = izquierda. Para desactivar un gesto puntual, poné None.
define touch_gesture_back = "e"       # deslizar ->  (derecha): Atrás (rollback)
define touch_gesture_history = "n"    # deslizar ^   (arriba):  Historial
define touch_gesture_menu = "s"       # deslizar v   (abajo):   Menú (pausa)

# Escala del quick menu en pantallas táctiles (1.0 = sin cambios).
define touch_quick_menu_scale = 1.25


# ============================================================================
# ESTADO DEL JUGADOR
# ============================================================================

# None = automático (táctil ON / PC OFF). True/False = elección explícita.
default persistent.touch_gestures = None


# ============================================================================
# LÓGICA
# ============================================================================

init python:
    def touch_gestures_on():
        """¿Los gestos táctiles están activos ahora?"""
        if persistent.touch_gestures is None:
            return bool(touch_gestures_auto) and renpy.variant("touch")
        return bool(persistent.touch_gestures)

    def touch_toggle_gestures():
        """Prende/apaga los gestos y re-aplica el mapeo."""
        persistent.touch_gestures = not touch_gestures_on()
        touch_aplicar_gestos()

    def touch_aplicar_gestos():
        """Activa o quita los gestos según la preferencia del jugador."""
        g = config.gestures
        for d in (touch_gesture_back, touch_gesture_history, touch_gesture_menu):
            if d:
                g.pop(d, None)
        if not touch_gestures_on():
            return
        if touch_gesture_back:
            g[touch_gesture_back] = "rollback"
        if touch_gesture_history:
            g[touch_gesture_history] = "touch_history"
        if touch_gesture_menu:
            g[touch_gesture_menu] = "game_menu"

    # Evento nuevo para Historial. Hay que declararlo en config.keymap (sin
    # teclas: se dispara solo por gesto) para que el Keymap sepa resolverlo;
    # si no, Ren'Py lo trata como keysym inválido. (rollback y game_menu ya
    # vienen de Ren'Py.)
    config.keymap["touch_history"] = []
    config.underlay.append(renpy.Keymap(
        touch_history = ShowMenu("history"),
    ))

    touch_aplicar_gestos()


transform quick_menu_touch:
    zoom (touch_quick_menu_scale if renpy.variant("touch") else 1.0)


# ============================================================================
# SECCIÓN DE AJUSTES (se incluye desde Ajustes DDLC con `use touch_preferences`)
# ============================================================================

screen touch_preferences():
    hbox:
        box_wrap True

        vbox:
            style_prefix "check"
            label _("Touch")
            textbutton _("Touch gestures"):
                action Function(touch_toggle_gestures)
                selected touch_gestures_on()

        vbox:
            style_prefix "name"
            label _("Accessibility")

            null height 3

            textbutton _("Accessibility Options") action ToggleScreen("_accessibility"):
                text_style "navigation_button_text"
