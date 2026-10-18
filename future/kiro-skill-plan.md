# Plan (no ejecutado) · Skill/steering de Kiro con la compuerta de la CLI 2.5

> Estado: **propuesta**. Se deja documentada por tiempos; no se construyó en esta PoC.

## Objetivo
Que la AI (Kiro) **se autovalide localmente** antes de pedir un apply o abrir un PR, en lugar de aprender de los
errores del cluster. Según la PoC, eso baja los turnos del agente de ~28 a ~11 y los créditos estimados a ~30 %.

## Componentes
1. **Skill `crossplane-composition-gate`**
   - `SKILL.md` con el procedimiento: escribir/editar → correr la compuerta → leer SOLO el resumen → corregir lo
     marcado → repetir hasta APROBADA → recién entonces proponer el PR.
   - `scripts/local_gate.py` (el de esta PoC) y `scripts/business_checks_<plataforma>.py`.
   - `references/`: cómo leer cada etapa de la compuerta, catálogo de defectos (D01–D11) y su corrección típica.
   - Principio de las skills existentes: **lo determinístico en scripts (0 créditos), la AI solo decide lo ambiguo**.
2. **Steering** (`crossplane-composition-conventions.md`, aplica a `**/composition*.yaml`):
   - Nunca `kubectl apply` para "probar": primero la compuerta.
   - Claves únicas por instancia al usar bloques generales; `managementPolicies` explícitas; naming con guardarraíles.
3. **Permisos del agente** (como `crossplane-adoption-agent`):
   - `allow`: `crossplane composition render *`, `crossplane resource validate *`, `crossplane resource trace *`,
     `python scripts/local_gate.py *`.
   - Prerrequisitos: CLI 2.5 y Docker instalados (si faltan → `PREREQUISITE_UNAVAILABLE`, sin instalar nada).
4. **Integración con la skill de migración**: paso "verificación antes del PR" con `adoption_checks.py` (AD-01..05).

## Cómo medir que funciona
- Repetir el caso API con Kiro real, con y sin la skill: turnos, créditos reales, vueltas en cluster.
- Meta: ≥ 60 % menos créditos y 0 vueltas de cluster por errores cubiertos por la compuerta.

## Esfuerzo estimado
~1 sprint de una persona: empaquetar scripts, escribir SKILL.md/steering, probar con 2–3 composiciones reales.
