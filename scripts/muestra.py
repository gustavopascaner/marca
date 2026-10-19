#!/usr/bin/env python3
"""Presentación de marca en video: locución fija (assets/locucion), música fija (assets/musica), placas de paleta y
tipografías (assets/scenes.js) y una story fija (assets/story.js). Por cliente cambian solo la marca y los textos.
uso: python3 -I muestra.py <work> <slug> [--tono=calido] [--formato=9:16] [--out=<mp4>] [--solo-hoja]
<work>/textos.json (lo escribe Claude con textos del cliente, cortos):
  {"rubro":"psicóloga", "nombre":["Jorgelina","Ientilezza"], "frase":["línea 1","línea 2","línea 3"],
   "titulo":"frase corta para la tipografía de títulos", "cuerpo":"párrafo de 1–2 líneas para la de lectura",
   "pilares":["pilar 1","pilar 2","pilar 3"]}
No guarda el look en el historial de la marca (la presentación no cuenta como video publicado).
"""
import json, os, shutil, subprocess, sys

MK = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
AS = os.path.join(MK, 'assets')
MSK = os.path.expanduser('~/.claude/skills/motion')
PY = os.path.join(MSK, '.venv', 'bin', 'python')
PY = PY if os.path.exists(PY) else sys.executable
arg = lambda k, d=None: next((a.split('=', 1)[1] for a in sys.argv if a.startswith(f'--{k}=')), d)
jload = lambda p: json.load(open(p, encoding='utf-8'))


def run(cmd, ok_fail=False):
    r = subprocess.run(cmd, capture_output=True, text=True)
    out = (r.stdout + r.stderr).strip()
    if out:
        print(out)
    if r.returncode and not ok_fail:
        sys.exit(f'✗ falló: {" ".join(cmd[:3])}…')


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    wd, slug = os.path.abspath(sys.argv[1]), sys.argv[2]
    tf = os.path.join(wd, 'textos.json')
    if not os.path.exists(tf):
        sys.exit(f'✗ falta {tf} (ver uso)')
    for f in ('voice.wav', 'words.json'):
        shutil.copy(os.path.join(AS, 'locucion', f), os.path.join(wd, f))
    for f in ('story.js', 'scenes.js'):
        shutil.copy(os.path.join(AS, f), os.path.join(wd, f))
    md = os.path.join(AS, 'musica')
    mus = sorted(x for x in os.listdir(md) if x.endswith(('.wav', '.mp3'))) if os.path.isdir(md) else []
    if not mus:
        print('⚠️  sin música en assets/musica: la presentación sale solo con voz')
    cfg = {'name': f'PRESENTACION_{slug.upper().replace("-", "_")}', 'out_dir': wd, 'edit_dir': wd,
           'format': arg('formato', '9:16'), 'fps': 30, 'brand': slug, 'tail': 1.6, 'keywords': [], 'sfx_max': 4,
           'music': {'path': os.path.join(AS, 'musica', mus[0]), 'offset': 0} if mus else {}, 'textos': jload(tf)}
    json.dump(cfg, open(os.path.join(wd, 'config.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    if mus:
        run([PY, '-I', f'{MSK}/scripts/beats.py', wd], ok_fail=True)
    run(['node', f'{MSK}/scripts/look.js', 'new', wd, f'--tono={arg("tono", "calido")}', '--estilo=auto', '--force'])
    run(['node', f'{MSK}/scripts/render.js', wd, '--check', '--at=mid,end'], ok_fail=True)   # la regla de "concept" de motion no aplica acá
    if '--solo-hoja' in sys.argv:
        return
    run(['node', f'{MSK}/scripts/render.js', wd, '--force'])
    run([PY, '-I', f'{MSK}/scripts/mix.py', wd])
    out = arg('out', os.path.join(wd, f'presentacion_{slug}.mp4'))
    shutil.copy(os.path.join(cfg['out_dir'], cfg['name'] + '.mp4'), out)
    sheet = os.path.join(os.path.dirname(out), f'hoja_{slug}.jpg')
    shutil.copy(os.path.join(wd, 'sheet.jpg'), sheet)
    print('✓ video:', out, '\n✓ hoja:', sheet)


main()
