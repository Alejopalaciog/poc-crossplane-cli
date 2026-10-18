# PoC · Crossplane CLI 2.5 — Documentación técnica (wiki)

| Página | Contenido |
|---|---|
| [00 · Alcance de las pruebas](00-alcance-de-las-pruebas.md) | Qué se probó, qué significa cada resultado y sus límites |
| [01 · Contexto y metodología](01-contexto-y-metodologia.md) | Por qué, línea base, escenarios, caso, entorno, cómo reproducir |
| [02 · Resultados](02-resultados.md) | KPIs, línea de tiempo, matriz de defectos, créditos, despliegue |
| [03 · Hallazgos y fricciones](03-hallazgos-y-fricciones.md) | Bugs latentes, restricciones del entorno, lo que cuesta la CLI |
| [04 · Recomendaciones y hoja de ruta](04-recomendaciones-y-hoja-de-ruta.md) | Veredicto, qué adoptar, fases, riesgos |

Documentos relacionados en el repo:
- `00-research/README.md` — releases 2.3 → 2.5 y equivalencia de comandos.
- `00-research/skill-migracion-tf-crossplane.md` — análisis de la skill de migración Terraform → Crossplane.
- `01-requirement/README.md` — requerimiento, contrato de negocio y catálogo de defectos.
- `06-evidence/README.md` — índice de evidencias (E1–E10) y cómo reproducirlas.
- `future/kiro-skill-plan.md` — plan (no ejecutado) de skill Kiro con la compuerta.

**En una frase:** la CLI 2.5, usada como compuerta local antes del cluster, encontró en segundos 11 de 11 errores
típicos y 4 bugs latentes en bloques que ya se usan, y bajaría los créditos de AI a ~30 % cuando la compuerta cubre el
error; el cluster sigue siendo la verificación final.
