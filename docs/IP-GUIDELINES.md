# IP Guidelines de Team Salvato

Este template es un proyecto de fans no oficial y sigue las **IP Guidelines**
de Team Salvato. El documento oficial y la versión más reciente están en:

**https://teamsalvato.com/ip-guidelines**

> Este archivo es solo un resumen orientativo para modders del template, no un
> documento legal. Consultá siempre el documento oficial.

## Puntos clave para mods y fangames

Resumen de lo que aplica a quien use este template:

- **No afiliación:** el mod debe dejar claro que es contenido de fans, no
  respaldado por Team Salvato, y que no estás afiliado ni representás a Team
  Salvato.
- **Aviso al primer arranque:** el mod debe declararse no afiliado y avisar que
  la historia original debe completarse antes de jugarlo, con un enlace a
  **https://ddlc.moe**.
- **Assets oficiales:** no se pueden empaquetar assets oficiales de DDLC
  (arte, música). Deben provenir de la instalación local de DDLC del jugador.
  **Por eso este template no los incluye:** aportá `audio.rpa`, `fonts.rpa` e
  `images.rpa` desde tu propia copia de DDLC a la carpeta `game/` (ver abajo).
- **Gratis, siempre:** los fangames/mods se distribuyen gratis; no se venden ni
  se monetizan.
- **Donaciones:** se aceptan, pero **fuera del juego** (solo en la página que lo
  aloja). No incluir enlaces de donación dentro del juego ni incitar a donar.
- **IA generativa:** no usar IA generativa para representar a los personajes de
  DDLC (texto, imágenes o audio), ni subir assets oficiales a modelos de IA.
- **Música (covers/remixes):** requieren el proceso de licencia del distribuidor
  y arte original.
- **Publicación en tiendas (itch.io, etc.):** solo PC; el título debe incluir
  "DDLC Fangame"; el logo debe ser original; la página no puede usar arte
  oficial de DDLC (salvo la sección de capturas); no se puede usar "Doki Doki"
  en el título.

## Créditos obligatorios

El template base (bronya_rand) **exige** acreditarse en tu mod:

```
This mod was made possible by bronya_rand's DDLC Mod Template 2.0:
https://github.com/Bronya-Rand/DDLCModTemplate2.0
```

Este template (MiTemplate / DDLC DokifileModTemplate) mantiene esa atribución en
el splash de arranque y en los créditos.

## Cómo aportar los assets oficiales

Este template **no incluye** los assets de DDLC (cumple las IP Guidelines). Para
que el juego funcione, copiá estos archivos de tu instalación de DDLC a la
carpeta `game/`:

```
audio.rpa
fonts.rpa
images.rpa
```

- `images.rpa` → provee `images/<doki>/…` (sprites), `images/bg/…` (fondos), etc.
- `audio.rpa` → provee `bgm/…` (música) y `sfx/…` (efectos).
- `fonts.rpa` → provee `gui/font/…` (fuentes).

Los `.rpa` están excluidos del control de versiones (`.gitignore`) para no
redistribuirlos. Cada modder/jugador debe colocarlos por su cuenta.
