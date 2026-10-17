# 01 · Requerimiento, contrato de negocio y catálogo de defectos

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
