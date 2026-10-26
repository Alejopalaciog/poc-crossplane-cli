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
| `07-presentation/` | Presentación ejecutiva en dos versiones: `presentacion-manual.html` (HTML autocontenido, scroll) y `beatdeck/` (interactiva por beats: `npm install && npm run present`) |
| `08-wiki/` | Documentación técnica para la wiki de Azure |
| `future/` | Plan (no ejecutado) de skill Kiro con la compuerta |

## Requisitos para reproducir
Docker, `tools/crossplane-2.5.0` y `tools/crank-2.2.6` (no versionados; ver `00-research`), Python 3.11+
con PyYAML, acceso de lectura a ECR para la función privada `function-jarvis-findresources`.

## Cómo abrirlo en otro equipo
El repo solo versiona lo necesario (~7 MB). Lo pesado se regenera o descarga (desde la raíz):

```bash
# 1. CLIs de Crossplane (no versionadas) — binarios oficiales
#    OS_ARCH: darwin_arm64 (Mac Apple Silicon), darwin_amd64 (Mac Intel) o linux_amd64
OS_ARCH=darwin_arm64
mkdir -p tools
curl -sfLo tools/crossplane-2.5.0 https://cli.crossplane.io/stable/v2.5.0/bin/$OS_ARCH/crossplane
curl -sfLo tools/crank-2.2.6 https://releases.crossplane.io/stable/v2.2.6/bin/$OS_ARCH/crank
chmod +x tools/*

# 2. Entorno Python para scripts de medición, compuerta y evidencias
python3 -m venv .venv && .venv/bin/pip install pyyaml

# 3. Presentación interactiva (beatdeck): librerías de Node y build
cd 07-presentation/beatdeck && npm install && npm run present
```

Solo para ver resultados no hace falta nada de lo anterior: `07-presentation/presentacion-manual.html` y
`08-wiki/` se abren directamente.
