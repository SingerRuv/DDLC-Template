## textshaders.rpy
## Text shaders del template (dev): efectos que se aplican al TEXTO del diálogo,
## no a los displayables. Requieren Model-Based Rendering (GL2), el default de
## Ren'Py 8.
##
## Se aplican por estilo, por personaje o por bloque de texto. Un bloque de texto
## usa text shaders **o no** los usa: no se mezclan dentro del mismo bloque.
##
##     define y_glitch = Character("Yuri", what_textshader="ts_glitch:0.6")
##
##     style mi_texto:
##         textshader "ts_glitch:0.6"
##
##     text "No..." textshader "ts_glitch:0.6"     # en un screen
##
## Los text shaders que trae Ren'Py (dissolve, flip, jitter, linetexture, offset,
## slowalpha, texture, typewriter, wave, zoom) se usan igual, sólo cambiando el
## nombre. Ver docs/02-referencia.md.

init -1 python:

    # Glitch de texto: cada glifo se sacude un poco y los canales rojo/azul se
    # separan. Respeta los outlines (sólo altera el texto principal) y el alpha
    # premultiplicado.
    #
    # Uniforms:
    #   u__intensidad 0..1: cuánto se desplazan/sacudan los glifos.
    #   u__velocidad: cambios por segundo (más alto = más nervioso).
    #
    # redraw=0.05 pide un redraw cada 50 ms: sin esto el efecto se congela
    # cuando termina el revelado, porque el texto deja de pedir frames.
    # Cuesta un redraw por frame mientras el diálogo está abierto.
    renpy.register_textshader(
        "ts_glitch",
        variables="""
        uniform sampler2D tex0;
        uniform vec2 res0;
        uniform float u__intensidad;
        uniform float u__velocidad;
        uniform float u_time;
        uniform float u_text_to_drawable;
        uniform float u_text_main;
        attribute vec2 a_tex_coord;
        attribute vec2 a_text_center;
        varying vec2 v__uv;
        """,
        vertex_50="""
        v__uv = a_tex_coord;

        // Cambia por glifo y por "tick" de tiempo. La semilla usa
        // a_text_center (idéntico en todos los vértices del glifo): con
        // a_text_index el random cae por vértice y el glifo se rompe en
        // triángulos sueltos en vez de temblar.
        float l__tick = floor(u_time * u__velocidad);
        float l__seed = dot(a_text_center, vec2(0.0129898, 0.078233)) + l__tick * 0.3719;
        float l__n = fract(sin(l__seed) * 43758.5453);
        float l__act = step(0.78, l__n) * clamp(u__intensidad, 0.0, 1.0);

        gl_Position.x += (l__n - 0.5) * 6.0 * l__act * u_text_to_drawable;
        """,
        fragment_300="""
        // Sólo el texto principal: los outlines quedan legibles.
        if (u_text_main == 1.0) {
            vec2 l__d = vec2(clamp(u__intensidad, 0.0, 1.0) * 3.0 / max(res0.x, 1.0), 0.0);
            vec4 l__c = texture2D(tex0, v__uv);
            l__c.r = texture2D(tex0, v__uv + l__d).r;
            l__c.b = texture2D(tex0, v__uv - l__d).b;
            gl_FragColor = l__c;
        }
        """,
        u__intensidad=0.6,
        u__velocidad=14.0,
        # Sin redraw el efecto se congela cuando termina el revelado: el
        # texto deja de pedir frames y u_time deja de avanzar.
        redraw=0.05,
        doc="""
        Glitch de texto del template: sacude cada glifo y separa los canales
        rojo y azul. Pensado para diálogo glitcheado (estilo DDLC).

        `u__intensidad`
            Fuerza del efecto, de 0.0 a 1.0.

        `u__velocidad`
            Cambios por segundo; más alto, más nervioso.
        """,
    )
