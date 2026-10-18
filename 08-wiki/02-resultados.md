# 02 · Resultados consolidados

## KPIs principales
| Indicador | Antes-1 (hoy) | Antes-2 (CLI 2.2) | Después (CLI 2.5 + compuerta) |
|---|---|---|---|
| Errores detectados antes de tocar el cluster (de 11) | 0 | 6 | **11** |
| Errores que nunca se detectan (llegan a AWS "bien" pero mal) | 3 | 3 | **0** |
| Tiempo por vuelta de validación | 2 – 3,5 min (cluster) | ~5–20 s local + cluster | **15 – 30 s** local |
| Vueltas en el cluster hasta Ready (caso API) | 3 (~12 min) | 2 (estimado) | 1 con compuerta completa · 2 medidas* |
| Créditos AI relativos (estimados) | 100 % | 77 % | **~30 %** (101 %*) |
| Turnos de la AI (estimados) | 28 | 22 | **11** (31*) |
| Bugs latentes en bloques generales detectados offline | — | 1 de 4 | **4 de 4** |

\* *Medido tal como ocurrió*: la colisión multi-instancia no estaba cubierta por la primera versión de la compuerta y se
descubrió en el cluster; al agregar la prueba multi-instancia se detecta localmente (D11). Muestra el principio clave:
**el ahorro depende de que la compuerta cubra el tipo de error**.

## Línea de tiempo medida (caso API)
| Escenario | Autoría | Validación local | Cluster | Total hasta API respondiendo |
|---|---|---|---|---|
| Antes-1 | ~2 min | — | 3 ciclos: 127 s + 144 s + 206 s, más diagnóstico manual (describe/eventos) | ~14 min |
| Después | ~1 min (SimpleSchema + scaffold) | 2 vueltas: 83 s + 101 s (en frío; en caliente 15 s) | 197 s + 2 ciclos por la colisión (132 s + 138 s) | ~12 min medido · **~5–7 min** con compuerta completa (1 ciclo de cluster) |

## Matriz de defectos (`05-measurements/defects.csv`)
| ID | Defecto | Solo cluster (hoy) | CLI 2.2 | CLI 2.5 + compuerta |
|---|---|---|---|---|
| D01 | Campo con nombre errado en bloque general | **Nunca** (se poda en silencio) | validate | validate |
| D02 | Tipo errado en recurso AWS | Runtime (minutos) | validate | validate |
| D03 | Falta campo requerido de bloque general | Runtime (~1 min) | validate | validate |
| D04 | Valor fuera de catálogo en la solicitud | Inmediato | validate | validate |
| D05 | Plantilla rota | Runtime | render | render |
| D06 | Falta tag `serviceid` | **Nunca** | ✗ | contrato de negocio |
| D07 | Retención de logs de 1 día | **Nunca** | ✗ | contrato de negocio |
| D08 | Nombre sin `cbo` (guardarraíl IAM) | Runtime (AccessDenied) | ✗ | contrato de negocio |
| D09 | apiVersion errada en bloque general | Runtime | validate | render anidado |
| D10 | Recurso emitido antes que su dependencia | Runtime (minutos) | ✗ | validate de pasadas intermedias |
| D11 | Nombres no únicos por instancia (colisión entre equipos) | Runtime, cuando llega el 2.º equipo | ✗ | prueba multi-instancia |

**Lectura:** la CLI 2.2 ya detectaba los errores de esquema; el salto de la 2.5 + compuerta está en los errores **de
negocio, de orden y de convivencia entre equipos**, que hoy llegan a AWS.

## Créditos AI (`05-measurements/credits.json`)
Modelo: cada turno del agente procesa contexto base + historial + salida nueva. Supuestos: contexto base 15.000 tokens,
consulta al cluster cada 30 s, 2 turnos de diagnóstico por error, corrección = 25 % de la composición.
| Escenario | Turnos | Tokens procesados | Relativo | Espera en cluster |
|---|---|---|---|---|
| Antes-1 | 28 | 757.920 | 100 % | 8,0 min |
| Antes-2 | 22 | 582.389 | 77 % | 5,8 min |
| Después medido | 31 | 766.627 | 101 % | 7,8 min |
| Después con compuerta completa | 11 | 228.593 | **30 %** | 2,3 min |

El feedback del cluster (eventos/describe) pesa 580–1.827 tokens por lectura; el de la compuerta, 155–300.

## Adopción (migración Terraform → Crossplane)
| Prueba | Resultado | Tiempo |
|---|---|---|
| Claim real `adopt-kms-test` (reglas de oro de la skill) | 10/10 | ~5 s |
| Mismo claim sin `managementPolicies` (error típico al editar) | 6/10: **sin external-name → crearía una llave nueva** | ~4 s |

## Despliegue real (EKS + AWS)
| Recurso | Antes (`cbopoccli1`) | Después (`cbopoccli2`) |
|---|---|---|
| XR | Ready | Ready (17 recursos, `resource trace`) |
| API `/health` | HTTP 200 | HTTP 200 (~0,3 s) |
| Access logs | — | Activos, cifrados con CMK propia, retención 14 días |
| Alarmas 5XX / latencia | Creadas | OK |
| Llave KMS | Rotación activa | Rotación activa |

## Variante Python (función embebida con modelos tipados)
- Equivalente funcional a go-templating: misma compuerta, 8 recursos, 11/11 reglas.
- Build: **falla en Windows**, funciona en Linux/WSL (~3 min la primera vez). `render` no la puede compilar en <60 s:
  se resolvió reutilizando la imagen de `project build`.
- Corre en un Crossplane real (`project run` en KIND): compone los XRs hijos.

## Evidencias
Ver `06-evidence/README.md` (E1–E10) y `img/`.
