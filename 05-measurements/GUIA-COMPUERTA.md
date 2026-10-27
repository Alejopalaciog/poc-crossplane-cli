# Guía de la compuerta local

Cómo correr la compuerta, leer su resultado y hacerla crecer: agregar reglas de negocio, bloques generales,
providers y nuevos tipos de composición. Es la "compuerta que aprende" de la propuesta: cada hallazgo se convierte en
una regla.

## 1. Las piezas

| Archivo | Qué hace | Quién lo toca |
|---|---|---|
| `local_gate.py` | Orquesta todo: render simulado, render anidado, multi-instancia, `resource validate` y contrato | Rara vez: al sumar un bloque general o una etapa nueva |
| `business_checks_api.py` | Contrato de negocio de `XPocCliApiService`: reglas API-00 a API-10 | **Aquí crecen las reglas** |
| `adoption_checks.py` | Reglas de adopción AD-01 a AD-05 (migración Terraform → Crossplane) | Al aprender algo nuevo de adopción |
| `defects.py` | Catálogo de defectos: inyecta cada error y mide si se detecta | Al agregar una regla, para probarla |
| `04-after-cli-2.5/extensions/` | `providers.yaml` y las XRDs contra las que valida `resource validate` | Al usar un provider o un bloque general nuevo |

Lo técnico (simular, renderizar y validar) lo hace la CLI 2.5. El criterio Nequi vive en los contratos.

## 2. Requisitos

- Docker en marcha. Las funciones de Crossplane corren como contenedores.
- `tools/crossplane-2.5.0` (ver el README del repo para descargarla).
- Python 3.11+ con PyYAML.
- Login de lectura a ECR para la función privada `function-jarvis-findresources`.
- El repo de composiciones generales clonado junto a este (`../local-argocd-crossplane-config`) o su ruta en
  `--general-dir`.
- La red de Docker de los contenedores "calientes", una sola vez: `docker network create poc-gate`.

## 3. Correrla

Desde la raíz del repo:

```bash
python 05-measurements/local_gate.py \
  --xr 04-after-cli-2.5/project/examples/xr.yaml \
  --composition 04-after-cli-2.5/project/apis/xpoccliapiservices/composition.yaml \
  --functions 04-after-cli-2.5/project/examples/functions.yaml \
  --nested-functions 04-after-cli-2.5/general-audit/functions-api.yaml \
  --extensions 04-after-cli-2.5/extensions \
  --contract 05-measurements/business_checks_api.py \
  --multi-instance
```

| Argumento | Para qué |
|---|---|
| `--xr` | Una solicitud de ejemplo (el XR que pediría un equipo) |
| `--composition` | La composición a probar |
| `--functions` | Funciones que usa esa composición |
| `--nested-functions` | Funciones de los bloques generales (incluye las privadas) |
| `--extensions` | Carpeta con `providers.yaml` + XRDs para validar |
| `--contract` | Script de reglas de negocio (opcional) |
| `--multi-instance` | Renderiza una 2.ª solicitud y verifica que no choquen nombres |
| `--out` | Dónde deja los renders (por defecto `05-measurements/gate-out`) |

La primera vez tarda ~100 s porque descarga imágenes. Después, ~15–30 s.

## 4. Leer el resultado

Ejemplo ilustrativo de una corrida rechazada:

```
ETAPA                                    RESULT    SEG  DETALLE
render plataforma (simulado)             OK       4.1  3 pasadas, 9 recursos
render anidado XKMS                      OK       2.0  2 pasadas, 2 recursos
multi-instancia (sin colisiones)         FALLA    0.0  choca: Integration/integration-health-get
validate esquemas (providers + XRDs)     OK       6.3  Total 31 resources: 0 missing schemas, 31 success cases, 0 failure cases
contrato de negocio                      FALLA    0.2  10/11 reglas de negocio cumplidas
      FAIL  API-03 retención logs          1 días (mínimo 14 en dev)

Compuerta local: RECHAZADA en 18.4 s (sin cluster ni AWS)
```

- El código de salida es 0 si se aprueba y 1 si se rechaza: sirve tal cual en CI.
- Si algo falla, el detalle dice qué y dónde. Los renders completos quedan en `--out` (`platform-render.yaml`,
  `all-rendered.yaml`).
- `'<no value>'` en un render anidado casi siempre es un bug del bloque general: un campo que la plantilla espera y
  no llega.

## 5. Agregar una regla de negocio

Es el caso más común. Ejemplo: "toda alarma debe notificar a un tópico SNS".

**1. Escribir la regla en el requerimiento.** Agrégala a la tabla de `01-requirement/README.md` (sección 6) con el
siguiente número libre, por ejemplo `API-11`, en una frase que entienda alguien de negocio.

**2. Implementarla en `check()` de `business_checks_api.py`.** Todas siguen el mismo patrón: buscar los recursos
en `kinds`, revisar y llamar `add(regla, ok, detalle)`.

```python
    # API-11 alarmas con notificación
    sin_sns = [a["metadata"]["name"] for a in alarms if not fp(a).get("alarmActions")]
    add("API-11 alarmas notifican", alarms and not sin_sns, ", ".join(sin_sns) or f"{len(alarms)} alarmas OK")
```

Helpers disponibles:

| Helper | Devuelve |
|---|---|
| `kinds["MetricAlarm"]` | Lista de recursos de ese kind en el render |
| `params(doc)` | `spec.parameters` (para XRs, como los bloques generales) |
| `fp(doc)` | `spec.forProvider` (para recursos AWS) |
| `walk(doc)` | Todos los pares (ruta, valor) del documento |
| `xp`, `env` | Parámetros de la solicitud y su ambiente |

Reglas de estilo:
- El detalle debe decir **qué** falló y **dónde**. Lo lee una persona o una AI con pocos créditos.
- Si un recurso todavía no se emite (espera una dependencia), la regla no debe fallar por eso. Mira cómo lo hacen
  API-07 y API-09.
- Una regla por cosa que se pueda explicar en una frase.

**3. Probarla con un defecto.** Agrega una tupla a `DEFECTS` en `defects.py` que rompa justo esa regla (buscar y
reemplazar un texto en la composición o el XR) y corre `python 05-measurements/defects.py`. La regla sirve si:
- con la composición buena la compuerta **aprueba**, y
- con el defecto la compuerta **rechaza** y el detalle apunta a la regla nueva.

**4. Probarla sola, sin la compuerta**, si quieres iterar más rápido sobre un render ya hecho:

```bash
python 05-measurements/business_checks_api.py 05-measurements/gate-out/platform-render.yaml
```

## 6. Otras formas de hacerla crecer

**Una composición de otro tipo (no `XPocCliApiService`).** Copia `business_checks_api.py` a
`business_checks_<tipo>.py`, cambia el kind que busca al inicio de `check()` y las reglas que apliquen. Pásalo con
`--contract`. Las reglas transversales (API-00 render íntegro, API-01 identidad y tags, API-08 cuenta y región)
aplican a casi todo: conviene moverlas a un módulo común cuando haya un segundo contrato.

**Un bloque general nuevo.** Agrégalo al diccionario `GENERAL` de `local_gate.py` (kind → carpeta en el repo de
composiciones generales) para que se renderice anidado. Si sus etapas esperan un valor del estado de otro recurso
(un ARN, un ID), agrega ese campo con un valor ficticio en `FAKE_ATPROVIDER`. Si no, la simulación se queda sin
avanzar y lo reporta como "no convergió".

**Un provider nuevo.** Agrégalo a `04-after-cli-2.5/extensions/providers.yaml` con **la misma versión que el
cluster**. Si la versión no coincide, la validación aprueba cosas que el cluster rechaza, o al revés.

**Una XRD nueva o cambiada.** Copia la XRD a `extensions/`. Así `resource validate` revisa también las solicitudes y
los bloques generales.

**Una función nueva.** Agrégala al archivo de `--functions` (o `--nested-functions` si la usa un bloque general),
con las anotaciones `render.crossplane.io/runtime-docker-*` para reutilizar el contenedor entre renders.

**Una regla de adopción.** Mismo patrón en `adoption_checks.py` (AD-06…), que corre sobre el render de un claim de
adopción antes del PR.

## 7. El ciclo: de hallazgo a regla

1. Algo llega al cluster que la compuerta no vio: un error en un despliegue, un comentario en una revisión de PR, un
   bug en un bloque general o un estándar nuevo de seguridad o gobierno.
2. Se pregunta: ¿se puede ver en el render? Si el dato está en el YAML que genera la composición, sí.
3. Si sí: regla nueva (sección 5) + defecto que la pruebe. Si no (permisos reales de AWS, cuotas, estado de recursos
   existentes): se documenta como límite de la compuerta. Lo cubre el cluster, y a futuro `simulate`.
4. La próxima vez ese error se detecta en segundos.

Así se agregó la prueba multi-instancia: la colisión de nombres se escapó al cluster en la PoC, se convirtió en
etapa de la compuerta y ahora se detecta antes.

## 8. Problemas comunes

| Síntoma | Causa probable |
|---|---|
| Tarda ~100 s | Primera vez: descarga imágenes. O los contenedores calientes se borraron |
| `pull access denied` en `function-jarvis-findresources` | Falta login a ECR |
| `network poc-gate not found` | Falta `docker network create poc-gate` |
| "no convergió" | Dependencia circular, o un campo de estado que falta en `FAKE_ATPROVIDER` |
| `missing schemas` en validate | Falta el provider o la XRD en `extensions/` |
| Aprueba algo que el cluster rechaza | Versiones distintas en `providers.yaml`, o un límite de la compuerta (permisos, recursos existentes) |
