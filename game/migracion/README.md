# Sistema de migración de assets

Actualiza el **template** de un mod a una versión nueva **sin perder tus assets**.
Cuando sale una versión nueva, el juego te avisa y, si aceptás, respalda tus
archivos, reemplaza el template y devuelve tus cosas.

> El sistema se activa **solo si el proyecto tiene `game/migracion/manifest.json`**
> (es decir, si viene de un ZIP de release). El repo fuente del template no lo
> tiene, así que ahí **no pregunta ni muestra** el botón de actualizaciones.

## Por qué un script externo

Ren'Py **no puede reemplazar su propio código mientras está en ejecución** (el
`.rpy` ya está cargado). Por eso el juego solo **detecta, avisa y prepara**;
el reemplazo real lo hace `migrar.py`, que corre **fuera** del juego y espera a
que éste se cierre.

## Piezas

| Archivo | Rol |
|---|---|
| `migracion/manifest.json` | Lo genera cada release: versión del template + hash sha256 de cada archivo. **Fuente de verdad** de la versión. |
| `migracion/migracion.rpy` | In-game: lee la versión, consulta la última release de GitHub, muestra la ventana, escribe el trabajo y lanza el script. |
| `migracion/migracion_ui.rpy` | In-game: las ventanas (aviso, confirmación, "al día", reporte). |
| `migracion/migrar.py` | Externo (stdlib): espera el cierre, descarga, respalda, aplica y relanza. |

## Qué se preserva (nunca se toca)

- `game/mod_assets/**` — tus imágenes, fondos, CGs y audio.
- Todo lo que **agregaste** (p. ej. `game/script.rpy` con tu historia, capítulos).
- Los `gui/**` que pisaste.

Lo demás sigue esta regla, archivo por archivo:

| Caso | Acción |
|---|---|
| Archivo del template que vos NO tocaste | Se actualiza al del template nuevo |
| Archivo del template que vos editaste y el template NO cambió | Se conserva el tuyo |
| Archivo del template que vos editaste **y** el template también cambió | **Se conserva el tuyo + aviso** |
| Archivo nuevo del template | Se agrega |
| Archivo que el template ya no trae | Se deja el tuyo (aviso) |

Nunca se tocan: `*.rpa`, `game/saves/`, `*.rpyc`, `game/cache/`, logs.

## Flujo

1. Al arrancar (modo dev), el juego consulta la última release de GitHub
   (con caché de 24 h) y, si hay una versión nueva, muestra la ventana.
   También podés forzarlo con **Buscar actualizaciones** en el menú.
2. Aceptás → se escribe un trabajo, se lanza `migrar.py` y el juego se cierra.
3. `migrar.py` espera el cierre, descarga el ZIP del release, respalda **solo
   tus archivos** en `migracion_backup/` (en la raíz del proyecto, fuera de
   `game/`), aplica el update y **relanza** el juego.
4. Al reabrir, ves el **reporte** (qué se actualizó, qué se conservó, avisos y
   dónde quedó el respaldo).

## Modo manual (fallback)

Si el juego no arranca, podés correr el migrador a mano con el ZIP del release:

```
python game/migracion/migrar.py --zip <ruta-al-zip> --project <ruta-del-proyecto>
```

Y para probar el algoritmo de mezcla:

```
python game/migracion/migrar.py --selftest
```

## Modo offline

Si no tenés internet, bajá el ZIP del release y ponelo como
`game/migracion/manual.zip`. Al aceptar la migración, se usa ese ZIP en vez de
descargarlo.

## Para el release (studio)

El workflow de release corre `tools/gen_manifest.py` sobre el árbol extraído y
mete `game/migracion/manifest.json` en el ZIP. No hay que tocar nada a mano.
