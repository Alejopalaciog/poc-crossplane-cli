# 01 · Contexto y metodología

## Por qué esta PoC
Crossplane publicó una CLI nueva (repo `crossplane/cli`, v2.3 en mayo 2026 → **v2.5 en agosto 2026**) con un modelo de
trabajo por **proyecto**: generar XRDs desde un esquema simple, funciones en lenguajes generales con modelos tipados,
previsualizar (`render`), validar contra esquemas reales (`validate`), empaquetar y correr un Crossplane local.
Desde la v2.4 la CLI **ya no va atada a la versión del core**: soporta core v2.3, así que se puede usar **sin actualizar
el cluster** (core v2.3.3).

La pregunta de negocio: **¿subir a la CLI 2.5 nos ahorra tiempo, errores y créditos de AI al construir y probar
composiciones —y en la migración Terraform → Crossplane—, o agrega trabajo?**

## Cómo trabaja hoy el equipo (línea base)
- ~65 composiciones en `jarvis_aws_xrds` (34 bloques generales) y `jarvis_platform_xrds` (31 de plataforma), todas YAML
  go-templating, construidas en gran parte con AI (Kiro).
- No hay `render`/`validate` en repos ni CI; no hay Configuration packages. **La validación real es aplicar al cluster**.
- La skill de migración (`tscbo_developerkit_Tool`) trabaja sobre el estado del cluster, después del apply.

## Escenarios
| Escenario | Herramientas | Cómo se valida |
|---|---|---|
| **Antes-1** | AI + YAML | Aplicar al cluster EKS y leer eventos |
| **Antes-2** | AI + YAML + CLI 2.2.6 | `render` + `beta validate` locales, luego cluster |
| **Después** | AI + proyecto CLI 2.5.0 + compuerta local | Compuerta (render simulado/anidado, validate, contrato, multi-instancia), luego cluster |

Mismo requerimiento y mismo **contrato de negocio** para los tres (ver `01-requirement/README.md`).

## El caso
**"API Service Platform" (`XPocCliApiService`)**: un equipo pide exponer una API con estándares Nequi y la plataforma
crea API REST regional + `/health`, llave KMS propia, log group de access logs cifrado (retención por ambiente), stage
con access logs y alarmas de 5XX y latencia. Compone 3 bloques generales (`XAPIGatewayRestStack`,
`XAPIGatewayIntegration`, `XKMS`) y 5 recursos directos; en total **17 recursos** en AWS/Kubernetes.

> El caso inicial era una plataforma Lambda; se cambió porque el rol del provider **no tiene permisos de Lambda/S3/SQS** y
> solo escribe recursos con `cbo` en el nombre. La corrida Lambda quedó como evidencia del "antes" (destapó 2 bugs).

## Entorno
- Cluster compartido `eks-terraform-ts-dev` (core Crossplane v2.3.3, providers AWS v2.5.0), cuenta Sandbox 634614730521.
- Kyverno con 4 políticas en Enforce: verificadas antes de cada apply; ninguna aplica a los recursos de la PoC.
- Todo lo creado lleva prefijo `poc-cli`, label `poc.nequi.com/experiment=cli-2.5` y tags estándar.
- Máquina Windows 11 + Docker Desktop (certificados corporativos vía trust store de Windows) + WSL Ubuntu.

## Cómo se midió
- `05-measurements/measure.ps1`: cronometra cada paso y guarda la salida completa (`runs/`) y una fila en `results.csv`
  (duración, código de salida, tokens estimados de la salida = feedback que leería la AI).
- `observe-xr.ps1`: ciclo "aplicar y esperar" en el cluster, tal como lo haría una persona/AI hoy.
- `local_gate.py`: la compuerta local (CLI 2.5).
- `defects.py`: matriz de 11 defectos inyectados.
- `estimate_credits.py`: modelo de créditos AI (supuestos explícitos en el script y en `credits.json`).

## Cómo reproducir
```bash
# Compuerta local sobre la composición de Después
python 05-measurements/local_gate.py \
  --xr 04-after-cli-2.5/project/examples/xr.yaml \
  --composition 04-after-cli-2.5/project/apis/xpoccliapiservices/composition.yaml \
  --functions 04-after-cli-2.5/project/examples/functions.yaml \
  --nested-functions 04-after-cli-2.5/general-audit/functions-api.yaml \
  --extensions 04-after-cli-2.5/extensions \
  --contract 05-measurements/business_checks_api.py --multi-instance

# Evidencias en pantalla (pasos 1-8)
python 06-evidence/replay.py 5
```
Requisitos: Docker, CLI 2.5 en `tools/`, Python con PyYAML, login de lectura a ECR para la función privada
`function-jarvis-findresources`.
