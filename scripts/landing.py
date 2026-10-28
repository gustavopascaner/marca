#!/usr/bin/env python3
"""Landing page estática de la marca: plantilla fija (assets/web/base.css) + brand.json + textos de la propuesta de valor.
uso: python3 -I landing.py <web.json> <slug> --out=<carpeta> [--foto=<imagen>] [--sin-captura]
Sale una carpeta lista (las capturas para revisar quedan al lado: web_desktop.png, web_mobile.png) para subir a cualquier hosting: index.html, styles.css, fonts/, img/, favicon.svg (sin dependencias externas).
<web.json> (lo escribe Claude con textos del cliente; *palabra* = se resalta con el color de la marca; todo bloque es opcional menos hero y cierre):
  {"seo":{"titulo":"Nombre · rubro","descripcion":"1 frase, ≤ 155 caracteres"},
   "hero":{"kicker":"rubro","titulo":"promesa con *una palabra* resaltada","bajada":"1–2 líneas","cta":"Agendá una entrevista"},
   "dolor":{"kicker":"…","titulo":"…","items":["…","…","…"]},
   "promesa":{"titulo":"…","texto":["párrafo","párrafo"]},
   "metodo":{"kicker":"…","titulo":"…","pasos":[{"titulo":"…","texto":"…"}]},
   "para_quien":{"titulo":"…","texto":"…","items":["…"]},
   "sobre":{"kicker":"…","titulo":"…","texto":["…"],"diferenciales":["…"]},
   "faq":[{"q":"…","a":"…"}],
   "cierre":{"titulo":"…","texto":"…","cta":"…"},
   "contacto":{"whatsapp":"+54 9 11 …","mensaje":"Hola, …","email":"…","instagram":"usuario","web":"…","direccion":"…"}}
Contacto: solo lo que esté en el material del cliente; sin datos, los botones van a #contacto y se avisa.
"""
import html, json, os, re, shutil, subprocess, sys, urllib.parse
from datetime import date

MK = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
BRANDS = os.path.expanduser('~/.config/motion/brands')
arg = lambda k, d=None: next((a.split('=', 1)[1] for a in sys.argv if a.startswith(f'--{k}=')), d)
jload = lambda p: json.load(open(p, encoding='utf-8'))
avisos = []


def lum(h):
    h = h.lstrip('#')
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    c = [x / 12.92 if x <= .03928 else ((x + .055) / 1.055) ** 2.4 for x in c]
    return .2126 * c[0] + .7152 * c[1] + .0722 * c[2]


def cr(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + .05) / (lb + .05)


def toward(a, b, k):   # mezcla hex a→b en proporción k
    a, b = (a.lstrip('#'), b.lstrip('#'))
    return '#' + ''.join(f"{round(int(a[i:i + 2], 16) * (1 - k) + int(b[i:i + 2], 16) * k):02X}" for i in (0, 2, 4))


def legible(col, bg, ink, need):   # el color de la marca, oscurecido/aclarado lo justo para leerse sobre bg
    k = 0
    while cr(toward(col, ink, k), bg) < need and k < 1:
        k += .04
    return toward(col, ink, min(k, 1))


def t(s):   # texto del cliente → HTML seguro, *x* resaltado
    return re.sub(r'\*(.+?)\*', r'<span class="hl">\1</span>', html.escape(s or ''))


def paras(x):
    return ''.join(f'<p>{t(p)}</p>' for p in ([x] if isinstance(x, str) else x or []))


def kick(s):
    return f'<span class="kicker">{t(s)}</span>' if s else ''


ARROW = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>'
CHECK = '<svg viewBox="0 0 26 26" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="13" cy="13" r="11.5" opacity=".35"/><path d="M8 13.4l3.3 3.2L18 9.6"/></svg>'


def deco(shape, c):
    a, b = c['accent'], c['accent2']
    if shape == 'blobs':
        g = (f'<path fill="{b}" opacity=".55" d="M402 64c84 30 160 112 158 214s-82 190-184 214-212-12-262-92-30-200 34-268 170-98 254-68z"/>'
             f'<path fill="{a}" opacity=".16" d="M286 190c66-22 158 6 196 70s22 150-38 196-160 44-214-6-60-136-16-196 6-42 72-64z"/>')
    elif shape == 'rings':
        g = ''.join(f'<circle cx="340" cy="300" r="{r}" fill="none" stroke="{a if i == 1 else b}" stroke-width="{2 if i else 26}" opacity="{.5 if i else .45}"/>'
                    for i, r in enumerate((250, 190, 130, 70)))
    elif shape == 'dots':
        g = ''.join(f'<circle cx="{110 + x * 46}" cy="{80 + y * 46}" r="{7 if (x + y) % 4 else 11}" fill="{a if (x * 3 + y) % 7 == 0 else b}" opacity=".7"/>'
                    for x in range(11) for y in range(10) if (x - 5) ** 2 + (y - 4.5) ** 2 < 30)
    else:   # clean: una forma grande y tenue
        g = f'<rect x="120" y="70" width="460" height="460" rx="230" fill="{b}" opacity=".45"/>'
    return f'<div class="deco" aria-hidden="true"><svg viewBox="0 0 680 600">{g}</svg></div>'


def fonts(b, bd, out):
    css, seen = [], set()
    os.makedirs(os.path.join(out, 'fonts'), exist_ok=True)
    for role in ('display', 'body', 'mono'):
        f = b['fonts'].get(role) or {}
        for fi in f.get('files', []):
            src = os.path.join(bd, fi['file'])
            if not os.path.exists(src) or src in seen:
                continue
            seen.add(src)
            name = os.path.basename(src)
            shutil.copy(src, os.path.join(out, 'fonts', name))
            fmt = {'ttf': 'truetype', 'otf': 'opentype', 'woff2': 'woff2', 'woff': 'woff'}.get(name.rsplit('.', 1)[-1].lower(), 'truetype')
            css.append(f"@font-face{{font-family:'{f['family']}';src:url('fonts/{name}') format('{fmt}');"
                       f"font-weight:{fi.get('weight', '400')};font-display:swap}}")
        if not f.get('files'):
            avisos.append(f'⚠️  la tipografía {role} ({f.get("family")}) no tiene archivos: correr brand.py setup')
    return '\n'.join(css)


def tema(b, bd, out):   # @font-face (copia las fuentes a out/fonts) + variables :root con contraste asegurado; lo usa también pdf.py
    c, st, F = b['colors'], b.get('style') or {}, b['fonts']
    on_acc = c['dark'] if cr(c['accent'], c['dark']) >= cr(c['accent'], c['light']) else c['light']
    if cr(c['accent'], on_acc) < 3:
        avisos.append(f'⚠️  accent {c["accent"]} con texto {on_acc}: contraste {cr(c["accent"], on_acc):.1f} < 3 (botones)')
    hl = legible(c['accent'], c['light'], c['dark'], 3)
    acc_txt = legible(c['accent'], c['light'], c['dark'], 4.5)
    hl_dark = next((x for x in (c['accent'], c['accent2']) if cr(x, c['dark']) >= 3), None) or legible(c['accent'], c['dark'], c['light'], 3)
    fam = lambda r: f"'{F[r]['family']}'," + ('ui-monospace,monospace' if r == 'mono' else 'system-ui,sans-serif')
    d = F['display']
    radius = int(st.get('radius', 24))
    root = (f":root{{--dark:{c['dark']};--light:{c['light']};--accent:{c['accent']};--accent2:{c['accent2']};--mute:{legible(c['mute'], toward(c['accent2'], c['light'], .68), c['dark'], 4.5)};"
            f"--on-accent:{on_acc};--hl:{hl};--hl-dark:{hl_dark};--accent-text:{acc_txt};"
            f"--tint:color-mix(in srgb,{c['accent2']} 32%,{c['light']});--line:color-mix(in srgb,{c['dark']} 12%,transparent);"
            f"--f-display:{fam('display')};--f-body:{fam('body')};--f-mono:{fam('mono')};"
            f"--w-display:{d.get('weight', 800)};--w-body:{min(int(F['body'].get('weight', 400)), 500)};"
            f"--tracking:{d.get('tracking', '-0.02em')};--leading:{max(float(d.get('leading', 1)), .95 if d.get('upper') else 1.02)};"
            f"--case:{'uppercase' if d.get('upper') else 'none'};--stretch:{d.get('stretch', '100%')};"
            f"--radius:{radius}px;--radius-btn:{999 if radius >= 28 else radius // 2}px}}")
    # lectura: el peso de body de los videos (700) es pesado para párrafos web; se usa ≤ 500 si hay archivo
    have = {int(fi.get('weight', 400)) for fi in F['body'].get('files', [])}
    if have and min(int(F['body'].get('weight', 400)), 500) not in have:
        root = root.replace(f"--w-body:{min(int(F['body'].get('weight', 400)), 500)}", f"--w-body:{min(have)}")
    return fonts(b, bd, out) + '\n' + root, on_acc


def destino(k, mensaje=None):   # contacto → link de los botones (WhatsApp con mensaje precargado, si no email, si no web); None si no hay nada
    wa = re.sub(r'\D', '', k.get('whatsapp', ''))
    mensaje = mensaje or k.get('mensaje')
    if wa:
        return f'https://wa.me/{wa}' + (f'?text={urllib.parse.quote(mensaje)}' if mensaje else '')
    if k.get('email'):
        return f'mailto:{k["email"]}'
    return k.get('web') or None


def main():
    if len(sys.argv) < 3 or not arg('out'):
        sys.exit(__doc__)
    w, slug, out = jload(sys.argv[1]), sys.argv[2], os.path.abspath(arg('out'))
    bd = os.path.join(BRANDS, slug)
    b = jload(os.path.join(bd, 'brand.json'))
    c, st = b['colors'], b.get('style') or {}
    radius = int(st.get('radius', 24))
    os.makedirs(out, exist_ok=True)
    for x in ('hero', 'cierre'):
        if not w.get(x):
            sys.exit(f'✗ web.json necesita "{x}"')
    css, on_acc = tema(b, bd, out)
    css += '\n' + open(os.path.join(MK, 'assets', 'web', 'base.css'), encoding='utf-8').read()
    open(os.path.join(out, 'styles.css'), 'w', encoding='utf-8').write(css)

    # contacto → destino de los botones
    k = w.get('contacto') or {}
    wa = re.sub(r'\D', '', k.get('whatsapp', ''))
    href = destino(k)
    if not href:
        href = '#contacto'
        avisos.append('⚠️  sin WhatsApp ni email: los botones apuntan a #contacto (pedirle a Gus el dato y volver a correr)')
    ext = ' target="_blank" rel="noopener"' if href.startswith('http') else ''
    btn = lambda txt, cls='btn': f'<a class="{cls}" href="{html.escape(href)}"{ext}>{t(txt)}{ARROW}</a>'

    # imágenes
    os.makedirs(os.path.join(out, 'img'), exist_ok=True)
    logo = ''
    if b.get('logo') and os.path.exists(os.path.join(bd, b['logo'])):
        shutil.copy(os.path.join(bd, b['logo']), os.path.join(out, 'img', os.path.basename(b['logo'])))
        logo = f'img/{os.path.basename(b["logo"])}'
    foto = ''
    if arg('foto'):
        ext_f = os.path.splitext(arg('foto'))[1].lower() or '.jpg'
        shutil.copy(arg('foto'), os.path.join(out, 'img', 'foto' + ext_f))
        foto = 'img/foto' + ext_f
    nombre = b['name'].split('·')[0].strip()
    ini = ''.join(p[0] for p in re.sub(r'^(Dr|Dra|Lic)\.?\s+', '', nombre).split()[:2]).upper()
    open(os.path.join(out, 'favicon.svg'), 'w', encoding='utf-8').write(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="{min(radius, 32)}" fill="{c["accent"]}"/>'
        f'<text x="32" y="42" text-anchor="middle" font-family="system-ui,sans-serif" font-weight="800" font-size="{26 if len(ini) > 1 else 32}" fill="{on_acc}">{html.escape(ini)}</text></svg>')

    # secciones
    h, S = w['hero'], []
    long_h = len(re.sub(r'\*', '', h.get('titulo', ''))) > 60
    S.append(f'<section class="hero{" wide" if long_h else ""}{" grid-bg" if st.get("grid") else ""}">{deco(st.get("shapes", "clean"), c)}<div class="wrap">'
             f'{kick(h.get("kicker"))}<h1 class="rv">{t(h["titulo"])}</h1><p class="lead rv">{t(h.get("bajada"))}</p>'
             f'<div class="actions rv">{btn(h.get("cta", "Escribime"))}'
             + (f'<a class="link" href="#metodo">{t(w["metodo"].get("link", "Cómo trabajo"))}</a>' if w.get('metodo') else '') + '</div></div></section>')
    if w.get('dolor'):
        x = w['dolor']
        S.append(f'<section class="s-dark"><div class="narrow">{kick(x.get("kicker"))}<h2 class="rv">{t(x["titulo"])}</h2>'
                 + (f'<ul class="pains">' + ''.join(f'<li class="rv">{t(i)}</li>' for i in x.get('items', [])) + '</ul>' if x.get('items') else '')
                 + '</div></section>')
    if w.get('promesa'):
        x = w['promesa']
        S.append(f'<section class="promise"><div class="wrap">{kick(x.get("kicker"))}<h2 class="rv">{t(x["titulo"])}</h2></div>'
                 f'<div class="wrap"><div class="rv" style="max-width:62ch">{paras(x.get("texto"))}</div></div></section>')
    if w.get('metodo'):
        x = w['metodo']
        S.append(f'<section class="s-tint" id="metodo"><div class="wrap">{kick(x.get("kicker"))}<h2 class="rv">{t(x["titulo"])}</h2>'
                 + (f'<p class="lead rv">{t(x["bajada"])}</p>' if x.get('bajada') else '')
                 + '<div class="steps">' + ''.join(f'<article class="step rv"><span class="n">{i + 1:02d}</span><h3>{t(p["titulo"])}</h3><p>{t(p.get("texto"))}</p></article>'
                                                   for i, p in enumerate(x.get('pasos', []))) + '</div></div></section>')
    if w.get('para_quien'):
        x = w['para_quien']
        S.append(f'<section><div class="wrap fit"><div>{kick(x.get("kicker"))}<h2 class="rv">{t(x["titulo"])}</h2>{paras(x.get("texto"))}</div>'
                 '<ul class="checks">' + ''.join(f'<li class="rv">{CHECK}<span>{t(i)}</span></li>' for i in x.get('items', [])) + '</ul></div></section>')
    if w.get('sobre'):
        x = w['sobre']
        img = f'<img class="rv" src="{foto}" alt="{html.escape(nombre)}" loading="lazy">' if foto else ''
        S.append(f'<section><div class="wrap about{"" if foto else " solo"}">{img}<div>'
                 f'{kick(x.get("kicker"))}<h2 class="rv">{t(x["titulo"])}</h2><div class="rv">{paras(x.get("texto"))}</div>'
                 + (f'<ul class="diffs">' + ''.join(f'<li>{t(i)}</li>' for i in x.get('diferenciales', [])) + '</ul>' if x.get('diferenciales') else '')
                 + '</div></div></section>')
    if w.get('faq'):
        S.append('<section class="faq"><div class="narrow"><span class="kicker">Preguntas frecuentes</span><h2 class="rv">Lo que suelen preguntarme</h2>'
                 + ''.join(f'<details class="rv"><summary>{t(q["q"])}</summary><p>{t(q["a"])}</p></details>' for q in w['faq']) + '</div></section>')
    x = w['cierre']
    S.append(f'<section class="s-accent close" id="contacto"><div class="wrap"><h2 class="rv">{t(x["titulo"])}</h2>'
             f'<p class="rv">{t(x.get("texto"))}</p><div class="rv">{btn(x.get("cta", h.get("cta", "Escribime")), "btn inv")}</div></div></section>')

    links = []
    if wa:
        links.append(f'<a href="https://wa.me/{wa}" target="_blank" rel="noopener">WhatsApp</a>')
    if k.get('email'):
        links.append(f'<a href="mailto:{html.escape(k["email"])}">{html.escape(k["email"])}</a>')
    if k.get('instagram'):
        u = k['instagram'].lstrip('@')
        links.append(f'<a href="https://instagram.com/{html.escape(u)}" target="_blank" rel="noopener">@{html.escape(u)}</a>')
    if k.get('direccion'):
        links.append(f'<span>{html.escape(k["direccion"])}</span>')
    mark = f'<img src="{logo}" alt="{html.escape(nombre)}">' if logo else html.escape(nombre)
    seo = w.get('seo') or {}
    title = seo.get('titulo') or nombre
    desc = seo.get('descripcion') or re.sub(r'\*', '', h.get('bajada', ''))
    grain = ('<svg class="grain" aria-hidden="true"><filter id="g"><feTurbulence type="fractalNoise" baseFrequency=".8" numOctaves="3" stitchTiles="stitch"/></filter>'
             '<rect width="100%" height="100%" filter="url(#g)"/></svg>') if st.get('grain') else ''
    page = f'''<!doctype html>
<html lang="es-AR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:type" content="website">
<meta name="theme-color" content="{c['light']}">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="preload" href="styles.css" as="style">
<link rel="stylesheet" href="styles.css">
</head>
<body>
<header class="nav"><div class="wrap"><a class="wordmark" href="#">{mark}</a>{btn(h.get("cta_corto", "Contacto"))}</div></header>
<main>
{chr(10).join(S)}
</main>
<footer><div class="wrap"><span>© {date.today().year} {html.escape(nombre)}</span><nav>{"".join(links)}</nav></div></footer>
{grain}
<script>
(()=>{{const els=document.querySelectorAll('.rv');if(!('IntersectionObserver' in window)){{els.forEach(e=>e.classList.add('in'));return}}
const io=new IntersectionObserver(es=>es.forEach(e=>{{if(e.isIntersecting){{e.target.classList.add('in');io.unobserve(e.target)}}}}),{{rootMargin:'0px 0px -8% 0px'}});
els.forEach(e=>io.observe(e))}})();
</script>
</body>
</html>
'''
    open(os.path.join(out, 'index.html'), 'w', encoding='utf-8').write(page)
    if len(desc) > 160:
        avisos.append(f'⚠️  descripción SEO de {len(desc)} caracteres (> 160)')
    print('✓ landing:', os.path.join(out, 'index.html'))
    if '--sin-captura' not in sys.argv:
        r = subprocess.run(['node', os.path.join(MK, 'scripts', 'captura.js'), out], capture_output=True, text=True)
        print((r.stdout + r.stderr).strip())
    print('\n'.join(avisos))


if __name__ == '__main__':
    main()
