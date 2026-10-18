# 01 · Requerimiento, contrato de negocio y catálogo de defectos

> **Cambio de caso (17-oct-2026).** La primera corrida con el caso Lambda (secciones 1–5) reveló en el
> cluster 2 bugs latentes en composiciones generales (`aws-iam-role`, `aws-cloudwatch`) y que el rol del
> provider solo puede escribir recursos con `cbo` en el nombre y **no tiene permisos de Lambda/S3/SQS**.
> Esa corrida queda como evidencia del "antes". El caso desplegable pasa a ser **API Service Platform**
> (sección 6), cubierto por los permisos reales del entorno, sin agregar permisos.

## 1. La solicitud (lo que el usuario le pide a la AI)

> "Necesito una composición de plataforma para desplegar **servicios Lambda con los estándares Nequi**:
> que el equipo solo diga su servicio, país, ambiente y funcionalidad, y la plataforma cree la Lambda,
> su rol IAM con mínimo privilegio, su log group cifrado con una llave KMS propia y con retención según
> el ambiente. Opcionalmente puede ir dentro de la VPC con su Security Group. Todo con naming y tags estándar."

Mismo texto para los 3 escenarios (Antes-1, Antes-2, Después).

## 2. Diseño objetivo: `XPocCliLambdaService` (`poc-cli.platform.nequi.com/v1alpha1`)

```
XPocCliLambdaService (plataforma)
├── XKMS            llave CMK + alias, rotación activa, policy que permite a CloudWatch Logs
├── XCLOUDWATCH     /aws/lambda/<nombre-lambda>, retención por ambiente, cifrado con la CMK   ← espera keyArn
├── XIAM            rol (trust solo lambda.amazonaws.com) + policy logs acotada al log group
├── XSecurityGroup  solo si vpc.enabled=true (sin ingress 0.0.0.0/0)
└── XLambda         código desde S3, rol del XIAM                                          ← espera roleArn
```
Reutiliza XRs generales ya desplegados en el cluster (`aws.platform.nequi.com`). Patrón "capture": la
composición lee `status.atProvider` de los XRs hijos (ARN de llave y de rol) y **solo emite** los recursos
dependientes cuando el dato existe (igual que `istio` en `jarvis_platform_xrds`).

Parámetros que expone al equipo (el resto lo decide la plataforma):
`serviceid`, `capacity`, `country`, `env`, `functionality`, `accountId`, `lambda.{runtime, handler, memorySize,
timeout, s3Bucket, s3Key, environmentVariables}`, `vpc.{enabled, vpcId, subnetIds}`, `providerConfigName`.

## 3. Contrato de negocio (ejecutable: `05-measurements/business_checks.py`)

| ID | Regla | Por qué importa al negocio |
|---|---|---|
| BR-01 | Todo XR compuesto lleva `serviceid`, `capacity`, `country`, `env` y `deployment=jarvis` | Costeo, CMDB, gobierno (lambdas `nequi-government-*` limpian lo no etiquetado) |
| BR-02 | Naming estándar `standardName: true` en todos los hijos | Trazabilidad y búsqueda en consola |
| BR-03 | Retención de logs: ≥14 días en dev/qa/sbx/stg, ≥90 en pdn | Cumplimiento y costo |
| BR-04 | Log group cifrado con la CMK de la plataforma (`kmsKeyId`) | Seguridad de datos |
| BR-05 | CMK con `enableKeyRotation: true` | Control de seguridad |
| BR-06 | Rol con trust solo `lambda.amazonaws.com`; permisos de logs acotados al ARN del log group (sin `*`) | Mínimo privilegio |
| BR-07 | Guardarraíles de costo: memoria 128–1024 MB, timeout ≤ 60 s | Costo controlado |
| BR-08 | `providerConfigRef` y región consistentes en todos los hijos | Despliegue en la cuenta correcta |
| BR-09 | Sin VPC → no se crea SG; con VPC → SG sin ingress 0.0.0.0/0 | Superficie de ataque |
| BR-10 | La Lambda solo se emite cuando el ARN del rol existe (sin referencias rotas) | Despliegues sin errores intermitentes |

## 4. Catálogo de defectos a inyectar (mismo para los 3 escenarios)

Defectos típicos que comete una persona **o la AI** al construir/modificar composiciones:

| ID | Defecto | Tipo |
|---|---|---|
| D01 | Campo que no existe en el XRD hijo (`memorySizeMb` en vez de `memorySize`) | Esquema |
| D02 | Tipo errado (`timeout: "30"` string en vez de integer) | Esquema |
| D03 | Falta un campo requerido del hijo (`roleArn` en XLambda) | Esquema |
| D04 | Valor fuera de enum (`country: colombia`) | Esquema |
| D05 | Template go roto (`{{ end }}` faltante) | Sintaxis |
| D06 | Falta el tag `serviceid` en un hijo | Negocio |
| D07 | Retención de logs de 1 día en pdn | Negocio |
| D08 | Policy IAM con `Resource: "*"` | Negocio/Seguridad |
| D09 | `apiVersion` del hijo errada (`v1alpha2`) | Esquema/Cluster |
| D10 | Emitir XLambda sin esperar el `roleArn` (referencia vacía) | Lógica |

Para cada defecto se registra **en qué momento se detecta** en cada escenario: render, validate, test de
negocio, `kubectl apply`, runtime en cluster (eventos/condiciones) o **nunca** (llega a AWS).

## 5. Insumos de despliegue (cuenta Sandbox 634614730521)
- Código: `s3://masivos-deployment/poc-cli-2.5/hello.zip` (subido para la PoC, con tags estándar; fuente en `lambda-src/`).
- Tags estándar: `serviceid=NEQ0169, capacity=jarvis, country=co, env=dev, deployment=jarvis, owner=alpalac@nequi.com`.
- Lambda **fuera de VPC** (decisión de la PoC); la rama con VPC se prueba solo con render.
- ProviderConfig: `sharedservices-jarvis-dev`.

---

## 6. Caso desplegable: `XPocCliApiService` (API Service Platform)

### Solicitud a la AI
> "Necesito una composición de plataforma para **exponer APIs REST con los estándares Nequi**: el equipo
> dice su servicio, país, ambiente y funcionalidad, y la plataforma crea la API (regional), un endpoint
> `/health`, la publica en un stage del ambiente con **access logs cifrados** con una llave KMS propia y
> retención según el ambiente, y deja **alarmas** de errores 5XX y de latencia. Naming y tags estándar."

### Diseño
```
XPocCliApiService (plataforma)
├── XAPIGatewayRestStack   [general]  API REST regional                       → status.restApiId, rootResourceId
├── XAPIGatewayIntegration [general]  /health GET MOCK 200                    ← espera restApiId
├── XKMS                   [general]  CMK + alias, rotación, policy para Logs
├── Group (logs)           [directo]  access logs cifrados, retención         ← espera keyArn      (XCLOUDWATCH tiene bug)
├── Deployment + Stage     [directo]  stage <env> con access logs             ← espera integración lista y log group
└── MetricAlarm ×2         [directo]  5XXError > 0, Latency p99 > umbral       ← espera stage
```
"Directo" = la composición de plataforma compone el managed resource porque el bloque general tiene un bug
(`aws-cloudwatch`) o no soporta la capacidad (access logs en `XAPIGatewayDeployment`, alarmas).

### Guardarraíles del entorno (sin agregar permisos)
- `functionality` debe contener `cbo` → todos los nombres derivados (alias, log group, alarmas) cumplen
  la restricción `*cbo*` del rol del provider. Tags estándar sin cambios.
- `XAPIGatewayIntegration` usa `managementPolicies: [Observe]` por defecto: la plataforma debe pasar `["*"]`.
- API Gateway ya tiene rol de CloudWatch a nivel de cuenta (`role-apigw-cloudwatch-dev`) → access logs viables.

### Contrato de negocio (`05-measurements/business_checks_api.py`)
| ID | Regla |
|---|---|
| API-00 | Render íntegro: ningún campo con `<no value>` |
| API-01 | Identidad: `serviceid`, `capacity`, `country`, `env`, `deployment=jarvis` en todos los hijos (params o tags) |
| API-02 | Nombres compatibles con el guardarraíl IAM: alias, log group y alarmas contienen `cbo` |
| API-03 | Retención de access logs ≥14 días (no productivo) / ≥90 (pdn) |
| API-04 | Access logs cifrados con la CMK de la plataforma |
| API-05 | CMK con rotación |
| API-06 | API REGIONAL y clasificación de datos declarada (confidencialidad/integridad/disponibilidad/pci) |
| API-07 | Observabilidad: alarma 5XX y alarma de latencia apuntando a la API y al stage |
| API-08 | `providerConfig` y región consistentes |
| API-09 | Stage con access logs hacia el log group de la plataforma |
| API-10 | Sin referencias rotas: integración solo con `apiId`; stage solo con deployment; recursos nuevos con `managementPolicies` que permitan crear |
