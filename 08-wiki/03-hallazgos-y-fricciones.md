# 03 · Hallazgos y fricciones

## A. Bugs latentes en composiciones generales (en uso hoy)
| # | Composición | Problema | Efecto | ¿Lo detecta la CLI 2.5 offline? |
|---|---|---|---|---|
| 1 | `aws-iam-role` | `permissionsBoundary: {{ ... }}` sin condición → envía `<no value>` | AWS rechaza CreateRole (400) si no se pasa boundary | ✅ render anidado (`<no value>`) |
| 2 | `aws-cloudwatch` | Usa `forProvider.name`, que no existe en el CRD `v1beta1` | No puede crear log groups nuevos | ✅ `resource validate` |
| 3 | `aws-apigateway-integration` | `uri: {{ ... }}` sin comillas → `null` | Integraciones MOCK imposibles | ✅ render anidado + validate |
| 4 | `aws-apigateway-integration` | Nombres de recursos = clave del claim, sin prefijo de instancia | Dos APIs con el mismo path en el mismo namespace **chocan** | ✅ prueba multi-instancia de la compuerta |
| 5 | `aws-apigateway-integration` | `managementPolicies` por defecto `["Observe"]` | Una API nueva no crea nada si no se pasa `["*"]` (sorpresa para quien la usa por primera vez) | ✅ contrato (API-10) |

Acción sugerida: issue/PR en `jarvis_aws_xrds` por cada uno; correr la compuerta sobre el catálogo completo.

## B. Restricciones del entorno (solo visibles en el cluster)
- El rol IRSA del provider (`role-eks-terraform-ts-terratocross-dev`) solo escribe IAM/KMS-alias/logs/alarmas con nombre
  `*cbo*` o `terraform-ts-dev*`, y **no tiene permisos de Lambda, S3 ni SQS**. Ninguna herramienta local lo ve; se
  propone codificarlo como regla del contrato (como se hizo con API-02).
- Las lambdas `nequi-government-*-delete` sugieren limpieza automática por tags: los tags estándar son obligatorios.

## C. Fricciones de la CLI 2.5 (lo que cuesta)
| Fricción | Impacto | Mitigación |
|---|---|---|
| Build de funciones Python **falla en Windows** (`Empty module name`) | Equipos en Windows no pueden usar funciones Python embebidas | WSL / devcontainer / build en CI Linux |
| `render` compila funciones embebidas con límite ~60 s | Python (apt+pip) no alcanza → render falla | Reutilizar imagen de `project build`; o preferir go-templating |
| `xrd generate` crea `scope: Namespaced` por defecto | La plataforma compone XRs *Cluster*: no funciona sin editar | Ajuste manual / plantilla del equipo |
| `composition generate`/dependencias nombran funciones `crossplane-contrib-function-*` | No coincide con los nombres instalados en el cluster (`function-*`) | Convención de nombres o instalar vía Configuration |
| `dependency add` no acepta archivos locales | Sin modelos tipados ni validación automática de los XRs generales | **Publicar `jarvis_aws_xrds` como Configuration package** |
| `--crossplane-version v2.3.3` falla (la ayuda muestra `v2.2.1`) | `project run` no arranca | Usar `2.3.3` sin "v" |
| Render de funciones crea red Docker por ejecución | Contenedores calientes requieren anotaciones (`runtime-docker-network/name/cleanup`) | Incluido en `functions.yaml` del proyecto |
| Funciones privadas (ECR) | Render anidado requiere login de lectura a ECR | `aws ecr get-login-password | docker login` |
| Comandos DevEx en **Beta** (`xr` en Alpha) | Pueden cambiar entre versiones | Fijar versión de CLI en el repo/CI |
| Docker obligatorio | Requisito de entorno para render/build/run | Ya disponible en las máquinas del equipo |

## D. Lo que NO cambia
- El cluster sigue siendo la verificación final (permisos, tiempos y comportamiento real de AWS).
- La skill de migración sigue siendo necesaria: el gap analysis requiere el estado real (`atProvider`).
- La CLI no trae "tests" automáticos todavía (anunciado como trabajo futuro): la compuerta y el contrato son nuestros.

## E. Hallazgos menores
- La llave KMS no recibe los tags propios de la solicitud (`owner`, `poc`) porque la plataforma no se los pasa a `XKMS`;
  el contrato solo exigía tags de identidad. Lección: **el contrato verifica solo lo que se le pide**.
- `kubectl apply` del XRD/composición acepta plantillas rotas: Kubernetes no ejecuta templates.
