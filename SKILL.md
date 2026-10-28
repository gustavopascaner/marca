---
name: marca
description: Crea la identidad visual de la marca de un cliente (paleta, tipografías, estilo, subtítulos, voz) a partir de su PROPUESTA DE VALOR, la guarda como brand.json para las skills /motion y /edicion entrega un video de presentación de la marca para el cliente (locución y música fijas que piden feedback, placas con sus textos, su paleta y sus tipografías) y una landing page estática con la propuesta de valor, que sube a Hostinger por FTP. Usar cuando el usuario escribe /marca con un texto o archivo, o pide "armá la marca de este cliente", "identidad visual para…", "marca nueva desde la propuesta de valor", "la landing / el sitio de <cliente>" (`/marca web <slug>`) o "subí la web de <cliente>" (`/marca subir <slug>`, todas en landing.misterrobot.net/<slug>/).
---

# /marca — propuesta de valor → identidad visual + video de muestra + landing + publicación

Hablarle a Gus en español rioplatense, corto. **Una sola propuesta, directo** (no ofrecer alternativas): decidir y ejecutar; Gus ajusta después.
`MSK` = `~/.claude/skills/motion` (motor y `brand.py`). `PY` = `$MSK/.venv/bin/python -I` (si no existe, `python3 -I`). `MK` = `~/.claude/skills/marca`.
Las marcas viven en `~/.config/motion/brands/<slug>/` y las leen **/motion** (`render.js`, `look.js`) y **/edicion** (`brand.js`): el formato tiene que ser exactamente el de abajo.

## 0 · Entrada
- La propuesta de valor (texto o archivo). Opcional: logo, colores, tipografías existentes, carpeta del cliente, **audio con la voz del cliente** (para clonarla: ver *Voz del cliente*).
- **Nombre** del profesional/marca: sacarlo del texto. Si no está, es lo único que se pregunta (una sola vez). `slug` = nombre en minúsculas con guiones, sin tildes. Si `brand.py list` ya tiene ese slug, avisar y preguntar si se pisa o se crea `<slug>-v2`.
- **Si trae logo o colores: respetarlos.** Logo → `$PY $MSK/scripts/brand.py colors <logo>` y mirarlo (estilo, peso, serif o no); la paleta parte de ahí y solo se completa lo que falte. Tipografías dadas → usarlas (Google Fonts por nombre).
- Carpeta de trabajo = la del archivo o el directorio actual. Salida: `<carpeta>/<slug>_MARCA/`.

## 1 · Leer la propuesta (en la cabeza, sin escribirlo largo)
Extraer: a quién le habla, qué dolor resuelve, la promesa, el método o los pilares, qué lo diferencia, el tono (cercano / experto / enérgico / sereno / premium) y 3 adjetivos de personalidad. De ahí sale todo; anotarlos en IDENTIDAD.md.

## 2 · Diseñar
Criterio: que se vea **de ese cliente y no de otro**. Correr `$PY $MSK/scripts/brand.py list` y no repetir la combinación de color de acento + tipografía display de una marca existente.
- **Colores** (hex): `dark` (fondo oscuro, texto sobre claro; se usa solo de vez en cuando), `light` (fondo claro, nunca blanco puro; es el fondo principal de los videos), `accent` (el color de la marca, resalta), `accent2` (secundario, contrasta con accent), `mute` (gris del tono de la paleta, textos secundarios). El color tiene que salir del sector y del tono, no del default (evitar azul genérico de salud si el tono es cálido, naranja si es sereno, etc.). Contraste: `light` sobre `dark` ≥ 7; `accent` usable como fondo con texto `dark` o `light` ≥ 3.
- **Tipografías** (Google Fonts): `display` (títulos: personalidad), `body` (lectura), `mono` (datos/kicks). **Solo 3 tipografías: no hay tipografía de acento** (ni itálica ni manuscrita; nunca agregar `accent` en `fonts`). Referencia de pares: `$PY $MSK/scripts/brand.py fonts`. Display en mayúsculas (`upper: true`, `leading` 0.9–0.95) para tonos enérgicos/directos; en minúsculas (`upper: false`, `leading` 1.0) para cálidos/serenos/premium.
- **Estilo**: `shapes` = `blobs` (orgánico) · `rings` · `dots` · `clean`; `grid` true para técnico/datos; `radius` 10–48 (más redondo = más amable); `grain` true.
- **Subtítulos**: `on: true`, `upper` como el display si es enérgico, `size` 62–68.
- **Voz**: según quién es la persona de la marca (del texto: "soy psicóloga" → mujer; "soy kinesiólogo" → hombre; si es una empresa o no se sabe, mujer). Guardarla en brand.json como `"voice": {"id": "mujer"}` o `{"id": "hombre"}` (así /motion la usa sin preguntar). **Si Gus pasó audio del cliente**, después del paso 3 se clona (ver *Voz del cliente*) y esa voz reemplaza a mujer/hombre.

## 3 · Guardar
1. `~/.config/motion/brands/<slug>/brand.json` (si hay logo, copiarlo ahí como `logo.png`/`logo.svg` y poner `"logo": "logo.png"`; si no, `null`):
```json
{"name":"<Nombre visible>",
 "colors":{"dark":"#","light":"#","accent":"#","accent2":"#","mute":"#"},
 "fonts":{"display":{"family":"…","weight":800,"upper":true,"stretch":"100%","tracking":"-0.02em","leading":0.95},
          "body":{"family":"…","weight":700},"mono":{"family":"…"}},
 "logo":null,
 "style":{"grain":true,"grid":false,"shapes":"blobs","radius":36,"progress":false},
 "captions":{"on":true,"upper":false,"size":64},
 "notes":"<1 línea de uso: qué color manda, qué evitar>"}
```
2. `$PY $MSK/scripts/brand.py setup <slug>` → baja las fuentes y chequea contraste. Corregir todos los ⚠️ (ajustar el hex, no ignorarlos) y repetir.
3. `IDENTIDAD.md` en la carpeta de la marca (≤ 15 líneas): idea de la marca en una frase, los 3 adjetivos, cada color con su rol, las tipografías y por qué, qué evitar. **Sin usuario de redes, sin títulos, credenciales ni resultados que no estén en el texto.**
4. Si hay carpeta del cliente: `$PY $MSK/scripts/brand.py remember "<carpeta>" <slug>` (así /motion y /edicion la detectan solas).

**Fondos de los videos:** predominan los claros (`light`), con `accent` y el `dark` solo eventualmente; los videos nunca van todos oscuros ni con el mismo fondo repetido. Elegir una paleta que funcione bien sobre `light`.

## 4 · Video de presentación de la marca (audio fijo, textos del cliente)
**Si la marca tiene la voz del cliente clonada** (`brand.json → voice.clone`), `muestra.py` genera la locución con esa voz (mismo texto fijo, ≈ 700 caracteres de ElevenLabs): la presentación es la prueba del clon. Sin clon, usa el audio fijo y no gasta.
Todo lo fijo vive en `$MK/assets/` y **no se toca por cliente**: `locucion/` (voz Agustina, ElevenLabs eleven_v4, 45 s; la anterior en v2 quedó en `locucion_v2_respaldo/`: saluda, dice que es la propuesta de identidad visual, pide mirar colores, tipografías y movimiento, y pide feedback; sin nombre del cliente), `musica/` (tema fijo licenciado), `story.js` (8 placas sincronizadas con la locución) y `scenes.js` (placas a medida `paleta` y `tipos`, que muestran los colores con su hex y las tipografías de títulos y lectura con su nombre).
Por cliente solo se escribe `<carpeta>/<slug>_MARCA/.work/textos.json`, con textos **sacados de la propuesta de valor** (cortos; nunca cifras, testimonios ni @usuarios inventados):
```json
{"rubro":"<qué hace, 1–3 palabras>", "nombre":["<Nombre>","<Apellido o resto>"],
 "frase":["<idea central>","<en 2–3 líneas>","<la última se resalta>"],
 "titulo":"<frase corta del cliente para mostrar la tipografía de títulos>",
 "cuerpo":"<frase del cliente de 1–2 líneas para la de lectura>",
 "pilares":["<pilar 1>","<pilar 2>","<pilar 3>"]}
```
Correr: `python3 -I $MK/scripts/muestra.py "<work>" <slug> --tono=<energico|calido|institucional|humor|sobrio> --out="<carpeta>/<slug>_MARCA/presentacion_<slug>.mp4"` (≈ 1 min: copia lo fijo, look nuevo, hoja, render y mezcla con `mix.py` de motion). `--estilo=<slug>` fija el estilo de /motion (`papel`, `liquido`… en `$MSK/scripts/estilos.js`) cuando el automático no se parece a la referencia del cliente (p. ej. sale oscuro; por defecto tienen que predominar los fondos claros). El ✗ de "concept" de la dirección de motion **se ignora acá**; el resto se corrige. Con `--solo-hoja` corta antes del video.
Mirar `<work>/sheet.jpg`: textos que no entran, colores que se pierden contra el fondo, contraste flojo → corregir textos.json o brand.json y volver a correr. La hoja queda copiada al lado del video (`hoja_<slug>.jpg`).
Cambiar la locución (solo si Gus lo pide): editar `assets/locucion/script.json`, `$PY $MSK/scripts/tts.py $MK/assets/locucion` y revisar que las palabras que usa `story.js` en `w('…')` sigan estando.

## Voz del cliente (clon en ElevenLabs)
Se usa al crear la marca (si Gus pasó audio) o sola sobre una marca existente: `/marca voz <slug>` + audio (o "cloná la voz de <cliente>").
1. Antes de subir nada, una sola línea a Gus: confirmar que el cliente autorizó clonar su voz (lo exigen las reglas de ElevenLabs). Es la única pregunta.
2. Audio: idealmente 1–3 min de la persona sola, sin música ni otras voces (sirven notas de WhatsApp, mp3/wav/m4a o un video). Si hay dudas del material: `python3 -I $MK/scripts/voz.py <slug> <audios…> --solo-preparar` (no gasta) muestra los segundos útiles.
3. `python3 -I $MK/scripts/voz.py <slug> <audio1> [audio2 …]` → crea el clon (Instant Voice Clone) y lo guarda en `brand.json → voice` con los ajustes de clon (similitud y fuerza del clon 1.0, estabilidad 0, sin `language_code`); el anterior queda en `voice_prev`. Si ya había clon frena: `--reemplazar` crea uno nuevo (el viejo **no** se borra en ElevenLabs; borrarlo solo si Gus lo pide). 401 = la clave necesita el permiso *Voices: Write* (Gus lo agrega en elevenlabs.io → Developers → API Keys).
4. Re-render de la presentación con la voz nueva: `muestra.py` con el mismo `<work>` y `--out` de antes (si el work ya tenía otro clon, agregar `--cambiar-voz`). Si la marca no tiene work todavía, escribir `textos.json` como en el paso 4. Mandar el MP4 y decir el voice_id.
5. Desde ahí /motion usa esa voz sola en todos los videos de la marca.
**/podcast no se toca nunca**: usa siempre la voz de Gus, fija en su propio script; nada de esta sección la cambia.

## 5 · Landing page (después del video)
Una sola página estática que vende la propuesta de valor, con la marca recién creada. También sola sobre una marca existente: `/marca web <slug>` (+ propuesta o material del cliente).
Plantilla fija (`$MK/assets/web/base.css` + `scripts/landing.py`): colores, tipografías (autoalojadas, sin Google), forma (`shapes`, `radius`, `grid`, `grain`) y mayúsculas salen de brand.json; el script ajusta solo el contraste del resaltado, botones y textos secundarios. Por cliente solo se escribe `<carpeta>/<slug>_MARCA/.work/web.json` (formato completo en el docstring de `landing.py`):
- **Textos sacados de la propuesta**, voseo y en la voz del cliente (1.ª persona si es un profesional). Recorrido: `hero` (promesa + 1 palabra resaltada con `*así*`) → `dolor` (3 cosas que vive su cliente) → `promesa` → `metodo` (pilares/pasos) → `para_quien` → `sobre` → `faq` → `cierre` (CTA). Todo es opcional menos `hero` y `cierre`: omitir el bloque si la propuesta no lo sostiene antes que rellenar.
- **Nunca inventar**: cifras, años de experiencia, títulos, testimonios, precios, @usuarios, teléfonos ni direcciones. `contacto` solo con datos que estén en el material; sin WhatsApp ni email los botones van a `#contacto` y el script avisa → pedírselo a Gus en una línea al entregar.
- Una palabra resaltada por título como mucho; CTA concreto ("Agendá una entrevista", no "Saber más").
Correr: `python3 -I $MK/scripts/landing.py "<work>/web.json" <slug> --out="<carpeta>/<slug>_MARCA/web" [--foto=<foto del profesional>]`. Si la marca tiene logo va en la barra; con `--foto` aparece en "sobre".
Mirar `web_desktop.png` y `web_mobile.png` (quedan al lado de `web/`): títulos que se cortan feo, bloques vacíos o muy largos, scroll horizontal (avisa) → corregir web.json y volver a correr.
La carpeta `web/` (index.html, styles.css, fonts/, img/, favicon.svg) se sube tal cual a cualquier hosting.

## 6 · Publicar en Hostinger (FTP)
Todas las landings viven en **un solo subdominio compartido**, cada cliente en su carpeta: `https://landing.misterrobot.net/<slug>/`. Solo cuando Gus lo pide (`/marca subir <slug>`, "subí la web de…"): publicar es hacia afuera, así que **antes de cada subida o baja decir la URL y esperar el sí**.
- **Hosting** (ya configurado, común a todos): `~/.config/motion/hosting.json` (host, usuario, dominio; sin contraseña). Para cambiarlo: `subir.py config --host=… --user=… --dominio=… [--dir=.]`. `dir` = `.` porque la cuenta FTP ya entra en la carpeta del subdominio.
- **Contraseña**: nunca por el chat ni en archivos. La carga **Gus en su terminal** (bloque `bash` para que lo corra): `python3 -I $MK/scripts/subir.py clave` → Llavero de macOS, servicio `marca-ftp`. Si Gus la pega en el chat, no usarla: pedirle que la cambie en hPanel y la cargue con `clave`.
- **Publicar / actualizar**: `python3 -I $MK/scripts/subir.py <slug> "<carpeta>/<slug>_MARCA/web"` (la primera vez antes `--prueba`: conecta y muestra qué haría sin tocar nada). Va por FTPS y **sincroniza**: sube solo lo nuevo o cambiado, borra lo que ese cliente ya no usa y nunca toca la carpeta de otro. Las tipografías van a `_fonts/` (una sola copia aunque las usen varios clientes; se borran solas cuando nadie las usa). El registro de qué subió cada cliente está en el servidor (`.landings.json`), así que funciona igual desde cualquier compu. Al final abre la URL y confirma que se ve.
- `subir.py lista` → clientes publicados con fecha y URL. `subir.py bajar <slug>` → despublica (borra solo lo que subió el script; primero `--prueba` y el OK de Gus).
- Otra URL que el slug: `--como=<carpeta>`. Si la carpeta ya existe y no la subió el script, o es de otro cliente, frena: `--forzar` solo con el OK de Gus.
- Errores: "no acepta FTPS" → `--sin-tls` solo si Gus lo autoriza (la contraseña viaja sin cifrar). "Rechazó usuario o contraseña" → revisar la cuenta FTP en hPanel o volver a cargar la clave. "No muestra la versión nueva" → caché: esperar o purgar en hPanel. Sin SSL → hPanel → Seguridad → SSL. **Error 525** = misterrobot.net pasa por Cloudflare y Hostinger no tiene certificado para ese subdominio: instalarlo en hPanel → Seguridad → SSL (si falla, poner el registro en Cloudflare como "DNS only", emitir y volver a activar el proxy).

## 7 · Entregar
Mandar el MP4 de presentación y `web_desktop.png` con `SendUserFile` y responder corto: nombre y slug, voz (por defecto o clon + voice_id), paleta (hex + rol en una línea), tipografías, la idea de la marca en una frase, dónde quedó (`~/.config/motion/brands/<slug>`, la landing en `<slug>_MARCA/web/`), qué falta para publicarla (contacto, foto; si ya se subió, la URL) y que la marca ya la usan `/motion` y `/edicion`. Si Gus pide cambios: editar brand.json, `brand.py setup`, y re-render de la muestra y la landing (no hace falta reescribir story.js).
