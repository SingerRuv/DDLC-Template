# Releases — Ryu Mod Template

Notas de cada versión, listas para pegar en GitHub Releases.
El historial detallado está en [`CHANGELOG.md`](CHANGELOG.md).

---

## 2.0.0 — 2026-11-10

### Cambiado (ruptura)
- **Nueva estructura del hub:** `game/tools/` → `game/plugins/` (plugins en la
  raíz) y `game/tl/spanish/tools/` → `game/tl/spanish/plugins/`. La migración
  2.0.0 lo renombra y aplana automáticamente, conservando tus plugins y con
  rollback si algo falla.
- **Nombre y marca:** el template pasa a llamarse **Ryu Mod Template**
  (`build.name` y `save_directory`: `RyuModTemplate`). Autoría: **Ryu MaGucci**.
- Documentación y scripts de mantenimiento actualizados a las rutas nuevas.

### Agregado
- **Migración entre carpetas:** detecta proyectos hermanos con manifest y
  ofrece pasar los archivos propios a la versión nueva; respalda el destino y
  elimina la carpeta vieja cuando el arranque fue correcto.
- **Sprites estándar de Bronya:** 703 variantes de las cuatro dokis, con
  full-body Yuri `4*` y resto `5*`, sin especiales/yandere. PoseLab los
  etiqueta.
- **PoseLab 2.4:** estado de habla `Activo`/`Atenuado` (tinte con
  `t_activo`/`t_atenuar`) y sprites full-body. El preview muestra el tinte.
- Nuevos transforms `t_activo` y `t_atenuar` (tinte blanco/gris),
  combinables con cualquier posición: `at f21, t_activo`.

---

## 1.6.0 — 2026-11-04

### Agregado
- **Chequeos al arrancar:** ahora el juego avisa claro si falta algún `.rpa` de
  DDLC, si estás en Ren'Py 7 o si el proyecto está dentro de OneDrive.
- **Consola de Monika:** la terminal de DDLC se puede mostrar desde el guion
  con `$ console("entrada", "salida")` o `$ console.show_screen()`.
- **Personajes en disco:** `delete_character("sayori")` borra su `.chr` y
  `restore_characters()` repone los que falten (copiá los `.chr` de tu DDLC a
  `characters/` y `game/chrs/`; el template no los incluye).
- **Pantalla Créditos** en el menú principal, con los créditos del template y
  la atribución a bronya_rand.
- Parches para Ren'Py 8 (Windows 11 y animaciones DDLC) y el guiño del botón
  Nueva Partida en el acto 2 (texto glitcheado).

### Corregido
- `start` se comporta como en Bronya: al terminar tu historia cae sola en
  `endgame` (la pantalla de fin), así que ya no hace falta `call endgame` al
  final del guion.

---

## 1.5.3 — 2026-11-03

### Cambiado
- **New Game** quedó igual que Bronya: si ya hay nombre arranca con `Start()`;
  si no, pide el nombre y después salta a `start`. Sin la bandera
  `start_from_menu`.

### Corregido
- **Nueva Partida no iniciaba** cuando el `call` a la historia quedaba dentro
  del guard `start_from_menu`. El botón ya no usa esa bandera: lo que pongas en
  `start` se ejecuta siempre.

---

## 1.5.2 — 2026-11-03

### Cambiado
- **Copiar en…** es otro panel: muestra el archivo con números de línea y una
  **fila verde con el código ya indentado** en el lugar donde va a entrar. Se
  elige **Antes/Después**, avisa si el resultado rompería el script y tiene
  atajos (`Enter`, `Esc`, flechas). **Deshacer** indica la fecha del backup.
- Insertar código **ya no reinicia el juego**: el botón **Recargar scripts**
  aplica los cambios cuando quieras probarlos.

### Corregido
- Insertar desde **Copiar en…** reiniciaba el juego a los ~1,5 s. Ya no.
- Los nombres de los personajes ya no se pisan al empezar: el cuadro de diálogo
  muestra Sayori, Monika, Natsuki y Yuri sin tener que escribir `$ s_name = ...`
  en la historia. Para el modo de nombres ocultos, cambiá los `default` o
  asigná el nombre cuando quieras revelarlo.
- **PoseLab** ahora crea al personaje completo: además de los sprites, escribe
  su `define`/`default` en `definitions.rpy` (con el nombre tomado del tag) y
  lo aplica al toque, así podés hacer `akira "..."` sin reiniciar. También te
  ofrece arreglar los personajes que ya tenías creados.

---

## 1.5.1 — 2026-11-02

### Cambiado
- **Discord RPC** ahora está en los ajustes de DDLC (no en los del template) y
  funciona como en Bronya: muestra si está conectado y tiene un botón para
  activarlo o desactivarlo, más **Reconectar**.
- El modo desarrollador se declara en `True`, igual que Bronya. Para publicar tu
  mod, poné `config.developer = False` en `game/definitions/definitions.rpy`.
- El menú de pausa mantiene su música aunque el modo desarrollador esté apagado.

### Corregido
- El botón **Plugins** ahora se oculta siempre que `config.developer` esté en
  `False`, sin importar en qué archivo lo hayas puesto.

---

## 1.5.0 — 2026-11-02

### Agregado
- **Instalador de plugins:** ahora podés instalar plugins sin tocar carpetas a
  mano. Dejás el `.zip` en `game/tools/plugins/_incoming/` y, desde **Plugins →
  Instalar…**, lo instalás, lo actualizás o lo desinstalás. El instalador revisa
  el ZIP antes de escribir, guarda la versión anterior cuando actualizás y te
  ofrece reiniciar para que el plugin aparezca.

### Corregido
- Un `tool.json` guardado con BOM ya no se instala para después quedar
  invisible: el hub y el instalador ahora validan igual.
- Si un plugin trae el mismo identificador que otro que ya tenés instalado, se
  avisa como conflicto en vez de reemplazarlo sin querer.
- El instalador avisa si el plugin pide una versión de la API más nueva (se
  instala igual) y rechaza los ZIP que no traen ningún `.rpy`.

### Cambiado
- **Reiniciar ahora** salta el splash de arranque, y mientras instala se ve un
  aviso en pantalla.

---

## 1.4.2 — 2026-11-01

### Corregido
- **Aviso de template:** ahora aparece solo al empezar una partida desde **Nueva
  Partida**. Si algo llama a `start` por otro camino (autoload, consola), ya no
  interrumpe.
- **Reporte de migración:** ya no muestra los archivos que el template dejó de
  incluir.

---

## 1.4.1 — 2026-10-31

### Corregido
- **Reporte de migración:** la ventana ya no te deja atrapado cuando la lista es
  larga: tiene scroll, el botón **Entendido** queda siempre visible y ESC / clic
  derecho también la cierran.
- El chequeo de actualizaciones vuelve a consultar al menos una vez por hora
  cuando no hay novedades (antes podía quedarse hasta 24 h mostrando una versión
  vieja).

### Cambiado
- **Ajustes del Template** quedó ordenado en tres columnas alineadas.
- En **Discord Presence** el estado es ahora el propio botón (**Activado** /
  **Desactivado**), y la lista de idiomas está a su lado.

---

## 1.3.1 — 2026-10-30

### Añadido
- **PoseLab:** **Reescanear** relee los archivos del juego (carpetas nuevas o
  borradas) sin reiniciar, y si borraste la carpeta de un personaje avisa y
  ofrece borrar las definiciones que quedaron sin sus imágenes.
- **PoseLab:** las definiciones que crea para personajes propios se aplican al
  instante.

### Corregido
- **Copiar en… / Deshacer:** ya no recargan el script (y con eso la partida) a
  los ~1,5 s de escribir el `.rpy`.

---

## 1.3.0 — 2026-10-28

### Añadido
- **Hub de Plugins:** todas las herramientas comparten la misma barra
  (Copiar, Copiar en…, Reiniciar, Abrir carpeta, Volver).
- **Copiar en…:** el snippet se puede insertar directamente en un `.rpy` del
  guion, con copia de seguridad y deshacer.
- **Shaders Lab:** vista previa de los shaders de fondo, con glitch por franjas y
  cuadrados estilo DDLC.
- **Diálogo:** énfasis en el texto del diálogo (negrita, itálica, subrayado,
  tachado, color y tamaño) sobre la frase que marques, con vista previa del
  textbox del juego.
- **Text shaders:** `ts_glitch` para diálogo glitcheado.
- **Docs reorganizadas** y referencia generada desde el código.

### Corregido
- El texto del `say` lleva contorno, para leerse sobre cualquier fondo.
- Se traducen al español los mensajes de error del motor.
- Se quita el personaje `mc` del template.

---

## 1.2.3 — 2026-10-22

### Corregido
- **Actualización del template:** las herramientas del hub de Plugins (incluido
  **PoseLab**) no se actualizaban al migrar desde una versión anterior. Ahora
  están incluidas en el manifest de la release y se reemplazan correctamente.
- Después de migrar se descarta el bytecode viejo (`.rpyc`), así los cambios se
  aplican sin tener que borrarlos a mano.

---

## 1.2.2 — 2026-10-22

Plantilla para crear mods de **DDLC** sobre **Ren'Py 8**, con el look del DDLC
Mod Template y sistemas listos para usar.

### Novedades
- **Migración más segura.** Si la actualización falla a mitad, revierte los
  cambios y deja un reporte; ya no reaparecen archivos que borraste. Además,
  `migrar.py --dry-run` muestra qué haría sin tocar nada.
- **PoseLab más robusto.** El panel "Código" se ve con colores, se copia con
  Ctrl+C y sus ventanas se mueven y fijan. Respeta los archivos (LF, backup y
  guardado atómico) y detecta `Composite` multilínea, comillas simples y BOM.
- **Android:** el botón Cancelar funciona mientras extrae y no hay traceback al
  cancelar. En iOS, un aviso claro en vez de un error.
- **Aviso legal en inglés** con traducción al español (según el idioma elegido).

### Corregido
- Definiciones duplicadas de Natsuki (`12b`/`42b`).
- `Tear` y `ParticleBurst` (efectos) usan bien el tiempo y la lista.
- Todos los `.rpy` normalizados a UTF-8 sin BOM y LF.

---

## 1.2.1 — 2026-10-21

Plantilla para crear mods de **DDLC** sobre **Ren'Py 8**, con el look del DDLC
Mod Template y sistemas listos para usar.

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

---

## 1.2.0 — 2026-10-14

Plantilla para crear mods de **DDLC** sobre **Ren'Py 8**, con el look del DDLC
Mod Template y sistemas listos para usar.

### Novedades

**Migración de assets entre versiones del template**
Cuando sale una versión nueva, el juego te avisa y te ofrece actualizar: respalda
**tus** archivos, reemplaza el template y te los devuelve. El reemplazo lo hace un
script externo (`game/migracion/migrar.py`) al cerrar el juego, porque Ren'Py no
puede reemplazar su propio código mientras corre.
- Solo se activa en proyectos derivados de un release (con
  `game/migracion/manifest.json`) → **no molesta** en el repositorio fuente.
- **Preserva:** `mod_assets/**`, tu historia (`script.rpy` y capítulos), tus
  `definitions` editados y tus `gui`.
- **Conflictos:** gana **tu** versión + aviso.
- Te avisa al abrir (si hay internet y versión nueva); también podés forzarlo con
  **Buscar actualizaciones** en *Ajustes del Template*.

**Controles táctiles (mobile-first)**
- Gestos: deslizar **→** Atrás · **↑** Historial · **↓** Menú.
- **Quick menu escalado** en pantallas táctiles.
- Configurable por el modder en `game/definitions/touch.rpy`.

**Accesibilidad**
- Botón en Ajustes que abre la **pantalla de accesibilidad de Ren'Py**
  (self-voicing + opciones de texto/tamaño).

**Soporte Android**
- En el **primer arranque**, el jugador **extrae los assets de DDLC** desde su
  **APK/XAPK** (o el **ZIP de PC**) a la carpeta del juego, con **barra de progreso**
  y **cancelación**, según las **IP Guidelines de Team Salvato**.
- iOS queda bloqueado (no soportado).

**PoseLab: familias de transforms**
- Ahora se elige la **familia** del transform (Normal / Instantáneo / Focus / Hop /
  Dip / Sink / Hop-focus / Entrada izq / Entrada der) además de la **posición**
  (slot 11..44).

**Nuevos transforms** (`definitions/transforms.rpy`)
- `sink`, `hopfocus` y las familias `s*` / `h*` / `d*` / `hf*`, más `l11` / `r11` y
  `thide`.

### Corregido
- Codificación (mojibake) de `definitions/splash.rpy`.
- El sistema de migración queda inerte en el repositorio fuente (no tiene manifest).

### Cambiado
- `screens.rpy`: la pantalla `choice` ya no usa la API obsoleta `im.MatrixColor` /
  `im.matrix` (migrada a `Transform(matrixcolor=…)` con `SaturationMatrix`,
  `ContrastMatrix` y `ColorizeMatrix`).
- `options.rpy`: el build incluye el target `android` y los permisos de
  almacenamiento.

### Limpieza
- Eliminado código muerto (~190 líneas): bloque comentado *"Display Resolutions"*,
  `viewframe_options` y sus estilos, `screen rigged_choice`,
  `screen fake_skip_indicator`, `class RectCluster`, `def pl_tool_por_id` y
  `style pl_panel`.

### Documentación
- `README.md`: secciones de controles táctiles/accesibilidad y de Android.
- `game/migracion/README.md` y `game/tools/plugins/README.md`.

### Requisitos e instalación
1. **Ren'Py 8.5.x** + **DDLC** (PC).
2. Copiá `audio.rpa`, `fonts.rpa` e `images.rpa` de tu copia de DDLC a `game/`.
3. Abrí el proyecto con el Launcher y ejecutalo.

### Assets
> No incluye assets oficiales de DDLC (cumple las IP Guidelines de Team Salvato).
> Se aportan desde tu propia copia del juego. En Android, el juego los extrae del
> APK/XAPK del jugador.

### Descarga
`DDLCBrokenDreamsModTemplate-1.2.0.zip`

---

## Versiones anteriores
- **1.1.0** (2026-10-11) y **1.0.0** (2026-10-07): ver [`CHANGELOG.md`](CHANGELOG.md).
