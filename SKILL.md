---
name: marca
description: Crea la identidad visual de la marca de un cliente (paleta, tipografías, estilo, subtítulos, voz) a partir de su PROPUESTA DE VALOR, la guarda como brand.json para las skills /motion y /edicion y entrega un video de presentación de la marca para el cliente (locución y música fijas que piden feedback, placas con sus textos, su paleta y sus tipografías). Usar cuando el usuario escribe /marca con un texto o archivo, o pide "armá la marca de este cliente", "identidad visual para…", "marca nueva desde la propuesta de valor".
---

# /marca — propuesta de valor → identidad visual + video de muestra

Hablarle a Gus en español rioplatense, corto. **Una sola propuesta, directo** (no ofrecer alternativas): decidir y ejecutar; Gus ajusta después.
`MSK` = `~/.claude/skills/motion` (motor y `brand.py`). `PY` = `$MSK/.venv/bin/python -I` (si no existe, `python3 -I`). `MK` = `~/.claude/skills/marca`.
Las marcas viven en `~/.config/motion/brands/<slug>/` y las leen **/motion** (`render.js`, `look.js`) y **/edicion** (`brand.js`): el formato tiene que ser exactamente el de abajo.

## 0 · Entrada
- La propuesta de valor (texto o archivo). Opcional: logo, colores, tipografías existentes, carpeta del cliente.
- **Nombre** del profesional/marca: sacarlo del texto. Si no está, es lo único que se pregunta (una sola vez). `slug` = nombre en minúsculas con guiones, sin tildes. Si `brand.py list` ya tiene ese slug, avisar y preguntar si se pisa o se crea `<slug>-v2`.
- **Si trae logo o colores: respetarlos.** Logo → `$PY $MSK/scripts/brand.py colors <logo>` y mirarlo (estilo, peso, serif o no); la paleta parte de ahí y solo se completa lo que falte. Tipografías dadas → usarlas (Google Fonts por nombre).
- Carpeta de trabajo = la del archivo o el directorio actual. Salida: `<carpeta>/<slug>_MARCA/`.

## 1 · Leer la propuesta (en la cabeza, sin escribirlo largo)
Extraer: a quién le habla, qué dolor resuelve, la promesa, el método o los pilares, qué lo diferencia, el tono (cercano / experto / enérgico / sereno / premium) y 3 adjetivos de personalidad. De ahí sale todo; anotarlos en IDENTIDAD.md.

## 2 · Diseñar
Criterio: que se vea **de ese cliente y no de otro**. Correr `$PY $MSK/scripts/brand.py list` y no repetir la combinación acento + tipografía display de una marca existente.
- **Colores** (hex): `dark` (fondo oscuro, texto sobre claro), `light` (fondo claro, nunca blanco puro), `accent` (el color de la marca, resalta), `accent2` (secundario, contrasta con accent), `mute` (gris del tono de la paleta, textos secundarios). El color tiene que salir del sector y del tono, no del default (evitar azul genérico de salud si el tono es cálido, naranja si es sereno, etc.). Contraste: `light` sobre `dark` ≥ 7; `accent` usable como fondo con texto `dark` o `light` ≥ 3.
- **Tipografías** (Google Fonts): `display` (títulos: personalidad), `body` (lectura), `mono` (datos/kicks), `accent` (itálica o manuscrita para palabras sueltas). Referencia de pares: `$PY $MSK/scripts/brand.py fonts`. Display en mayúsculas (`upper: true`, `leading` 0.9–0.95) para tonos enérgicos/directos; en minúsculas (`upper: false`, `leading` 1.0) para cálidos/serenos/premium.
- **Estilo**: `shapes` = `blobs` (orgánico) · `rings` · `dots` · `clean`; `grid` true para técnico/datos; `radius` 10–48 (más redondo = más amable); `grain` true.
- **Subtítulos**: `on: true`, `upper` como el display si es enérgico, `size` 62–68.
- **Voz**: según quién es la persona de la marca (del texto: "soy psicóloga" → mujer; "soy kinesiólogo" → hombre; si es una empresa o no se sabe, mujer). Guardarla en brand.json como `"voice": {"id": "mujer"}` o `{"id": "hombre"}` (así /motion la usa sin preguntar).

## 3 · Guardar
1. `~/.config/motion/brands/<slug>/brand.json` (si hay logo, copiarlo ahí como `logo.png`/`logo.svg` y poner `"logo": "logo.png"`; si no, `null`):
```json
{"name":"<Nombre visible>",
 "colors":{"dark":"#","light":"#","accent":"#","accent2":"#","mute":"#"},
 "fonts":{"display":{"family":"…","weight":800,"upper":true,"stretch":"100%","tracking":"-0.02em","leading":0.95},
          "body":{"family":"…","weight":700},"mono":{"family":"…"},"accent":{"family":"…","italic":true}},
 "logo":null,
 "style":{"grain":true,"grid":false,"shapes":"blobs","radius":36,"progress":false},
 "captions":{"on":true,"upper":false,"size":64},
 "notes":"<1 línea de uso: qué color manda, qué evitar>"}
```
2. `$PY $MSK/scripts/brand.py setup <slug>` → baja las fuentes y chequea contraste. Corregir todos los ⚠️ (ajustar el hex, no ignorarlos) y repetir.
3. `IDENTIDAD.md` en la carpeta de la marca (≤ 15 líneas): idea de la marca en una frase, los 3 adjetivos, cada color con su rol, las tipografías y por qué, qué evitar. **Sin usuario de redes, sin títulos, credenciales ni resultados que no estén en el texto.**
4. Si hay carpeta del cliente: `$PY $MSK/scripts/brand.py remember "<carpeta>" <slug>` (así /motion y /edicion la detectan solas).

## 4 · Video de presentación de la marca (audio fijo, textos del cliente)
Todo lo fijo vive en `$MK/assets/` y **no se toca por cliente**: `locucion/` (voz Agustina, ElevenLabs, 47 s: saluda, dice que es la propuesta de identidad visual, pide mirar colores, tipografías y movimiento, y pide feedback; sin nombre del cliente), `musica/` (tema fijo licenciado), `story.js` (8 placas sincronizadas con la locución) y `scenes.js` (placas a medida `paleta` y `tipos`, que muestran los colores con su hex y las tipografías de títulos, acento y lectura con su nombre).
Por cliente solo se escribe `<carpeta>/<slug>_MARCA/.work/textos.json`, con textos **sacados de la propuesta de valor** (cortos; nunca cifras, testimonios ni @usuarios inventados):
```json
{"rubro":"<qué hace, 1–3 palabras>", "nombre":["<Nombre>","<Apellido o resto>"],
 "frase":["<idea central>","<en 2–3 líneas>","<la última se resalta>"],
 "titulo":"<frase corta del cliente para mostrar la tipografía de títulos>",
 "acento":"<frase corta del cliente (2–5 palabras) para mostrar la tipografía de acento>",
 "cuerpo":"<frase del cliente de 1–2 líneas para la de lectura>",
 "pilares":["<pilar 1>","<pilar 2>","<pilar 3>"]}
```
Correr: `python3 -I $MK/scripts/muestra.py "<work>" <slug> --tono=<energico|calido|institucional|humor|sobrio> --out="<carpeta>/<slug>_MARCA/presentacion_<slug>.mp4"` (≈ 1 min: copia lo fijo, look nuevo, hoja, render y mezcla con `mix.py` de motion). `--estilo=<slug>` fija el estilo de /motion (`papel`, `liquido`… en `$MSK/scripts/estilos.js`) cuando el automático no se parece a la referencia del cliente (p. ej. sale oscuro y la marca es de fondo claro). El ✗ de "concept" de la dirección de motion **se ignora acá**; el resto se corrige. Con `--solo-hoja` corta antes del video.
Mirar `<work>/sheet.jpg`: textos que no entran, colores que se pierden contra el fondo, contraste flojo → corregir textos.json o brand.json y volver a correr. La hoja queda copiada al lado del video (`hoja_<slug>.jpg`).
Cambiar la locución (solo si Gus lo pide): editar `assets/locucion/script.json`, `$PY $MSK/scripts/tts.py $MK/assets/locucion` y revisar que las palabras que usa `story.js` en `w('…')` sigan estando.

## 5 · Entregar
Mandar el MP4 de presentación con `SendUserFile` y responder corto: nombre y slug, paleta (hex + rol en una línea), tipografías, la idea de la marca en una frase, dónde quedó (`~/.config/motion/brands/<slug>`) y que ya la usan `/motion` y `/edicion`. Si Gus pide cambios: editar brand.json, `brand.py setup`, y re-render de la muestra (no hace falta reescribir story.js).
