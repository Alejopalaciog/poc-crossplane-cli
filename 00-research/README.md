# 00 · Investigación: Crossplane CLI 2.3 → 2.5

## 1. Qué cambió y cuándo

| Versión | Fecha (2026) | Qué trae | Impacto para nosotros |
|---|---|---|---|
| **v2.3.0** | 21 may | Primer release del repo `crossplane/cli` (antes vivía en `crossplane/crossplane`). Árbol de comandos *noun-first* (`crossplane render` → `crossplane composition render`, alias conservado). Comandos beta en el árbol principal. **DevEx "Project"**: `project init/run/stop`, `xrd generate`, `composition generate`, `function generate`, `dependency add`. | Cambia la forma de trabajar: proyecto único (APIs + funciones + ejemplos + tests). |
| v2.3.1–2.3.4 | may–jul | Fixes de render (timestamps estables, orden de recursos, stderr), inferencia de enteros en `xrd generate`. | Render determinístico → apto para diffs en PR. |
| **v2.4.0** | 24 jun | **CLI desacoplada del core**: soporta Crossplane v2.3, v2.2, v2.1 y v1.20. Nuevos: `xr generate` (claim→XR), `xr patch` (aplica defaults de XRD), `xpkg get-crds`. `resource validate` con salida YAML/JSON. `composition render --required-resources/--extra-resources` repetibles. Impersonación `--as`. Funciones pre-construidas en cualquier lenguaje dentro del proyecto. | **Podemos usar la CLI más nueva sin tocar el core v2.3.3 del cluster.** |
| v2.4.1 | 24 jul | `validate` usa imagen `crossplane:stable` por defecto, render context por TCP, builds multi-arch Python. | Estabilidad. |
| **v2.5.0** | 21 ago | `xrd convert --json-schema`, `xrd generate --replace`, **SimpleSchema con tipos custom**, modelos Go con GetX/SetX + `runtime.Object`, `validate` reconoce recursos built-in de Kubernetes. | Evolucionar XRDs desde SimpleSchema sin borrar a mano; validar también ConfigMaps/Secrets compuestos. |

Siguiente release del core: v2.5 (nov 2026).

## 2. Compatibilidad verificada en esta PoC

```
crossplane-2.5.0.exe version   → Client v2.5.0 · Server v2.3.3   ✅
crank-2.2.6.exe version        → Client v2.2.6 · Server v2.3.3   ✅
```
Evidencia: `05-measurements/runs/setup/`.

## 3. Equivalencia de comandos: "antes" (2.2.6) vs "después" (2.5.0)

| Necesidad | CLI 2.2.6 (antes) | CLI 2.5.0 (después) | Estado en 2.5 |
|---|---|---|---|
| Crear estructura de proyecto | — (a mano) | `project init` | Beta |
| Escribir el XRD (OpenAPI) | a mano | `xrd generate --from simpleschema` / `--from xr` | Beta |
| Esqueleto de Composition | a mano | `composition generate` | Beta |
| Función de composición | YAML go-templating inline | `function generate -l go-templating\|python\|go\|kcl` (embebida, con bindings tipados) | Beta |
| Bindings/schemas de providers | — | `dependency add <provider>` | Beta |
| Previsualizar recursos | `render xr.yaml comp.yaml functions.yaml` | `composition render xr.yaml comp.yaml` (lee funciones del proyecto) | GA |
| Validar contra schemas | `beta validate` | `resource validate` (+ JSON/YAML, built-ins) | Beta |
| Claim → XR / defaults | — | `xr generate`, `xr patch` | Alpha (oculto) |
| CRDs de dependencias | — | `xpkg get-crds` | GA |
| Control plane local | — (kind + helm a mano) | `project run` / `project stop` | Beta |
| Empaquetar y versionar | `xpkg build` (manual, crossplane.yaml a mano) | `project build` / `project push` (Configuration + funciones) | Beta |
| Troubleshooting | `beta trace` | `resource trace` | Beta |

## 4. Beneficios declarados por la comunidad (a validar con pruebas)
- Una sola fuente de verdad: configuración + código de funciones en un proyecto versionado como unidad.
- Autocompletado, hover y type-checking en funciones gracias a bindings generados.
- Ciclo rápido de render antes de desplegar; control plane local de un comando.
- Mejor para agentes AI: lenguajes generales (Python/Go) bien conocidos por los modelos.

## 5. Advertencias declaradas
- Requiere Docker (render de funciones, builds, KIND). Primer `project run` lento.
- Tests automatizados (render-based y e2e) y simulaciones **aún no disponibles** ("future work" en el blog).
- TypeScript en progreso. La mayoría de comandos DevEx son **Beta**; `xr` es **Alpha**.
- El ejemplo oficial usa solo APIs de Kubernetes; para nube hay que añadir providers como dependencia.

## 6. Contexto Nequi relevante
- Core del cluster: v2.3.3 (chart). Providers AWS v2.5.0 (family). Funciones: go-templating, P&T, auto-ready, jarvis-findresources (ECR).
- ~65 composiciones (34 en `jarvis_aws_xrds`, 31 en `jarvis_platform_xrds`), todas YAML go-templating; ninguna usa render/validate en repo ni CI; sin Configuration packages.
- Docker Desktop en la máquina de pruebas descarga funciones desde `xpkg.upbound.io` sin configuración adicional (usa el trust store de Windows): ~7–9 s por función.

## Fuentes
- [Introducing the new Crossplane CLI developer experience (blog)](https://blog.crossplane.io/introducing-the-new-crossplane-cli-developer-experience/)
- [crossplane/cli (GitHub)](https://github.com/crossplane/cli) · [Releases](https://github.com/crossplane/cli/releases)
- [Get started with control plane projects (docs v2.4)](https://docs.crossplane.io/cli/v2.4/get-started/get-started-with-control-plane-projects/)
- [Command reference (docs)](https://docs.crossplane.io/latest/cli/command-reference/)
- [Crossplane Testing: Rendering and Validating Compositions (Upbound)](https://blog.upbound.io/composition-testing-patterns-rendering)
- [Authoring XRDs in a Control Plane Project (Upbound)](https://docs.upbound.io/build/authoring-xrds)
- Ayuda integrada de ambos binarios (`--help`), capturada en esta PoC.
