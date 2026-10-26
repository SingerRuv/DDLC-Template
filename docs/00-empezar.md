# Empezar

Esta guía lleva un proyecto vacío a "arranca y puedo probar mi primera escena".

## 1. Requisitos

- **Ren'Py 8.5.x** (el template se probó con 8.5.3).
- **Doki Doki Literature Club** (versión PC), para aportar los assets oficiales.

> [!WARNING]
> No pongas Ren'Py ni el proyecto en una carpeta de nube (OneDrive, Google
> Drive, etc.): Ren'Py no soporta bien el bloqueo de archivos ahí y el juego
> puede fallar al arrancar.

## 2. Aportar los assets de DDLC

Por las [IP Guidelines](IP-GUIDELINES.md) el template **no incluye** los assets
oficiales. Copiá estos tres archivos de tu instalación de DDLC a `game/`:

```
audio.rpa
fonts.rpa
images.rpa
```

Con eso se resuelven las rutas `images/…`, `bgm/…`, `sfx/…` y `gui/…` (interfaz,
fuentes, botones). Los `.rpa` están en `.gitignore`: no se versionan ni viajan en
el ZIP del template.

Si te faltan, el juego arranca igual, pero no vas a ver sprites, fondos,
interfaz ni escuchar música.

### Android

En Android los `.rpa` no se pueden copiar a `game/`. En el **primer arranque** el
juego pide elegir el APK/XAPK de DDLC (o el ZIP de PC) y extrae los assets a la
carpeta escribible del juego. No hay que hacer nada más: la pantalla está en
`screens.rpy` y la lógica en `game/definitions/py/android_assets_ren.py`.

## 3. Abrir el proyecto

1. Abrí el **Ren'Py Launcher**.
2. Elegí el proyecto **DDLC BrokenDreamsModTemplate**.
3. **Launch Project**.

Con un proyecto recién clonado, `label start` (en `game/script.rpy`) muestra un
diálogo avisando que todavía no hay historia. Eso es lo normal.

## 4. Dónde va tu historia

Ren'Py carga **todos** los `.rpy` que estén debajo de `game/`, sin registrarlos en
ningún lado. Tenés dos formas:

- **Rápida:** escribí directo en `game/script.rpy`, dentro de `label start`.
- **Recomendada:** un archivo por capítulo en `game/story/` (por ejemplo
  `game/story/capitulo1.rpy`) y llamalos desde `start`:

```renpy
label start:
    call capitulo1
    call capitulo2
    return
```

Cada capítulo define su propio `label`:

```renpy
label capitulo1:
    scene bg class
    show sayori at t11
    s "¡Hola!"
    return
```

Reglas para no romperse:

- `label start` **tiene que existir una sola vez** en todo el proyecto.
- Los nombres de `label` son únicos; si repetís uno, Ren'Py falla al arrancar.
- No borres `game/script.rpy` sin dejar otro `label start`.

Ver [`01-historia.md`](01-historia.md) para el flujo completo.

## 5. Tus assets propios

Todo lo que no sea de DDLC va en `game/mod_assets/` (imágenes, CGs, audio) y se
declara en `game/definitions/`. Ver `game/mod_assets/README.md`.

## 6. Probar y revisar

- **Probar:** *Launch Project* en el launcher. Mientras el juego corre, los
  cambios en `.rpy` se recargan con `Shift+R`.
- **Revisar errores estáticos:** desde la consola del SDK,

  ```
  renpy.exe <ruta-del-proyecto> lint
  ```

  `lint` avisa de labels duplicados, imágenes inexistentes, variables sin
  definir y errores de estilo. Conviene correrlo antes de cada commit o release.

## 7. Errores comunes

| Síntoma | Causa probable |
|---|---|
| No se ven sprites, fondos ni la interfaz | Faltan `images.rpa`, `fonts.rpa` o `audio.rpa` en `game/` |
| `Label 'start' is defined twice` | Copiaste un `.rpy` con `label start` |
| `Image 'sayori 1a' not found` | Tag/pose mal escrito, o falta `images.rpa` |
| Cambios que no aparecen | Quedó un `.rpyc` viejo: borralo y volvé a lanzar |
| Acentos rotos o el archivo no compila | El `.rpy` no está en UTF-8 sin BOM |
| Ren'Py no abre el proyecto | Ruta con nube, espacios raros o `.rpy` corrupto |

## Siguiente

- [`01-historia.md`](01-historia.md) — escribir la historia.
- [`02-referencia.md`](02-referencia.md) — qué sprite/transform/audio usar.
