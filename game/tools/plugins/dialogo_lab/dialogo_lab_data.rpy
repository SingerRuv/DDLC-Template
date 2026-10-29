## dialogo_lab_data.rpy
## Diálogo — Lógica: estado del editor, catálogos y construcción de la línea.
##
## No hay motor: el énfasis se aplica con tags de Ren'Py ({b}, {i}, {u}, {s},
## {color=}, {size=}), que son markup nativo. La línea que arma la herramienta
## se pega en el guion y funciona tal cual, sin plugins ni código extra.
##
## La interfaz vive en dialogo_lab_ui.rpy, la vista previa en
## dialogo_lab_preview.rpy y el screen raíz (dialogo_lab) en dialogo_lab.rpy.

init python:

    DLG_PREFIJO = "dlg"

    # Ancho interior del campo de texto: la ventana mide 372, el marco de la
    # ventana agrega 14 por lado y el del campo 8 más. El input necesita ancho
    # fijo: si se ajusta a su contenido, un campo vacío queda sin área
    # clickeable y no se puede escribir en él.
    DLG_INPUT_ANCHO = 328

    # Ejemplo que se muestra en la vista previa mientras no haya línea escrita.
    _DLG_EJEMPLO = "Esto no debería estar pasando."

    # Personajes del template: variable del Character y nombre del namebox.
    _DLG_PERSONAJES = {
        "sayori": ("s", "Sayori"),
        "monika": ("m", "Monika"),
        "natsuki": ("n", "Natsuki"),
        "yuri": ("y", "Yuri"),
        "narrator": ("narrator", "Narrador"),
    }

    # Paleta del texto. "Ninguno" deja el color del estilo; "Personalizado"
    # usa el hex que se escribe en el campo de color.
    _DLG_COLORES = [
        ("Ninguno", "Sin cambio"),
        ("Personalizado", "Personalizado"),
        ("#ffffff", "Blanco"),
        ("#d8d8d8", "Gris claro"),
        ("#8a8f98", "Gris"),
        ("#4a505e", "Gris oscuro"),
        ("#000000", "Negro"),
        ("#ff8acc", "Rosa"),
        ("#ff5555", "Rojo"),
        ("#ff9e64", "Naranja"),
        ("#ffd479", "Amarillo"),
        ("#8fd18f", "Verde"),
        ("#7fb0ff", "Azul"),
        ("#c792ea", "Violeta"),
    ]

    # Tamaños: pasos relativos al tamaño del estilo del diálogo (24 px).
    _DLG_TAMANOS = [
        ("Pequeño", -4),
        ("Chico", -2),
        ("Normal", 0),
        ("Grande", 2),
        ("Enorme", 4),
    ]

    dlg_state = {
        "linea": "",            # texto del diálogo (sin comillas)
        "frase": "",            # frase a resaltar (opcional)
        "negrita": False,
        "italica": False,
        "subrayado": False,
        "tachado": False,
        "color": "Ninguno",     # valor de _DLG_COLORES
        "color_hex": "#ff8acc", # usado cuando color == "Personalizado"
        "tamano": "Normal",     # nombre de _DLG_TAMANOS
        "personaje": "yuri",
        "con_personaje": True,
        "controles": True,
    }

    # Copia de los valores por defecto (la usa `dlg_reset`).
    _DLG_DEFAULTS = dict(dlg_state)

    # ------------------------------------------------------------------
    # Catálogos
    # ------------------------------------------------------------------

    def dlg_color_actual():
        """Color elegido. "Ninguno" = el del estilo; "Personalizado" = el hex."""
        color = dlg_state.get("color", "Ninguno")
        if color == "Personalizado":
            return dlg_state.get("color_hex") or "#ffffff"
        return color

    def dlg_tamano_delta():
        """Paso de tamaño (relativo al tamaño del estilo)."""
        for nombre, delta in _DLG_TAMANOS:
            if nombre == dlg_state.get("tamano"):
                return delta
        return 0

    def dlg_personaje():
        """(variable del Character, nombre del namebox) del personaje elegido."""
        return _DLG_PERSONAJES.get(dlg_state.get("personaje"), ("narrator", "Narrador"))

    # ------------------------------------------------------------------
    # Construcción de la línea
    # ------------------------------------------------------------------

    def dlg_tags():
        """Tags de apertura y de cierre (el cierre va en orden inverso)."""
        abre = []
        cierra = []

        color = dlg_color_actual()
        if color and color != "Ninguno":
            abre.append("{color=%s}" % color)
            cierra.append("{/color}")

        delta = dlg_tamano_delta()
        if delta:
            abre.append("{size=%+d}" % delta)
            cierra.append("{/size}")

        for clave, tag in (("negrita", "b"), ("italica", "i"),
                           ("subrayado", "u"), ("tachado", "s")):
            if dlg_state.get(clave):
                abre.append("{%s}" % tag)
                cierra.append("{/%s}" % tag)

        return "".join(abre), "".join(reversed(cierra))

    def dlg_frase_encontrada():
        """True si la frase a resaltar aparece en la línea."""
        linea = (dlg_state.get("linea") or "").strip()
        frase = (dlg_state.get("frase") or "").strip()
        if not linea or not frase:
            return True
        return frase in linea

    def dlg_texto():
        """La línea con los tags, para la vista previa.

        Sin frase marcada, los tags envuelven toda la línea. Con frase, la
        envuelven todas sus apariciones.
        """
        linea = (dlg_state.get("linea") or "").strip()
        if not linea:
            return ""

        abre, cierra = dlg_tags()
        if not abre:
            return linea

        frase = (dlg_state.get("frase") or "").strip()
        if not frase:
            return abre + linea + cierra

        if frase not in linea:
            return linea

        return linea.replace(frase, abre + frase + cierra)

    def dlg_linea():
        """Línea lista para pegar en el guion: y "…{b}…{/b}…"."""
        texto = dlg_texto()
        if not texto:
            return ""

        if not dlg_state.get("con_personaje", True):
            # Sin el personaje se devuelve el texto pelado: el modder lo pega
            # dentro de sus propias comillas.
            return texto

        # Las comillas internas se escapan: la línea es una sentencia de
        # Python/ Ren'Py entre comillas dobles.
        return '%s "%s"' % (dlg_personaje()[0], texto.replace('"', '\\"'))

    def dlg_codigo():
        """La línea como código: los tags se ven literales, no interpretados.

        Ren'Py usa "{{" para mostrar una llave literal, así que se escapan.
        """
        return dlg_linea().replace("{", "{{")

    # ------------------------------------------------------------------
    # Avisos y resúmenes
    # ------------------------------------------------------------------

    def dlg_aviso():
        """Aviso bajo los campos ('' si no hay nada que avisar)."""
        if dlg_frase_encontrada():
            return ""
        return "La frase a resaltar no aparece en la línea: no se aplica ningún efecto."

    def dlg_resumen_efectos():
        partes = []
        if dlg_state.get("negrita"):
            partes.append("Negrita")
        if dlg_state.get("italica"):
            partes.append("Itálica")
        if dlg_state.get("subrayado"):
            partes.append("Subrayado")
        if dlg_state.get("tachado"):
            partes.append("Tachado")
        color = dlg_color_actual()
        if color and color != "Ninguno":
            partes.append("Color")
        if dlg_tamano_delta():
            partes.append("Tamaño")
        return " · ".join(partes)

    def dlg_resumen_linea():
        """Qué se está resaltando: una frase o la línea entera."""
        return "Frase" if dlg_state.get("frase") else "Línea entera"

    def dlg_resumen_salida():
        """Personaje de la línea que sale."""
        if dlg_state.get("con_personaje", True):
            return dlg_personaje()[1]
        return "Sin personaje"

    # ------------------------------------------------------------------
    # Ventanas flotantes (posición persistida; la registra el hub)
    # ------------------------------------------------------------------

    # Las ventanas arrancan bajo la barra de herramientas (arriba, ~40 px).
    # La vista previa va a la derecha: el panel de la izquierda crece cuando
    # se abre una sección y llegaría a taparla.
    _DLG_VENTANAS = {"controls": (24, 64), "preview": (430, 64)}

    def dlg_alternar_controles():
        """Muestra u oculta la ventana de controles."""
        dlg_state["controles"] = not dlg_state.get("controles", True)
        renpy.restart_interaction()

    def dlg_reset():
        """Vuelve la herramienta a su estado inicial."""
        dlg_state.clear()
        dlg_state.update(_DLG_DEFAULTS)
        tool_ventana_reiniciar("controls", DLG_PREFIJO, "dialogo_lab")
        tool_ventana_reiniciar("preview", DLG_PREFIJO, "dialogo_lab")
        tool_toast("Diálogo reiniciado")


# Posiciones por defecto de las ventanas flotantes del plugin (las registra
# el hub; ver game/tools/ui_styles.rpy).
init 10 python:

    tool_ventanas_defecto(_DLG_VENTANAS, DLG_PREFIJO)
