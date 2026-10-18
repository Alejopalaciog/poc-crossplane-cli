# 06 · Evidencias

Pantallazos para la wiki de Azure. Cada evidencia se reproduce desde la raíz del repo con
`python 06-evidence/replay.py N` (multiplataforma; en Windows usar `.venv/Scripts/python`).
Guardar las imágenes en `06-evidence/img/` con el nombre indicado.

| ID | Qué muestra | Cómo reproducir | Imagen |
|---|---|---|---|
| E1 | CLI 2.2.6 y 2.5.0 funcionando contra el core v2.3.3 (sin actualizar el cluster) | `replay.py 1` | `img/E1-versiones.png` |
| E2 | Errores que solo aparecieron en el cluster en la 1.ª corrida "antes" (2,4 min, ~5.200 tokens) | `replay.py 2` · log completo: `05-measurements/runs/before-1/observe-cluster-01.log` | `img/E2-errores-cluster.png` |
| E3 | CLI 2.5 detecta offline los 2 bugs de composiciones generales (`aws-cloudwatch`, `aws-iam-role`) | `replay.py 3` | `img/E3-validate-offline.png` |
| E4 | Adopción: claim real `adopt-kms-test` verificado offline (10/10) y variante insegura detectada (crearía en vez de adoptar) | `replay.py 4` | `img/E4-adopcion-offline.png` |
| E5 | Llave KMS de la 1.ª corrida en `PendingDeletion` (limpieza) | Consola AWS → KMS → Customer managed keys → `a1fc7105-51dd-4c07-8ea3-09bc672cf2b7` | `img/E5-kms-pending-deletion.png` |

Siguientes (caso API desplegable): E6 render/validate/contrato del caso nuevo · E7 KIND `project run` ·
E8 XR Ready en EKS + `crossplane resource trace` · E9 API en consola AWS (API Gateway, stage, logs, alarmas) ·
E10 matriz de defectos · E11 limpieza.
