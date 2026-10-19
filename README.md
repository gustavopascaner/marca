# marca

Skill de Claude Code: a partir de la **propuesta de valor** de un cliente crea su identidad visual (paleta, tipografías, estilo, subtítulos, voz) y entrega un **video de presentación de la marca** para que el cliente la mire y dé feedback.

- La marca se guarda en `~/.config/motion/brands/<slug>/brand.json` (+ `IDENTIDAD.md`) y la usan directamente las skills [motion](https://github.com/gustavopascaner/motion) y [edicion](https://github.com/gustavopascaner/edicion).
- El video de presentación usa una **locución fija** (voz femenina argentina, ElevenLabs) que explica qué está viendo el cliente y pide feedback, placas propias de **paleta** y **tipografías**, y textos sacados de la propuesta de valor del cliente.

## Requisitos
- La skill **motion** instalada en `~/.claude/skills/motion` (motor de render, `brand.py`, `mix.py`).

## Instalación
```bash
git clone https://github.com/gustavopascaner/marca ~/.claude/skills/marca
```
**Música:** no viene incluida (es licenciada). Poné un tema instrumental tuyo (`.wav` o `.mp3`) en `assets/musica/`; sin música, el video sale solo con voz.

## Uso
En Claude Code: `/marca` + la propuesta de valor (texto o archivo). Opcional: logo, colores o la carpeta del cliente.

## Archivos
| | |
|---|---|
| `SKILL.md` | Instrucciones de la skill |
| `scripts/muestra.py` | Arma y renderiza el video de presentación |
| `assets/story.js` | Placas sincronizadas con la locución |
| `assets/scenes.js` | Placas a medida: `paleta` y `tipos` |
| `assets/locucion/` | Locución fija (`voice.wav`, `words.json`, guion en `script.json`) |
