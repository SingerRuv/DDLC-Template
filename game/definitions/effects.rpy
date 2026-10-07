## effects.rpy
# Clases y screens que se usan para efectos especiales
# (rectángulos glitch, ráfagas de partículas, cortes de pantalla, invert, transform dizzy).

init python:
    import random
    import math
    from renpy.display.particle import SpriteManager

    def screenshot_srf_size():
        """Devuelve el tamaño de una superficie de captura 16:9 que coincide con la ventana."""
        width, height = renpy.get_physical_size()
        if float(width) / float(height) > 16.0 / 9.0:
            width = height * 16 / 9
        else:
            height = width * 9 / 16
        return (width, height)

    def screenshot_srf():
        """Devuelve una superficie de captura que coincide con el tamaño de la ventana."""
        srf = renpy.display.draw.screenshot(None)
        srf = renpy.display.scale.smoothscale(srf, screenshot_srf_size())
        return srf

    def invert():
        """Devuelve una copia con los colores invertidos de la pantalla actual."""
        srf = screenshot_srf()
        inv = renpy.Render(srf.get_width(), srf.get_height()).canvas().get_surface()
        inv.fill((255, 255, 255, 255))
        inv.blit(srf, (0, 0), None, 2)
        return inv

    class Invert(renpy.Displayable):
        """Displayable que muestra la pantalla invertida."""
        def __init__(self, delay=0.0, screenshot_delay=0.0):
            super(Invert, self).__init__()
            self.width, self.height = screenshot_srf_size()
            self.srf = invert()
            self.delay = delay

        def render(self, width, height, st, at):
            render = renpy.Render(self.width, self.height)
            if st >= self.delay:
                render.blit(self.srf, (0, 0))
            return render

    class RectCluster(python_object):
        """Crea un cúmulo de rectángulos de color sólido (para efectos glitch)."""
        __slots__ = ("sm", "rects", "timers", "displayable", "numRects", "rectWidth", "rectHeight")

        def __init__(self, theDisplayable, numRects=12, rectWidth=30, rectHeight=30):
            self.sm = SpriteManager(update=self.update)
            self.rects = []
            self.timers = []
            self.displayable = theDisplayable
            self.numRects = numRects
            self.rectWidth = rectWidth
            self.rectHeight = rectHeight
            for i in range(self.numRects):
                self.add(self.displayable)
                self.timers.append(random.random() * 0.4 + 0.1)

        def add(self, d):
            s = self.sm.create(d)
            s.x = random.randint(0, 40) * 32
            s.y = random.randint(0, 23) * 32
            s.width = self.rectWidth
            s.height = self.rectHeight
            self.rects.append(s)

        def update(self, st):
            for i, s in enumerate(self.rects):
                if st >= self.timers[i]:
                    s.x = random.randint(0, 40) * 32
                    s.y = random.randint(0, 23) * 32
                    self.timers[i] = st + random.random() * 0.4 + 0.1
            return 0

    class ParticleBurst(python_object):
        """Ráfaga de partículas que irradia desde un punto (usada en el menú principal)."""
        __slots__ = ("sm", "stars", "displayable", "explodeTime", "numParticles",
                     "particleTime", "particleXSpeed", "particleYSpeed",
                     "gravity", "timePassed")

        def __init__(self, theDisplayable, explodeTime=0, numParticles=20,
                     particleTime=0.500, particleXSpeed=3, particleYSpeed=5):
            self.sm = SpriteManager(update=self.update)
            self.stars = []
            self.displayable = theDisplayable
            self.explodeTime = explodeTime
            self.numParticles = numParticles
            self.particleTime = particleTime
            self.particleXSpeed = particleXSpeed
            self.particleYSpeed = particleYSpeed
            self.gravity = 240
            self.timePassed = 0
            for i in range(self.numParticles):
                self.add(self.displayable, 1)

        def add(self, d, speed):
            s = self.sm.create(d)
            speed = random.random()
            angle = random.random() * 3.14159 * 2
            xSpeed = speed * math.cos(angle) * self.particleXSpeed
            ySpeed = speed * math.sin(angle) * self.particleYSpeed - 1
            s.x = xSpeed * 24
            s.y = ySpeed * 24
            pTime = self.particleTime
            self.stars.append((s, ySpeed, xSpeed, pTime))

        def update(self, st):
            # Posición absoluta calculada desde `st` (no acumulada), con gravedad
            # para formar el arco, y vida `particleTime` (destroy + pop al expirar).
            sindex = 0
            for s, ySpeed, xSpeed, particleTime in self.stars:
                if st < particleTime:
                    s.x = xSpeed * 120 * (st + 0.20)
                    s.y = ySpeed * 120 * (st + 0.20) + (self.gravity * st * st)
                else:
                    s.destroy()
                    self.stars.pop(sindex)
                sindex += 1
            return 0

    class Piece(python_object):
        """Una franja horizontal usada por el efecto Tear."""
        __slots__ = ("startY", "endY", "offset", "timer", "ontime", "offtime", "targetOffset")

        def __init__(self, startY, endY):
            self.startY = startY
            self.endY = endY
            self.offset = 0
            self.timer = 0.0
            self.ontime = 0.0
            self.offtime = 0.0
            self.targetOffset = 0

    class Tear(renpy.Displayable):
        """Corta la pantalla en franjas horizontales que se desplazan arriba/abajo."""
        def __init__(self, number=10, offtimeMult=1, ontimeMult=1,
                     offsetMin=0, offsetMax=50, srf=None):
            super(Tear, self).__init__()
            self.width, self.height = screenshot_srf_size()
            self.srf = srf if srf is not None else screenshot_srf()
            self.pieces = []
            for i in range(number):
                self.pieces.append(self._new_piece(i, number, offtimeMult,
                                                    ontimeMult, offsetMin, offsetMax))

        def _new_piece(self, i, number, offtimeMult, ontimeMult,
                       offsetMin, offsetMax):
            startY = (i * self.height) // number
            endY = ((i + 1) * self.height) // number
            p = Piece(startY, endY)
            p.timer = random.random() * 0.5
            p.ontime = ontimeMult * random.random() * 0.05
            p.offtime = offtimeMult * (random.random() * 0.4 + 0.1)
            p.targetOffset = random.randint(offsetMin, offsetMax) * (1 if random.random() < 0.5 else -1)
            return p

        def render(self, width, height, st, at):
            render = renpy.Render(self.width, self.height)
            for piece in self.pieces:
                piece.timer += at
                if piece.timer >= piece.offtime + piece.ontime:
                    piece.timer = 0.0
                    piece.targetOffset = random.randint(-50, 50)
                if piece.timer < piece.ontime:
                    piece.offset = piece.targetOffset
                else:
                    piece.offset = 0
                subsrf = self.srf.subsurface((0, piece.startY, self.width, piece.endY - piece.startY))
                render.blit(subsrf, (piece.offset, piece.startY))
            renpy.redraw(self, 0)
            return render

    def recolorize(image, blackColor="#000", whiteColor="#fff", tintAmount=1):
        """
        Devuelve una imagen nueva donde los píxeles oscuros se tiñen hacia
        `blackColor` y los claros hacia `whiteColor`. `tintAmount` (0..1)
        controla la intensidad del recoloreado. Implementado con im.MatrixColor
        usando un gradiente de luminancia al objetivo — rápido y compatible con Ren'Py 8.
        """
        from store import im
        bc = renpy.easy.color(blackColor)
        wc = renpy.easy.color(whiteColor)
        m = [
            wc[0], 0, 0, 0, bc[0],
            0, wc[1], 0, 0, bc[1],
            0, 0, wc[2], 0, bc[2],
            0, 0, 0, tintAmount, 0,
        ]
        return im.MatrixColor(image, m)

# ----- Screens que invocan los efectos --------------------------------------

screen invert(length, delay=0.0):
    add Invert(delay) size (1280, 720)
    timer max(delay, 0.01) action PauseAudio("music")
    timer max(delay, 0.01) action Play("sound", audio.glitch1)
    timer length + delay action Hide("invert")
    on "hide" action PauseAudio("music", False)
    on "hide" action Stop("sound")

screen tear(number=10, offtimeMult=1, ontimeMult=1, offsetMin=0, offsetMax=50, srf=None):
    zorder 150
    add Tear(number, offtimeMult, ontimeMult, offsetMin, offsetMax, srf) size (1280, 720)

# ----- Animaciones ---------------------------------------------------------

# Sacude la imagen como si el jugador estuviera mareado (usado en escenas de muerte).
transform dizzy(m, t, subpixel=True):
    subpixel subpixel
    parallel:
        xoffset 0
        ease 0.75 * t xoffset 10 * m
        ease 0.75 * t xoffset 5 * m
        ease 0.75 * t xoffset -5 * m
        ease 0.75 * t xoffset -3 * m
        ease 0.75 * t xoffset -10 * m
        ease 0.75 * t xoffset 0
        ease 0.75 * t xoffset 5 * m
        ease 0.75 * t xoffset 0
        repeat
    parallel:
        yoffset 0
        ease 1.0 * t yoffset 5 * m
        ease 2.0 * t yoffset -5 * m
        easein 1.0 * t yoffset 0
        repeat
