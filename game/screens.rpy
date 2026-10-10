## screens.rpy

# Este archivo declara todas las pantallas y estilos de DDLC.

## Initialization
################################################################################

init offset = -1

# Gracias RenpyTom! Tomado del Launcher de Ren'Py
init python:
    import math

    def scan_translations():

        languages = renpy.known_languages()

        if not languages:
            return None

        rv = [(i, renpy.translate_string("{#language name and font}", i)) for i in languages ]
        rv.sort(key=lambda a : renpy.filter_text_tags(a[1], allow=[]).lower())

        rv.insert(0, (None, "English"))

        bound = math.ceil(len(rv)/2.)

        return (rv[:bound], rv[bound:2*bound])

default translations = scan_translations()

# Permite añadir mas ajustes al juego, como el Modo Sin Censura.
default extra_settings = True
# Si vas a usar idiomas adicionales, pon esto en True.
default enable_languages = True

## Estilos de color
################################################################################

# Esto controla el color de los contornos del juego, como
# texto, dialogue, navegacion, etiquetas, etc.
define -2 text_outline_color = "#b59"

## Styles
################################################################################

style default:
    font gui.default_font
    size gui.text_size
    color gui.text_color
    outlines [(2, "#000000aa", 0, 0)]
    line_overlap_split 1
    line_spacing 1

style normal is default:
    xpos gui.text_xpos
    xanchor gui.text_xalign
    xsize gui.text_width
    ypos gui.text_ypos

    text_align gui.text_xalign
    layout ("subtitle" if gui.text_xalign else "tex")

style input:
    color gui.accent_color

style splash_text:
    size 24
    color "#000"
    font gui.default_font
    text_align 0.5
    outlines []

style gui_text:
    font gui.interface_font
    color gui.interface_text_color
    size gui.interface_text_size


style button:
    properties gui.button_properties("button")

style button_text is gui_text:
    properties gui.button_text_properties("button")
    yalign 0.5


style label_text is gui_text:
    color gui.accent_color
    size gui.label_text_size

style prompt_text is gui_text:
    color gui.text_color
    size gui.interface_text_size

style vbar:
    xsize gui.bar_size
    top_bar Frame("gui/bar/top.png", gui.vbar_borders, tile=gui.bar_tile)
    bottom_bar Frame("gui/bar/bottom.png", gui.vbar_borders, tile=gui.bar_tile)

style bar:
    ysize 18
    base_bar Frame("gui/scrollbar/horizontal_poem_bar.png", tile=False)
    thumb Frame("gui/scrollbar/horizontal_poem_thumb.png", top=6, right=6, tile=True)

style scrollbar:
    ysize 18
    base_bar Frame("gui/scrollbar/horizontal_poem_bar.png", tile=False)
    thumb Frame("gui/scrollbar/horizontal_poem_thumb.png", top=6, right=6, tile=True)
    unscrollable "hide"
    bar_invert True

style vscrollbar:
    xsize 18
    base_bar Frame("gui/scrollbar/vertical_poem_bar.png", tile=False)
    thumb Frame("gui/scrollbar/vertical_poem_thumb.png", left=6, top=6, tile=True)
    unscrollable "hide"
    bar_invert True

style slider:
    ysize 18
    base_bar Frame("gui/scrollbar/horizontal_poem_bar.png", tile=False)
    thumb "gui/slider/horizontal_hover_thumb.png"

style vslider:
    xsize gui.slider_size
    base_bar Frame("gui/slider/vertical_[prefix_]bar.png", gui.vslider_borders, tile=gui.slider_tile)
    thumb "gui/slider/vertical_[prefix_]thumb.png"


style frame:
    padding gui.frame_borders.padding
    background Frame("gui/frame.png", gui.frame_borders, tile=gui.frame_tile)
    # background Frame(recolorize("gui/frame.png"), gui.frame_borders, tile=gui.frame_tile)

################################################################################
## Pantallas del juego
################################################################################


## Pantalla say ##################################################################
##
## La pantalla say se usa para mostrar dialogo al jugador. Recibe dos
## parametros, who y what, que son el nombre del personaje que habla y
## el texto a mostrar, respectivamente. (who puede ser None si no
## hay nombre.)
##
## Esta pantalla debe crear un displayable de texto con id "what", ya que Ren'Py
## lo usa para gestionar la visualizacion del texto. Tambien puede crear displayables con id "who"
## e id "window" para aplicar propiedades de estilo.
##
## https://www.renpy.org/doc/html/screen_special.html#say

screen say(who, what):
    style_prefix "say"

    window:
        id "window"

        text what id "what"

        if who is not None:

            window:
                style "namebox"
                text who id "who"

    # Si hay una side image, mostrarla encima del texto. No mostrarla
    # en la variante de telefono - no hay espacio.
    if not renpy.variant("small"):
        add SideImage() xalign 0.0 yalign 1.0

    use quick_menu


style window is default
style say_label is default
style say_dialogue is default
style say_thought is say_dialogue

style namebox is default
style namebox_label is say_label


style window:
    xalign 0.5
    xfill True
    yalign gui.textbox_yalign
    ysize gui.textbox_height

    background Transform("gui/textbox.png", xalign=0.5, yalign=1.0)

style namebox:
    xpos gui.name_xpos
    xanchor gui.name_xalign
    xsize gui.namebox_width
    ypos gui.name_ypos
    ysize gui.namebox_height

    background Frame("gui/namebox.png", gui.namebox_borders, tile=gui.namebox_tile, xalign=gui.name_xalign)
    padding gui.namebox_borders.padding

style say_label:
    color gui.accent_color
    font gui.name_font
    size gui.name_text_size
    xalign gui.name_xalign
    yalign 0.5
    outlines [(3, text_outline_color, 0, 0), (1, text_outline_color, 1, 1)]
    #outlines [(3, "#b59", 0, 0), (1, "#b59", 1, 1)]

style say_dialogue:
    xpos gui.text_xpos
    xanchor gui.text_xalign
    xsize gui.text_width
    ypos gui.text_ypos

    text_align gui.text_xalign
    layout ("subtitle" if gui.text_xalign else "tex")

image ctc:
    xalign 0.81 yalign 0.98 xoffset -5 alpha 0.0 subpixel True
    "gui/ctc.png"
    block:
        easeout 0.75 alpha 1.0 xoffset 0
        easein 0.75 alpha 0.5 xoffset -5
        repeat

## Pantalla input ################################################################
##
## Esta pantalla se usa para mostrar renpy.input. El parametro prompt se usa para
## pasar un texto de indicacion.
##
## Esta pantalla debe crear un displayable de entrada con id "input" para aceptar los
## distintos parametros de entrada.
##
## http://www.renpy.org/doc/html/screen_special.html#input

image input_caret:
    Solid("#b59")
    size (2,25) subpixel True
    block:
        linear 0.35 alpha 0
        linear 0.35 alpha 1
        repeat

screen input(prompt):
    style_prefix "input"

    window:

        vbox:
            xpos gui.text_xpos
            xanchor 0.5
            ypos gui.text_ypos

            text prompt style "input_prompt"
            input id "input"


style input_prompt is default

style input_prompt:
    xmaximum gui.text_width
    xalign gui.text_xalign
    text_align gui.text_xalign

style input:
    caret "input_caret"
    xmaximum gui.text_width
    xalign 0.5
    text_align 0.5


## Pantalla choice ###############################################################
##
## Esta pantalla se usa para mostrar las opciones del juego que presenta la sentencia
## menu. El unico parametro, items, es una lista de objetos, cada uno con los campos
## caption y action.
##
## Nuevo desde 3.0.0
##    - Ahora puedes pasar argumentos a las opciones del menu para colorear
##      el menu a tu gusto. Añade (kwargs=[color hex o nombre de estilo]) al
##      nombre de la opcion y obtendras botones distintos!
##
##      Examples: "Option 1 (kwargs=#00fbff)" | "Option 2 (kwargs=#00fbff, #6cffff)"
##
## http://www.renpy.org/doc/html/screen_special.html#choice

screen choice(items):
    style_prefix "choice"

    vbox:

        for i in items:

            if "kwargs=" in i.caption:

                $ kwarg = i.caption.split("(kwargs=")[-1].replace(")", "")
                $ caption = i.caption.replace(" (kwargs=" + kwarg + ")", "")

                if "#" in kwarg:

                    $ kwarg = kwarg.replace(", ", ",").split(",")

                    if len(kwarg) == 1:
                        $ kwarg.append('#ffe6f4')

                    $ arg1 = kwarg[0]
                    $ arg2 = kwarg[-1]

                    textbutton caption:
                        idle_background Frame(im.MatrixColor(im.MatrixColor("gui/button/choice_idle_background.png", im.matrix.desaturate() * im.matrix.contrast(1.29) * im.matrix.colorize("#00f", "#fff") * im.matrix.saturation(120)),
                            im.matrix.desaturate() * im.matrix.colorize(arg1, arg2)), gui.choice_button_borders)
                        hover_background Frame(im.MatrixColor(im.MatrixColor("gui/button/choice_hover_background.png", im.matrix.desaturate() * im.matrix.contrast(1.29) * im.matrix.colorize("#00f", "#fff") * im.matrix.saturation(120)),
                            im.matrix.desaturate() * im.matrix.colorize(arg1, "#fff")), gui.choice_button_borders)
                        action i.action

                else:

                    textbutton caption:
                        style kwarg
                        action i.action

            else:

                textbutton i.caption action i.action


## Cuando es True, el narrador dice los titulos del menu. Cuando es False,
## los titulos se muestran como botones vacios.
define config.narrator_menu = True


style choice_vbox is vbox
style choice_button is button
style choice_button_text is button_text

style choice_vbox:
    xalign 0.5
    ypos 270
    yanchor 0.5

    spacing gui.choice_spacing

style choice_button is default:
    properties gui.button_properties("choice_button")
    hover_sound gui.hover_sound
    activate_sound gui.activate_sound
    idle_background Frame("gui/button/choice_idle_background.png", gui.choice_button_borders)
    hover_background Frame("gui/button/choice_hover_background.png", gui.choice_button_borders)

style choice_button_text is default:
    properties gui.button_text_properties("choice_button")
    outlines []


init python:
    def RigMouse():
        currentpos = renpy.get_mouse_pos()
        targetpos = [640, 345]
        if currentpos[1] < targetpos[1]:
            renpy.display.draw.set_mouse_pos((currentpos[0] * 9 + targetpos[0]) / 10.0, (currentpos[1] * 9 + targetpos[1]) / 10.0)

screen rigged_choice(items):
    style_prefix "choice"

    vbox:
        for i in items:
            textbutton i.caption action i.action

    timer 1.0/30.0 repeat True action Function(RigMouse)




################################################################################
# Pantallas del menu principal y de pausa
################################################################################

## Pantalla de navegacion ###########################################################
##
## Esta pantalla se incluye en el menu principal y de pausa, y da navegacion
## a otros menus y para iniciar el juego.

init python:
    def FinishEnterName(launchGame=True):
        if not player: return
        persistent.playername = player
        renpy.save_persistent()
        renpy.hide_screen("name_input")
        if launchGame:
            renpy.jump_out_of_context("start")



style hyperlink_text:
    properties gui.text_properties("hyperlink", accent=True)
    idle_color gui.idle_color
    hover_color gui.hover_color
    hover_underline True

## Pantallas de guardar y cargar #######################################################
##
## Estas pantallas permiten al jugador guardar la partida y cargarla
## de nuevo. Como comparten casi todo, ambas se implementan
## mediante una tercera pantalla, file_slots.
##
## https://www.renpy.org/doc/html/screen_special.html#save
## https://www.renpy.org/doc/html/screen_special.html#load

screen save():

    tag menu

    use file_slots(_("Save"))


screen load():

    tag menu

    use file_slots(_("Load"))


screen file_slots(title):

    default page_name_value = FilePageNameInputValue()

    use game_menu(title):

        fixed:

            ## Esto asegura que la entrada reciba el evento enter antes que
            ## ninguno de los botones.
            order_reverse True

            # El nombre de la pagina, que se puede editar haciendo clic en un boton.

            button:
                style "page_label"

                #key_events True
                xalign 0.5
                #action page_name_value.Toggle()

                input:
                    style "page_label_text"
                    value page_name_value

            ## La cuadricula de ranuras de archivo.
            grid gui.file_slot_cols gui.file_slot_rows:
                style_prefix "slot"

                xalign 0.5
                yalign 0.5

                spacing gui.slot_spacing

                for i in range(gui.file_slot_cols * gui.file_slot_rows):

                    $ slot = i + 1

                    button:
                        action FileAction(slot)

                        has vbox

                        add FileScreenshot(slot) xalign 0.5

                        text FileTime(slot, format=_("{#file_time}%A, %B %d %Y, %H:%M"), empty=_("empty slot")):
                            style "slot_time_text"

                        text FileSaveName(slot):
                            style "slot_name_text"

                        key "save_delete" action FileDelete(slot)

            ## Botones para acceder a otras paginas.
            hbox:
                style_prefix "page"

                xalign 0.5
                yalign 1.0

                spacing gui.page_spacing

                #textbutton _("<") action FilePagePrevious(max=9, wrap=True)

                #textbutton _("{#auto_page}A") action FilePage("auto")

                #textbutton _("{#quick_page}Q") action FilePage("quick")

                # range(1, 10) da los numeros del 1 al 9.
                for page in range(1, 10):
                    textbutton "[page]" action FilePage(page)

                #textbutton _(">") action FilePageNext(max=9, wrap=True)


style page_label is gui_label
style page_label_text is gui_label_text
style page_button is gui_button
style page_button_text is gui_button_text

style slot_button is gui_button
style slot_button_text is gui_button_text
style slot_time_text is slot_button_text
style slot_name_text is slot_button_text

style page_label:
    xpadding 50
    ypadding 3

style page_label_text:
    color "#000"
    outlines []
    text_align 0.5
    layout "subtitle"
    hover_color gui.hover_color

style page_button:
    properties gui.button_properties("page_button")

style page_button_text:
    properties gui.button_text_properties("page_button")
    outlines []

style slot_button:
    properties gui.button_properties("slot_button")
    idle_background Frame("gui/button/slot_idle_background.png", gui.choice_button_borders)
    hover_background Frame("gui/button/slot_hover_background.png", gui.choice_button_borders)

style slot_button_text:
    properties gui.button_text_properties("slot_button")
    color "#666"
    outlines []

screen viewframe_options(title):

    style_prefix "viewframe"

    add "gui/overlay/confirm.png"

    frame:

        vbox:
            xalign .5
            yalign .5
            spacing 2

            label title

            null height 10

            transclude

style viewframe_frame is confirm_frame
style viewframe_label is confirm_prompt:
    xalign 0.5
style viewframe_label_text is confirm_prompt_text
style viewframe_button is confirm_button
style viewframe_button_text is confirm_button_text
style viewframe_text is confirm_prompt_text:
    size 20
    yalign 0.7

## Resoluciones en ventana
## Las resoluciones en ventana permiten escalar el juego a distintas resoluciones.
## Descomenta los # de abajo para activarlo.
# screen confirm_res(old_res):

#     ## Asegura que otras pantallas no reciban input mientras esta se muestra.
#     modal True

#     zorder 200

#     style_prefix "confirm"

#     add "gui/overlay/confirm.png"

#     frame:

#         vbox:
#             xalign .5
#             yalign .5
#             spacing 30

#             ## Este if-else muestra un cuadro de texto normal o
#             ## glitcheado si estas en la escena de muerte de Sayori y
#             ## estas saliendo del juego.
#             # if in_sayori_kill and message == layout.QUIT:
#             #     add "confirm_glitch" xalign 0.5
#             # else:
#             label _("Would you like to keep these changes?"):
#                 style "confirm_prompt"
#                 xalign 0.5

#             add DynamicDisplayable(res_text_timer) xalign 0.5

#             hbox:
#                 xalign 0.5
#                 spacing 100

#                 ## Este if-else desactiva salir desde el cuadro de salida
#                 ## si estas en la escena de muerte de Sayori; si no, cuadro normal.
#                 # if in_sayori_kill and message == layout.QUIT:
#                 #     textbutton _("Yes") action NullAction()
#                 #     textbutton _("No") action Hide("confirm")
#                 # else:
#                 textbutton _("Yes") action Hide("confirm_res")
#                 textbutton _("No") action [Function(renpy.set_physical_size, old_res), Hide("confirm_res")]

#     timer 5.0 action [Function(renpy.set_physical_size, old_res), Hide("confirm_res")]

# init python:
#     def res_text_timer(st, at):
#         if st <= 5.0:
#             time_left = str(round(5.0 - st))
#             return Text(time_left, style="confirm_prompt"), 0.1
#         else: return Text("0", style="confirm_prompt"), 0.0

#     def set_physical_resolution(res):
#         old_res = renpy.get_physical_size()
#         renpy.set_physical_size(res)
#         renpy.show_screen("confirm_res", old_res=old_res)

# screen display_options():

#     style_prefix "viewframe"

#     modal True

#     zorder 150

#     use viewframe_options(_("Display Resolutions")):

#         default scale = renpy.get_physical_size()

#         vbox:
#             xmaximum 500
#             ysize 120
#             viewport:
#                 style_prefix "radio"
#                 scrollbars "vertical"
#                 mousewheel True
#                 draggable True
#                 has vbox

#                 textbutton "1280x720" action SetScreenVariable("scale", (1280, 720))
#                 textbutton "1600x900" action SetScreenVariable("scale", (1600, 900))

#         null height 10

#         hbox:
#             xalign 0.5
#             spacing 100

#             textbutton _("Reset") action [Hide("display_options"), Function(renpy.reset_physical_size)]
#             textbutton _("Set") action [Hide("display_options"), Function(set_physical_resolution, scale)]

screen ddlc_preferences():
    hbox:
        box_wrap True

        if renpy.variant("pc"):

            vbox:
                style_prefix "radio"
                label _("Display")
                textbutton _("Windowed") action Preference("display", "window")
                textbutton _("Fullscreen") action Preference("display", "fullscreen")
                # textbutton _("More") action Show("display_options")

        if config.developer:
            vbox:
                style_prefix "radio"
                label _("Rollback Side")
                textbutton _("Disable") action Preference("rollback side", "disable")
                textbutton _("Left") action Preference("rollback side", "left")
                textbutton _("Right") action Preference("rollback side", "right")

        vbox:
            style_prefix "check"
            label _("Skip")
            textbutton _("Unseen Text") action Preference("skip", "toggle")
            textbutton _("After Choices") action Preference("after choices", "toggle")
            # textbutton _("Transitions") action InvertSelected(Preference("transitions", "toggle"))

    null height (4 * gui.pref_spacing)

    hbox:
        style_prefix "slider"
        box_wrap True

        vbox:

            hbox:
                label _("Text Speed")

                null width 5

                text str(preferences.text_cps) style "value_text"

            #bar value Preference("text speed")
            bar value FieldValue(_preferences, "text_cps", range=180, max_is_zero=False, style="slider", offset=20)

            hbox:
                label _("Auto-Forward Time")

                null width 5

                text str(round(preferences.afm_time)) style "value_text"

            bar value Preference("auto-forward time")

        vbox:

            if config.has_music:
                hbox:
                    label _("Music Volume")

                    null width 5

                    text str(round(preferences.get_mixer("music") * 100)) style "value_text"

                hbox:
                    bar value Preference("music volume")

            if config.has_sound:

                hbox:
                    label _("Sound Volume")

                    null width 5

                    text str(round(preferences.get_mixer("sfx") * 100)) style "value_text"

                hbox:
                    bar value Preference("sound volume")

                    if config.sample_sound:
                        textbutton _("Test") action Play("sound", config.sample_sound)

            if config.has_voice:
                hbox:
                    label _("Voice Volume")

                    null width 5

                    text str(round(preferences.get_mixer("voice") * 100)) style "value_text"

                hbox:
                    bar value Preference("voice volume")

                    if config.sample_voice:
                        textbutton _("Test") action Play("voice", config.sample_voice)

            if config.has_music or config.has_sound or config.has_voice:
                null height gui.pref_spacing

                textbutton _("Mute All"):
                    action Preference("all mute", "toggle")
                    style "mute_all_button"

screen template_preferences():
    hbox:
        box_wrap True

        if extra_settings:
            vbox:
                style_prefix "check"
                label _("Game Modes")
                textbutton _("Uncensored Mode") action If(persistent.uncensored_mode,
                    ToggleField(persistent, "uncensored_mode"),
                    Show("confirm", message="Are you sure you want to turn on Uncensored Mode?\nDoing so will enable more adult/sensitive\ncontent in your playthrough.\n\nThis setting will be dependent on the modder if\nthey programmed these checks in their story.",
                        yes_action=[Hide("confirm"), ToggleField(persistent, "uncensored_mode")],
                        no_action=Hide("confirm")
                    ))

        vbox:
            style_prefix "check"
            xsize 340
            label _("Interface")
            textbutton _("Quick Menu") action ToggleField(persistent, "show_quick_menu")
            textbutton _("Menu Animations") action ToggleField(persistent, "menu_nav_anim")
            textbutton _("Menu Particles") action ToggleField(persistent, "menu_particles")

        vbox:
            style_prefix "name"
            label _("Player Name")

            null height 3

            if player == "":
                text _("No Name Set") xalign 0.5
            else:
                text "[player]" xalign 0.5

            textbutton _("Change Name") action Show(screen="name_input", message="Please enter your name", ok_action=Function(FinishEnterName, launchGame=False)):
                text_style "navigation_button_text"

        python:
            has_discord_module = True
            try:
                RPC
            except NameError:
                has_discord_module = False

        if not renpy.android and has_discord_module:
            vbox:
                style_prefix "name"
                label _("Discord RPC")

                python:
                    connect_status = _("Disconnected")
                    if not persistent.enable_discord:
                        connect_status = _("Disabled")
                    if RPC.rpc_connected:
                        connect_status = _("Connected")

                null height 3

                text "[connect_status]" xalign 0.5

                python:
                    enable_text = _("Enable")
                    if persistent.enable_discord:
                        enable_text = _("Disable")

                textbutton enable_text action [ToggleField(persistent, "enable_discord"),
                    If(persistent.enable_discord, Function(RPC.disconnect), Function(RPC.connect))]:
                    text_style "navigation_button_text"
                if persistent.enable_discord and not RPC.rpc_connected:
                    textbutton _("Reconnect") action Function(RPC.connect):
                        text_style "navigation_button_text"

    null height (2 * gui.pref_spacing)

    hbox:
        box_wrap True

        vbox:
            style_prefix "name"
            label _("Data")

            null height 3

            textbutton _("Delete All Data") action Show("confirm", message="This will delete all saves and settings.\nThis cannot be undone. Continue?",
                yes_action=[Hide("confirm"), Function(delete_all_saves), Function(renpy.utter_restart)],
                no_action=Hide("confirm")):
                text_style "navigation_button_text"

    null height (4 * gui.pref_spacing)

    hbox:
        box_wrap True

        if enable_languages and translations:
            vbox:
                style_prefix "radio"
                label _("Language")
                hbox:
                    viewport:
                        mousewheel True
                        scrollbars "vertical"
                        ysize 120
                        has vbox

                        for tran in translations:
                            vbox:
                                for tlid, tlname in tran:
                                    textbutton tlname:
                                        action Language(tlid)

## Pantalla preferences ##########################################################
##
## La pantalla de preferencias permite al jugador configurar el juego a su gusto.
##
## https://www.renpy.org/doc/html/screen_special.html#preferences

screen preferences():

    tag menu

    if renpy.mobile:
        $ cols = 2
    else:
        $ cols = 4

    default ddlc_settings = True

    use game_menu(_("Settings"), scroll="viewport"):

        vbox:
            xoffset 50

            # Las pestañas (DDLC / Template Settings) son solo para el modder:
            # al publicar (config.developer = False) queda únicamente la de DDLC.
            if config.developer:
                hbox:
                    style_prefix "navigation"
                    xoffset 150
                    spacing 5
                    textbutton _("DDLC Settings") action [SetScreenVariable("ddlc_settings", True), SensitiveIf(not ddlc_settings)]
                    textbutton _("Template Settings") action [SetScreenVariable("ddlc_settings", False), SensitiveIf(ddlc_settings)]

                null height 10

            if ddlc_settings:
                use ddlc_preferences
            else:
                use template_preferences

    text "v[config.version]":
                xalign 1.0 yalign 1.0
                xoffset -10 yoffset -10
                style "main_menu_version"

style pref_label is gui_label
style pref_label_text is gui_label_text
style pref_vbox is vbox

style radio_label is pref_label
style radio_label_text is pref_label_text
style radio_button is gui_button
style radio_button_text is gui_button_text
style radio_vbox is pref_vbox

style check_label is pref_label
style check_label_text is pref_label_text
style check_button is gui_button
style check_button_text is gui_button_text
style check_vbox is pref_vbox

style slider_label is pref_label
style slider_label_text is pref_label_text
style slider_slider is gui_slider
style slider_button is gui_button
style slider_button_text is gui_button_text
style slider_pref_vbox is pref_vbox

style mute_all_button is check_button
style mute_all_button_text is check_button_text

style pref_label:
    top_margin gui.pref_spacing
    bottom_margin 2

style pref_label_text:
    font "gui/font/RifficFree-Bold.ttf"
    size 24
    color "#fff"
    outlines [(3, "#b59", 0, 0), (1, "#b59", 1, 1)]
    yalign 1.0

style pref_vbox:
    xsize 225

style radio_vbox:
    spacing gui.pref_button_spacing

style radio_button:
    properties gui.button_properties("radio_button")
    foreground "gui/button/check_[prefix_]foreground.png"

style radio_button_text:
    properties gui.button_text_properties("radio_button")
    font "gui/font/Halogen.ttf"
    outlines []

style check_vbox:
    spacing gui.pref_button_spacing

style check_button:
    properties gui.button_properties("check_button")
    foreground "gui/button/check_[prefix_]foreground.png"

style check_button_text:
    properties gui.button_text_properties("check_button")
    font "gui/font/Halogen.ttf"
    outlines []

style slider_slider:
    xsize 350

style slider_button:
    properties gui.button_properties("slider_button")
    yalign 0.5
    left_margin 10

style slider_button_text:
    properties gui.button_text_properties("slider_button")

style slider_vbox:
    xsize 450

style name_label is pref_label
style name_label_text is pref_label_text

style name_text:
    font "gui/font/Halogen.ttf"
    size 24
    color gui.idle_color
    outlines []

style value_text:
    size 18
    color "#000"
    outlines []
    yalign 0.65

## Pantalla history ##############################################################
##
## Esta pantalla muestra el historial de dialogo al jugador. Aunque
## no tiene nada especial, debe acceder al
## historial de dialogo guardado en _history_list.
##
## https://www.renpy.org/doc/html/history.html

screen history():
    tag menu

    ## Evita predecir esta pantalla, ya que puede ser muy grande.
    predict False

    use game_menu(_("History"), scroll=("vpgrid" if gui.history_height else "viewport")):

        style_prefix "history"

        for h in _history_list:

            window:

                ## Esto organiza todo correctamente si history_height es None.
                has fixed:
                    yfit True

                if h.who:

                    label h.who:
                        style "history_name"
                        substitute False

                        ## Toma el color del texto who del Character, si
                        ## esta definido.
                        if "color" in h.who_args:
                            text_color h.who_args["color"]

                $ what = renpy.filter_text_tags(h.what, allow=gui.history_allow_tags)
                text what:
                    substitute False

        if not _history_list:
            label _("The dialogue history is empty.")

define gui.history_allow_tags = set()

style history_window is empty

style history_name is gui_label
style history_name_text is gui_label_text
style history_text is gui_text

style history_label is gui_label
style history_label_text is gui_label_text

style history_window:
    xfill True
    ysize gui.history_height

style history_name:
    xpos gui.history_name_xpos
    xanchor gui.history_name_xalign
    ypos gui.history_name_ypos
    xsize gui.history_name_width

style history_name_text:
    min_width gui.history_name_width
    text_align gui.history_name_xalign

style history_text:
    xpos gui.history_text_xpos
    ypos gui.history_text_ypos
    xanchor gui.history_text_xalign
    xsize gui.history_text_width
    min_width gui.history_text_width
    text_align gui.history_text_xalign
    layout ("subtitle" if gui.history_text_xalign else "tex")

style history_label:
    xfill True

style history_label_text:
    xalign 0.5


################################################################################
## Additional screens
################################################################################

screen name_input(message, ok_action):

    ## Asegura que otras pantallas no reciban input mientras esta se muestra.
    modal True

    zorder 200

    style_prefix "confirm"

    add "gui/overlay/confirm.png"
    key "K_RETURN" action [Play("sound", gui.activate_sound), ok_action]
    key "dismiss" action [Play("sound", gui.activate_sound), ok_action]

    frame:

        vbox:
            xalign .5
            yalign .5
            spacing 30

            label _(message):
                style "confirm_prompt"
                xalign 0.5

            input default "" value VariableInputValue("player") length 12 allow "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzÁÉÍÓÚÑáéíóúñ"

            hbox:
                xalign 0.5
                spacing 100

                textbutton _("OK") action ok_action

screen dialog(message, ok_action):

    ## Asegura que otras pantallas no reciban input mientras esta se muestra.
    modal True

    zorder 200

    style_prefix "confirm"

    key "dismiss" action [Play("sound", gui.activate_sound), ok_action]

    add "gui/overlay/confirm.png"

    frame:

        vbox:
            xalign .5
            yalign .5
            spacing 30

            label _(message):
                style "confirm_prompt"
                xalign 0.5

            hbox:
                xalign 0.5
                spacing 100

                textbutton _("OK") action ok_action

image confirm_glitch:
    "gui/overlay/confirm_glitch.png"
    pause 0.02
    "gui/overlay/confirm_glitch2.png"
    pause 0.02
    repeat

## Pantalla confirm ##############################################################
##
## La pantalla confirm se llama cuando Ren'Py quiere hacerle al jugador una pregunta
## de si o no.
##
## http://www.renpy.org/doc/html/screen_special.html#confirm
screen confirm(message, yes_action, no_action):

    ## Asegura que otras pantallas no reciban input mientras esta se muestra.
    modal True

    zorder 200

    style_prefix "confirm"

    key "dismiss" action no_action

    add "gui/overlay/confirm.png"

    frame:

        vbox:
            xalign .5
            yalign .5
            spacing 30

            ## Este if-else muestra un cuadro de texto normal o
            ## glitcheado si estas en la escena de muerte de Sayori y
            ## estas saliendo del juego.
            # if in_sayori_kill and message == layout.QUIT:
            #     add "confirm_glitch" xalign 0.5
            # else:
            label _(message):
                style "confirm_prompt"
                xalign 0.5

            hbox:
                xalign 0.5
                spacing 100

                ## Este if-else desactiva salir desde el cuadro de salida
                ## si estas en la escena de muerte de Sayori; si no, cuadro normal.
                # if in_sayori_kill and message == layout.QUIT:
                #     textbutton _("Yes") action NullAction()
                #     textbutton _("No") action Hide("confirm")
                # else:
                textbutton _("Yes") action yes_action
                textbutton _("No") action no_action

    ## Clic derecho y escape responden "no".
    #key "game_menu" action no_action


style confirm_frame is gui_frame
style confirm_prompt is gui_prompt
style confirm_prompt_text is gui_prompt_text
style confirm_button is gui_medium_button
style confirm_button_text is gui_medium_button_text

style confirm_frame:
    background Frame("gui/frame.png", gui.confirm_frame_borders, tile=gui.frame_tile)
    # background Frame(recolorize("gui/frame.png"), gui.confirm_frame_borders, tile=gui.frame_tile)
    padding gui.confirm_frame_borders.padding
    xalign .5
    yalign .5

style confirm_prompt_text:
    color "#000"
    outlines []
    text_align 0.5
    layout "subtitle"

style confirm_button:
    properties gui.button_properties("confirm_button")
    hover_sound gui.hover_sound
    activate_sound gui.activate_sound

style confirm_button_text is navigation_button_text:
    properties gui.button_text_properties("confirm_button")


## Pantalla del indicador de skip #######################################################
##
## La pantalla skip_indicator se muestra para indicar que el salto esta
## en curso.
##
## https://www.renpy.org/doc/html/screen_special.html#skip-indicator
screen fake_skip_indicator():
    use skip_indicator

screen skip_indicator():

    zorder 100
    style_prefix "skip"

    frame:

        hbox:
            spacing 6

            text _("Skipping")

            text "▸" at delayed_blink(0.0, 1.0) style "skip_triangle"
            text "▸" at delayed_blink(0.2, 1.0) style "skip_triangle"
            text "▸" at delayed_blink(0.4, 1.0) style "skip_triangle"


## Este transform hace parpadear las flechas una tras otra.
transform delayed_blink(delay, cycle):
    alpha .5

    pause delay

    block:
        linear .2 alpha 1.0
        pause .2
        linear .2 alpha 0.5
        pause (cycle - .4)
        repeat


style skip_frame is empty
style skip_text is gui_text
style skip_triangle is skip_text

style skip_frame:
    ypos gui.skip_ypos
    background Frame("gui/skip.png", gui.skip_frame_borders, tile=gui.frame_tile)
    padding gui.skip_frame_borders.padding

style skip_text:
    size gui.notify_text_size

style skip_triangle:
    # Hay que usar una fuente que tenga el TRIANGULO NEGRO PEQUENO HACIA LA DERECHA
    # glyph in it.
    font "DejaVuSans.ttf"


## Pantalla notify ###############################################################
##
## La pantalla notify se usa para mostrar un mensaje al jugador. (Por ejemplo, cuando
## el juego se guarda rapido o se toma una captura.)
##
## https://www.renpy.org/doc/html/screen_special.html#notify-screen

screen notify(message):

    zorder 100
    style_prefix "notify"

    frame at notify_appear:
        text message

    timer 3.25 action Hide('notify')


transform notify_appear:
    on show:
        alpha 0
        linear .25 alpha 1.0
    on hide:
        linear .5 alpha 0.0


style notify_frame is empty
style notify_text is gui_text

style notify_frame:
    ypos gui.notify_ypos

    background Frame("gui/notify.png", gui.notify_frame_borders, tile=gui.frame_tile)
    padding gui.notify_frame_borders.padding

style notify_text:
    size gui.notify_text_size

## Aviso de musica del menu de pausa (dev) ######################################
##
## Muestra, en modo developer, el nombre de la pista que suena en la pausa.
## Se incluye desde screen game_menu (menu_screens.rpy), asi que solo aparece
## al pausar, no en el menu principal.

screen pause_music_notify():
    if not main_menu and config.developer:
        frame:
            style_prefix "notify"
            xalign 1.0
            at musica_slide_in

            hbox:
                spacing 15

                text "🎵":
                    size 35
                    yalign 0.5
                    outlines []

                vbox:
                    yalign 0.5
                    text "Ahora suena:" size 16 color "#FFFFFF"
                    text "[musica_nombre()]" size 22 color "#FFFA8E" bold True

## Pantalla NVL ##################################################################
##
## Esta pantalla se usa para el dialogo y menus en modo NVL.
##
## http://www.renpy.org/doc/html/screen_special.html#nvl


screen nvl(dialogue, items=None):

    window:
        style "nvl_window"

        has vbox:
            spacing gui.nvl_spacing

        ## Muestra el dialogo en un vpgrid o en el vbox.
        if gui.nvl_height:

            vpgrid:
                cols 1
                yinitial 1.0

                use nvl_dialogue(dialogue)

        else:

            use nvl_dialogue(dialogue)

        ## Muestra el menu, si lo hay. El menu puede mostrarse mal si
        ## config.narrator_menu esta en True, como arriba.
        for i in items:

            textbutton i.caption:
                action i.action
                style "nvl_button"

    add SideImage() xalign 0.0 yalign 1.0


screen nvl_dialogue(dialogue):

    for d in dialogue:

        window:
            id d.window_id

            fixed:
                yfit gui.nvl_height is None

                if d.who is not None:

                    text d.who:
                        id d.who_id

                text d.what:
                    id d.what_id

## Esto controla el numero maximo de entradas en modo NVL que se pueden mostrar a
## la vez.
define config.nvl_list_length = 6

style nvl_window is default
style nvl_entry is default

style nvl_label is say_label
style nvl_dialogue is say_dialogue

style nvl_button is button
style nvl_button_text is button_text

style nvl_window:
    xfill True
    yfill True

    background "gui/nvl.png"
    padding gui.nvl_borders.padding

style nvl_entry:
    xfill True
    ysize gui.nvl_height

style nvl_label:
    xpos gui.nvl_name_xpos
    xanchor gui.nvl_name_xalign
    ypos gui.nvl_name_ypos
    yanchor 0.0
    xsize gui.nvl_name_width
    min_width gui.nvl_name_width
    text_align gui.nvl_name_xalign

style nvl_dialogue:
    xpos gui.nvl_text_xpos
    xanchor gui.nvl_text_xalign
    ypos gui.nvl_text_ypos
    xsize gui.nvl_text_width
    min_width gui.nvl_text_width
    text_align gui.nvl_text_xalign
    layout ("subtitle" if gui.nvl_text_xalign else "tex")

style nvl_thought:
    xpos gui.nvl_thought_xpos
    xanchor gui.nvl_thought_xalign
    ypos gui.nvl_thought_ypos
    xsize gui.nvl_thought_width
    min_width gui.nvl_thought_width
    text_align gui.nvl_thought_xalign
    layout ("subtitle" if gui.nvl_text_xalign else "tex")

style nvl_button:
    properties gui.button_properties("nvl_button")
    xpos gui.nvl_button_xpos
    xanchor gui.nvl_button_xalign

style nvl_button_text:
    properties gui.button_text_properties("nvl_button")

screen choose_language():
    default local_lang = _preferences.language
    default chosen_lang = _preferences.language

    modal True
    style_prefix "radio"

    # Click fuera de la ventana = cerrar
    button:
        style "empty"
        xfill True
        yfill True
        action [Hide("choose_language"), Return()]

    key "dismiss" action [Hide("choose_language"), Return()]

    add "gui/overlay/confirm.png"

    frame:
        style "confirm_frame"

        vbox:
            xalign .5
            yalign .5
            xsize 760
            spacing 30

            label renpy.translate_string(_("{#in language font}Please select a language"), local_lang):
                style "confirm_prompt"
                xalign 0.5

            hbox:
                xalign .5
                for tran in translations:
                    vbox:
                        for tlid, tlname in tran:
                            textbutton tlname:
                                xalign .5
                                action SetScreenVariable("chosen_lang", tlid)
                                hovered SetScreenVariable("local_lang", tlid)
                                unhovered SetScreenVariable("local_lang", chosen_lang)

            $ lang_name = renpy.translate_string("{#language name and font}", local_lang)

            hbox:
                xalign 0.5
                spacing 100

                textbutton renpy.translate_string(_("{#in language font}Select"), local_lang):
                    style "confirm_button"
                    action [Language(chosen_lang), SetField(persistent, "has_chosen_language", True), Hide("choose_language"), Return()]

translate None strings:
    old "{#language name and font}"
    new "English"

label choose_language:
    call screen choose_language
    return


## Pantalla end ###############################################################
##
## Se muestra cuando el juego termina. Por defecto muestra la imagen
## 'gui/end.png' con la posibilidad de volver al menú principal.

screen end():
    tag menu
    modal True

    add "gui/end.png"

    frame:
        background None
        xalign 0.5
        yalign 0.85
        xsize 400
        ypadding 20

        vbox:
            xalign 0.5
            spacing 10

            textbutton _("Return to Main Menu") action MainMenu() style "navigation_button"
            textbutton _("Quit") action Quit(confirm=True) style "navigation_button"

    key "K_ESCAPE" action MainMenu()
