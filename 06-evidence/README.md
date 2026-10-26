# 06 · Evidencias

Pantallazos para la wiki de Azure. Cada evidencia se reproduce desde la raíz del repo con
`python 06-evidence/replay.py N` (multiplataforma).
Guardar las imágenes en `06-evidence/img/` con el nombre indicado.

| ID | Qué muestra | Cómo reproducir | Imagen |
|---|---|---|---|
| E1 | CLI 2.2.6 y 2.5.0 funcionando contra el core v2.3.3 (sin actualizar el cluster) | `replay.py 1` | `img/E1-versiones.png` |
| E2 | Errores que solo aparecieron en el cluster en la 1.ª corrida "antes" (2,4 min, ~5.200 tokens) | `replay.py 2` · log completo: `05-measurements/runs/before-1/observe-cluster-01.log` | `img/E2-errores-cluster.png` |
| E3 | CLI 2.5 detecta offline los 2 bugs de composiciones generales (`aws-cloudwatch`, `aws-iam-role`) | `replay.py 3` | `img/E3-validate-offline.png` |
| E4 | Adopción: claim real `adopt-kms-test` verificado offline (10/10) y variante insegura detectada (crearía en vez de adoptar) | `replay.py 4` | `img/E4-adopcion-offline.png` |
| E5 | Llave KMS de la 1.ª corrida en `PendingDeletion` (limpieza) | Consola AWS → KMS → Customer managed keys → `a1fc7105-51dd-4c07-8ea3-09bc672cf2b7` | `img/E5-kms-pending-deletion.png` |

### Caso API desplegable

| ID | Qué muestra | Cómo reproducir | Imagen |
|---|---|---|---|
| E6 | Compuerta local CLI 2.5: rechaza la composición de Antes (colisión multi-instancia) y aprueba la de Después, sin cluster | `replay.py 5` (~2 min) | `img/E6-compuerta-antes.png`, `img/E6b-compuerta-despues.png` |
| E7 | `crossplane project run`: control plane local KIND con Configuration, funciones (incl. Python) y XRD instalados | `replay.py 6` | `img/E7-project-run-kind.png` |
| E8 | Después en EKS: árbol completo Ready (`crossplane resource trace`) y la API respondiendo HTTP 200 | `replay.py 7` | `img/E8-trace-eks.png` |
| E9 | Consola AWS (ver lista abajo) | Consola | `img/E9-*.png` |
| E10 | Matriz de detección de 11 defectos: CLI 2.2 = 6/11, CLI 2.5 + compuerta = 11/11 | `replay.py 8` | `img/E10-matriz-defectos.png` |
| E11 | Limpieza (al final, con tu confirmación) | — | `img/E11-limpieza.png` |

#### E9 · Consola AWS (región us-east-1, cuenta Sandbox 634614730521)
- **API Gateway** → APIs → `apigw-jarvis-co-cbopoccli2-dev` → Resources (`/health` GET) y Stages → `dev` (pestaña *Logs/tracing*: access logs al log group). Imagen `E9a-apigw.png`.
  (La de Antes es `apigw-jarvis-co-cbopoccli1-dev`, misma estructura.)
- **CloudWatch** → Log groups → `/aws/apigateway/access-jarvis-co-cbopoccli2-dev`: retención 14 días y *KMS key ID* asignada; abrir un log stream para ver el JSON de acceso. Imagen `E9b-logs-kms.png`.
- **CloudWatch** → Alarms → `alarm-jarvis-co-cbopoccli2-dev-5xx` y `-latency` en estado OK. Imagen `E9c-alarmas.png`.
- **KMS** → Customer managed keys → alias `alias-jarvis-co-cbopoccli2-dev`: rotación automática habilitada y tags estándar. Imagen `E9d-kms.png`.
- **Tags** (cualquiera de los anteriores): `serviceid=NEQ0169`, `capacity=jarvis`, `country=co`, `env=dev`, `deployment=jarvis`, `owner`, `poc`. Imagen `E9e-tags.png`.
