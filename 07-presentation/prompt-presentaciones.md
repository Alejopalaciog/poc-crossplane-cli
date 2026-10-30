Actúa como analista técnico y diseñador de presentaciones ejecutivas. Vas a documentar una prueba de concepto, implementación, migración o proyecto en **dos presentaciones HTML**, con la línea gráfica de Nequi y con datos verificables.

Si la sección "Información del proyecto" está vacía, pídeme esa información y no generes nada todavía. Si solo faltan datos que cambian el mensaje (cifras, comparación, conclusión o evidencias), pregúntalos todos juntos en un solo mensaje. No los supongas.

## 1. Entregables

Dentro de la carpeta `presentacion/` del proyecto, salvo que yo indique otra:

| Archivo | Contenido |
|---|---|
| `datos-verificados.md` | Tabla con cada cifra y afirmación clave: valor, fuente, si es medido o estimado, y qué incluye o excluye |
| `template-corta.html` | Fuente de la presentación corta |
| `template-extensa.html` | Fuente de la presentación extensa |
| `build.py` | Incrusta las imágenes y genera los HTML finales |
| `presentacion-corta.html` | Resultado final, autocontenido |
| `presentacion-extensa.html` | Resultado final, autocontenido |

Trabaja en este orden: primero `datos-verificados.md`, luego la extensa, y al final la corta, resumida a partir de la extensa. Las dos presentaciones deben usar las mismas cifras.

## 2. Reglas de contenido

**Veracidad**
- Usa solo datos que yo entregue o que encuentres en los archivos del proyecto. Nunca inventes cifras, nombres, fechas, resultados ni evidencias.
- Marca como "(estimado)" todo lo que no se haya medido, y explica en una frase cómo se estimó.
- Si una cifra deja algo por fuera, dilo junto a la cifra con una nota al pie. Ejemplo: "Solo el tiempo de ejecución; no incluye la aprobación del PR".
- Indica sobre qué se midió: ambiente, tamaño de la muestra y cuántas repeticiones hubo.
- Incluye lo que no funcionó, los costos y los límites. Una presentación sin riesgos no es creíble.
- Si dos fuentes se contradicen, no elijas en silencio: dímelo.

**Redacción**
- Escribe en español claro, para una audiencia mixta. Explica cada término técnico en la misma frase o cámbialo por uno común.
- Cada título dice la conclusión de la slide, no su tema. Mejor "Menos errores, más rápido" que "Resultados".
- Frases cortas. Máximo unas 60 palabras de texto corrido por slide.
- Escribe siempre Nequi con N mayúscula.
- No menciones que algo fue construido con AI, salvo que sea parte del tema.
- No pongas en la última slide enlaces al repositorio, a documentación técnica ni a carpetas de evidencias.

**Evidencias**
- Usa capturas reales, con un pie que diga qué demuestra cada una.
- Antes de incluir una imagen, revísala: no puede mostrar secretos, tokens, credenciales ni datos personales. Tampoco identificadores de cuentas, salvo que yo lo autorice. Si encuentras algo así, no la uses y avísame.
- No generes capturas simuladas ni imágenes decorativas.

**Gráficos**
- Usa barras horizontales `.hb`. El ancho es proporcional al valor: `ancho % = valor / máximo × 100`.
- Usa magenta (`.fill`) para lo que se quiere destacar y gris (`.fill.ref`) para las referencias.
- Incluye siempre `role="img"` y un `aria-label` con los valores.
- Si una barra vale 0, usa `style="width:0;min-width:0;display:block"`.
- Las magnitudes distintas van en gráficos separados.

## 3. Presentación corta (5 a 7 slides)

Para contarla en unos 10 minutos a quien decide. No lleva capturas. Cada slide es una `section` con este orden y fondos:

| # | Fondo | Slide | Contenido |
|---|---|---|---|
| 1 | `dark` | Portada y problema | Etiqueta, título, pregunta que se quiso responder y flujo actual con `.flow`, incluida la espera o el dolor |
| 2 | `soft` | Qué se usó | 3 o 4 tarjetas con las capacidades que aportaron valor |
| 3 | `lila` | Qué se probó | Flujo probado y dos tarjetas: lo que trae la herramienta y lo que aportó el equipo |
| 4 | blanco | Resultados | 2 o 3 tarjetas con barras, nota al pie y un `.note` con la advertencia principal |
| 5 | `dark` | Hallazgos | Lo que apareció en el camino y no se esperaba |
| 6 | `soft` | Balance | Lo que cuesta, riesgos y lo que viene |
| 7 | `dark` | Propuesta | Decisión que se pide, flujo propuesto y 3 cifras clave con `.stat` |

Puedes unir slides para llegar a 5 si el contenido no da para 7.

## 4. Presentación extensa (16 a 24 slides)

Para consulta y para quien quiera el detalle. Incluye las evidencias. Omite la sección que no tenga información real; no la rellenes.

| Bloque | Slides | Fondo sugerido |
|---|---|---|
| Inicio | Portada; Contexto; Qué buscamos | `dark`, `lila`, `dark` |
| Tecnología | Qué es o qué se usó | `soft` |
| Separador | "La prueba" | `div`, con número grande |
| La prueba | Metodología y alternativas comparadas; Solución; Roles o forma de trabajo | blanco, `lila`, `dark` |
| Separador | "Resultados" | `div` |
| Resultados | Una slide por métrica; matriz de comparación con `table.t.mx` si aplica | alterna blanco, `lila`, `soft` |
| Hallazgos | Hallazgos no esperados | `dark` |
| Evidencia | Evidencia de la prueba; evidencia del ambiente real, con `.fig` | blanco, `soft` |
| Casos adicionales | Otro caso o migración, si existe | blanco |
| Balance | Costos y riesgos; Lo que viene | blanco, `soft` |
| Separador | "Pasos a seguir" | `div` |
| Cierre | Hoja de ruta con `.tl` o `.step`; Cierre con frase principal `.quote` y cifras | `dark`, `dark` |

## 5. Línea gráfica

Respeta estos puntos sin cambiarlos:

- **Colores:** tinta `#200020`, magenta `#DA0081`, rosado suave `#FFE9F5`, lila `#F6EEFA`. Usa las variables del CSS y no agregues colores nuevos.
- **Fuente:** Poppins, de 400 a 800.
- **Logo:** texto "Nequi." en la barra superior, con el punto magenta. No uses imágenes de logo si yo no las entrego.
- **Navegación:** barra fija, barra de progreso, puntos laterales, teclado (flechas, espacio, AvPág y RePág) y ampliar imágenes con clic.
- **Formas:** tarjetas redondeadas, etiquetas tipo píldora, flujos con nodos y flechas.
- **Iconos:** un emoji por tarjeta como máximo.
- **Responsive e impresión:** ya los resuelve el CSS. No los elimines.

Copia el CSS y el JavaScript siguientes **tal como están**, en ambas plantillas. Si necesitas un ajuste puntual, usa `style` en el elemento.

### Estructura del HTML

```html
<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>[Título] — [Tipo de proyecto]</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>/* CSS base */</style>
</head>
<body>
<div class="bar"><span class="logo">Nequi<i>.</i></span><span class="sec" id="secname">[Título corto]</span></div>
<div class="prog" id="prog"></div>
<nav class="dots" id="dots" aria-label="Navegación"></nav>
<div id="lb" role="dialog" aria-label="Imagen ampliada"><img alt=""></div>

<section class="s dark" data-sec="Portada" id="portada">
 <div class="wrap">...</div>
</section>

<script>/* JavaScript base */</script>
</body>
</html>
```

Cada `section` necesita `class="s ..."`, un `id` único y `data-sec` con el nombre que se ve en la barra.

### CSS base

```css
:root{
  --ink:#200020; --ink2:#3a0a3a; --mag:#DA0081; --mag-d:#b00068; --soft:#FFE9F5; --lila:#F6EEFA;
  --line:#ead7e6; --ok:#0fa578; --warn:#e8930c; --bad:#d6324a; --txt:#2a1a2a; --mut:#7a6a7a;
  --f:'Poppins','Segoe UI',system-ui,-apple-system,sans-serif;
}
*{box-sizing:border-box;margin:0;padding:0}
html{scroll-snap-type:y proximity;scroll-behavior:smooth}
body{font-family:var(--f);color:var(--txt);background:#fff;line-height:1.5;-webkit-font-smoothing:antialiased}
a{color:var(--mag);font-weight:600}
code{font-family:ui-monospace,Menlo,Consolas,monospace;font-size:.86em;background:var(--soft);color:var(--mag-d);padding:1px 7px;border-radius:6px}
.dark code{background:rgba(255,255,255,.12);color:#ffc2e5}
.bar{position:fixed;inset:0 0 auto 0;height:56px;display:flex;align-items:center;justify-content:space-between;padding:0 28px;z-index:50;background:rgba(32,0,32,.92);backdrop-filter:blur(8px);color:#fff}
.logo{font-weight:800;font-size:26px;letter-spacing:-1px;color:#fff}
.logo i{color:var(--mag);font-style:normal}
.bar .sec{font-size:13px;font-weight:500;opacity:.85}
.prog{position:fixed;top:56px;left:0;height:3px;background:var(--mag);width:0;z-index:51;transition:width .2s}
.dots{position:fixed;right:14px;top:50%;transform:translateY(-50%);display:flex;flex-direction:column;gap:7px;z-index:50}
.dots a{width:9px;height:9px;border-radius:50%;background:rgba(218,0,129,.28);border:1px solid rgba(218,0,129,.6);display:block}
.dots a.on{background:var(--mag);transform:scale(1.35)}
.s{min-height:100vh;padding:96px 7vw 56px;scroll-snap-align:start;display:flex;flex-direction:column;justify-content:center;position:relative}
.s.dark{background:var(--ink);color:#fff}
.s.lila{background:var(--lila)}
.s.soft{background:var(--soft)}
.wrap{max-width:1180px;margin:0 auto;width:100%}
h1{font-size:clamp(40px,6.4vw,84px);line-height:1.02;font-weight:800;letter-spacing:-2px}
h2{font-size:clamp(28px,3.6vw,46px);line-height:1.1;font-weight:700;letter-spacing:-1px;margin-bottom:10px}
h3{font-size:18px;font-weight:700;margin-bottom:6px}
.lead{font-size:clamp(16px,1.5vw,20px);color:var(--mut);max-width:62ch;margin-bottom:28px}
.dark .lead{color:#d9bfd6}
.tag{display:inline-block;font-size:13px;font-weight:600;background:var(--mag);color:#fff;padding:5px 14px;border-radius:99px;margin-bottom:16px}
.tag.o{background:transparent;border:1.5px solid var(--mag);color:var(--mag)}
.mag{color:var(--mag)}
.div{background:linear-gradient(135deg,var(--mag) 0%,#8f0a73 55%,var(--ink) 100%);color:#fff}
.div .big{font-size:clamp(90px,16vw,220px);font-weight:800;line-height:.9;opacity:.22;letter-spacing:-6px}
.div h2{font-size:clamp(34px,5vw,64px)}
.div p{font-size:18px;max-width:52ch;opacity:.92}
.g{display:grid;gap:18px}
.g2{grid-template-columns:repeat(2,1fr)}.g3{grid-template-columns:repeat(3,1fr)}.g4{grid-template-columns:repeat(4,1fr)}
.card{background:#fff;border:1px solid var(--line);border-radius:20px;padding:22px}
.lila .card,.soft .card{border-color:transparent;box-shadow:0 6px 24px rgba(32,0,32,.06)}
.dark .card{background:rgba(255,255,255,.07);border-color:rgba(255,255,255,.14)}
.card .ic{font-size:30px;margin-bottom:8px;display:block}
.card p{font-size:14.5px;color:var(--mut)}
.dark .card p{color:#d9bfd6}
.card.hl{background:var(--mag);border-color:var(--mag);color:#fff}
.card.hl p{color:#ffe0f1}
.flow{display:flex;align-items:stretch;gap:0;flex-wrap:wrap;margin:6px 0 20px;row-gap:10px}
.node{background:#fff;border:2px solid var(--mag);color:var(--ink);border-radius:16px;padding:12px 16px;font-weight:600;font-size:14px;text-align:center;min-width:110px;display:flex;flex-direction:column;justify-content:center}
.node small{display:block;font-weight:400;color:var(--mut);font-size:11.5px}
.node.off{border-color:#c7b3c4;border-style:dashed;color:#9a8699;background:#faf5fa}
.node.new{background:var(--mag);color:#fff}
.node.new small{color:#ffd5ec}
.dark .node{background:rgba(255,255,255,.08);color:#fff;border-color:#ff5db5}
.dark .node small{color:#d9bfd6}
.dark .node.new{background:var(--mag);border-color:var(--mag)}
.arr{align-self:center;padding:0 7px;color:var(--mag);font-weight:800;font-size:20px}
table.t{width:100%;border-collapse:separate;border-spacing:0;font-size:14px;background:#fff;border-radius:16px;overflow:hidden;border:1px solid var(--line)}
.t th{background:var(--ink);color:#fff;text-align:left;padding:11px 14px;font-weight:600;font-size:13px}
.t td{padding:10px 14px;border-top:1px solid var(--line);vertical-align:top}
.t tr:nth-child(even) td{background:#fdf7fb}
.t td:first-child{font-weight:600}
.dark .t{border-color:rgba(255,255,255,.15);color:var(--txt)}
.b{display:inline-block;font-size:12px;font-weight:700;padding:2px 10px;border-radius:99px;white-space:nowrap}
.b.ok{background:#d9f5ec;color:#07785a}.b.wa{background:#fdeccc;color:#9a5d00}.b.ba{background:#fcdce1;color:#a3192f}.b.gr{background:#ece3ee;color:#5a4a5a}.b.mg{background:var(--soft);color:var(--mag-d)}
.stat{text-align:left}
.stat b{display:block;font-size:clamp(36px,4.4vw,58px);font-weight:800;color:var(--mag);line-height:1;letter-spacing:-1.5px}
.dark .stat b{color:#ff5db5}
.stat span{font-size:14px;color:var(--mut);display:block;margin-top:6px}
.dark .stat span{color:#d9bfd6}
.fig{background:#fff;border-radius:18px;border:1px solid var(--line);padding:10px;cursor:zoom-in;overflow:hidden}
.fig img{width:100%;display:block;border-radius:10px}
.fig figcaption{font-size:12.5px;color:var(--mut);padding:8px 6px 2px}
.dark .fig{border-color:rgba(255,255,255,.2);background:rgba(255,255,255,.06)}
.dark .fig figcaption{color:#d9bfd6}
#lb{position:fixed;inset:0;background:rgba(20,0,20,.92);display:none;align-items:center;justify-content:center;z-index:100;cursor:zoom-out;padding:24px}
#lb img{max-width:100%;max-height:100%;border-radius:10px;background:#fff}
#lb.on{display:flex}
.step{display:flex;gap:16px;align-items:flex-start;background:#fff;border-radius:16px;padding:14px 18px;border:1px solid var(--line)}
.step .n{flex:none;width:34px;height:34px;border-radius:50%;background:var(--mag);color:#fff;font-weight:700;display:grid;place-items:center;font-size:15px}
.step p{font-size:14px;color:var(--mut)}
.step b{font-size:15.5px}
.dark .step{background:rgba(255,255,255,.07);border-color:rgba(255,255,255,.14)}
.dark .step p{color:#d9bfd6}
.tl{position:relative;display:grid;gap:12px;padding-left:34px}
.tl::before{content:"";position:absolute;left:12px;top:6px;bottom:6px;width:3px;background:var(--mag);border-radius:3px;opacity:.35}
.tl .it{position:relative;background:#fff;border:1px solid var(--line);border-radius:16px;padding:12px 18px}
.tl .it::before{content:"";position:absolute;left:-29px;top:18px;width:15px;height:15px;border-radius:50%;background:var(--mag);border:3px solid #fff;box-shadow:0 0 0 2px var(--mag)}
.tl .it small{display:block;color:var(--mag);font-weight:700;font-size:12px;letter-spacing:.3px}
.tl .it p{font-size:13.5px;color:var(--mut)}
.tl .it b{font-size:15px}
.dark .tl .it{background:rgba(255,255,255,.07);border-color:rgba(255,255,255,.14)}
.dark .tl .it p{color:#d9bfd6}
.dark .tl .it small{color:#ff5db5}
.quote{font-size:clamp(20px,2.3vw,30px);font-weight:600;line-height:1.3;letter-spacing:-.5px;max-width:30ch}
.pill-row{display:flex;flex-wrap:wrap;gap:8px}
.foot{font-size:12.5px;color:var(--mut);margin-top:14px}
.dark .foot{color:#bfa0bb}
.links a{display:inline-flex;align-items:center;gap:8px;background:#fff;border:1.5px solid var(--mag);border-radius:99px;padding:8px 16px;font-size:13.5px;text-decoration:none;margin:0 8px 8px 0}
.links a:hover{background:var(--mag);color:#fff}
.hero-grid{display:grid;grid-template-columns:1.2fr .8fr;gap:40px;align-items:center}
/* barras (una serie: magnitud) */
.hb .row{display:grid;grid-template-columns:190px 1fr 70px;align-items:center;gap:12px;margin:12px 0;font-size:14.5px}
.hb .lab{font-weight:600}
.hb .lab small{display:block;font-weight:400;color:var(--mut);font-size:12px}
.hb .trk{background:#f0e2ee;border-radius:4px;height:22px;position:relative}
.hb .fill{height:100%;border-radius:0 4px 4px 0;background:var(--mag);min-width:4px}
.hb .fill.ref{background:#b8a3b5}
.hb .val{font-weight:800;font-size:20px;color:var(--ink);text-align:right}
.dark .hb .trk{background:rgba(255,255,255,.12)}
.dark .hb .val{color:#fff}
.dark .hb .lab small{color:#d9bfd6}
.hb .row:hover .fill{filter:brightness(1.1)}
.hb.sm .row{grid-template-columns:80px 1fr 62px;margin:8px 0}.hb.sm .trk{height:16px}.hb.sm .val{font-size:16px}
.hb.sm+p{margin-top:10px}
.mx td,.mx th{font-size:13px}
.mx td:nth-child(n+3),.mx th:nth-child(n+3){text-align:center}
.mx .k{font-weight:400;color:var(--mut);font-size:12px;display:block}
.note{border-left:4px solid var(--mag);background:#fff;border-radius:0 14px 14px 0;padding:12px 16px;font-size:14px;color:var(--txt)}
.dark .note{background:rgba(255,255,255,.07);color:#fff}
@media(max-width:900px){.g2,.g3,.g4,.hero-grid{grid-template-columns:1fr}.dots{display:none}.s{padding:84px 5vw 40px}.bar .sec{display:none}.hb .row{grid-template-columns:120px 1fr 54px}}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
@media print{.bar,.dots,.prog{display:none}.s{min-height:auto;page-break-after:always}}
a:focus-visible,.fig:focus-visible{outline:3px solid var(--mag);outline-offset:3px}
```

### JavaScript base

```js
const secs=[...document.querySelectorAll('.s')];
const dots=document.getElementById('dots');
secs.forEach((s,i)=>{const a=document.createElement('a');a.href='#'+s.id;a.setAttribute('aria-label',s.dataset.sec);dots.appendChild(a)});
const da=[...dots.children];
function upd(){
  const y=window.scrollY+window.innerHeight/2;
  let cur=0;secs.forEach((s,i)=>{if(s.offsetTop<=y)cur=i});
  da.forEach((d,i)=>d.classList.toggle('on',i===cur));
  document.getElementById('secname').textContent=secs[cur].dataset.sec;
  const h=document.documentElement.scrollHeight-window.innerHeight;
  document.getElementById('prog').style.width=(h>0?window.scrollY/h*100:0)+'%';
  return cur;
}
addEventListener('scroll',upd,{passive:true});upd();
addEventListener('keydown',e=>{
  if(['ArrowRight','ArrowDown','PageDown',' '].includes(e.key)){e.preventDefault();const c=upd();secs[Math.min(c+1,secs.length-1)].scrollIntoView()}
  if(['ArrowLeft','ArrowUp','PageUp'].includes(e.key)){e.preventDefault();const c=upd();secs[Math.max(c-1,0)].scrollIntoView()}
});
const lb=document.getElementById('lb');
document.querySelectorAll('.fig img').forEach(im=>im.addEventListener('click',()=>{lb.querySelector('img').src=im.src;lb.classList.add('on')}));
lb.addEventListener('click',()=>lb.classList.remove('on'));
addEventListener('keydown',e=>{if(e.key==='Escape')lb.classList.remove('on')});
```

### Componentes

```html
<!-- Etiqueta y título -->
<span class="tag">Resultados</span>
<h2>Conclusión de la slide</h2>
<p class="lead">Contexto en una o dos frases.</p>

<!-- Tarjetas: g2, g3 o g4. La tarjeta hl es la destacada -->
<div class="g g3">
 <div class="card"><span class="ic">✅</span><h3>Título</h3><p>Texto.</p></div>
 <div class="card hl"><h3>Destacada</h3><p>Texto.</p></div>
</div>

<!-- Flujo: node, node new (destacado), node off (paso que duele) -->
<div class="flow">
 <div class="node new">Paso 1<small>detalle</small></div><div class="arr">→</div>
 <div class="node">Paso 2<small>detalle</small></div><div class="arr">→</div>
 <div class="node off">Paso 3<small>detalle</small></div><div class="arr">↺</div>
</div>

<!-- Barras -->
<div class="hb sm" role="img" aria-label="Tiempo: antes 160, después 15">
 <div class="row"><span class="lab">Antes</span><span class="trk"><span class="fill ref" style="width:100%;display:block"></span></span><span class="val">160</span></div>
 <div class="row"><span class="lab">Después</span><span class="trk"><span class="fill" style="width:9%;display:block"></span></span><span class="val">15</span></div>
</div>

<!-- Cifras clave -->
<div class="g g3"><div class="stat"><b>11/11</b><span>qué significa</span></div></div>

<!-- Tabla. mx centra las columnas desde la tercera -->
<table class="t mx">
 <tr><th>Criterio</th><th>Detalle</th><th>Antes</th><th>Después</th></tr>
 <tr><td>Fila</td><td>Texto</td><td><span class="b ba">No</span></td><td><span class="b ok">Sí</span></td></tr>
</table>

<!-- Estados: ok, wa, ba, gr, mg -->
<span class="b ok">Aprobado</span>

<!-- Advertencia y nota al pie -->
<div class="note"><b>Ojo:</b> la advertencia principal.</div>
<p class="foot">* Qué incluye o excluye la cifra.</p>

<!-- Evidencia: se amplía con clic -->
<figure class="fig"><img src="{{img:captura.png}}" alt="Qué muestra"><figcaption>Qué demuestra.</figcaption></figure>

<!-- Separador -->
<section class="s div" data-sec="Resultados" id="d2">
 <div class="wrap"><div class="big">02</div><h2>Resultados</h2><p>Qué se va a ver.</p></div>
</section>

<!-- Pasos -->
<div class="step"><span class="n">1</span><div><b>Paso</b><p>Detalle.</p></div></div>

<!-- Hoja de ruta -->
<div class="tl"><div class="it"><small>FASE 1</small><b>Qué se hace</b><p>Detalle.</p></div></div>

<!-- Frase principal -->
<p class="quote">Una frase que resuma la decisión.</p>
```

## 6. Build

Crea `build.py` con este contenido. Las imágenes van en `presentacion/img/` y en las plantillas se referencian como `{{img:archivo.png}}`.

```python
"""Genera las presentaciones autocontenidas a partir de las plantillas.

Reemplaza {{img:archivo}} por la imagen de img/ en base64.
Uso: python presentacion/build.py
"""

import base64
import mimetypes
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
IMG = HERE / "img"


def inline(match):
    path = IMG / match.group(1)
    mime = mimetypes.guess_type(path.name)[0] or "image/png"
    data = base64.b64encode(path.read_bytes()).decode()
    return f"data:{mime};base64,{data}"


for name in ("corta", "extensa"):
    source = (HERE / f"template-{name}.html").read_text(encoding="utf-8")
    html = re.sub(r"\{\{img:([^}]+)\}\}", inline, source)
    (HERE / f"presentacion-{name}.html").write_text(html, encoding="utf-8")
    print(f"presentacion-{name}.html: {len(html) / 1024 / 1024:.1f} MB")
```

## 7. Verificación antes de entregar

Ejecuta `build.py`, abre ambas presentaciones en un navegador y comprueba:

1. Ninguna slide se corta o se desborda en 1920×1080 ni en 1366×768.
2. No hay scroll horizontal en 390 px de ancho.
3. La consola no muestra errores.
4. No queda ningún `{{img:` sin resolver y todas las imágenes cargan.
5. Funcionan el teclado, los puntos laterales y la ampliación de imágenes.
6. Cada cifra de las presentaciones aparece en `datos-verificados.md`, con el mismo valor en ambas.
7. El ancho de cada barra coincide con su valor.
8. Lo estimado dice "(estimado)".
9. Ninguna evidencia expone datos sensibles.

Si no puedes abrir un navegador, dilo y no marques esos puntos como comprobados.

Al terminar, dime qué archivos generaste, qué comprobaste, qué información faltó y qué afirmaciones quedaron como estimadas.

## 8. Información del proyecto

```text
Título:
Tipo (PoC, implementación, migración, otro):
Área o equipo que aparece en la etiqueta:
Audiencia y decisión que se busca:

Problema o situación actual:
Pregunta que se quiso responder:
Flujo actual, paso a paso, y dónde duele:

Tecnología o solución evaluada:
Capacidades que aportaron valor:
Alternativas comparadas:
Ambiente y método de medición:

Métricas (nombre | antes | después | unidad | medido o estimado | qué excluye):

Hallazgos no esperados:
Lo que no funcionó:
Costos, riesgos y límites:
Lo que viene:

Propuesta o decisión recomendada:
Hoja de ruta:

Carpeta de evidencias:
Evidencias que deben aparecer (archivo | qué demuestra):
Documentos o repositorios de referencia:
```
