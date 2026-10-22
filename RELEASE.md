# Notas de la versión — listas para pegar en GitHub Releases

> Título sugerido del Release:
> `DDLC BrokenDreamsModTemplate 1.2.1`
>
> Tag: `1.2.1`

---

## DDLC BrokenDreamsModTemplate 1.2.1

Plantilla para crear mods de DDLC (Ren'Py 8), con el look del DDLC Mod Template
y sistemas listos para usar.

### Novedades
- **PoseLab: sprites "cuerpo + expresión".** Soporte de sprites armados con dos
  capas (cuerpo + expresión), tanto con definiciones `Composite` como con las
  carpetas `Poses/` + `Expressions/`. Además avisa cuántos personajes detecta al
  abrir y suma el botón **Reescanear**.
- **Variantes de cara de Yuri y Natsuki.** Yuri suma `a2`–`e2` (rubor) y `y1`–`y7`;
  Natsuki suma las cabezas manga casuales (`12b`/`42b`) y `scream`, en todas sus
  poses.

### Corregido
- **Menú principal:** al cambiar de idioma ya no se repite la animación de
  entrada (logo, fondo, sprites). Solo cambia el texto y el fondo sigue con su
  paneo.

### Instalación
1. Ren'Py 8.5.x + DDLC (PC).
2. Copiá `audio.rpa`, `fonts.rpa` e `images.rpa` de tu copia de DDLC a `game/`.
3. Arrancá el proyecto con el Launcher.

### Android
En Android, el juego pide extraer los assets de DDLC desde tu APK/XAPK (o el ZIP de
PC) en el primer arranque. Ver el README.

### Assets
> Este template **no incluye** assets oficiales de DDLC (cumple las IP Guidelines
> de Team Salvato). Se aportan desde tu propia copia del juego.

### Descarga
Bajá el ZIP adjunto `DDLCBrokenDreamsModTemplate-1.2.1.zip` y extraelo dentro de tu
carpeta `renpy-8.x.x-sdk/proyectos/`.
