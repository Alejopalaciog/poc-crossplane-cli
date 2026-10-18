# PoC · Crossplane CLI 2.5 — ¿vale la pena para la plataforma Nequi?

Evaluación, con pruebas reales en EKS/AWS, del valor de usar la **Crossplane CLI 2.5** (vs. el flujo actual y la CLI
2.2) para construir, probar y migrar composiciones —incluido el trabajo asistido por AI (Kiro)—.

**Resultado en una línea:** usada como **compuerta local antes del cluster**, la CLI 2.5 detectó **11 de 11** errores
típicos (CLI 2.2: 6; hoy: 0 antes del cluster), encontró **4 bugs latentes** en bloques generales en uso, y bajaría los
**créditos de AI a ~30 %** cuando la compuerta cubre el error. No reemplaza la verificación en el cluster.

👉 Empieza por **[08-wiki/00-alcance-de-las-pruebas.md](08-wiki/00-alcance-de-las-pruebas.md)** y luego
[08-wiki/README.md](08-wiki/README.md).

## Estructura
| Carpeta | Contenido |
|---|---|
| `00-research/` | Releases 2.3→2.5, comandos, análisis de la skill de migración |
| `01-requirement/` | Requerimiento, contrato de negocio, catálogo de defectos, mocks |
| `02-before-1-yaml/` | Antes-1: composición escrita a mano (casos Lambda y API) |
| `03-before-2-cli-2.2/` | Antes-2: render/validate con CLI 2.2 |
| `04-after-cli-2.5/` | Después: proyecto CLI 2.5 (go-templating y Python), auditoría de bloques generales, demo de adopción |
| `05-measurements/` | Scripts de medición, compuerta, contratos, defectos, créditos y `results.csv` |
| `06-evidence/` | Índice de evidencias y `replay.py` para reproducirlas |
| `07-presentation/` | Presentación ejecutiva (HTML) |
| `08-wiki/` | Documentación técnica para la wiki de Azure |
| `future/` | Plan (no ejecutado) de skill Kiro con la compuerta |

## Requisitos para reproducir
Docker, `tools/crossplane-2.5.0(.exe)` y `tools/crank-2.2.6(.exe)` (no versionados; ver `00-research`), Python 3.11+
con PyYAML (`python -m venv .venv && .venv/Scripts/pip install pyyaml`), acceso de lectura a ECR para la función
privada `function-jarvis-findresources`. En Windows, el build de funciones Python requiere WSL.
