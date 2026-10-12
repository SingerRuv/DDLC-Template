# Notas de la versión — listas para pegar en GitHub Releases

> Título sugerido del Release:
> `DDLC BrokenDreamsModTemplate 1.1.0`
>
> Tag: `1.1.0`

---

## DDLC BrokenDreamsModTemplate 1.1.0

Plantilla para crear mods de DDLC (Ren'Py 8), con el look del DDLC Mod Template
y sistemas listos para usar.

### Novedades
- `mod_assets/` ahora está en el searchpath de Ren'Py: tus assets propios se
  pueden referenciar con nombre corto (`"images/bg/mi_cuarto.png"`) igual que
  los de DDLC.
- La pestaña **Template Settings** (y su contenido) ya no aparece al publicar
  el juego.

### Correcciones
- `recolorize()` (`definitions/effects.rpy`) ya no usa el manipulador de imagen
  obsoleto `im.MatrixColor`.

### Instalación
1. Ren'Py 8.5.x + DDLC (PC).
2. Copiá `audio.rpa`, `fonts.rpa` e `images.rpa` de tu copia de DDLC a `game/`.
3. Arrancá el proyecto con el Launcher.

### Assets
> Este template **no incluye** assets oficiales de DDLC (cumple las IP Guidelines
> de Team Salvato). Se aportan desde tu propia copia del juego.

### Descarga
Bajá el ZIP adjunto `DDLCBrokenDreamsModTemplate-1.1.0.zip` y extraelo dentro de tu
carpeta `renpy-8.x.x-sdk/proyectos/`.
