# Skill de migración Terraform → Crossplane (tscbo_developerkit_Tool) vs CLI 2.5

Rama analizada: `feat/2026/sp20/ha-7921988` vs `trunk` — 10 commits (14-oct-2026), 19 archivos, +2.188 líneas.

## 1. Qué trae la rama

| Artefacto | Qué hace | Cómo obtiene los datos |
|---|---|---|
| `skills/crossplane-discover-architecture` (+ `discover-by-tag.py`, 350 l) | Inventario por capa de los recursos ya adoptados, filtrando por tags de origen (`tfmodule`, `repository`...) | `kubectl get` sobre el cluster |
| `skills/crossplane-adoption-gap` (+ `gap-analysis.py`, 578 l, 5 references) | Diff `forProvider` vs `atProvider`, clasificación de riesgo, flags (`TAG_CONFLICT`, `INVALID_TAG_RENDER`, `NO_EXTERNAL_NAME`, `WOULD_WRITE_ON_MANAGED`...). La AI solo decide los flags y edita el claim | `kubectl get` (estado observado en AWS) |
| `skills/crossplane-activate-managed` (+ `preflight-activate.py`, 378 l) | Semáforo LISTO/BLOQUEADO antes de pasar de Observe a gestión, orden por capas, permisos IAM | Reutiliza el motor del gap |
| `agents/crossplane-adoption-agent.md` | Orquesta los 3 pasos, permisos Kiro (solo `kubectl get` y scripts; deny de apply/delete/curl/pip...), gate humano | — |
| `prompts/adoption-plan.md` | El mismo flujo como prompt ejecutable | — |

Diseño muy sólido: **determinístico en scripts (0 créditos), la AI solo decide lo ambiguo, gate humano no negociable.**

## 2. El hueco que tiene el flujo hoy

Todo el flujo trabaja **después del apply**: el claim editado por la AI (Step 2) solo se puede
comprobar llevándolo a Git → ArgoCD → cluster → reconciliación → volver a correr el gap.
Cada vuelta = PR + sync + minutos de reconciliación + re-lectura del reporte (créditos).
No existe un paso **"antes del PR"** que responda: *¿qué va a generar este claim editado?*

## 3. Dónde la CLI 2.5 suma (evidencia de esta PoC)

| Regla / pitfall de la skill | Hoy se detecta | Con CLI 2.5 (offline, antes del PR) | Evidencia |
|---|---|---|---|
| Propagación de `managementPolicies` a toda la cadena (regla de oro 5) | Preflight, sobre el cluster | `composition render` + `adoption_checks.py` AD-01/02 | Claim real `adopt-kms-test`: 10/10 OK en 5 s |
| `external-name` presente en todos los MRs (regla 2, flag `NO_EXTERNAL_NAME`) | Gap, sobre el cluster | AD-03 sobre el render | Variante sin `managementPolicies`: la composición KMS **quita el external-name** → crearía una llave nueva con política `*` (incluye Delete). Detectado offline en ~4 s |
| `<no value>` por go-template fallido (flag `INVALID_TAG_RENDER`) | Solo en **tags**, sobre el cluster | AD-04 en **cualquier campo** | Bug real `aws-iam-role`: `permissionsBoundary: <no value>` (no es un tag → la skill no lo vería; AWS lo rechaza con 400) |
| Comentarios go-template que rompen el YAML (pitfall) | Al aplicar (error en cluster) | El render falla localmente con el mensaje exacto | — |
| Campos inexistentes en el CRD del provider | En el cluster (`field not declared in schema`) | `resource validate` contra el provider | Bug real `aws-cloudwatch`: `forProvider.name` |
| Cambiar una composición general "para hacerla configurable" (regla 3) | Riesgo de romper otros claims, se ve en cluster | Renderizar todos los claims existentes con la composición vieja y la nueva y comparar | (propuesto) |
| "Plan" de la activación | No existe (Crossplane no tiene plan) | `render --observed-resources` con un snapshot real de los MRs → ver lo que se emitiría al activar; alimentar `gap-analysis.py` con ese render = **gap "what-if" sin aplicar** | (propuesto, siguiente iteración) |

## 4. Dónde NO suma (y hay que decirlo)

- **Discover y gap necesitan el estado real de AWS (`atProvider`)**: la CLI no lo reemplaza. Las skills siguen siendo necesarias.
- **Permisos del agente**: habría que permitir `crossplane composition render *` y `crossplane resource validate *` (solo lectura, offline). El agente prohíbe instalar binarios → la CLI y Docker pasan a ser **prerrequisitos** del entorno Kiro (`PREREQUISITE_UNAVAILABLE` si faltan).
- **Funciones privadas** (`function-jarvis-findresources` en ECR): el render necesita login a ECR o mocks (`--observed-resources` / `--required-resources`).
- Comandos DevEx en **Beta**: pueden cambiar.

## 5. Recomendación

**Seguir con las skills propias y agregarles un paso offline con la CLI 2.5**, no reemplazarlas:

1. *Step 2.5 — "Verificación antes del PR"* en `crossplane-adoption-gap`: tras editar el claim, `composition render` + reglas AD-01..AD-05 (script determinístico, mismo patrón "0 créditos").
2. Generalizar `INVALID_TAG_RENDER` a cualquier campo (`<no value>` en todo el render).
3. Siguiente iteración: gap "what-if" (render con observados + `gap-analysis.py`) para que el preflight diga LISTO/BLOQUEADO **antes** de que la persona haga el cambio de modo en Git.
4. Agregar al agente el allowlist de `crossplane composition render`/`resource validate`.

Impacto esperado: menos vueltas PR→sync→re-gap por servicio migrado (cada vuelta evitada ahorra minutos de reconciliación y la re-lectura del reporte por la AI), y se cierra la clase de error más peligrosa de la adopción: **crear en vez de adoptar**.
