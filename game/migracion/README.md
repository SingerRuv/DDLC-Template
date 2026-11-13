# Sistema de migración de assets

Actualiza el **template** de un mod a una versión nueva **sin perder tus assets**.
Cuando sale una versión nueva, el juego te avisa y, si aceptás, respalda tus
archivos, reemplaza el template y devuelve tus cosas.

> El sistema se activa **solo si el proyecto tiene `game/migracion/manifest.json`**
> (es decir, si viene de un ZIP de release) **y** corre en modo dev (el modder).
> El repo fuente del template no lo tiene, así que ahí **no pregunta ni muestra**
> el aviso ni el botón de actualizaciones.

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
| `migracion/migracion_carpetas.rpy` | In-game: detecta carpetas hermanas, lista candidatas y lanza la migración entre carpetas. |
| `migracion/migrar_carpetas.py` | Externo (stdlib): copia archivos propios a otra carpeta, respalda, arranca el destino y elimina la vieja. |

## Qué se preserva (nunca se toca)

- `game/mod_assets/**` — tus imágenes, fondos, CGs y audio.
- Todo lo que **agregaste** (p. ej. `game/script.rpy` con tu historia, capítulos).
  También lo que esté **fuera de `game/`** (`characters/`, tus propias carpetas).
- Los `gui/**` que pisaste.

Lo demás sigue esta regla, archivo por archivo:

| Caso | Acción |
|---|---|
| Archivo del template que vos NO tocaste | Se actualiza al del template nuevo |
| Archivo del template que vos editaste y el template NO cambió | Se conserva el tuyo |
| Archivo del template que vos editaste **y** el template también cambió | **Se conserva el tuyo + aviso** |
| Archivo nuevo del template | Se agrega |
| Archivo del template que **vos borraste** | Se respeta: no se vuelve a crear |
| Archivo que el template ya no trae | Se deja el tuyo (aviso) |

Nunca se tocan: `*.rpa`, `game/saves/`, `*.rpyc`, `game/cache/`, logs, la
basura de sistema (`Thumbs.db`, `.DS_Store`, `*.log`, `*.tmp`) ni las carpetas
ajenas del primer nivel (`.git/`, `.github/`, `.vscode/`, `.idea/`, `.vs/`,
`dist/`, `ZIPs/`, `tools/`, `migracion_backup/`, `plugin_backups/`). De
`game/plugins/_incoming/` solo se ignora lo interno (`_tmp/`, `_backups/`):
los ZIPs de `instalados/` son tuyos y se respaldan.

## Cambio de estructura en v2.0.0

A partir de 2.0.0 el hub de Plugins vive en `game/plugins/` (antes
`game/tools/`), con los plugins en la raíz de esa carpeta (antes
`game/tools/plugins/`). Antes de comparar el manifest, `migrar.py`:

1. mueve `game/tools/` a `game/plugins/` y aplana su `plugins/`;
2. mueve `game/tl/spanish/tools/` a `game/tl/spanish/plugins/`;
3. reescribe las claves del manifest viejo con la nueva ruta.

Los plugins propios del modder se mueven con la carpeta. Si algo falla, el
renombrado se revierte junto con el resto de la migración.

## Migración entre carpetas

Si el proyecto tiene otra carpeta hermana con `game/migracion/manifest.json`,
al arrancar se ofrece migrar entre carpetas. Requisitos y reglas:

- Solo en modo dev. Se puede iniciar desde cualquiera de las dos carpetas:
  siempre se copia de la versión menor a la mayor. Si la carpeta nueva inicia,
  importa la vieja.
- Se listan las hermanas con manifest; se recomienda la versión más nueva.
- Si las versiones son iguales, se avisa y se pregunta cuál usar como origen
  (por si una carpeta está corrupta).
- Se copian solo los archivos propios del origen, dentro y fuera de `game/`,
  según los hashes del manifest. No se copian docs/tools/README del template.
- `game/script.rpy` siempre se conserva de la plantilla destino; la historia
  del origen va en sus propios `.rpy`.
- En conflictos se conserva la versión propia del origen y se avisa.
- Las saves del origen se copian solo si el destino no tiene saves.
- Se copian al destino solo los `.rpa` que falten.
- La carpeta vieja queda intacta hasta que el destino confirma el arranque;
  después se elimina. Si el destino falla, se restaura y la vieja se conserva.
- La carpeta destino queda marcada con `.migracion_destino` y no se vuelve a
  ofrecer como candidata.
- Se ofrece una vez por arranque, antes del chequeo de GitHub; ambos flujos
  son independientes.
- Sin manifest en el proyecto actual no se ofrece nada.

## Flujo

1. Al arrancar (**modo dev**), el juego consulta la última release de GitHub
   (con caché de 24 h). Si hay una versión nueva, el **menú principal** muestra
   `Actualizar vX.Y.Z` arriba de Nueva Partida (con un latido); al tocarlo se abre la
   ventana para migrar. No hay ventanas automáticas: el aviso queda visible
   hasta que migrás o elegís "No volver a preguntar por esta versión". También
   podés forzar el chequeo con **Buscar actualizaciones** en Ajustes.
2. Aceptás → se escribe un trabajo, se lanza `migrar.py` y el juego se cierra.
3. `migrar.py` espera el cierre, descarga el ZIP del release, **valida** que sea
   un ZIP sano y más nuevo, respalda **solo tus archivos** en
   `migracion_backup/` (en la raíz del proyecto, fuera de `game/`), aplica el
   update (archivo por archivo, de forma atómica) y **relanza** el juego.
   Si algo falla a mitad, **revierte** los archivos ya reemplazados y deja un
   reporte de error. Todo queda registrado en `migracion/migracion.log`.
4. Al reabrir, ves el **reporte** (qué se actualizó, qué se conservó, avisos y
   dónde quedó el respaldo).

## Modo manual (fallback)

Si el juego no arranca, podés correr el migrador a mano con el ZIP del release:

```
python game/migracion/migrar.py --zip <ruta-al-zip> --project <ruta-del-proyecto>
```

Para ver qué haría, sin escribir nada:

```
python game/migracion/migrar.py --zip <ruta-al-zip> --project <ruta-del-proyecto> --dry-run
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
