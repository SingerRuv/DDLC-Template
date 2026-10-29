# Referencia — Text shaders

> Generado por `tools/gen_docs.py` desde `game/definitions/textshaders.rpy`.
> **No editar a mano**: corré `python tools/gen_docs.py` después de tocar el código.

Text shaders propios del template. Los que trae Ren'Py (dissolve, flip, jitter, linetexture, offset, slowalpha, texture, typewriter, wave, zoom) se usan igual y están explicados en la guía [`02-referencia.md`](../02-referencia.md).

| Text shader | Uniforms | Qué hace |
|---|---|---|
| `ts_glitch` | `u__intensidad` = `0.6`, `u__velocidad` = `14.0` | Glitch de texto del template: sacude cada glifo y separa los canales rojo y azul. Pensado para diálogo glitcheado (estilo DDLC). |
