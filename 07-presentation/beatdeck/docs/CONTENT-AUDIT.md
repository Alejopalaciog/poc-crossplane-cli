# Content audit — Crossplane CLI 2.5 en Nequi

Source: `reference/presentacion-manual-template.html` (22 slides, versión manual) y `reference/0*.md` (wiki
técnica: alcance, metodología, resultados, hallazgos, recomendaciones). Design reference: marca Nequi
(colores y tipografía Poppins de la versión manual) sobre el modelo de beats.
Rule: the source decides **what** is said; the design reference decides **how** it looks and moves.

## Facts (never guess)

| Fact | Value | Source |
| --- | --- | --- |
| Title | Crossplane CLI 2.5 en Nequi | versión manual, portada |
| Speaker / role | COE · Cloud Platform | versión manual, tag de portada |
| Event · city · date | TODO (reunión con líderes; fecha por definir) | — |
| QR target | TODO (no hay URL pública: el repo y la wiki son internos) | — |
| Errores detectados antes del cluster | Hoy 0 · CLI 2.2 6 · CLI 2.5 + compuerta 11 (de 11) | 02-resultados.md |
| Tiempo por vuelta | cluster ~160 s (127/144/206 s medidos) · compuerta ~15 s | 02-resultados.md |
| Créditos AI (estimado) | 100 % · 77 % · ~30 % (101 % cuando un error se escapó) | 02-resultados.md |
| Turnos AI | 28 · 22 · 11 | 02-resultados.md |
| Bugs latentes | 4 (roles IAM, log groups, integraciones MOCK, choque entre equipos) | 03-hallazgos |
| Adopción | claim real 10/10; sin managementPolicies 6/10 → crearía una llave nueva | 02-resultados.md |
| Tiempo total caso API | hoy ~14 min (3 vueltas) · CLI 2.5 ~5–7 min | 02-resultados.md |

## Slide → beat mapping

| Slide (manual) | What the source says | Beat(s) | Status | Notes |
| --- | --- | --- | --- | --- |
| 01 Portada | Título + 3 KPIs (11/11, ~30 %, 4) | 1.1–1.3 | kept | KPIs como contadores en su propio beat |
| 02 Contexto | Hoy hay que desplegar para saber si funciona; lento, caro, invisible | 2.1–2.3 | kept | el ciclo se dibuja como diagrama |
| 03 Qué buscamos | 4 preguntas | 3.1 | merged | condensado a una pregunta + qué trae la CLI |
| 04 Qué trae la CLI 2.5 | Previsualizar, validar, generar, empaquetar; sin actualizar el cluster | 3.2–3.3 | kept | |
| 05 Divisor / La prueba | Caso API, 17 recursos, 3 escenarios | 4.1–4.2 | kept | |
| 06 Compuerta | Flujo de la compuerta; aporta CLI / aportamos nosotros | 4.3–4.4 | kept | |
| 07 AI + persona | Estándar como reglas ejecutables, 11/11 reglas | 4.4 | merged | en el mismo beat que "lo que aportamos" |
| 08 Errores | Barras 0/6/11 | 5.1–5.3 | kept | una barra por beat |
| 09 Matriz | 11 filas | 5.4 | merged | se muestra la clase de errores (invisibles, convivencia, orden); matriz completa en evidencia 8.2 |
| 10 Tiempo | ~160 s vs ~15 s; ~14 min vs ~5–7 min | 6.1–6.2 | kept | |
| 11 Créditos | 100/77/30; Ojo 101 % | 6.3–6.4 | kept | |
| 12 Bugs | 4 bugs | 7.1 | kept | |
| 13–14 Evidencia | Compuerta, matriz, trace, AWS | 8.1–8.4 | kept | capturas reales |
| 15 Migración | crear vs adoptar; 10/10 vs 6/10 | 7.2 | kept | |
| 16 Roles | 6 roles | 7.3 | kept | agregado a pedido del usuario (19-oct) |
| 17 Balance | bueno / cuesta / ojo | 9.1 | kept | |
| 18–19 Ruta | 4 fases | 9.2 | kept | |
| 20 Cierre | Frase final | 9.3 | kept | |

## Real artefacts

| Artefact | File | Used in | Rights / credit |
| --- | --- | --- | --- |
| Compuerta antes/después (terminal) | `deck/assets/5.png` | 8.1 | propio (PoC) |
| Matriz de defectos (terminal) | `deck/assets/8.png` | 8.2 | propio |
| resource trace + curl (terminal) | `deck/assets/7.png` | 8.3 | propio |
| Consola AWS: stage, logs, evento, alarmas | `deck/assets/aws2.png`, `aws4.png`, `aws5.png`, `aws6.png` | 8.4 | propio (cuenta Sandbox) |
| Verificación adopción (terminal) | `deck/assets/4.png` | 7.2 | propio |

## Open questions

- [ ] Fecha / reunión de la presentación.
- [ ] ¿URL interna (wiki de Azure) para el QR final? Hoy queda `TODO` y no se muestra QR.

## Decisions taken on the speaker's behalf

- Marca Nequi (fondo #200020, acento #DA0081, Poppins) en lugar del tema neutro, para ser coherente con las PoC anteriores.
- "Valor por rol" se omitió en la primera versión; el usuario pidió incluirla (beat 7.3).
- La matriz completa de 11 defectos se muestra como captura real (8.2), no se redibuja.
