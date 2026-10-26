## shaders_lab_data.rpy
## Shaders Lab — Lógica: registro de los shaders (bd.*), transforms listos para
## el modder (sh_*), el helper `sh_combinar` y el estado de la demo.
##
## La interfaz vive en shaders_lab_ui.rpy, el lienzo en shaders_lab_preview.rpy
## y el screen raíz (shaders_lab) en shaders_lab.rpy.
##
## Uso desde la historia (no requiere abrir la herramienta):
##
##     show yuri 1a at sh_scanlines
##     show bg class at sh_aberracion(offset=0.003)
##     show sayori 2b at sh_glitch
##     show monika 1a at sh_vigneta(fuerza=0.6)
##     show yuri 1a at sh_crt              # combinado (scanlines + aberración + viñeta)
##
## Efectos pensados para personajes:
##
##     show yuri 1a at sh_contorno                        # borde blanco
##     show sayori 1a at sh_silueta((0.5, 0.1, 0.2, 1.0)) # silueta roja
##     show monika 1a at sh_palidez(0.8)                  # pálida
##     show natsuki 1a at sh_flash(0.9)                   # destello
##
## Para combinar otros: `sh_combinar` (un Transform solo admite un `shader`).
##
##     show expression sh_combinar("bg class", "bd.scanlines bd.vigneta",
##                                 u_intensidad=0.4, u_fuerza=0.5)
##
## Cómo crear uno propio:
##   1. `renpy.register_shader("mi.nombre", variables="""...""", fragment_300="""...""")`.
##   2. En `variables` declarás los uniform/varying que uses (p. ej. `uniform float u_x;`).
##      Al declararlo, `u_x` queda disponible como propiedad de `Transform` y se puede
##      animar desde ATL (`linear 1.0 u_x 1.0`).
##   3. El código de `fragment_300` modifica `gl_FragColor` DESPUÉS de que Ren'Py
##      compuso la textura (`renpy.texture` usa la prioridad 200; `renpy.alpha` la 500).
##
## Nota: requieren el renderer GL2 (el default de Ren'Py 8). En equipos muy viejos
## sin GL2 los efectos simplemente no se aplican.

init -1 python:

    # Líneas de TV/CRT: oscurece bandas horizontales.
    renpy.register_shader("bd.scanlines", variables="""
        uniform sampler2D tex0;
        varying vec2 v_tex_coord;
        uniform float u_intensidad;
        uniform float u_lineas;
    """, fragment_300="""
        float bd_onda = 0.5 + 0.5 * sin(v_tex_coord.y * u_lineas * 6.2831853);
        float bd_factor = 1.0 - u_intensidad * (1.0 - bd_onda) * 0.5;
        gl_FragColor.rgb *= bd_factor;
    """)

    # Aberración cromática: separa los canales rojo y azul en horizontal.
    renpy.register_shader("bd.aberracion", variables="""
        uniform sampler2D tex0;
        varying vec2 v_tex_coord;
        uniform float u_offset;
    """, fragment_300="""
        vec2 bd_uv = v_tex_coord;
        float bd_r = texture2D(tex0, bd_uv + vec2(u_offset, 0.0)).r;
        float bd_g = texture2D(tex0, bd_uv).g;
        float bd_b = texture2D(tex0, bd_uv - vec2(u_offset, 0.0)).b;
        gl_FragColor = vec4(vec3(bd_r, bd_g, bd_b) * gl_FragColor.a, gl_FragColor.a);
    """)

    # Glitch: bandas horizontales desplazadas + canales RGB partidos.
    # `u_fase` se anima desde el transform (0..1, repetido).
    renpy.register_shader("bd.glitch", variables="""
        uniform sampler2D tex0;
        varying vec2 v_tex_coord;
        uniform float u_intensidad;
        uniform float u_bandas;
        uniform float u_fase;
    """, fragment_300="""
        float bd_banda = floor(v_tex_coord.y * u_bandas);
        float bd_n = fract(sin(bd_banda * 12.9898 + u_fase * 78.233) * 43758.5453);
        float bd_activa = step(0.72, bd_n);
        vec2 bd_uv = v_tex_coord;
        bd_uv.x += (bd_n - 0.5) * 0.12 * u_intensidad * bd_activa;
        vec4 bd_col = texture2D(tex0, bd_uv);
        bd_col.r = texture2D(tex0, bd_uv + vec2(0.006 * u_intensidad * bd_activa, 0.0)).r;
        bd_col.b = texture2D(tex0, bd_uv - vec2(0.006 * u_intensidad * bd_activa, 0.0)).b;
        gl_FragColor = vec4(bd_col.rgb * gl_FragColor.a, gl_FragColor.a);
    """)

    # Viñeta: oscurece los bordes.
    renpy.register_shader("bd.vigneta", variables="""
        uniform sampler2D tex0;
        varying vec2 v_tex_coord;
        uniform float u_fuerza;
    """, fragment_300="""
        vec2 bd_d = v_tex_coord - vec2(0.5, 0.5);
        float bd_r = length(bd_d) * 1.41421356;
        float bd_f = 1.0 - u_fuerza * smoothstep(0.45, 1.0, bd_r);
        gl_FragColor.rgb *= bd_f;
    """)

    # Combinado: scanlines + aberración + viñeta en un solo shader.
    renpy.register_shader("bd.crt", variables="""
        uniform sampler2D tex0;
        varying vec2 v_tex_coord;
        uniform float u_intensidad;
        uniform float u_lineas;
        uniform float u_offset;
        uniform float u_fuerza;
    """, fragment_300="""
        vec2 bd_uv = v_tex_coord;
        float bd_cr = texture2D(tex0, bd_uv + vec2(u_offset, 0.0)).r;
        float bd_cg = texture2D(tex0, bd_uv).g;
        float bd_cb = texture2D(tex0, bd_uv - vec2(u_offset, 0.0)).b;
        vec3 bd_col = vec3(bd_cr, bd_cg, bd_cb);

        float bd_onda = 0.5 + 0.5 * sin(bd_uv.y * u_lineas * 6.2831853);
        bd_col *= 1.0 - u_intensidad * (1.0 - bd_onda) * 0.5;

        vec2 bd_d = bd_uv - vec2(0.5, 0.5);
        float bd_vr = length(bd_d) * 1.41421356;
        bd_col *= 1.0 - u_fuerza * smoothstep(0.45, 1.0, bd_vr);

        gl_FragColor = vec4(bd_col * gl_FragColor.a, gl_FragColor.a);
    """)

    # ---- Efectos pensados para PERSONAJES ----------------------------------

    # Silueta: pinta todo el sprite de un color plano (mantiene la forma).
    # Ojo: Ren'Py usa alpha premultiplicado; el RGB se multiplica por el alpha
    # para no pintar el espacio transparente que rodea al sprite.
    renpy.register_shader("bd.silueta", variables="""
        uniform sampler2D tex0;
        varying vec2 v_tex_coord;
        uniform vec4 u_color;
    """, fragment_300="""
        vec4 bd_c = texture2D(tex0, v_tex_coord);
        float bd_a = bd_c.a * u_color.a;
        gl_FragColor = vec4(u_color.rgb * bd_a, bd_a);
    """)

    # Contorno: dibuja un borde del color elegido alrededor del sprite.
    renpy.register_shader("bd.contorno", variables="""
        uniform sampler2D tex0;
        varying vec2 v_tex_coord;
        uniform vec4 u_color;
        uniform float u_paso;
    """, fragment_300="""
        vec4 bd_c = texture2D(tex0, v_tex_coord);
        float bd_borde = 0.0;
        bd_borde = max(bd_borde, texture2D(tex0, v_tex_coord + vec2(u_paso, 0.0)).a);
        bd_borde = max(bd_borde, texture2D(tex0, v_tex_coord - vec2(u_paso, 0.0)).a);
        bd_borde = max(bd_borde, texture2D(tex0, v_tex_coord + vec2(0.0, u_paso)).a);
        bd_borde = max(bd_borde, texture2D(tex0, v_tex_coord - vec2(0.0, u_paso)).a);
        float bd_cont = clamp(bd_borde - bd_c.a, 0.0, 1.0) * u_color.a;
        float bd_a = max(bd_c.a, bd_cont);
        gl_FragColor = vec4(mix(bd_c.rgb, u_color.rgb * bd_a, bd_cont), bd_a);
    """)

    # Palidez: desatura y aclara un poco (susto, recuerdo, fantasma).
    renpy.register_shader("bd.palidez", variables="""
        uniform sampler2D tex0;
        varying vec2 v_tex_coord;
        uniform float u_fuerza;
    """, fragment_300="""
        float bd_a = gl_FragColor.a;
        float bd_luma = dot(gl_FragColor.rgb, vec3(0.299, 0.587, 0.114));
        vec3 bd_gris = vec3(bd_luma) + vec3(0.12 * bd_a);
        gl_FragColor.rgb = mix(gl_FragColor.rgb, bd_gris, u_fuerza);
    """)

    # Flash: mezcla el sprite hacia blanco (golpe, revelación).
    renpy.register_shader("bd.flash", variables="""
        uniform sampler2D tex0;
        varying vec2 v_tex_coord;
        uniform float u_fuerza;
    """, fragment_300="""
        gl_FragColor.rgb = mix(gl_FragColor.rgb, vec3(gl_FragColor.a), u_fuerza);
    """)


transform sh_scanlines(intensidad=0.35, lineas=240.0):
    mesh True
    shader "bd.scanlines"
    u_intensidad intensidad
    u_lineas lineas

transform sh_aberracion(offset=0.002):
    mesh True
    shader "bd.aberracion"
    u_offset offset

transform sh_vigneta(fuerza=0.55):
    mesh True
    shader "bd.vigneta"
    u_fuerza fuerza

transform sh_glitch(intensidad=0.8, bandas=24.0, velocidad=0.5):
    mesh True
    shader "bd.glitch"
    u_intensidad intensidad
    u_bandas bandas
    u_fase 0.0
    linear velocidad u_fase 1.0
    repeat

# Combinado: las tres capas del look CRT.
transform sh_crt(intensidad=0.30, offset=0.002, fuerza=0.45):
    mesh True
    shader "bd.crt"
    u_intensidad intensidad
    u_lineas 240.0
    u_offset offset
    u_fuerza fuerza


# ---- Transforms para personajes -------------------------------------------

transform sh_silueta(color=(0.55, 0.10, 0.15, 1.0)):
    mesh True
    shader "bd.silueta"
    u_color color

transform sh_contorno(color=(1.0, 1.0, 1.0, 1.0), paso=0.0015):
    mesh True
    shader "bd.contorno"
    u_color color
    u_paso paso

transform sh_palidez(fuerza=0.7):
    mesh True
    shader "bd.palidez"
    u_fuerza fuerza

transform sh_flash(fuerza=0.8):
    mesh True
    shader "bd.flash"
    u_fuerza fuerza


init python:

    def sh_combinar(d, shaders, **uniformes):
        """Aplica VARIOS shaders a un displayable (un Transform admite uno solo).

        Uso:
            show expression sh_combinar("bg class", "bd.scanlines bd.vigneta",
                                        u_intensidad=0.4, u_fuerza=0.5)
        """
        m = renpy.display.model.Model().texture(renpy.displayable(d))
        # `renpy.texture` declara y escribe `v_tex_coord`: sin él, los shaders
        # que lo usan no compilan.
        for nombre in ("renpy.texture",) + tuple(shaders.split()):
            m = m.shader(nombre)
        for clave, valor in uniformes.items():
            m = m.uniform(clave, valor)
        return m

    # Estado de la demo (en el store: así los `use` pueden leerlo/escribirlo).
    shl_state = {
        "sujeto": "Fondo",      # "Fondo" | "Personaje"
        "efecto": "Scanlines",
        "intensidad": 0.5,
        "doki": "yuri",
    }
    _SHL_EFECTOS = ["Ninguno", "Scanlines", "Aberración", "Viñeta", "Glitch", "CRT",
                    "Cuadros"]
    _SHL_EFECTOS_PJ = ["Ninguno", "Contorno", "Silueta", "Palidez", "Flash",
                       "Glitch", "Scanlines", "Glitch (slices)", "Glitch animado"]
    _SHL_DOKIS = ["sayori", "natsuki", "yuri", "monika"]

    # ---- Helpers de los efectos por slices (ChromaGlitch, vendorizado) ------

    def sh_glitch_slices(d, offset=30, chroma=True, randomkey="shl_slices",
                         minbandheight=1, nslices=None):
        """Franjas desplazadas. `randomkey=None` = distinto en cada render."""
        return glitch(d, offset=offset, chroma=chroma, randomkey=randomkey,
                      minbandheight=minbandheight, nslices=nslices)

    def sh_glitch_animado(d, timeout_base=0.1, timeout_vanilla=None, offset=30,
                          chroma=True, randomkey="shl_animado"):
        """Como `sh_glitch_slices`, pero cambia solo con el tiempo."""
        return animated_glitch(d, timeout_base=timeout_base,
                               timeout_vanilla=timeout_vanilla, offset=offset,
                               chroma=chroma, randomkey=randomkey)

    def sh_glitch_squares(d, squareside=20, chroma=0.25, permutes=None,
                          randomkey="shl_cuadros"):
        """Corta la imagen en cuadrados y los permuta."""
        return squares_glitch(d, squareside=squareside, chroma=chroma,
                              permutes=permutes, randomkey=randomkey)

    def shl_envolver(efecto, d, intensidad):
        """Envuelve un displayable con los efectos de slices. None si no aplica."""
        if efecto == "Glitch (slices)":
            return sh_glitch_slices(d, offset=int(10 + 50 * intensidad))
        if efecto == "Glitch animado":
            return sh_glitch_animado(d, offset=int(10 + 50 * intensidad))
        if efecto == "Cuadros":
            return sh_glitch_squares(d, squareside=int(round(40 - 28 * intensidad)))
        return None

    def shl_reset_efecto():
        """Al cambiar de sujeto, el efecto anterior puede no existir en la otra lista."""
        shl_state["efecto"] = "Ninguno"

    def shl_transform(efecto, intensidad):
        """Transform del efecto elegido. None para 'Ninguno'."""
        if efecto == "Scanlines":
            return sh_scanlines(intensidad)
        if efecto == "Aberración":
            return sh_aberracion(0.002 + 0.012 * intensidad)
        if efecto == "Viñeta":
            return sh_vigneta(0.2 + intensidad)
        if efecto == "Glitch":
            return sh_glitch(intensidad, 24.0, 0.35)
        if efecto == "CRT":
            return sh_crt(intensidad)
        # Personajes
        if efecto == "Contorno":
            return sh_contorno(paso=0.0010 + 0.0015 * intensidad)
        if efecto == "Silueta":
            return sh_silueta()
        if efecto == "Palidez":
            return sh_palidez(0.2 + intensidad)
        if efecto == "Flash":
            return sh_flash(intensidad)
        return None
