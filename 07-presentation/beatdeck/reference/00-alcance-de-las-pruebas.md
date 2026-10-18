# 00 · Alcance de las pruebas: qué se probó y qué significa cada resultado

Este documento explica, en lenguaje simple, cada cosa que se probó en la PoC de Crossplane CLI 2.5:
qué significa, cómo se midió, qué resultado dio y cuál es su límite. Las cifras vienen de
`05-measurements/results.csv`, `defects.csv` y `credits.json`; las evidencias, de `06-evidence/`.

> **Escenarios comparados**
> - **Antes-1 (hoy, sin CLI):** la AI escribe la composición en YAML y se valida aplicándola al cluster.
> - **Antes-2 (CLI vieja 2.2):** igual, más `render` + `beta validate` locales.
> - **Después (CLI 2.5 + compuerta local):** proyecto CLI 2.5 y una "compuerta" que valida todo en la máquina antes de tocar el cluster.

---

## 1. Detección de errores antes del cluster

**Qué significa.** Hoy, para saber si una composición funciona, hay que aplicarla al cluster (Argo o kubectl)
y esperar a que Crossplane intente crear los recursos en AWS; los errores aparecen minutos después, en eventos de
Kubernetes. "Antes del cluster" = descubrir el error **en la máquina del desarrollador (o de la AI), en segundos,
sin tocar el cluster compartido ni AWS**.

**Cómo se probó.** Se tomó la composición final (que funciona) y se le inyectaron **11 errores típicos**, uno a la vez
(`05-measurements/defects.py`). Cada versión dañada se pasó por la herramienta de cada escenario:
- *Antes-1 (solo cluster):* no se aplicaron los 11 a AWS (para no ensuciar la cuenta). Se documentó con base en cómo
  se comporta Kubernetes/Crossplane y en los errores **reales** que sí vimos en la PoC.
- *Antes-2 (CLI 2.2):* `render` + `beta validate` (medido).
- *Después (CLI 2.5 + compuerta):* render simulado y anidado, validate, contrato de negocio y prueba multi-instancia (medido).

**Resultado.** CLI 2.2: **6 de 11** · CLI 2.5 + compuerta: **11 de 11**. Además, **3 errores que con el método actual
nunca se detectan**: se despliega "bien" pero queda mal (sin tag de costeo, retención de logs de 1 día, campo mal
escrito que se ignora en silencio).

**Límite.** Los 11 errores son representativos, no exhaustivos. El 11/11 es **CLI 2.5 + una compuerta construida
encima**: la CLI aporta el render (incluido anidado con funciones privadas) y el validate; las reglas de negocio y la
simulación de reconciliación son nuestras (`05-measurements/local_gate.py`, `business_checks_api.py`).

Evidencia: E6, E10.

---

## 2. Ciclo de feedback: cuánto se tarda en saber si algo está bien

**Qué significa.** Tiempo entre "hice un cambio" y "sé si funciona". Cuantas más vueltas tiene un desarrollo, más pesa.

**Cómo se probó.** Cronometrando cada vuelta con `05-measurements/measure.ps1`: en el cluster (apply → esperar
Ready o error, `observe-xr.ps1`) y en local (compuerta).

**Resultado.**
| | Por vuelta | Vueltas hasta funcionar (caso API) |
|---|---|---|
| Cluster | 2 – 3,5 min | Antes-1: **3 vueltas, ~12 min** hasta Ready |
| Compuerta local | **15 – 30 s** (100 s la 1.ª vez, descarga de imágenes) | Después: **2 vueltas locales (~3 min)** y luego el cluster |

**Límite.** El cluster sigue siendo necesario para la verificación final (permisos reales de AWS, tiempos de AWS).

Evidencia: E2, E6, E8.

---

## 3. Créditos de AI (Kiro)

**Qué significa.** Cuánto consume la AI para llegar a una composición que funciona. Lo que más gasta **no es escribir
el YAML**, sino los **turnos en que la AI espera y consulta el cluster** (`kubectl get`, describe, eventos): en cada
turno se re-envía todo el contexto.

**Cómo se calculó.** Modelo de estimación (`05-measurements/estimate_credits.py`), no se ejecutó Kiro real.
Usa **datos medidos** (iteraciones, minutos de espera en cluster, tamaño real del feedback: eventos 900–1.800 tokens
vs. salida de la compuerta ~170–300) y **supuestos explícitos** (contexto base 15k tokens, la AI consulta cada 30 s,
2 turnos de diagnóstico por error).

**Resultado.**
| Escenario | Turnos | Créditos relativos | Espera en cluster |
|---|---|---|---|
| Antes-1 (YAML + cluster) | 28 | 100 % | 8,0 min |
| Antes-2 (CLI 2.2 + cluster) | 22 | 77 % | 5,8 min |
| Después, tal como ocurrió (un error se escapó al cluster) | 31 | 101 % | 7,8 min |
| **Después con la compuerta completa** | **11** | **~30 %** | **2,3 min** |

**Límite.** Es una estimación, no la factura de Kiro. Lo sólido es la tendencia y la razón: menos turnos esperando
el cluster. Y una lección clave: **el ahorro existe solo si la compuerta cubre el tipo de error**; si se escapa al
cluster, se vuelve al costo de siempre.

---

## 4. Bugs latentes en composiciones generales

**Qué significa.** Al construir la composición nueva reutilizando los bloques generales que ya existen
(`jarvis_aws_xrds`), aparecieron errores **que ya estaban ahí** y nadie había visto porque nadie había usado esos caminos.

**Los 4 encontrados:**
1. `aws-iam-role`: si no se pasa `permissionsBoundary`, manda el texto `<no value>` a AWS → falla la creación del rol.
2. `aws-cloudwatch`: usa un campo (`forProvider.name`) que no existe en el provider → no puede crear log groups.
3. `aws-apigateway-integration`: no soporta integraciones MOCK (manda `uri: null`).
4. `aws-apigateway-integration`: nombra sus recursos sin prefijo por instancia → **dos equipos con `/health` en el mismo namespace chocan**.

**Resultado.** Los 3 primeros los detecta la CLI 2.5 **offline en segundos** (render anidado + validate); el 4.º la
prueba multi-instancia de la compuerta. En el cluster costaron 2–3,5 min cada uno y lectura de eventos.

**Límite.** Solo se revisaron los bloques que tocó este caso (5 de 34). Puede haber más: buena razón para correr la
compuerta sobre todo el catálogo.

Evidencia: E2, E3, E6.

---

## 5. Adopción (migración Terraform → Crossplane)

**Qué significa.** Se revisó la skill de migración (`tscbo_developerkit_Tool`, rama `feat/2026/sp20/ha-7921988`). Esa
skill trabaja **después** del apply, sobre el estado del cluster. El riesgo más grave en adopción es que, por un error
en el claim, Crossplane **cree un recurso nuevo en vez de adoptar el existente** (o quede con permiso de borrar).

**Cómo se probó.** Con el claim real `adopt-kms-test`: render offline y verificación de las reglas de oro de la skill
(`Observe`/políticas en toda la cadena, `external-name` presente, sin `Delete`, sin `<no value>`) con
`05-measurements/adoption_checks.py`. Luego se simuló el error típico de una AI al editar: quitar `managementPolicies`.

**Resultado.** Claim correcto: 10/10 en ~5 s. Claim dañado: la composición KMS **borra el `external-name`** →
Crossplane **crearía una llave nueva** con permiso de borrado. Detectado **antes del PR**, en ~4 s.

**Límite.** La CLI **no reemplaza** la skill (el gap analysis necesita el estado real de AWS). Recomendación:
**agregar a la skill un paso offline antes del PR** (ver `00-research/skill-migracion-tf-crossplane.md`).

Evidencia: E4.

---

## 6. Funcionalidades nuevas de la CLI 2.5 (experiencia de desarrollo)

| Funcionalidad | Qué hace | Resultado |
|---|---|---|
| `project init` | Crea la estructura del proyecto | ✅ Instantáneo |
| `xrd generate` (SimpleSchema) | 27 líneas simples → 133 líneas de OpenAPI | ✅ Pero lo genera *Namespaced*; hubo que pasarlo a *Cluster* a mano |
| `composition generate` | Esqueleto de composición | ✅ Aporta poco (solo trae `auto-ready`); nombres de funciones distintos a los del cluster |
| `dependency add` | Trae esquemas de providers y genera modelos tipados | ✅ No acepta archivos locales → los XRDs generales deben publicarse como paquete |
| `function generate` (Python) | Función Python con modelos tipados (autocompletado, validación) | ✅ Equivalente a go-templating; **no compila en Windows** (sí en WSL/Linux); el render corta a los 60 s si debe compilarla |
| `project build` | Empaqueta todo como Configuration versionado | ✅ En Linux, ~3 min |
| `project run` | Crossplane local en KIND con el paquete instalado | ✅ ~4 min; `--crossplane-version` falla con prefijo "v" |
| `composition render` / `resource validate` / `resource trace` | Previsualizar, validar, ver el árbol | ✅ **Es lo de más valor** |

**Límite.** La mayoría de estos comandos son **Beta**; pueden cambiar.

Evidencia: E1, E7, E8.

---

## 7. Despliegue real en AWS

**Qué significa.** Confirmar que lo construido funciona de verdad, no solo en simulación.

**Resultado.** Ambas versiones (Antes y Después) quedaron `Ready` en EKS: API Gateway con `/health` respondiendo
**HTTP 200**, access logs **cifrados con KMS propia** llegando al log group, alarmas 5XX y latencia, tags estándar.

**Límite del entorno.** El rol del provider solo puede crear recursos con **`cbo` en el nombre** y **no tiene permisos
de Lambda/S3/SQS** → el caso cambió de Lambda a API. Hallazgo útil: esos permisos solo se descubren en el cluster.

Evidencia: E5, E8, E9.

---

## 8. Valor por rol (más allá de quien crea composiciones)

- **Equipos que piden infraestructura:** ven **qué recursos AWS crearía su solicitud** antes del PR (render).
- **Revisor de PR:** revisa la salida del render y la compuerta, no cientos de líneas de template.
- **Gobierno / seguridad:** las reglas (tags, cifrado, retención, naming) quedan **ejecutables**, no solo en un documento.
- **SRE / plataforma:** `resource trace` muestra el árbol completo; la compuerta audita los bloques generales.
- **Migración Terraform → Crossplane:** evita "crear en vez de adoptar".
- **Agentes AI (Kiro):** feedback corto y estructurado → menos turnos y créditos.

---

## Qué NO cubre la prueba

- No se ejecutó Kiro real: los créditos son estimación con supuestos explícitos.
- Una sola corrida por escenario (plazo de 1–2 días), sin promedios ni variabilidad.
- No se probó el flujo GitOps con ArgoCD ni la integración en Azure Pipelines (queda como recomendación).
- Solo se auditaron los 5 bloques generales del caso (de 34).
- Sesgo de conocimiento: el escenario Después partió de la misma versión inicial que produjo la AI en Antes-1 para
  comparar ciclos de corrección de forma justa; la autoría desde cero no es comparable en tiempo.
