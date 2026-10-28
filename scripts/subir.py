#!/usr/bin/env python3
"""Publica las landings de todos los clientes en UN hosting compartido (Hostinger por FTPS), cada una en su carpeta:
  https://<dominio>/<slug>/
Sincroniza en vez de pisar: sube solo lo nuevo o cambiado, borra lo que ese cliente ya no usa y nunca toca la carpeta
de otro cliente. Las tipografías van a una carpeta compartida (_fonts/, nombre con hash: una sola copia por archivo) y
se borran solas cuando ningún cliente las usa. El estado vive en el servidor, en .landings.json.

uso:
  python3 -I subir.py config --host=ftp.dominio.com --user=u123.claude --dominio=landing.dominio.com [--dir=.] [--puerto=21]
      → guarda los datos del hosting (sin contraseña) en ~/.config/motion/hosting.json
  python3 -I subir.py clave
      → pide la contraseña FTP en la terminal y la guarda en el Llavero de macOS; la corre Gus, nunca Claude
  python3 -I subir.py <slug> <carpeta web> [--como=<carpeta remota>] [--prueba] [--forzar]
      → publica en https://<dominio>/<carpeta remota>/ (por defecto el slug). --prueba: muestra qué haría, sin tocar nada.
        --forzar: adoptar una carpeta que ya existía en el servidor y no subió este script.
  python3 -I subir.py lista          → qué clientes están publicados, cuándo y su URL
  python3 -I subir.py bajar <slug> [--prueba]   → despublica: borra los archivos de ese cliente (solo los que subió este script)
La contraseña también puede venir de MARCA_FTP_PASS. --sin-tls: FTP sin cifrar, solo si el servidor rechaza FTPS.
"""
import ftplib, hashlib, io, json, os, posixpath, re, ssl, subprocess, sys, urllib.error, urllib.request
from datetime import datetime

CONF = os.environ.get('MARCA_HOSTING', os.path.expanduser('~/.config/motion/hosting.json'))
KC = 'marca-ftp'   # servicio en el Llavero
MAN = '.landings.json'
FONTS = '_fonts'
arg = lambda k, d=None: next((a.split('=', 1)[1] for a in sys.argv if a.startswith(f'--{k}=')), d)
PRUEBA = '--prueba' in sys.argv
SKIP = {'.DS_Store', 'Thumbs.db'}
RESERVADO = {FONTS, MAN, 'index.html', '.htaccess', 'cgi-bin', '.well-known'}
PORTADA = b'<!doctype html><meta charset="utf-8"><meta name="robots" content="noindex"><title>.</title>\n'
# sin listado de carpetas y sin acceso al registro: que nadie vea la lista de clientes
HTACCESS = (b'# marca: generado por subir.py\nOptions -Indexes\n'
            b'<Files ".landings.json">\n  Require all denied\n</Files>\n')
HTACCESS_VIEJOS = {b'Options -Indexes\n'}
HASHED = re.compile(r'-[0-9a-f]{10}\.\w+$')


def conf():
    if not os.path.exists(CONF):
        sys.exit(f'✗ falta configurar el hosting: python3 -I {os.path.abspath(__file__)} config --host=… --user=… --dominio=…')
    return json.load(open(CONF, encoding='utf-8'))


def cuenta(w):
    return f"{w['user']}@{w['host']}"


def clave(w):
    if os.environ.get('MARCA_FTP_PASS'):
        return os.environ['MARCA_FTP_PASS']
    r = subprocess.run(['security', 'find-generic-password', '-s', KC, '-a', cuenta(w), '-w'], capture_output=True, text=True)
    if r.returncode:
        sys.exit(f'✗ no hay contraseña guardada para {cuenta(w)}: que Gus corra en su terminal\n'
                 f'   python3 -I {os.path.abspath(__file__)} clave')
    return r.stdout.rstrip('\n')


def login(f, w):
    try:
        f.login(w['user'], clave(w))
    except ftplib.error_perm as e:
        sys.exit(f'✗ el servidor rechazó el usuario o la contraseña ({e}). Revisar en Hostinger → Archivos → Cuentas FTP')


def conectar(w):
    host, port = w['host'], int(w.get('puerto', 21))
    if '--sin-tls' in sys.argv:   # último recurso (o FTP local de prueba): la contraseña viaja sin cifrar
        f = ftplib.FTP(timeout=30)
        f.connect(host, port)
        login(f, w)
        print(f'⚠️  conectado SIN cifrar a {host}')
    else:
        ctx, nota = ssl.create_default_context(), ''
        for _ in (1, 2):
            f = ftplib.FTP_TLS(context=ctx, timeout=30)
            f.connect(host, port)
            try:
                f.auth()
                break
            except ssl.SSLCertVerificationError:
                # Hostinger a veces presenta el certificado del servidor compartido y no del dominio: sigue cifrado, sin validar el nombre
                f.close()
                ctx = ssl.create_default_context()
                ctx.check_hostname, ctx.verify_mode = False, ssl.CERT_NONE
                nota = ' (⚠️  el certificado no es del dominio; la conexión igual va cifrada)'
            except ftplib.error_perm as e:
                sys.exit(f'✗ el servidor no acepta FTPS ({e}). Solo si Gus lo confirma: --sin-tls (la contraseña viaja sin cifrar)')
        login(f, w)
        f.prot_p()
        print(f'✓ conectado por FTPS a {host}{nota}')
    f.set_pasv(True)
    base = (w.get('dir') or '.').strip()
    if base not in ('', '.', '/'):
        try:
            f.cwd(base)
        except ftplib.error_perm:
            sys.exit(f'✗ no existe {base} en el servidor (si la cuenta FTP ya entra en la carpeta del subdominio, usar --dir=.)')
    return f


def cerrar(f):
    try:
        f.quit()
    except Exception:
        f.close()


class Remoto:
    """Operaciones sobre el servidor; con --prueba solo las anuncia."""

    def __init__(self, f):
        self.f, self.dirs = f, set()

    def nombres(self, d='.'):
        try:
            return {posixpath.basename(x.rstrip('/')) for x in self.f.nlst(d)} - {'.', '..', ''}
        except ftplib.error_perm:
            return set()

    def leer(self, p):
        b = io.BytesIO()
        try:
            self.f.retrbinary(f'RETR {p}', b.write)
        except ftplib.error_perm:
            return None
        return b.getvalue()

    def mkdirs(self, d):
        cur = ''
        for p in [x for x in d.split('/') if x]:
            cur = f'{cur}/{p}' if cur else p
            if cur not in self.dirs:
                try:
                    self.f.mkd(cur)
                except ftplib.error_perm:
                    pass   # ya existía
                self.dirs.add(cur)

    def poner(self, p, data, etiqueta=None):
        print('  ↑', etiqueta or p)
        if PRUEBA:
            return
        self.mkdirs(posixpath.dirname(p))
        tmp = p + '.subiendo'
        self.f.storbinary(f'STOR {tmp}', io.BytesIO(data))
        try:
            self.f.delete(p)
        except ftplib.error_perm:
            pass
        self.f.rename(tmp, p)   # nunca queda un archivo a medio subir con el nombre final

    def borrar(self, p):
        print('  ✗', p)
        if not PRUEBA:
            try:
                self.f.delete(p)
            except ftplib.error_perm:
                pass

    def limpiar_dirs(self, raiz, paths):   # borra carpetas que quedaron vacías, de la más profunda a la del cliente
        ds = {raiz}
        for p in paths:
            d = posixpath.dirname(p)
            while d.startswith(raiz + '/'):
                ds.add(d)
                d = posixpath.dirname(d)
        for d in sorted(ds, key=lambda x: -x.count('/')):
            if not PRUEBA and not self.nombres(d):
                try:
                    self.f.rmd(d)
                except ftplib.error_perm:
                    pass


def sha(b):
    return hashlib.sha256(b).hexdigest()


def leer_manifiesto(r):
    raw = r.leer(MAN)
    if raw is None:
        return {'clientes': {}}
    try:
        return json.loads(raw.decode('utf-8'))
    except ValueError:
        sys.exit(f'✗ {MAN} del servidor está dañado: no sigo para no borrar de más (revisarlo a mano)')


def guardar_manifiesto(r, m):
    r.poner(MAN, json.dumps(m, ensure_ascii=False, indent=1).encode('utf-8'), etiqueta=f'{MAN} (registro de clientes)')


def fuentes_en_uso(m):
    return {x for c in m['clientes'].values() for x in c.get('fonts', [])}


def barrer_fuentes(r, m, candidatas):   # borra de _fonts/ las que ya no usa ningún cliente
    for x in sorted(candidatas - fuentes_en_uso(m)):
        r.borrar(f'{FONTS}/{x}')


def preparar(src):
    """Archivos locales → {ruta relativa: bytes} y fuentes compartidas {nombre con hash: bytes}."""
    files, fonts, ren = {}, {}, {}
    for root, dirs, names in os.walk(src):
        dirs[:] = sorted(x for x in dirs if not x.startswith('.'))
        for n in sorted(names):
            if n in SKIP or n.startswith('.'):
                continue
            p = os.path.join(root, n)
            rel = os.path.relpath(p, src).replace(os.sep, '/')
            data = open(p, 'rb').read()
            if rel.startswith('fonts/') and rel.count('/') == 1:
                stem, ext = os.path.splitext(n)
                hn = f'{stem}-{sha(data)[:10]}{ext}'
                fonts[hn], ren[n] = data, hn
            else:
                files[rel] = data
    if 'styles.css' in files and ren:   # las fuentes salen de la carpeta compartida
        css = files['styles.css'].decode('utf-8')
        css = re.sub(r"url\('fonts/([^']+)'\)", lambda mt: f"url('../{FONTS}/{ren.get(mt.group(1), mt.group(1))}')", css)
        files['styles.css'] = css.encode('utf-8')
    return files, fonts


def publicar(slug, src):
    w = conf()
    src = os.path.abspath(src)
    if not os.path.exists(os.path.join(src, 'index.html')):
        sys.exit(f'✗ {src} no tiene index.html')
    carpeta = arg('como', slug).strip('/')
    if not re.fullmatch(r'[a-z0-9][a-z0-9-]*', carpeta) or carpeta in RESERVADO:
        sys.exit(f'✗ "{carpeta}" no sirve como carpeta (minúsculas, números y guiones)')
    files, fonts = preparar(src)
    f = conectar(w)
    r = Remoto(f)
    try:
        raiz = r.nombres()
        m = leer_manifiesto(r)
        prev = m['clientes'].get(carpeta)
        if prev is None and carpeta in raiz and '--forzar' not in sys.argv:
            sys.exit(f'✗ ya existe /{carpeta}/ en el servidor y no la subió este script: no la toco. Con el OK de Gus: --forzar')
        if prev and prev.get('slug') != slug and '--forzar' not in sys.argv:
            sys.exit(f'✗ /{carpeta}/ es de otro cliente ({prev.get("slug")}): elegir otra con --como=… o --forzar con el OK de Gus')
        print(f'{"PRUEBA (no toca nada) · " if PRUEBA else ""}{slug} → https://{w["dominio"]}/{carpeta}/')
        otros = sorted(x for x in raiz - RESERVADO - set(m['clientes']) - {carpeta} if not x.startswith('.') and x != 'default.php')
        if otros:
            print(f'ℹ️  en la raíz hay cosas que no son landings de este script (no se tocan): {", ".join(otros)}')
        # raíz del sitio: portada vacía y sin listado de carpetas, solo si no existen
        if 'index.html' not in raiz and 'index.php' not in raiz:
            r.poner('index.html', PORTADA, etiqueta='index.html (portada vacía de la raíz)')
        ht = r.leer('.htaccess') if '.htaccess' in raiz else None
        if ht is None or (ht != HTACCESS and (ht in HTACCESS_VIEJOS or ht.startswith(b'# marca:'))):   # uno ajeno no se toca
            r.poner('.htaccess', HTACCESS, etiqueta='.htaccess (sin listado de carpetas ni acceso al registro)')
        elif ht != HTACCESS and b'.landings.json' not in ht:
            print('⚠️  hay un .htaccess que no es de este script: el registro .landings.json podría verse desde el navegador')
        # fuentes compartidas: solo las que faltan
        en_server = r.nombres(FONTS) if FONTS in raiz else set()
        fnuevas = sorted(set(fonts) - en_server)
        for n in fnuevas:
            r.poner(f'{FONTS}/{n}', fonts[n])
        # archivos del cliente: subir lo cambiado, borrar lo que sobra
        viejos = (prev or {}).get('files', {})
        nuevos = {p: sha(d) for p, d in files.items()}
        cambiados = sorted(p for p in files if viejos.get(p) != nuevos[p])
        for p in cambiados:
            r.poner(f'{carpeta}/{p}', files[p])
        sobran = sorted(set(viejos) - set(nuevos))
        for p in sobran:
            r.borrar(f'{carpeta}/{p}')
        if sobran:
            r.limpiar_dirs(carpeta, [f'{carpeta}/{p}' for p in sobran])
        antes = fuentes_en_uso(m) | {x for x in en_server if HASHED.search(x)}
        m['clientes'][carpeta] = {'slug': slug, 'fecha': datetime.now().isoformat(timespec='seconds'),
                                  'files': nuevos, 'fonts': sorted(fonts)}
        barrer_fuentes(r, m, antes)
        if not (cambiados or sobran or fnuevas):
            print('= sin cambios')
        guardar_manifiesto(r, m)
        print(('· fin de la prueba' if PRUEBA else '✓ listo') +
              f' ({len(cambiados)} subidos, {len(sobran)} borrados, {len(fnuevas)} fuentes nuevas, {len(files) - len(cambiados)} sin cambios)')
    finally:
        cerrar(f)
    if not PRUEBA:
        verificar(f'https://{w["dominio"]}/{carpeta}/', os.path.join(src, 'index.html'))


def bajar(slug):
    w = conf()
    f = conectar(w)
    r = Remoto(f)
    try:
        m = leer_manifiesto(r)
        carpeta = next((k for k, v in m['clientes'].items() if k == slug or v.get('slug') == slug), None)
        if not carpeta:
            sys.exit(f'✗ {slug} no está publicado (ver: subir.py lista)')
        c = m['clientes'].pop(carpeta)
        print(f'{"PRUEBA (no toca nada) · " if PRUEBA else ""}despublicar https://{w["dominio"]}/{carpeta}/ ({len(c["files"])} archivos)')
        for p in sorted(c['files']):
            r.borrar(f'{carpeta}/{p}')
        r.limpiar_dirs(carpeta, [f'{carpeta}/{p}' for p in c['files']])
        barrer_fuentes(r, m, set(c.get('fonts', [])))
        guardar_manifiesto(r, m)
        quedan = set() if PRUEBA else r.nombres(carpeta)
        print(('· fin de la prueba' if PRUEBA else '✓ despublicado') +
              (f' (en /{carpeta}/ quedan archivos que no subió este script: {", ".join(sorted(quedan))})' if quedan else ''))
    finally:
        cerrar(f)


def lista():
    w = conf()
    f = conectar(w)
    try:
        m = leer_manifiesto(Remoto(f))
    finally:
        cerrar(f)
    if not m['clientes']:
        print('(nada publicado)')
    for k, v in sorted(m['clientes'].items()):
        print(f"{k:28} {v.get('fecha', '')[:16].replace('T', ' ')}  https://{w['dominio']}/{k}/")


def verificar(url, local):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'marca-subir/2', 'Cache-Control': 'no-cache'})
        body = urllib.request.urlopen(req, timeout=20).read().decode('utf-8', 'replace')
        t = open(local, encoding='utf-8').read().split('<title>')[1].split('</title>')[0]
        print(f'✓ en línea: {url}' if f'<title>{t}</title>' in body else
              f'⚠️  {url} responde pero todavía no muestra la versión nueva (caché: esperar unos minutos o purgar en hPanel)')
    except urllib.error.HTTPError as e:
        print(f'⚠️  {url} da error {e.code}' + (': Cloudflare no logra conexión segura con Hostinger → falta el certificado SSL del subdominio en hPanel → Seguridad → SSL (los archivos ya están subidos)' if e.code in (525, 526) else ''))
    except Exception as e:
        print(f'⚠️  no pude abrir {url} ({e}); si el subdominio es nuevo puede tardar en propagar o no tener SSL todavía')


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    cmd = sys.argv[1]
    if cmd == 'config':
        w = json.load(open(CONF, encoding='utf-8')) if os.path.exists(CONF) else {}
        for k in ('host', 'user', 'dir', 'dominio', 'puerto'):
            if arg(k) is not None:
                w[k] = int(arg(k)) if k == 'puerto' else arg(k)
        w.setdefault('dir', '.')
        if w.get('dominio'):
            w['dominio'] = re.sub(r'^https?://', '', w['dominio']).strip('/')
        os.makedirs(os.path.dirname(CONF), exist_ok=True)
        json.dump(w, open(CONF, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print('✓ hosting →', json.dumps(w, ensure_ascii=False))
    elif cmd == 'clave':
        w = conf()
        print(f'Contraseña FTP de {cuenta(w)} (la pide el Llavero dos veces, no se ve al escribir):')
        rc = subprocess.run(['security', 'add-generic-password', '-U', '-s', KC, '-a', cuenta(w), '-w']).returncode   # -w al final: pregunta en la terminal
        sys.exit('✗ no se pudo guardar') if rc else print('✓ guardada en el Llavero (servicio marca-ftp)')
    elif cmd == 'lista':
        lista()
    elif cmd == 'bajar' and len(sys.argv) > 2:
        bajar(sys.argv[2])
    elif len(sys.argv) > 2:
        publicar(cmd, sys.argv[2])
    else:
        sys.exit(__doc__)


main()
