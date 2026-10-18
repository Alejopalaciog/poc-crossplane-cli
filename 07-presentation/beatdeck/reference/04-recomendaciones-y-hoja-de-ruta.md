# 04 · Recomendaciones y hoja de ruta

## Veredicto
**Sí vale la pena adoptar la CLI 2.5, por partes.** El valor está en **validar antes del cluster** (render, render
anidado, validate, trace) combinado con una **compuerta local** con reglas de negocio. Las funciones Python tipadas y el
proyecto completo aportan, pero hoy tienen fricciones (Windows, tiempos de build, nombres) que no justifican migrar
todo el catálogo de una vez.

## Qué adoptar ya (bajo esfuerzo, alto valor)
1. **CLI 2.5 fijada en el repo** (no requiere actualizar el cluster; soporta core v2.3).
2. **Compuerta local** (`local_gate.py`) como paso obligatorio antes del PR de cualquier composición:
   render simulado + anidado, validate contra providers/XRDs, contrato de negocio, multi-instancia.
3. **Contrato de negocio ejecutable** por tipo de plataforma (tags, naming/guardarraíles IAM, cifrado, retención,
   observabilidad): convierte estándares escritos en reglas que corren en segundos.
4. **Corregir los 4 bugs latentes** de `jarvis_aws_xrds` encontrados.

## Qué adoptar después (requiere trabajo)
5. **Compuerta en Azure Pipelines** (PR de `jarvis_aws_xrds` y `jarvis_platform_xrds`).
6. **Publicar `jarvis_aws_xrds` como Configuration package versionado**: habilita `dependency add`, modelos tipados y
   validación automática de los bloques generales desde las plataformas, y dependencias explícitas entre repos.
7. **Skill de migración + paso offline** antes del PR (reglas AD-01..05) y, después, "gap what-if" con render +
   observados (ver `00-research/skill-migracion-tf-crossplane.md`).
8. **Skill/steering de Kiro** que use la compuerta para autovalidarse (plan en `future/kiro-skill-plan.md`).

## Qué evaluar más adelante
9. Funciones Python embebidas: cuando el equipo trabaje en WSL/devcontainer o el build se haga en CI.
10. `project run` para pruebas de instalación de paquetes (útil cuando existan Configurations).

## Hoja de ruta sugerida
| Fase | Qué | Resultado esperado |
|---|---|---|
| 1 · Sprint actual | CLI 2.5 fijada + compuerta y contrato en el repo + issues de los 4 bugs | Errores detectados antes del cluster en composiciones nuevas |
| 2 · Siguiente sprint | Compuerta en CI + correrla sobre todo el catálogo + paso offline en la skill de migración | Calidad continua; menos sorpresas en migración |
| 3 · Trimestre | `jarvis_aws_xrds` como Configuration package + skill Kiro con compuerta | Dependencias versionadas, modelos tipados, menos créditos AI |
| 4 · Evaluación | Funciones tipadas (Python/Go) para composiciones complejas (ej. `ecs`, `istio`) | Mantenibilidad de las composiciones grandes |

## Riesgos y cómo mitigarlos
- **Falsa confianza**: la compuerta solo detecta lo que cubre (se vio con la colisión). Mitigar: cada error nuevo
  que llegue al cluster se convierte en una regla de la compuerta.
- **Comandos Beta**: fijar versión y revisar release notes antes de subir.
- **Curva de aprendizaje**: el equipo ya domina go-templating; empezar por render/validate/compuerta, no por funciones.
