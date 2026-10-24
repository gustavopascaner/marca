#!/usr/bin/env python3
"""Voz del cliente: clona su voz en ElevenLabs (Instant Voice Clone) y la guarda en la marca para /motion.
uso: python3 -I voz.py <slug> <audio1> [audio2 …] [--nombre="Nombre visible"] [--reemplazar] [--solo-preparar]
  · audios: mp3, wav, m4a, ogg/opus (WhatsApp) o video; se unen, se cortan silencios largos, se normalizan y se usan ≤ 3 min.
  · Escribe brand.json → "voice" con el clon (y el anterior en "voice_prev"). Si ya había un clon, frena salvo --reemplazar
    (el clon viejo NO se borra en ElevenLabs: se informa su id).
  · --solo-preparar: arma el audio y muestra la duración, sin subir nada (no gasta).
La clave es la de /motion (ELEVENLABS_API_KEY o ~/.config/motion/elevenlabs_key) y necesita el permiso "Voices: Write".
/podcast NO usa esto: su voz (la de Gus) es fija en su propio script.
"""
import json, os, subprocess, sys, tempfile, urllib.error, urllib.request, uuid

MSK = os.path.expanduser('~/.claude/skills/motion')
sys.path.insert(0, os.path.join(MSK, 'scripts'))
from tts import eleven_key   # misma clave que /motion, sin duplicar dónde se lee

BRANDS = os.path.expanduser('~/.config/motion/brands')
MAX_S, MIN_S = 180, 45
# Ajustes de clon: similitud y fuerza del clon al 100 %, expresiva y SIN language_code (con "es" sale acento de España)
CLON = {'model': 'eleven_v4', 'similarity': 1.0, 'clone_strength': 1.0, 'stability': 0.0, 'lang': None}
arg = lambda k, d=None: next((a.split('=', 1)[1] for a in sys.argv if a.startswith(f'--{k}=')), d)


def dur(f):
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f], capture_output=True, text=True)
    return float(r.stdout.strip() or 0)


def preparar(audios, out):
    """Une los audios, saca silencios largos, mono 44,1 kHz, −18 LUFS, ≤ 3 min → un mp3 (< 10 MB)."""
    args = ['ffmpeg', '-v', 'error', '-y']
    for a in audios:
        args += ['-i', a]
    n = len(audios)
    fc = ''.join(f'[{k}:a:0]aresample=44100,aformat=channel_layouts=mono[a{k}];' for k in range(n))
    fc += ''.join(f'[a{k}]' for k in range(n)) + f'concat=n={n}:v=0:a=1,'
    fc += 'silenceremove=stop_periods=-1:stop_duration=0.7:stop_threshold=-40dB,loudnorm=I=-18:TP=-1.5:LRA=11,aresample=44100,asetpts=N/SR/TB[o]'
    subprocess.run(args + ['-filter_complex', fc, '-map', '[o]', '-t', str(MAX_S), '-ac', '1', '-ar', '44100', '-b:a', '192k', out], check=True)
    return dur(out)


def subir(nombre, mp3, slug):
    b = uuid.uuid4().hex
    campos = [('name', nombre), ('remove_background_noise', 'true'),
              ('description', f'Clon de voz del cliente de la marca {slug} (para /motion)'),
              ('labels', json.dumps({'accent': 'argentine', 'marca': slug}))]
    body = b''.join(f'--{b}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode() for k, v in campos)
    body += (f'--{b}\r\nContent-Disposition: form-data; name="files"; filename="{slug}.mp3"\r\nContent-Type: audio/mpeg\r\n\r\n').encode()
    body += open(mp3, 'rb').read() + f'\r\n--{b}--\r\n'.encode()
    req = urllib.request.Request('https://api.elevenlabs.io/v1/voices/add', body,
                                 {'xi-api-key': eleven_key(), 'Content-Type': f'multipart/form-data; boundary={b}'})
    try:
        return json.loads(urllib.request.urlopen(req, timeout=180).read())['voice_id']
    except urllib.error.HTTPError as e:
        msg = e.read().decode('utf-8', 'replace')[:400]
        hint = {401: 'la clave no tiene permiso para crear voces: agregarle "Voices: Write" en elevenlabs.io → Developers → API Keys',
                402: 'sin créditos en la cuenta', 422: 'audio o parámetros inválidos'}.get(e.code, '')
        if 'voice_limit' in msg or 'maximum' in msg.lower():
            hint = 'se llegó al límite de voces del plan: borrar alguna en ElevenLabs (preguntarle a Gus cuál)'
        sys.exit(f'✗ ElevenLabs {e.code}: {hint}\n{msg}')


def main():
    pos = [a for a in sys.argv[1:] if not a.startswith('--')]
    if len(pos) < 2:
        sys.exit(__doc__)
    slug, audios = pos[0], [os.path.abspath(a) for a in pos[1:]]
    bf = os.path.join(BRANDS, slug, 'brand.json')
    if not os.path.exists(bf):
        sys.exit(f'✗ no existe la marca {slug} ({bf}): crearla primero con /marca')
    for a in audios:
        if not os.path.exists(a):
            sys.exit(f'✗ no existe {a}')
    brand = json.load(open(bf, encoding='utf-8'))
    old = brand.get('voice') or {}
    if old.get('clone') and '--reemplazar' not in sys.argv:
        sys.exit(f"✗ la marca ya tiene un clon ({old.get('name')} · {old.get('id')}). Para cambiarlo: --reemplazar")
    nombre = f"{arg('nombre', brand.get('name') or slug)} (clon)"
    with tempfile.TemporaryDirectory() as td:
        mp3 = os.path.join(td, f'{slug}.mp3')
        s = preparar(audios, mp3)
        print(f'audio preparado: {s:.0f} s útiles de {sum(map(dur, audios)):.0f} s ({os.path.getsize(mp3) / 1e6:.1f} MB)')
        if s < MIN_S:
            print(f'⚠️  menos de {MIN_S} s de voz limpia: el clon puede salir flojo; conviene pedir más audio (ideal 1–3 min, una sola persona, sin música)')
        if '--solo-preparar' in sys.argv:
            return
        vid = subir(nombre, mp3, slug)
    if old:
        brand['voice_prev'] = old
    brand['voice'] = {'engine': 'eleven', 'id': vid, 'name': nombre, 'clone': True, **CLON}
    json.dump(brand, open(bf, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'✓ clon creado: {nombre} · voice_id {vid}\n✓ guardado en {bf}')
    if old.get('clone'):
        print(f"ℹ️  el clon anterior sigue en ElevenLabs ({old.get('id')}); borrarlo solo si Gus lo pide")


main()
