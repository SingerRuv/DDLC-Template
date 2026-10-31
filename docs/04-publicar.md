# Publicar (mantenedores)

Guía para quien mantiene **el template**, no para mods derivados. Si estás
publicando tu mod, mirá el flujo de build del launcher de Ren'Py.

## Versionado

La versión del template vive en `game/options.rpy`:

```renpy
define config.version = "1.3.0"
```

Usa **SemVer** (`MAYOR.MENOR.PARCHE`):

- **MAYOR**: cambios que rompen compatibilidad (los saves viejos dejan de servir).
- **MENOR**: funciones o contenido nuevo compatible.
- **PARCHE**: correcciones y ajustes chicos.

En la rama `dev`, `config.version` se deja en `"0.0.0"`.

## Ramas

| Rama | Contenido |
|---|---|
| `dev` | Desarrollo: `config.version = "0.0.0"`, `.vscode/`, plugins en progreso |
| `main` | Releases: versión real, `CHANGELOG.md` / `RELEASE.md` / `RELEASES.md`, `.github/` (workflow del ZIP) |

Un **plugin en desarrollo vive solo en `dev`**: no pasa a `main` hasta que esté
listo.

Cuando un plugin pasa a `main`, van con él **sus documentos**: el generador
borra `docs/referencia/<plugin>.md` si el código del plugin no está (la
sección se saltea) y los links desde `docs/02-referencia.md` quedan rotos, así
que `gen_docs.py --check` falla. Subí el plugin y su referencia en el mismo
commit, o sacá los links.

Para sincronizar: commit en `dev` → push → `checkout main` → **cherry-pick** →
push → volver a `dev`. Antes de cambiar de rama, dejá sin commitear los archivos
locales (por ejemplo los sprites propios) o guardalos con `stash`.

## Checklist de release

1. **Versión**: subir `config.version` en `game/options.rpy` (rama `main`).
2. **Changelog**: actualizar `CHANGELOG.md` con lo agregado/corregido.
3. **Referencia**: regenerar/verificar la documentación generada.

   ```
   python tools/gen_docs.py --check
   ```

   Si falla, corré `python tools/gen_docs.py` y commiteá el resultado. Hacelo
   **en la rama que se publica**, porque la tabla de sprites depende de lo que
   esté commiteado. Si el fallo es `sobra docs/referencia/<plugin>.md`, el
   plugin todavía no llegó a esta rama: subilo con su referencia o sacá los
   links.
4. **Manifest**: lo genera el workflow con `tools/gen_manifest.py`; no se
   commitea (`game/migracion/manifest.json` está en `.gitignore`).
5. **Pruebas**:

   ```
   renpy.exe <ruta-del-proyecto> lint
   ```

   - Arrancar el juego y jugar el tramo inicial.
   - Probar el splash y el aviso legal.
   - `python game/migracion/migrar.py --selftest` (algoritmo de migración).
6. **Commit, tag y Release**: crear el tag (`1.3.0`) y la GitHub Release. El
   workflow arma el ZIP con `git archive`.

## Qué entra en el ZIP

`.gitattributes` marca como `export-ignore` (no van al ZIP):

```
.github/  .gitattributes  .gitignore  .vscode/
CHANGELOG.md  RELEASE.md  RELEASES.md  /tools/
```

> [!WARNING]
> `/tools/` está **anclado a la raíz**. No lo cambies por `tools/`: eso también
> excluiría `game/tools/` (el hub de Plugins) y rompería el juego publicado.

Tampoco viajan: `.rpa` de DDLC, `game/saves/`, `game/cache/`, `*.rpyc`, logs ni
respaldos de migración.

El ZIP **sí** incluye `docs/` y `docs/referencia/` (documentación para el
modder), y `game/migracion/` con el manifest generado.

## Migración entre versiones

El sistema de migración compara el manifest viejo con el nuevo: lo que el
modder no tocó se actualiza, lo que tocó se conserva, y lo agregado se respalda.
El aviso vive en el menú principal (`Actualizar vX.Y.Z`) y solo
aparece en modo dev; el jugador final nunca lo ve. Detalles en
`game/migracion/README.md`.

Consecuencia para el release: **todo archivo del template tiene que estar en el
manifest**. Si agregás algo fuera de `game/` que el manifiesto no liste (por
error de las reglas de `gen_manifest.py`), en la próxima migración se va a
respaldar y reemplazar como si fuera del modder. Si tocás las reglas, corré el
generador y revisá el conteo.

## Android

El build Android se hace desde el launcher de Ren'Py (*Android* → configurar →
*Build Package*). Recordá que los assets de DDLC no viajan en el APK: el jugador
los aporta en el primer arranque (ver [`00-empezar.md`](00-empezar.md)).

## Documentación

- Guías para modders: `docs/`.
- READMEs por carpeta: `game/README.md`, `game/tools/README.md`,
  `game/tools/plugins/README.md`, `game/migracion/README.md`, `game/tl/`.
- Scripts de mantenimiento: `tools/README.md`.
