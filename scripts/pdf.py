#!/usr/bin/env python3
"""PDF de presentación de la marca: la misma propuesta que la landing, en placas verticales 9:16 para leer en el celular (una sección por placa), con su marca y sin texturas (igual que la web).
uso: python3 -I pdf.py <web.json> <slug> --out=<archivo.pdf> [--foto=<imagen>] [--url=<web del cliente>] [--sin-url]
Lee el mismo web.json que landing.py (ver su docstring). Para el PDF suma, opcional, en "contacto":
  "mensaje_pdf":"Hola …, vi tu presentación y …"   → texto precargado del WhatsApp que sale del PDF (sin él usa "mensaje" y avisa)
CTA en la última placa: botón con link (wa.me + mensaje_pdf; si no hay WhatsApp, email), QR del mismo link y el número escrito;
en el pie de cada placa el contacto con link y, en la última, la URL de la landing (landing.misterrobot.net/<slug>/ o --url).
Sale <archivo.pdf> y al lado la hoja para revisar (<archivo>.jpg). Fuentes incrustadas; los links quedan clickeables (se verifica).
"""
import html, os, re, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import landing as L   # noqa: E402  (mismos colores, tipografías y helpers que la web)
import qr             # noqa: E402

MK, t, paras, kick, arg = L.MK, L.t, L.paras, L.kick, L.arg
avisos = L.avisos


def landing_url(slug):
    cfg = {}
    for p in (os.path.join(MK, 'assets', 'hosting.json'), os.path.expanduser('~/.config/motion/hosting.json')):
        if os.path.exists(p):
            cfg.update(L.jload(p))
    return f'https://{cfg["dominio"]}/{slug}/' if cfg.get('dominio') else None


def main():
    if len(sys.argv) < 3 or not arg('out'):
        sys.exit(__doc__)
    w, slug, pdf = L.jload(sys.argv[1]), sys.argv[2], os.path.abspath(arg('out'))
    bd = os.path.join(L.BRANDS, slug)
    b = L.jload(os.path.join(bd, 'brand.json'))
    c, st = b['colors'], b.get('style') or {}
    for x in ('hero', 'cierre'):
        if not w.get(x):
            sys.exit(f'✗ web.json necesita "{x}"')
    work = os.path.join(os.path.dirname(os.path.abspath(sys.argv[1])), 'pdf')
    os.makedirs(os.path.join(work, 'img'), exist_ok=True)
    css, _ = L.tema(b, bd, work)
    css += '\n' + open(os.path.join(MK, 'assets', 'web', 'pdf.css'), encoding='utf-8').read()
    open(os.path.join(work, 'styles.css'), 'w', encoding='utf-8').write(css)

    # CTA: el mismo destino que la web, con mensaje propio del PDF
    k = w.get('contacto') or {}
    wa_num = k.get('whatsapp', '').strip()
    if wa_num and not k.get('mensaje_pdf'):
        avisos.append('⚠️  sin "mensaje_pdf" en contacto: el WhatsApp del PDF usa el mismo mensaje que la web (no se distingue de dónde llegó)')
    href = L.destino(k, k.get('mensaje_pdf'))
    if not href:
        avisos.append('⚠️  sin WhatsApp ni email: el PDF sale sin botón ni QR (pedirle a Gus el dato y volver a correr)')
    btn = (lambda txt, cls='btn': f'<a class="{cls}" href="{html.escape(href)}">{t(txt)}{L.ARROW}</a>') if href else (lambda *a: '')
    if wa_num:
        contacto_pie = f'<a href="{html.escape(href)}">WhatsApp {html.escape(wa_num)}</a>'
    elif k.get('email'):
        contacto_pie = f'<a href="mailto:{html.escape(k["email"])}">{html.escape(k["email"])}</a>'
    else:
        contacto_pie = ''
    web = None if '--sin-url' in sys.argv else (arg('url') or k.get('web') or landing_url(arg('como', slug)))
    if web and not (arg('url') or k.get('web')):
        avisos.append(f'⚠️  el PDF lleva la URL {web}: publicar la landing (/marca subir {slug}) antes de mandarlo')

    logo = ''
    if b.get('logo') and os.path.exists(os.path.join(bd, b['logo'])):
        L.shutil.copy(os.path.join(bd, b['logo']), os.path.join(work, 'img', os.path.basename(b['logo'])))
        logo = f'img/{os.path.basename(b["logo"])}'
    foto = ''
    if arg('foto'):
        ext_f = os.path.splitext(arg('foto'))[1].lower() or '.jpg'
        L.shutil.copy(arg('foto'), os.path.join(work, 'img', 'foto' + ext_f))
        foto = 'img/foto' + ext_f
    nombre = b['name'].split('·')[0].strip()
    mark = f'<img src="{logo}" alt="{html.escape(nombre)}">' if logo else html.escape(nombre)

    S = []   # (clase, contenido)
    h = w['hero']
    long_h = len(re.sub(r'\*', '', h.get('titulo', ''))) > 60
    S.append((f'cover{" grid-bg" if st.get("grid") else ""}',
              f'{L.deco(st.get("shapes", "clean"), c)}<span class="wordmark">{mark}</span><div class="hero-txt">{kick(h.get("kicker"))}'
              f'<h1{" class=wide" if long_h else ""}>{t(h["titulo"])}</h1><p class="lead">{t(h.get("bajada"))}</p></div>'))
    if w.get('dolor'):
        x = w['dolor']
        S.append(('s-dark', f'<div class="cols"><div>{kick(x.get("kicker"))}<h2>{t(x["titulo"])}</h2></div>'
                  + ('<ul class="pains">' + ''.join(f'<li>{t(i)}</li>' for i in x.get('items', [])) + '</ul>' if x.get('items') else '<div></div>')
                  + '</div>'))
    if w.get('promesa'):
        x = w['promesa']
        S.append(('promise', f'<div class="cols"><div>{kick(x.get("kicker"))}<h2>{t(x["titulo"])}</h2></div><div class="txt">{paras(x.get("texto"))}</div></div>'))
    if w.get('metodo'):
        x = w['metodo']
        pasos = x.get('pasos', [])
        S.append(('s-tint', f'{kick(x.get("kicker"))}<h2>{t(x["titulo"])}</h2>'
                  + (f'<p class="lead">{t(x["bajada"])}</p>' if x.get('bajada') else '')
                  + '<div class="steps">' + ''.join(f'<article class="step"><span class="n">{i + 1:02d}</span><h3>{t(p["titulo"])}</h3><p>{t(p.get("texto"))}</p></article>'
                                                             for i, p in enumerate(pasos)) + '</div>'))
    if w.get('para_quien'):
        x = w['para_quien']
        S.append(('', f'<div class="cols"><div>{kick(x.get("kicker"))}<h2>{t(x["titulo"])}</h2>{paras(x.get("texto"))}</div>'
                  '<ul class="checks">' + ''.join(f'<li>{L.CHECK}<span>{t(i)}</span></li>' for i in x.get('items', [])) + '</ul></div>'))
    if w.get('sobre'):
        x = w['sobre']
        img = f'<img src="{foto}" alt="{html.escape(nombre)}">' if foto else ''
        S.append(('', f'<div class="about{"" if foto else " solo"}">{img}<div>{kick(x.get("kicker"))}<h2>{t(x["titulo"])}</h2>{paras(x.get("texto"))}'
                  + ('<ul class="diffs">' + ''.join(f'<li>{t(i)}</li>' for i in x.get('diferenciales', [])) + '</ul>' if x.get('diferenciales') else '')
                  + '</div></div>'))
    faq = w.get('faq') or []
    for i in range(0, len(faq), 4):   # 4 preguntas por placa
        S.append(('s-tint' if not w.get('metodo') else '', f'<span class="kicker">Preguntas frecuentes</span><h2>Lo que suelen preguntarme</h2><div class="faqs">'
                  + ''.join(f'<div><h3>{t(q["q"])}</h3><p>{t(q["a"])}</p></div>' for q in faq[i:i + 4]) + '</div>'))
    x = w['cierre']
    caja = ''
    if href:
        cap = 'Escaneá para escribirme por WhatsApp' if wa_num else 'Escaneá para escribirme'
        dato = html.escape(wa_num or k.get('email', ''))
        caja = (f'<div class="qr"><a href="{html.escape(href)}">{qr.svg(href, fg=c["dark"])}</a><p class="cap">{cap}</p>'
                f'<a class="num" href="{html.escape(href)}">{dato}</a></div>')
    S.append(('s-accent', f'<div class="cta"><div><h2>{t(x["titulo"])}</h2><p class="txt">{t(x.get("texto"))}</p>'
              f'{btn(x.get("cta", h.get("cta", "Escribime")), "btn inv")}</div>{caja}</div>'))

    total, out = len(S), []
    for i, (cls, body) in enumerate(S, 1):
        izq = f'<a href="{html.escape(web)}">{html.escape(re.sub(r"^https?://|/$", "", web))}</a>' if (i == total and web) else html.escape(nombre)
        der = (contacto_pie if i not in (1, total) else '') + f'<span>{i:02d} / {total:02d}</span>'
        out.append(f'<section class="slide {cls}">{body}<div class="foot"><span>{izq}</span><span class="r">{der}</span></div></section>')
    page = f'''<!doctype html>
<html lang="es-AR"><head><meta charset="utf-8"><title>{html.escape(nombre)}</title><link rel="stylesheet" href="styles.css"></head>
<body>
{chr(10).join(out)}
</body></html>
'''
    open(os.path.join(work, 'index.html'), 'w', encoding='utf-8').write(page)
    os.makedirs(os.path.dirname(pdf), exist_ok=True)
    r = subprocess.run(['node', os.path.join(MK, 'scripts', 'pdf.js'), work, pdf], capture_output=True, text=True)
    print((r.stdout + r.stderr).strip())
    if not os.path.exists(pdf):
        sys.exit('✗ no se generó el PDF')
    if href:   # que el link del CTA quede como anotación clickeable
        raw = open(pdf, 'rb').read()
        if b'/URI' not in raw or href.split('?')[0].encode() not in raw:
            avisos.append('⚠️  el PDF no tiene el link del CTA como link clickeable: revisar')
        else:
            print(f'✓ CTA clickeable: {href}')
    print('\n'.join(avisos))


main()
