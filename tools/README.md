# `tools/` — scripts de mantenimiento

Scripts para quien mantiene el **template**. **No se distribuyen**: `/tools/`
está en `export-ignore` de `.gitattributes`, así que no viaja en el ZIP del
release (a diferencia de `game/tools/`, que sí es el hub de Plugins).

Todos son Python 3 con biblioteca estándar: no hace falta instalar nada.

## `gen_manifest.py`

Genera `game/migracion/manifest.json`: versión del template + hash sha256 de
cada archivo. El sistema de migración lo usa para distinguir lo que tocó el
modder de lo que cambió el template.

```
python tools/gen_manifest.py <raiz> --version 1.3.0 [--repo owner/repo]
python tools/gen_manifest.py --selftest
```

- Sin `--version` toma `config.version` de `options.rpy`.
- Lo corre el workflow de release; el manifest **no se commitea**
  (`game/migracion/manifest.json` está en `.gitignore`).
- Ignora `.rpa`, `*.rpyc`, `saves/`, `cache/`, logs y los `tools/` de la raíz.
  **No** ignora `game/tools/`: el hub de Plugins tiene que estar en el manifest.

## `gen_docs.py`

Genera la referencia de `docs/referencia/` a partir del código (sprites,
transforms, audio, efectos y plugins) y valida los enlaces relativos de toda la
documentación.

```
python tools/gen_docs.py            # regenera los .md
python tools/gen_docs.py --check    # no escribe: falla si hay diferencias o enlaces rotos
```

- Los `.md` generados **se commitean** y viajan en el release.
- No editar `docs/referencia/*` a mano: se pisa en la próxima corrida.
- La tabla de sprites solo lista los assets **versionados** (git): un set propio
  sin commitear no aparece en la documentación del template.
- En el ZIP no hay `.git`, así que el generador lista todo; por eso conviene
  correr `--check` en la rama que se publica.

## Flujo de release (resumen)

1. `python tools/gen_docs.py` y commitear si cambió algo.
2. Verificar `python tools/gen_docs.py --check`.
3. `renpy.exe <proyecto> lint`.
4. El workflow corre `gen_manifest.py` sobre el árbol y arma el ZIP con
   `git archive`.

El detalle está en [`docs/04-publicar.md`](../docs/04-publicar.md).
