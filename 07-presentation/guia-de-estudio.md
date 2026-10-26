# Guía de estudio · PoC Crossplane CLI 2.5

Guía para dominar la presentación (`presentacion-manual.html`) y responder cualquier pregunta. Tiene 5 partes:

1. La historia en 60 segundos y las cifras que hay que saberse.
2. Glosario: los conceptos que aparecen en las preguntas.
3. Slide por slide: qué dice, qué hay detrás y preguntas probables con su respuesta.
4. Preguntas fuera de las slides: metodología, alternativas, adopción, costos y seguridad.
5. Puntos débiles y cifras que parecen inconsistentes: cómo explicarlos antes de que te los señalen.

> Regla de oro al responder: **separar lo medido, lo estimado y lo que no se probó**. La PoC es fuerte justamente
> porque dice dónde están sus límites.

---

## 1. La historia en 60 segundos

Hoy, para saber si una composición de Crossplane funciona, hay que aplicarla al cluster compartido y esperar 2–3
minutos a que Crossplane intente crear los recursos en AWS. Los errores aparecen tarde, en eventos difíciles de leer, y
algunos nunca aparecen: el recurso queda "bien" pero mal configurado. Además, la AI (Kiro) gasta créditos esperando y
leyendo esos eventos.

La CLI 2.5 trae herramientas para previsualizar (`render`) y validar (`validate`) en la máquina, sin cluster. Sobre
ellas construimos una **compuerta local**: simula el despliegue paso a paso, valida contra los esquemas reales de AWS,
revisa las reglas de negocio de Nequi y prueba que dos equipos puedan convivir. Todo en unos 15–30 segundos.

Se probó el mismo requerimiento (una API con estándares Nequi, 17 recursos) de tres formas: hoy, con la CLI 2.2 y con
la CLI 2.5 + compuerta. Con 11 errores típicos inyectados, la detección antes del cluster fue de 0, 6 y 11. Además
aparecieron 4 bugs ocultos en bloques generales que ya usamos, y se detectó offline el error más caro de la migración:
crear un recurso en vez de adoptarlo.

**Propuesta:** usar la CLI 2.5 con una compuerta local que se va nutriendo de cada hallazgo: cada error que llegue al
cluster, cada bug o cada estándar nuevo se convierte en una regla. Lo que más valor da es la compuerta, no las
funciones Python ni el proyecto completo. El cluster sigue siendo la verificación final. Es una propuesta para validar
con el equipo, no una decisión tomada.

### Cifras que hay que saberse

| Cifra | Qué es | Tipo |
|---|---|---|
| **0 / 6 / 11** de 11 | Errores detectados antes del cluster: hoy / CLI 2.2 / CLI 2.5 + compuerta | Medido (hoy: documentado, no desplegado) |
| **3** | Errores que hoy nunca se detectan: campo mal escrito, sin tag `serviceid`, retención de 1 día | Medido |
| **~160 s** vs **~15 s** | Una vuelta de prueba en el cluster (127, 144 y 206 s) vs. la compuerta en caliente | Medido |
| **100 s** | Primera ejecución de la compuerta (descarga de imágenes) | Medido |
| **~14 min** vs **~5–7 min** | Caso completo hasta que la API responde: hoy (3 vueltas) vs. CLI 2.5 con compuerta completa | Hoy medido; 5–7 min estimado |
| **100 % / 77 % / ~30 %** | Créditos de AI relativos: hoy / 2.2 / 2.5 + compuerta | **Estimado** con un modelo |
| **28 / 22 / 11** | Turnos de la AI en cada escenario | Estimado |
| **101 %** | Créditos de la corrida real de "después", porque un error se escapó al cluster | Estimado sobre lo ocurrido |
| **4 bugs** | Bugs latentes en bloques generales de `jarvis_aws_xrds` | Medido |
| **5 de 34** | Bloques generales revisados de 34 | Hecho |
| **17** | Recursos que crea el caso API | Medido (`resource trace`) |
| **11 reglas** | Contrato de negocio API-00 a API-10 | Hecho |
| **10/10 y 6/10** | Adopción: claim real correcto vs. claim con la línea olvidada | Medido (~4–5 s) |
| **~65 composiciones** | 34 bloques generales (`jarvis_aws_xrds`) + 31 de plataforma (`jarvis_platform_xrds`) | Contexto |
| **v2.3.3** | Versión del core de Crossplane en el cluster; la CLI 2.5 funciona con ella | Verificado |

---

## 2. Glosario mínimo

- **Crossplane**: extensión de Kubernetes para crear infraestructura cloud declarando objetos YAML en el cluster.
  Un controlador "reconcilia": compara lo declarado con lo real y corrige sin parar.
- **Provider** (`provider-family-aws` v2.5.0): el componente que habla con AWS. Usa el rol IRSA
  `role-eks-terraform-ts-terratocross-dev`.
- **Managed Resource (MR)**: un recurso AWS concreto como objeto de Kubernetes (un `Stage`, una `MetricAlarm`).
- **XRD**: define la API propia, por ejemplo "XPocCliApiService con servicio, país, ambiente". Es el "contrato de
  entrada".
- **Composition**: la receta que traduce una solicitud (XR) en recursos. En Nequi se escriben con la función
  **go-templating** (plantillas YAML).
- **XR (composite resource)**: la solicitud concreta ("quiero la API del servicio X en dev").
- **Bloque general**: composición reutilizable de `jarvis_aws_xrds` (API REST, integración, KMS…). Una **composición
  de plataforma** (`jarvis_platform_xrds`) combina varios bloques.
- **Función de composición**: un contenedor que ejecuta la lógica de la composición (go-templating, auto-ready,
  `function-jarvis-findresources`, privada en ECR).
- **`render`**: ejecuta la composición localmente con Docker y muestra qué recursos produciría. No toca el cluster.
- **Render anidado**: renderizar también los bloques generales que la plataforma usa por dentro, incluidos los que
  usan funciones privadas.
- **Recursos observados** (`--observed-resources`): se le dice al render "imagina que estos recursos ya existen con
  este estado". Permite simular las siguientes vueltas de reconciliación.
- **`validate`**: compara los recursos renderizados contra los esquemas reales (CRDs de los providers y XRDs).
- **`trace`**: muestra el árbol de recursos de un XR desplegado y su estado.
- **Compuerta local** (`05-measurements/local_gate.py`): nuestro script. Encadena render simulado y anidado,
  validate, contrato de negocio y prueba multi-instancia.
- **Contrato de negocio** (`business_checks_api.py`): las 11 reglas API-00 a API-10 del estándar Nequi.
- **Prueba multi-instancia**: renderizar dos solicitudes distintas en el mismo espacio y verificar que no generen
  nombres iguales.
- **`managementPolicies`**: qué puede hacer Crossplane con el recurso. `["Observe"]` = solo mirar; `["*"]` = todo,
  incluido borrar.
- **`external-name`**: anotación que dice "este MR corresponde a este recurso AWS que ya existe". Sin ella, Crossplane
  crea uno nuevo.
- **Adopción**: tomar un recurso creado con Terraform y ponerlo bajo Crossplane sin recrearlo.
- **Kyverno**: motor de políticas del cluster. Tiene 4 políticas en modo Enforce; se revisaron antes de aplicar y
  ninguna afectaba a la PoC.
- **KIND**: Kubernetes dentro de Docker, en la máquina. `project run` lo usa para levantar un Crossplane local.
- **Configuration package**: forma oficial de empaquetar y versionar XRDs y composiciones.
- **SimpleSchema**: formato corto para escribir un XRD. En la PoC, 27 líneas generaron 133 de OpenAPI.

---

## 3. Slide por slide

### Slide 1 · Portada: "Crossplane CLI 2.5 en Nequi"

**Qué dice.** Es la tercera PoC del COE Cloud Platform. Pregunta si construimos y migramos composiciones más rápido,
con menos errores y menos créditos de AI. Muestra tres cifras: 11/11, ~30 % y 4 bugs.

**Lo que hay detrás.**
- Las PoC anteriores evaluaron Crossplane frente a Terraform. Esta evalúa la herramienta para construir y probar.
- El asterisco del ~30 % importa: es una estimación y solo aplica cuando la compuerta cubre el error.

**Preguntas probables.**
- *¿11/11 quiere decir que detecta todos los errores?* No. Detectó los 11 errores típicos que inyectamos; son
  representativos, no todos los posibles. Errores de permisos reales de AWS, por ejemplo, solo se ven en el cluster.
- *¿El 30 % es lo que vamos a ahorrar en la factura de Kiro?* No es la factura. Es un modelo con datos medidos
  (vueltas, esperas, tamaño de los mensajes) y supuestos explícitos. Lo sólido es la tendencia: menos turnos de la AI
  esperando al cluster.
- *¿Por qué "PoC 3"?* Es la tercera del COE sobre Crossplane, con la misma metodología: medir antes y después en el
  entorno real.

### Slide 2 · Contexto: "Hoy, para saber si algo funciona, hay que desplegarlo"

**Qué dice.** Migramos de Terraform a Crossplane con unas 65 composiciones hechas en gran parte con AI. El ciclo
actual es: pedir → la AI escribe → aplicar al cluster → esperar → leer eventos → repetir. Tiene tres dolores: es
lento, es caro en créditos y deja errores invisibles.

**Lo que hay detrás.**
- Hoy no hay `render` ni `validate` en los repos ni en CI, y no hay Configuration packages.
- El cluster `eks-terraform-ts-dev` es compartido: cada prueba ocupa un recurso común.
- "Errores invisibles" son tres concretos: un campo mal escrito que Kubernetes descarta en silencio, la falta del tag
  de costeo y una retención de logs de 1 día. AWS los acepta como válidos.

**Preguntas probables.**
- *¿Por qué Kubernetes ignora un campo mal escrito?* Los CRDs son "estructurales": el API server poda los campos que
  no están en el esquema y no avisa. El recurso se crea con el valor por defecto.
- *¿Nadie usa render hoy?* No en los repos ni en CI. Puede que alguien lo use a mano, pero no es parte del flujo.
- *¿De dónde salen los 2–3 minutos?* De lo medido: 127, 144 y 206 s por vuelta. Es el tiempo de reconciliación más
  las llamadas a AWS.

### Slide 3 · Cuatro preguntas

**Qué dice.** La PoC responde cuatro cosas: ¿menos errores?, ¿más rápido y barato?, ¿ayuda a la migración? y ¿qué
cuesta?

**Lo que hay detrás.** La cuarta pregunta es la que da credibilidad: se midieron también las fricciones (slide 17).

**Preguntas probables.**
- *¿Y la calidad o la alineación con el negocio de lo que construye la AI?* Está cubierta por el contrato de negocio
  (slide 7): el estándar Nequi convertido en reglas que se ejecutan.

### Slide 4 · Qué trae la CLI 2.5: "Un taller local para composiciones"

**Qué dice.** Previsualizar, validar, generar y empaquetar. Desde la v2.4 funciona con nuestro core v2.3: no hay que
actualizar el cluster.

**Lo que hay detrás.**
- Línea de tiempo:
  - **v2.3** (21 may 2026): primer release del repo separado `crossplane/cli` y modelo de proyecto.
  - **v2.4** (24 jun): la CLI se independiza del core y soporta core v2.3, v2.2, v2.1 y v1.20.
  - **v2.5** (21 ago): mejoras de SimpleSchema y `validate` reconoce recursos nativos de Kubernetes.
- Antes, la CLI salía junto con el core (el binario `crank` 2.2.6 que usamos como "antes").
- Se verificó: `crossplane version` → cliente 2.5.0, servidor 2.3.3 ✅.
- Equivalencias:
  - `render` pasó a `composition render`.
  - `beta validate` pasó a `resource validate`.
  - `beta trace` pasó a `resource trace`.
  - Lo nuevo es `project init/build/run`, `xrd generate`, `function generate` y `dependency add`.
- Casi todo lo nuevo es **Beta**. `xr` y `operation` son **Alpha**.

**Preguntas probables.**
- *¿Hay que actualizar Crossplane en el cluster?* No. La CLI 2.5 trabaja con el core v2.3.3 actual; se verificó.
- *¿Qué riesgo tiene que sea Beta?* Los comandos pueden cambiar entre versiones. Mitigación: fijar la versión de la
  CLI en el repo y en CI y revisar las notas de cada release antes de subir.
- *¿Por qué se compara con la 2.2 y no con la 2.4?* La 2.2.6 es la última CLI que venía con el core: representa lo
  que ya podíamos tener sin cambiar nada. La 2.4 es casi igual a la 2.5.
- *¿La CLI necesita acceso al cluster?* `render` y `validate` no. `trace` sí, porque lee el cluster.

### Divisor 01 · La prueba

### Slide 5 · La prueba: "Necesito exponer una API con los estándares Nequi"

**Qué dice.** La AI construye una composición de plataforma que reutiliza bloques generales: API REST, `/health`,
llave KMS, logs cifrados y alarmas. Son 17 recursos y se probaron tres escenarios.

**Lo que hay detrás.**
- La composición se llama `XPocCliApiService`.
  - Compone 3 bloques generales: `XAPIGatewayRestStack`, `XAPIGatewayIntegration` y `XKMS`.
  - Compone 5 recursos directos: log group, deployment, stage y 2 alarmas.
  - Contando los recursos internos de los bloques, son 17.
- El log group y las alarmas van "directos" porque el bloque `aws-cloudwatch` tiene un bug y el bloque de deployment
  no soporta access logs.
- **El caso iba a ser una plataforma Lambda.** Se cambió porque el rol del provider no tiene permisos de Lambda, S3 ni
  SQS y solo crea recursos IAM con `cbo` en el nombre. Agregar permisos no era opción. La corrida Lambda quedó como
  evidencia del "antes" y destapó 2 de los bugs.
- Dos despliegues reales: `cbopoccli1` ("antes") y `cbopoccli2` ("después").
- Los tres escenarios usan el mismo requerimiento y el mismo contrato.

**Preguntas probables.**
- *¿Por qué un caso tan "simple"?* No es trivial: son 17 recursos con dependencias, KMS, logs cifrados y alarmas.
  Además estaba limitado por los permisos reales del entorno. Las composiciones grandes (ECS, Istio) son un buen
  siguiente caso.
- *¿Fue Kiro el que escribió la composición?* La escribió un agente de AI (Claude, vía Claude Code) siguiendo el mismo
  requerimiento. Los créditos de Kiro se estimaron; Kiro no se ejecutó. **Confírmalo con el equipo antes de afirmarlo.**
- *¿Por qué no se probó con una composición existente?* Sí se tocaron 5 bloques existentes; la composición de
  plataforma es nueva para poder medir el ciclo completo de construcción.

### Slide 6 · Una compuerta local antes del cluster

**Qué dice.** En unos 20 segundos y sin AWS, la compuerta simula el despliegue, valida contra bloques y esquemas,
revisa las reglas de negocio y prueba dos equipos a la vez. Solo después se va al cluster. Aclara qué aporta la CLI y
qué aportamos nosotros.

**Lo que hay detrás (cómo funciona `local_gate.py`).**
1. **Render simulado por pasadas.**
   - Primera pasada: render sin nada existente.
   - Luego se fabrican "recursos observados" falsos como si AWS ya los hubiera creado (por ejemplo, con un
     `restApiId`) y se renderiza otra vez, hasta que todo queda listo.
   - Así se imita la reconciliación real y se ve en qué orden aparecen los recursos.
2. **Render anidado** de los bloques generales con sus funciones, incluida la privada de ECR (requiere login de
   lectura a ECR).
3. **`resource validate`** de todo, **incluidas las pasadas intermedias**. Así se detecta un recurso emitido antes de
   tiempo (D10).
4. **Contrato de negocio**: las 11 reglas API-00 a API-10.
5. **Multi-instancia**: dos solicitudes en el mismo espacio y ningún nombre repetido.
6. **Contenedores calientes**: anotaciones `render.crossplane.io/runtime-docker-*` para que las funciones no se
   reinicien en cada vuelta. Esto baja el tiempo de ~100 s a ~15 s.

**Preguntas probables.**
- *¿Qué es de la CLI y qué es nuestro?*
  - La CLI aporta render (incluido el anidado con funciones privadas y los estados simulados) y validate.
  - Nosotros aportamos el orquestador, el contrato de negocio y la prueba multi-instancia.
  - Sin el render de la CLI no podríamos hacerlo; sin nuestras reglas, la CLI solo vería errores de esquema.
- *¿Hay que mantener ese script?* Sí. Es código de PoC y habría que endurecerlo y empaquetarlo como paso de CI. Cada
  error nuevo que llegue al cluster se convierte en una regla.
- *¿Necesita credenciales de AWS?* No para crear nada. Solo necesita login de lectura a ECR para bajar la función
  privada.
- *¿En qué equipo corre?* En cualquiera con Docker y Python, y también en un agente de CI.
- *¿20, 15 o 30 segundos?* 15 s en caliente, 15–30 s con todas las pruebas y 100 s la primera vez. "~20 s" es el
  número redondo.

### Slide 7 · El estándar Nequi, convertido en reglas que se ejecutan

**Qué dice.** Nadie tiene que leer 400 líneas de plantilla: la compuerta responde si se cumplen la identidad, la
seguridad, el cumplimiento, la observabilidad y los guardarraíles. 11/11 reglas.

**Lo que hay detrás: las 11 reglas.**

| ID | Regla |
|---|---|
| API-00 | Render íntegro: ningún `<no value>` (plantilla que no encontró un dato) |
| API-01 | Tags de identidad `serviceid`, `capacity`, `country`, `env`, `deployment=jarvis` en todos los hijos |
| API-02 | Nombres con `cbo` (guardarraíl de permisos IAM del entorno) |
| API-03 | Retención ≥14 días en no productivo y ≥90 en producción |
| API-04 | Logs cifrados con la llave propia |
| API-05 | Rotación de la llave KMS |
| API-06 | API regional y clasificación de datos declarada |
| API-07 | Alarmas de 5XX y de latencia apuntando a la API y al stage |
| API-08 | Un solo `providerConfig` y una sola región |
| API-09 | Stage con access logs hacia el log group de la plataforma |
| API-10 | Sin referencias rotas y con `managementPolicies` que permitan crear |

- **Cuidado: "11/11 reglas" (esta slide) no es lo mismo que "11/11 errores" (slide 8).** Que haya 11 de cada uno es
  coincidencia. Aquí son las reglas que la composición final cumple; allá, los errores inyectados que se detectaron.

**Preguntas probables.**
- *¿Quién define las reglas?* Hoy las escribió la PoC a partir del requerimiento y los estándares. En adopción deben
  definirlas el equipo de plataforma con seguridad y gobierno, una por tipo de plataforma.
- *¿Son reglas de Kyverno?* No. Kyverno actúa en el cluster al aplicar; estas corren antes, en la máquina o en CI, y
  pueden mirar la composición entera. Se complementan.
- *¿Por qué no usar OPA o Kyverno CLI para esto?* Podría hacerse. Escribirlo en Python fue lo más rápido para la PoC;
  el motor de reglas se decide al llevarlo al repo.
- *¿Y las reglas que no pusimos?* El contrato solo verifica lo que se le pide. Ejemplo real: la llave KMS no recibió
  los tags `owner` y `poc` porque nadie lo exigió.

### Divisor 02 · Resultados

### Slide 8 · Errores típicos detectados antes de tocar el cluster

**Qué dice.** Se inyectaron 11 errores, uno a uno. Hoy se detectan 0 antes del cluster, con la 2.2 se detectan 6 y
con la 2.5 + compuerta se detectan 11. Hay tres grupos de errores: invisibles, de convivencia y de orden.

**Lo que hay detrás.**
- `defects.py` daña la composición final con un solo defecto, corre cada herramienta y anota si lo detecta y en
  cuánto tiempo.
- Los 6 de la CLI 2.2 son los errores **de esquema y sintaxis** (D01–D05 y D09).
- Los 5 que solo detecta la compuerta son **de negocio** (D06–D08), **de orden** (D10) y **de convivencia** (D11).
- **"Hoy" no se desplegó 11 veces a AWS**, para no ensuciar la cuenta compartida. Se documentó con el comportamiento
  conocido de Kubernetes y Crossplane y con los errores reales vistos en la PoC.

**Preguntas probables.**
- *¿Entonces el salto no es la CLI sino la compuerta?* Correcto, y la presentación lo dice. Los errores de esquema ya
  los veía la 2.2. El salto a 11 viene de la compuerta montada sobre el render de la CLI.
- *¿Por qué "hoy" es 0 si el error de catálogo (D04) se detecta "inmediato"?* Porque se detecta al aplicar al cluster:
  es inmediato, pero ya en el cluster.
- *¿Cómo eligieron los 11?* Son errores frecuentes en composiciones hechas con AI y varios ocurrieron de verdad en la
  PoC: campo requerido faltante, AccessDenied por nombres sin `cbo`, colisión entre equipos.
- *¿Y los falsos positivos?* La composición correcta pasa todas las pruebas: 11/11 reglas y 0 colisiones.
- *En "errores de convivencia", ¿qué es lo que choca? ¿El endpoint de API Gateway o un Service de Kubernetes?*
  Ninguno de los dos.
  - En AWS cada equipo tiene su propia API, así que ahí no hay choque.
  - Lo que choca son los **objetos de Kubernetes que crea Crossplane**. El bloque `aws-apigateway-integration` nombra
    sus recursos (Integration, Method, MethodResponse…) solo con la ruta, por ejemplo `integration-health-get`, sin
    un prefijo del equipo o la instancia.
  - Si dos equipos exponen `/health` en el mismo namespace, los dos intentan crear un objeto con el mismo nombre. El
    segundo falla con "Only one reference can have Controller set to true".

### Slide 9 · ¿Dónde se descubre cada error? (matriz)

| # | Error | Hoy | CLI 2.2 | 2.5 + compuerta: con qué |
|---|---|---|---|---|
| D01 | Campo mal escrito en un bloque (`endpointTypes`) | Nunca (se poda) | validate | validate |
| D02 | Tipo errado (umbral como texto) | Minutos | validate | validate |
| D03 | Falta un campo requerido (`confidentiality`) | ~1 min | validate | validate |
| D04 | Valor fuera de catálogo (`country: colombia`) | Inmediato al aplicar | validate | validate |
| D05 | Plantilla rota (falta `{{- end }}`) | Al reconciliar | render | render |
| D06 | Falta el tag `serviceid` | Nunca | ✗ | contrato (API-01) |
| D07 | Retención de 1 día | Nunca | ✗ | contrato (API-03) |
| D08 | Nombre de alarma sin `cbo` | Minutos (AccessDenied) | ✗ | contrato (API-02) |
| D09 | `apiVersion` errada en un bloque | Al reconciliar | validate (aviso) | render anidado |
| D10 | Stage emitido antes que su deployment | Minutos | ✗ | validate de pasadas intermedias |
| D11 | Nombres repetidos entre dos equipos | Cuando llega el 2.º equipo | ✗ | multi-instancia |

**Preguntas probables.**
- *¿Por qué la 2.2 no ve D10?* Porque solo renderiza el estado final. La compuerta valida cada pasada intermedia y
  encuentra el stage con `deploymentId` vacío.
- *¿D11 pasó de verdad?* Sí. Al desplegar "después" junto a "antes" en el mismo namespace, chocaron los recursos de
  `/health`: "Only one reference can have Controller set to true". Por eso se agregó la prueba multi-instancia.
- *¿Cuánto tarda cada detección?* En la matriz, entre 30 y 112 s por defecto, porque cada uno corrió la compuerta
  completa en frío. En el trabajo diario, con contenedores calientes, son unos 15 s.

### Slide 10 · Cada vuelta de prueba: de minutos a segundos

**Qué dice.** En el cluster una vuelta toma ~160 s; con la compuerta local, ~15 s. El caso completo pasa de ~14 min a
~5–7 min.

**Lo que hay detrás.**
- Cluster: `observe-xr.ps1` aplica y espera Ready o error. Midió 127, 144 y 206 s.
- **Hoy, ~14 min**: 3 vueltas en el cluster más el diagnóstico manual hasta que la API responde. La wiki dice "~12 min
  hasta Ready": son 12 hasta que todo queda Ready y 14 hasta que la API responde.
- **Después, ~5–7 min**: es una estimación con la compuerta completa (2 vueltas locales y un despliegue). Lo medido en
  la corrida real fue ~12 min, porque la colisión se escapó al cluster y costó 2 vueltas más. Hay que decirlo si
  preguntan.

**Preguntas probables.**
- *¿Los 5–7 minutos son medidos?* Son estimados a partir de tiempos medidos: 2 vueltas locales de 83 y 101 s en frío
  más un despliegue de 197 s. La corrida real tardó ~12 min porque la compuerta v1 no cubría la colisión.
- *¿Una sola corrida es representativa?* Es una limitación: una corrida por escenario, sin promedios. La diferencia
  (segundos vs. minutos) es grande, así que la conclusión se sostiene, pero los números exactos pueden variar.
- *¿Por qué la primera vez tarda 100 s?* Descarga las imágenes de las funciones (unos 7–9 s cada una) y arranca los
  contenedores.

### Slide 11 · Lo caro no es escribir: es esperar al cluster

**Qué dice.** Créditos relativos: 100 %, 77 % y ~30 %; turnos: 28, 22 y 11. Un error escapado devuelve el costo a
~100 %.

**Lo que hay detrás (`estimate_credits.py`).**
- En cada turno, el agente vuelve a procesar el contexto base, el historial y la salida nueva. Por eso los turnos de
  espera son caros aunque no escriban nada.
- Supuestos:
  - Contexto base de 15.000 tokens.
  - La AI consulta el cluster cada 30 s.
  - 2 turnos de diagnóstico por error.
  - Corregir cuesta el 25 % de la composición.
  - 4 caracteres por token.
- Tamaño medido de lo que lee la AI: eventos y describe del cluster pesan 580–1.827 tokens; la salida de la
  compuerta, 155–300.
- Tokens procesados: 757.920 (hoy) · 582.389 (2.2) · 766.627 (después real) · 228.593 (después con compuerta
  completa).

**Preguntas probables.**
- *¿Midieron Kiro?* No. Kiro no se ejecutó; es un modelo de estimación con supuestos públicos en el script.
- *¿Por qué no da 100 % → 0 %?* Porque escribir la composición y desplegar una vez siguen costando.
- *¿Qué pasa si cambian los supuestos?* Cambian los números, pero no el orden. La mayor parte del costo está en los
  turnos de espera y diagnóstico, y eso es lo que la compuerta elimina.
- *¿Y el 101 %?* Es la corrida real: la primera versión de la compuerta no cubría la colisión, el error llegó al
  cluster y se volvió al costo de siempre. La lección es que el ahorro existe solo si la compuerta cubre el tipo de
  error.

### Slide 12 · 4 bugs ocultos en bloques que ya usamos

| # | Bloque | Bug | Efecto | Detecta |
|---|---|---|---|---|
| 1 | `aws-iam-role` | `permissionsBoundary` sin condición manda el texto `<no value>` | AWS rechaza crear el rol (400) si no se pasa boundary | render anidado |
| 2 | `aws-cloudwatch` | Usa `forProvider.name`, que no existe en el CRD | No puede crear log groups nuevos | validate |
| 3 | `aws-apigateway-integration` | `uri` sin comillas queda `null` | Integraciones MOCK imposibles | render anidado + validate |
| 4 | `aws-apigateway-integration` | Nombres sin prefijo por instancia | Dos APIs con el mismo path en el mismo namespace chocan | multi-instancia |

**Preguntas probables.**
- *¿Qué es un bloque general?* Una composición del repo `jarvis_aws_xrds` que envuelve un servicio AWS con los
  estándares Nequi (rol IAM, KMS, log group, API REST, integración…). Hay 34. Las composiciones de plataforma de
  `jarvis_platform_xrds` (31) los combinan para armar soluciones completas. Son "los bloques que ya usamos" porque
  están instalados en el cluster y otras composiciones dependen de ellos.
- *¿Cómo saben que son bugs y no límites de AWS o de la herramienta?* Porque en los cuatro casos AWS y Crossplane sí
  permiten hacerlo, y el problema está en la plantilla del bloque. Además, los cuatro ocurrieron de verdad al
  desplegar en esta PoC, y la causa se confirmó leyendo la plantilla.
  - **Boundary**: no tiene nada que ver con Kyverno. El XRD declara `permissionsBoundary` como opcional, pero la
    plantilla lo usa sin un `if`. Cuando no se envía, go-templating escribe el texto `<no value>`, ese texto llega a
    AWS como si fuera un ARN y AWS rechaza crear el rol (error 400). Se arregla con una condición.
  - **MOCK**: API Gateway sí soporta integraciones MOCK, que no tienen backend ni `uri`. El bloque escribe la `uri`
    sin comillas; cuando no hay valor queda `null` y el recurso es inválido. Es un límite del bloque, no de AWS ni de
    Crossplane, y se arregla en una línea.
  - **Log groups**: el bloque usa `forProvider.name`, un campo que no existe en el esquema del provider. `validate` lo
    marca directamente.
  - **Choque**: es el caso de nombres explicado en la slide 8.
- *¿Si están en uso, por qué nadie los vio?* Porque nadie había recorrido esos caminos: crear un rol sin boundary,
  crear un log group nuevo con ese bloque, una integración MOCK o dos APIs con `/health` en el mismo namespace.
- *¿Afectan producción?* Solo si alguien usa esos caminos. No se revisó qué composiciones de producción los usan; es
  parte de la acción sugerida (un issue por bug).
- *¿Hay más bugs?* Probablemente. Solo se revisaron 5 de 34 bloques; por eso se propone correr la compuerta sobre
  todo el catálogo.
- *¿La wiki menciona un 5.º?* Sí: `aws-apigateway-integration` usa `managementPolicies: ["Observe"]` por defecto, así
  que una API nueva no crea nada si no se pasa `["*"]`. No se contó como bug porque es un comportamiento por defecto
  sorpresivo, no un error. Lo cubre la regla API-10.
- *¿La CLI 2.2 los detectaba?* La tabla de resultados registra 1 de 4 con la 2.2. El render anidado y la prueba
  multi-instancia son los que destapan el resto.

### Slide 13 · Evidencia: la misma compuerta, antes y después

**Qué dice.** Hay dos pantallazos. La compuerta rechaza la composición "antes" por colisión y aprueba "después" en
~29 s. La matriz muestra 6/11 contra 11/11.

**Lo que hay detrás.**
- Todo es reproducible con `python 06-evidence/replay.py N`: el paso 5 es la compuerta y el 8 es la matriz.
- El índice está en `06-evidence/README.md` (E1–E11).

**Preguntas probables.**
- *¿Lo puedo correr yo?* Sí. Necesitas Docker, la CLI en `tools/`, Python con PyYAML y login de lectura a ECR. El
  README explica cómo armarlo en otro PC.

### Slide 14 · Desplegado en EKS y AWS: la API responde

**Qué dice.** 17 recursos Ready, `/health` responde HTTP 200, access logs cifrados, retención por ambiente, alarmas y
tags estándar.

**Lo que hay detrás.**
- `resource trace` muestra el árbol Ready.
- La API se llama `apigw-jarvis-co-cbopoccli2-dev` y respondió en ~0,3 s.
- El log group `/aws/apigateway/access-jarvis-co-cbopoccli2-dev` tiene 14 días de retención y KMS propia.
- Alarmas: `-5xx` y `-latency`, en estado OK.
- Tags: `serviceid=NEQ0169`, `capacity=jarvis`, `country=co`, `env=dev`, `deployment=jarvis`.
- Cuenta Sandbox 634614730521, región us-east-1.

**Preguntas probables.**
- *¿Sigue desplegado?* No. La limpieza se hizo el 19 de octubre, con tu aprobación: XRs, composiciones y XRDs
  `poc-cli*` en cascada. Las 3 llaves KMS quedaron en borrado programado, que AWS exige; sus fechas eran 24 y 26 de
  octubre. El cluster quedó en su línea base: 21 XRDs y la adopción `adopt-kms-cbo-ts-dev` Ready.
- *¿Por qué una integración MOCK y no un backend real?* Para probar el patrón sin depender de un servicio y porque no
  hay permisos de Lambda.

### Slide 15 · Migración: "Evita el error más caro: crear en vez de adoptar"

**Qué dice.** La skill de adopción trabaja después de desplegar; la CLI agrega un paso offline antes del PR. El claim
real da 10/10; con una línea olvidada da 6/10 y crearía una llave nueva con permiso de borrar.

**Lo que hay detrás.**
- Se revisó la skill de migración `tscbo_developerkit_Tool`, rama `feat/2026/sp20/ha-7921988`.
- Se usó el claim real `adopt-kms-test`.
- `adoption_checks.py` revisa 5 reglas sobre cada recurso: 2 recursos × 5 reglas = 10 verificaciones.

| ID | Regla |
|---|---|
| AD-01 | Sin `Delete` ni `*` en `managementPolicies` |
| AD-02 | La política del claim se propaga a todos los recursos |
| AD-03 | `external-name` presente, para que no intente crear |
| AD-04 | Sin `<no value>` |
| AD-05 | `deployment=jarvis` |

- Prueba del error: se quitó `managementPolicies` del claim. La composición KMS borra el `external-name` en ese
  camino, así que Crossplane crearía una llave nueva y con permiso para borrar. Se detectó en ~4 s.

**Preguntas probables.**
- *¿La CLI reemplaza la skill?* No. La skill hace el análisis de brechas con el estado real de AWS (`atProvider`), y
  eso requiere el cluster. La CLI agrega un chequeo previo, offline.
- *¿Esto ya está en la skill?* No; es una recomendación.
- *¿Por qué es "el error más caro"?* Porque crea recursos duplicados en producción y, con permiso de borrar, puede
  terminar eliminando el recurso real.

### Slide 16 · Balance: lo bueno, lo que cuesta y el ojo

**Lo bueno.** Detecta errores en segundos, convierte los estándares en reglas ejecutables, no hay que actualizar el
cluster y encontró bugs reales.

**Lo que cuesta.** En la slide queda una sola cosa: la mayoría de comandos nuevos están en **Beta** y pueden cambiar
entre versiones. Por eso se fija la versión de la CLI en el repo y en CI.

Si preguntan por más detalle, hubo fricciones menores que no están en la slide:
- `xrd generate` crea XRDs `Namespaced` por defecto y nuestra plataforma usa `Cluster`: hay que editarlo.
- `composition generate` nombra las funciones `crossplane-contrib-function-*`, distinto de las del cluster
  (`function-*`).
- `dependency add` no acepta archivos locales: para tener modelos tipados de los bloques generales, `jarvis_aws_xrds`
  tendría que publicarse como paquete.
- Las funciones Python tardan en compilar (~3 min la primera vez) y `render` corta a los 60 s si tiene que
  compilarlas. Se resolvió reutilizando la imagen de `project build`.
- Docker es obligatorio.

**El ojo.** La compuerta solo ve lo que cubre. Los permisos reales de AWS solo se ven en el cluster, y el cluster
sigue siendo la verificación final.

**Preguntas probables.**
- *¿Vale la pena Python si el equipo sabe go-templating?* Hoy no como prioridad: la PoC mostró que es equivalente
  (misma compuerta, 11/11 reglas), pero el build es más lento y agrega complejidad. Queda para evaluar en
  composiciones grandes.
- *¿Por qué no Go o KCL?* No se probaron. Python fue la opción elegida para la variante tipada; Go y KCL quedan
  abiertos.

### Slide 17 · Lo que viene: `simulate` ("terraform plan" para Crossplane)

**Qué dice.** `simulate` mostrará qué cambiaría un cambio frente a lo que ya existe, en el cluster y en AWS. Hay dos
comandos y ninguno está en la 2.5.0.

**Lo que hay detrás.**
- Repositorio `crossplane/cli`:
  - **PR 181** (14 sep): solo el documento de diseño, sin código. Estado "Accepted".
  - **PR 429** (20 oct): implementa `resource simulate` en alpha. Hubo ajustes en los PRs 441 y 443.
  - **PR 436**: `project simulate`, todavía abierto.
- La última versión oficial es la **v2.5.0, del 21 de agosto**: no incluye nada de esto. Llegará en la próxima
  versión, sin fecha.
- Tiene dos capas:
  1. **Cluster**: qué recursos se agregan, cambian o borran. Se construye sobre la herramienta comunitaria
     `crossplane-diff` (crossplane-contrib), que renderiza y compara contra lo vivo.
  2. **Nube**: si AWS obliga a recrear algo. Para eso el provider debe exponer un "servidor de diff" (protocolo
     PlanService de upjet, fusionado en septiembre). Si el provider no lo tiene, el diff sale marcado como
     aproximado.
- **`project simulate`**: para quien cambia composiciones o funciones. Renderiza de nuevo todos los XR que usan esa
  composición y muestra el impacto.
- **`resource simulate`**: para recursos AWS concretos. También puede anticipar qué pasaría al actualizar la versión
  del provider sobre toda la flota.
- Dato clave: Crossplane **no destruye y recrea** para aplicar un cambio, como sí hace Terraform. Si el cambio lo
  exige, el recurso queda "unsynced" (trabado) hasta que alguien intervenga.

**Preguntas probables.**
- *¿Por qué no lo probaron?* No existía en la versión evaluada. Hay una compilación de desarrollo de `main` que podría
  traer `resource simulate` (alpha), pero no se probó.
- *¿Qué tan distinto es de lo que hace la compuerta?* La compuerta responde qué crearía la composición. `simulate`
  responde qué cambia respecto de lo que ya existe y si AWS exige recrear. Se complementan.
- *¿Se podría usar `crossplane-diff` hoy?* Sí, es una herramienta comunitaria que existe hoy y solo lee el cluster. No
  se evaluó en esta PoC; es un buen candidato a probar mientras sale `simulate`.

### Divisor 03 · Pasos a seguir

### Slide 18 · Propuesta: "CLI 2.5 + una compuerta que aprende"

**Qué dice.** Se propone, no se decide, usar la CLI 2.5 con una compuerta local antes del cluster. La compuerta no es
fija: crece con cada hallazgo. El ciclo es: cambio → compuerta → el cluster confirma → hallazgo nuevo → nueva regla → ↺.

**Lo que hay detrás.**
- **Arranca con lo de esta PoC**: las 11 reglas del contrato, la prueba entre equipos y los 4 bugs.
- **Crece con el uso**:
  - Cada error que se escape al cluster se analiza y se vuelve una regla. Así pasó con la colisión: se escapó, se
    agregó la prueba multi-instancia y ahora se detecta en segundos.
  - Lo mismo con un bug nuevo en un bloque general o un estándar nuevo de seguridad o gobierno.
- **Atenta a lo que viene**: `simulate`, cuando salga en una versión oficial.
- Por qué es la idea central: el ahorro de tiempo y créditos solo existe para los errores que la compuerta cubre
  (la lección del 101 %). Una compuerta que aprende va ampliando esa cobertura.

**Preguntas probables.**
- *¿Qué se necesita para arrancar?* Fijar la versión de la CLI, llevar la compuerta y el contrato al repo, documentar
  cómo correrla y abrir issues de los 4 bugs.
- *¿Quién agrega las reglas?* El equipo de plataforma, con seguridad y gobierno cuando aplique. El disparador es
  cualquier hallazgo: un error en el cluster, una revisión de PR o un estándar nuevo.
- *¿Dónde corre?* En la máquina de quien construye (persona o AI) y, idealmente, en CI. CI necesita un agente con
  Docker y login de lectura a ECR.
- *¿Y si la compuerta crece y se vuelve lenta?* Hoy son ~15 s. Las reglas de negocio son lo más barato: revisan el
  YAML ya renderizado. Lo costoso es el render, y ese no crece con el número de reglas.
- *¿Por qué no adoptar todo (funciones tipadas, proyecto completo) de una vez?* Porque esas partes tienen fricciones
  que no compensan reescribir 65 composiciones. La compuerta funciona sobre las composiciones go-templating actuales.

### Slide 19 · Cierre

"Probar antes de desplegar: la AI construye, la compuerta verifica el estándar en segundos y el cluster solo
confirma." Con las tres cifras: 11/11, ~15 s y ~30 %.

---

## 4. Preguntas fuera de las slides

### Las que ya hicieron
- **¿Usaron `crossplane simulate`, que es como un `terraform plan`?** No existe en la CLI 2.5.0, ni siquiera con los
  comandos alpha habilitados (se verificó en el binario). Está diseñado (PR 181) y `resource simulate` ya tiene código
  en `main` (PR 429), pero no hay versión oficial que lo traiga. Lo más cercano que usamos es el render con recursos
  observados, que dice qué se crearía pero no compara contra lo que existe. Ver slide 17.
- **¿Qué es exactamente la compuerta?**
  - Es un script de Python (`05-measurements/local_gate.py`) que llama a la CLI 2.5 y a nuestros chequeos.
  - Analiza el **YAML que produce el render**, es decir, exactamente los recursos que se enviarían al cluster.
  - En orden:
    1. Render por pasadas con estados simulados.
    2. Render anidado de los bloques generales.
    3. `crossplane resource validate` contra los esquemas de AWS y los XRDs.
    4. Las 11 reglas de `business_checks_api.py` sobre ese YAML.
    5. Render de dos solicitudes distintas para comparar que no repitan nombres.
  - Responde con una lista de PASS/FAIL legible.
- **¿Qué diferencia hay entre `render` y `simulate`?**
  - `render` responde "¿qué recursos produce esta composición?". No conoce el cluster: calcula el estado deseado
    desde cero, offline.
  - `simulate` responde "¿qué cambiaría si aplico esto?". Renderiza, lo compara con lo que ya existe en el cluster
    (qué se crea, cambia o borra) y le pregunta al provider si AWS exigiría recrear algo. Necesita acceso de lectura
    al cluster.
- **¿Qué cambió del `render` de la 2.2 al de la 2.5?** Respuesta honesta: para nuestras composiciones go-templating,
  el resultado del render es prácticamente el mismo. Lo que cambió está alrededor:
  - El comando pasó a `composition render` y lee las funciones del proyecto, incluidas las embebidas en Python o Go,
    que compila.
  - La salida es determinística (timestamps estables, orden de recursos fijo), lo que sirve para comparar en un PR.
  - Captura mejor los errores de las funciones (stderr y errores fatales).
  - Permite pasar recursos requeridos o extra varias veces.
  - Junto al render, `validate` mejoró: salida JSON y reconoce recursos nativos de Kubernetes.
  - El salto de 6 a 11 errores no viene de un render "mejor": viene de cómo lo usa la compuerta (por pasadas, anidado,
    con reglas y con dos instancias).
- **¿Qué es una "vuelta"?** Un ciclo completo de prueba: hago un cambio → lo pruebo → espero el resultado → leo el
  error → corrijo.
  - En el cluster: aplicar, esperar a que Crossplane intente crear en AWS (Ready o error) y leer eventos.
  - En local: correr la compuerta y leer el resultado.
  - Sí, es lo que describes: aplicar, revisar, ver que sigue fallando y volver a cambiar.
  - Los números salen de las corridas reales, cronometradas con `measure.ps1` y `observe-xr.ps1` (`results.csv`).
    - "Hoy": 3 vueltas de 127, 144 y 206 s. La 1.ª falló al componer la integración `/health` (el bloque general
      rechazó la solicitud). La 2.ª falló en AWS al crear la respuesta de la integración. La 3.ª quedó Ready.
    - "Después": 2 vueltas de compuerta, de 83 y 101 s en frío. La primera encontró errores y la segunda pasó.
      Luego vino el despliegue al cluster.
- **¿Qué es un "turno"?** Cada vez que el agente de AI procesa y responde, por ejemplo "corro `kubectl get`", "leo el
  resultado" o "corrijo el YAML". No son los mensajes de la persona: una sola petición puede generar decenas de turnos
  internos. En cada turno el modelo vuelve a procesar todo el contexto acumulado, y eso es lo que consume créditos.
  Por eso esperar al cluster es caro: cada consulta de "¿ya terminó?" es un turno completo.

### Metodología
- **¿Cuántas corridas hicieron?** Una por escenario, en 1–2 días. No hay promedios ni varianza. La diferencia es de
  órdenes de magnitud (segundos vs. minutos), así que la conclusión es robusta; los números exactos no.
- **¿No hay sesgo porque el "después" ya sabía las respuestas?** Se controló en parte: el escenario "después" partió
  de la misma versión inicial que produjo la AI en "antes". Así se compara el ciclo de corrección, no la autoría desde
  cero, que no es comparable en tiempo.
- **¿Por qué el "hoy" de la matriz no se midió en el cluster?** Desplegar 11 versiones rotas en una cuenta compartida
  ensucia y tarda. Se documentó con el comportamiento conocido de Kubernetes y Crossplane y con errores reales que sí
  ocurrieron (AccessDenied, campo requerido, colisión).
- **¿Qué no cubre la PoC?**
  - Kiro real.
  - El flujo GitOps con ArgoCD.
  - Azure Pipelines.
  - 29 de los 34 bloques generales.
  - Producción.
  - Funciones Go o KCL.
  - `crossplane-diff` y `simulate`.
- **¿Qué cuidados tuvieron en el cluster compartido?**
  - Antes de cada apply se revisaron las 4 políticas de Kyverno en Enforce.
  - Todo lleva el prefijo `poc-cli`, el label `poc.nequi.com/experiment=cli-2.5` y los tags estándar.
  - No se tocó la línea base.
  - Solo se borró lo creado por la PoC, con aprobación previa.

### Comparaciones y alternativas
- **¿No podríamos lograr casi lo mismo con la CLI 2.2 más nuestra compuerta?** Es la pregunta más difícil; responder
  con honestidad.
  - Parte de la compuerta (contrato y multi-instancia) es nuestra y en teoría podría montarse sobre el render de la
    2.2.
  - Razones para la 2.5:
    - Es la línea mantenida e independiente del core.
    - `validate` mejoró: salida JSON y recursos nativos de Kubernetes.
    - Trae el modelo de proyecto, el empaquetado y las dependencias tipadas.
    - Será donde llegue `simulate`.
  - Subir de versión cuesta poco: no exige tocar el cluster.
- **¿Cómo se compara con Terraform?**
  - Terraform tiene `plan`; Crossplane aún no lo tiene oficialmente (llega con `simulate`).
  - Crossplane reconcilia de forma continua y nunca destruye para actualizar.
  - La compuerta cubre el hueco de "probar antes de aplicar" en cuanto a qué se crea.
- **¿Upbound (la versión comercial) no trae todo esto?** Upbound tiene su CLI `up` y control planes gestionados con
  funciones de prueba y simulación. No se evaluó: requiere su plataforma. La CLI open source viene de ahí y va
  incorporando esas capacidades.
- **¿Por qué no `crossplane beta test` o un framework de tests?** La CLI 2.5 no trae tests automáticos todavía; están
  anunciados como trabajo futuro. Por eso la compuerta es nuestra.
- **¿Kyverno no detectaría los errores de negocio?** Solo al aplicar en el cluster y viendo un recurso a la vez. La
  compuerta actúa antes y ve la composición entera, incluido el orden de las pasadas y la convivencia entre dos
  instancias.

### Adopción, costo y operación
- **¿Cuánto esfuerzo es arrancar?** Poco: fijar la CLI, llevar la compuerta y el contrato al
  repo, documentar y abrir issues. El script existe, pero es de PoC: hay que endurecerlo, darle tests y empaquetarlo.
- **¿Quién mantiene las reglas?** El equipo de plataforma, con seguridad y gobierno. Cada error que llegue al cluster
  se convierte en una regla nueva.
- **¿Qué pasa con las 65 composiciones existentes?** No hay que reescribirlas: la compuerta funciona sobre
  go-templating. Se propone correrla sobre todo el catálogo para encontrar bugs.
- **¿Qué necesita cada desarrollador?** Docker, la CLI 2.5 (un binario), Python y login de lectura a ECR.
- **¿Cuánto pesa o tarda instalarlo?** La CLI es un binario único, de unos 100 MB o más. La primera vez se descargan
  las imágenes de las funciones.
- **¿Funciona con ArgoCD?** No cambia el flujo GitOps: la compuerta corre antes del PR o en CI, y Argo sigue
  desplegando igual.
- **¿Y si sale la CLI 2.6 y rompe algo?** Por eso se fija la versión. Se sube de forma controlada después de revisar
  las notas del release.
- **¿Hay que actualizar el core de Crossplane a 2.5 (noviembre de 2026)?** No es requisito para nada de esto.

### Seguridad
- **¿La compuerta toca AWS o el cluster?** No. Corre en Docker local. Solo `trace`, y la verificación final, usan el
  cluster.
- **¿Se dieron permisos nuevos?** No. Se trabajó dentro de los permisos existentes; de hecho, ese límite cambió el
  caso de Lambda a API.
- **¿Las funciones privadas salen de la red?** Se bajan de ECR con login de lectura, igual que lo hace el cluster.

### AI
- **¿Kiro podría correr la compuerta solo?** Es un siguiente paso natural: una skill o steering de Kiro que corra la
  compuerta y corrija hasta pasar, antes de proponer el PR. Hay un plan en `future/kiro-skill-plan.md`; no se ejecutó.
- **¿La AI no podría "hacer trampa" para pasar las reglas?** Las reglas viven fuera de la composición y las revisa el
  PR. Además, el cluster sigue siendo la verificación final.
- **¿La salida de la compuerta es más fácil para la AI?** Sí: 155–300 tokens con el error exacto, frente a 580–1.827
  tokens de eventos del cluster que hay que interpretar.

---

## 5. Puntos débiles y cifras que parecen inconsistentes

| Lo que alguien puede notar | Explicación |
|---|---|
| "~20 s" (slide 6), "~15 s" (slide 10), "~29 s" (evidencia), 30–112 s (matriz) | 15 s es en caliente; 15–30 s con todas las pruebas; ~29 s la demo antes y después; la matriz corrió cada defecto en frío. La primera vez son 100 s. |
| "~14 min" en la slide y "~12 min" en la wiki | 12 min hasta Ready; 14 hasta que la API responde, con el diagnóstico. |
| "~5–7 min" | Estimado con la compuerta completa. La corrida real midió ~12 min porque la colisión se escapó. |
| 4 bugs en la slide, 5 en la wiki | El 5.º es un default sorpresivo (`Observe`), no un bug. |
| "11/11 reglas" y "11/11 errores" | Son cosas distintas; la coincidencia del 11 es casual. |
| ~30 % de créditos | Estimación, no la factura de Kiro. En la corrida real fue 101 %. |
| "Hoy = 0" | Por definición: sin herramientas locales nada se detecta antes del cluster. Los 11 no se desplegaron a AWS. |
| El 11/11 lo logra "la CLI" | Lo logra la CLI más nuestra compuerta. La 2.2 ya veía los 6 errores de esquema. |
| Caso cambiado de Lambda a API | Por permisos del rol del provider; esto se puede presentar como un hallazgo. |
| Una sola corrida | Limitación declarada; la magnitud de la diferencia sostiene la conclusión. |

### Frases útiles cuando no sabes
- "Eso no lo medimos en esta PoC; lo dejo anotado como pregunta abierta."
- "Esa cifra es estimada, no medida: el modelo y sus supuestos están en `estimate_credits.py`."
- "Lo que sí puedo afirmar es…" (y volver a una cifra medida).
