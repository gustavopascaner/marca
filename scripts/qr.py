#!/usr/bin/env python3
"""Código QR sin dependencias (modo byte, corrección M, máscara con menor penalización) → SVG.
uso: python3 -I qr.py "<texto>" [salida.svg]   ·   desde Python: qr.svg(texto, fg, bg)
Algoritmo según ISO/IEC 18004 (mismo esquema que la implementación de referencia de Nayuki)."""
import sys

# corrección M, por versión (índice 0 sin uso)
ECC = [-1, 10, 16, 26, 18, 24, 16, 18, 22, 22, 26, 30, 22, 22, 24, 24, 28, 28, 26, 26, 26, 26, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28]
BLOCKS = [-1, 1, 1, 1, 2, 2, 4, 4, 4, 5, 5, 5, 8, 9, 9, 10, 10, 11, 13, 14, 16, 17, 17, 18, 20, 21, 23, 25, 26, 28, 29, 31, 33, 35, 37, 38, 40, 43, 45, 47, 49]
FORMAT_M = 0


def raw_modules(v):
    r = (16 * v + 128) * v + 64
    if v >= 2:
        n = v // 7 + 2
        r -= (25 * n - 10) * n - 55
        if v >= 7:
            r -= 36
    return r


def data_codewords(v):
    return raw_modules(v) // 8 - ECC[v] * BLOCKS[v]


def gf_mul(x, y):
    z = 0
    for i in reversed(range(8)):
        z = (z << 1) ^ ((z >> 7) * 0x11D)
        z ^= ((y >> i) & 1) * x
    return z


def rs_divisor(n):
    r = [0] * (n - 1) + [1]
    root = 1
    for _ in range(n):
        for j in range(n):
            r[j] = gf_mul(r[j], root)
            if j + 1 < n:
                r[j] ^= r[j + 1]
        root = gf_mul(root, 2)
    return r


def rs_remainder(data, div):
    r = [0] * len(div)
    for b in data:
        f = b ^ r.pop(0)
        r.append(0)
        for i, c in enumerate(div):
            r[i] ^= gf_mul(c, f)
    return r


def encode(text):
    """→ matriz de booleanos (True = módulo oscuro), sin zona de silencio."""
    data = text.encode('utf-8')
    for v in range(1, 41):
        cc = 8 if v < 10 else 16
        if 4 + cc + len(data) * 8 <= data_codewords(v) * 8:
            break
    else:
        raise ValueError('texto demasiado largo para un QR')
    cap = data_codewords(v) * 8
    bits = [0, 1, 0, 0] + [(len(data) >> i) & 1 for i in reversed(range(cc))]
    for b in data:
        bits += [(b >> i) & 1 for i in reversed(range(8))]
    bits += [0] * min(4, cap - len(bits))
    bits += [0] * (-len(bits) % 8)
    cw = [int(''.join(map(str, bits[i:i + 8])), 2) for i in range(0, len(bits), 8)]
    pad = 0xEC
    while len(cw) < cap // 8:
        cw.append(pad)
        pad ^= 0xEC ^ 0x11

    # bloques + corrección, intercalados
    nb, el, raw = BLOCKS[v], ECC[v], raw_modules(v) // 8
    nshort, slen = nb - raw % nb, raw // nb
    div, blocks, k = rs_divisor(el), [], 0
    for i in range(nb):
        d = cw[k:k + slen - el + (0 if i < nshort else 1)]
        k += len(d)
        e = rs_remainder(d, div)
        if i < nshort:
            d = d + [0]
        blocks.append(d + e)
    final = [blk[i] for i in range(len(blocks[0])) for j, blk in enumerate(blocks) if i != slen - el or j >= nshort]

    size = v * 4 + 17
    M = [[False] * size for _ in range(size)]
    F = [[False] * size for _ in range(size)]

    def fn(x, y, d):
        M[y][x], F[y][x] = d, True

    for i in range(size):
        fn(6, i, i % 2 == 0)
        fn(i, 6, i % 2 == 0)
    for cx, cy in ((3, 3), (size - 4, 3), (3, size - 4)):
        for dy in range(-4, 5):
            for dx in range(-4, 5):
                x, y = cx + dx, cy + dy
                if 0 <= x < size and 0 <= y < size:
                    fn(x, y, max(abs(dx), abs(dy)) not in (2, 4))
    if v > 1:
        n = v // 7 + 2
        step = (v * 8 + n * 3 + 5) // (n * 4 - 4) * 2
        pos = [6] + [size - 7 - i * step for i in range(n - 1)][::-1]
        for i, a in enumerate(pos):
            for j, b in enumerate(pos):
                if (i, j) in ((0, 0), (0, n - 1), (n - 1, 0)):
                    continue
                for dy in range(-2, 3):
                    for dx in range(-2, 3):
                        fn(a + dx, b + dy, max(abs(dx), abs(dy)) != 1)

    def draw_format(mask):
        d = FORMAT_M << 3 | mask
        r = d
        for _ in range(10):
            r = (r << 1) ^ ((r >> 9) * 0x537)
        b = (d << 10 | r) ^ 0x5412
        g = lambda i: (b >> i) & 1 == 1
        for i in range(6):
            fn(8, i, g(i))
        fn(8, 7, g(6))
        fn(8, 8, g(7))
        fn(7, 8, g(8))
        for i in range(9, 15):
            fn(14 - i, 8, g(i))
        for i in range(8):
            fn(size - 1 - i, 8, g(i))
        for i in range(8, 15):
            fn(8, size - 15 + i, g(i))
        fn(8, size - 8, True)

    draw_format(0)
    if v >= 7:
        r = v
        for _ in range(12):
            r = (r << 1) ^ ((r >> 11) * 0x1F25)
        b = v << 12 | r
        for i in range(18):
            d = (b >> i) & 1 == 1
            a, c = size - 11 + i % 3, i // 3
            fn(a, c, d)
            fn(c, a, d)

    i, right = 0, size - 1
    while right >= 1:
        if right == 6:
            right = 5
        for vert in range(size):
            for j in range(2):
                x = right - j
                y = size - 1 - vert if ((right + 1) & 2) == 0 else vert
                if not F[y][x] and i < len(final) * 8:
                    M[y][x] = (final[i >> 3] >> (7 - (i & 7))) & 1 == 1
                    i += 1
        right -= 2

    masks = [lambda x, y: (x + y) % 2 == 0, lambda x, y: y % 2 == 0, lambda x, y: x % 3 == 0, lambda x, y: (x + y) % 3 == 0,
             lambda x, y: (x // 3 + y // 2) % 2 == 0, lambda x, y: x * y % 2 + x * y % 3 == 0,
             lambda x, y: (x * y % 2 + x * y % 3) % 2 == 0, lambda x, y: ((x + y) % 2 + x * y % 3) % 2 == 0]

    def apply(m):
        for y in range(size):
            for x in range(size):
                if not F[y][x] and masks[m](x, y):
                    M[y][x] = not M[y][x]

    def penalty():
        p = 0
        lines = [''.join('1' if c else '0' for c in row) for row in M]
        lines += [''.join('1' if M[y][x] else '0' for y in range(size)) for x in range(size)]
        for s in lines:
            run = 1
            for a, b in zip(s, s[1:]):
                if a == b:
                    run += 1
                else:
                    p += run - 2 if run >= 5 else 0
                    run = 1
            p += run - 2 if run >= 5 else 0
            pad = '0000' + s + '0000'
            p += 40 * (pad.count('10111010000') + pad.count('00001011101'))
        for y in range(size - 1):
            for x in range(size - 1):
                if M[y][x] == M[y][x + 1] == M[y + 1][x] == M[y + 1][x + 1]:
                    p += 3
        dark, tot = sum(map(sum, M)), size * size
        return p + ((abs(dark * 20 - tot * 10) + tot - 1) // tot - 1) * 10

    best = None
    for m in range(8):
        apply(m)
        draw_format(m)
        s = penalty()
        if best is None or s < best[0]:
            best = (s, m)
        apply(m)   # la máscara es XOR: se deshace aplicándola de nuevo
    apply(best[1])
    draw_format(best[1])
    return M


def svg(text, fg='#000', bg=None, quiet=4):
    M = encode(text)
    n = len(M) + quiet * 2
    d = ''.join(f'M{x + quiet} {y + quiet}h1v1h-1z' for y, row in enumerate(M) for x, c in enumerate(row) if c)
    back = f'<rect width="{n}" height="{n}" fill="{bg}"/>' if bg else ''
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {n} {n}" shape-rendering="crispEdges">'
            f'{back}<path fill="{fg}" d="{d}"/></svg>')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    out = svg(sys.argv[1], bg='#fff')
    if len(sys.argv) > 2:
        open(sys.argv[2], 'w').write(out)
    else:
        print(out)
