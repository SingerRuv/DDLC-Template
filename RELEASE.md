# Notas de la versión — listas para pegar en GitHub Releases

> Título sugerido del Release:
> `DDLC BrokenDreamsModTemplate 1.2.0`
>
> Tag: `1.2.0`

---

## DDLC BrokenDreamsModTemplate 1.2.0

Plantilla para crear mods de DDLC (Ren'Py 8), con el look del DDLC Mod Template
y sistemas listos para usar.

### Novedades
- **Migración de assets:** cuando sale una versión nueva del template, el juego
  avisa y actualiza el template **conservando tus assets** (`mod_assets`, tu
  historia, tus `definitions` y `gui`). Solo se activa en proyectos derivados de
  un release.
- **Controles táctiles + accesibilidad:** gestos (deslizar) para Atrás/Historial/
  Menú, quick menu escalado en pantallas táctiles, y acceso a la pantalla de
  accesibilidad de Ren'Py.
- **Soporte Android:** en el primer arranque, el jugador extrae los assets de DDLC
  desde su APK/XAPK (o el ZIP de PC), con barra de progreso y cancelación
  (IP Guidelines de Team Salvato).
- **PoseLab** ahora elige la **familia** del transform además de la posición, y se
  sumaron transforms: `sink`/`hopfocus`, las familias `s*`/`h*`/`d*`/`hf*`,
  `l11`/`r11` y `thide`.

### Correcciones y limpieza
- Codificación de `splash.rpy`; pantalla `choice` migrada a la API vigente
  (`matrixcolor`); eliminado código muerto (~190 líneas).

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
Bajá el ZIP adjunto `DDLCBrokenDreamsModTemplate-1.2.0.zip` y extraelo dentro de tu
carpeta `renpy-8.x.x-sdk/proyectos/`.
