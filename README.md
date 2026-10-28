# marca

Skill de Claude Code: a partir de la **propuesta de valor** de un cliente crea su identidad visual (paleta, tipografías, estilo, subtítulos, voz) entrega un **video de presentación de la marca** para que el cliente la mire y dé feedback, y una **landing page** estática con su propuesta de valor, que se sube a Hostinger por FTPS.

- La marca se guarda en `~/.config/motion/brands/<slug>/brand.json` (+ `IDENTIDAD.md`) y la usan directamente las skills [motion](https://github.com/gustavopascaner/motion) y [edicion](https://github.com/gustavopascaner/edicion).
- El video de presentación usa una **locución fija** (voz femenina argentina, ElevenLabs) que explica qué está viendo el cliente y pide feedback, placas propias de **paleta** y **tipografías**, y textos sacados de la propuesta de valor del cliente.

## Requisitos
- La skill **motion** instalada en `~/.claude/skills/motion` (motor de render, `brand.py`, `mix.py`).

## Instalación
```bash
git clone https://github.com/gustavopascaner/marca ~/.claude/skills/marca
```
**Música:** fija en `assets/musica/` (Warm Acoustic de ereymusic, licenciada en Envato Elements por Gus). Repo privado: no redistribuir.

## Publicar landings (una vez por compu)
```bash
python3 -I ~/.claude/skills/marca/scripts/subir.py clave
```
Pide la contraseña de la cuenta FTP de landing.misterrobot.net y la guarda en el Llavero de macOS.

## Uso
En Claude Code: `/marca` + la propuesta de valor (texto o archivo). Opcional: logo, colores o la carpeta del cliente.

## Archivos
| | |
|---|---|
| `SKILL.md` | Instrucciones de la skill |
| `scripts/muestra.py` | Arma y renderiza el video de presentación |
| `scripts/landing.py` | Arma la landing estática (`web/`) desde brand.json + `web.json` |
| `scripts/subir.py` | Publica cada landing en `<subdominio>/<slug>/` por FTPS, sincronizando (datos en `assets/hosting.json`, contraseña en el Llavero de cada compu) |
| `scripts/captura.js` | Capturas desktop/mobile de la landing para revisarla |
| `assets/hosting.json` | Hosting común de las landings (sin contraseña) |
| `assets/web/base.css` | Plantilla fija de la landing |
| `assets/story.js` | Placas sincronizadas con la locución |
| `assets/scenes.js` | Placas a medida: `paleta` y `tipos` |
| `assets/locucion/` | Locución fija (`voice.wav`, `words.json`, guion en `script.json`) |
| `assets/musica/` | Música fija de fondo |
