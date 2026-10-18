import type { SceneDef } from 'beatdeck';

/**
 * Mapa de beats. Un clic = un beat.
 * `ref` = de dónde sale (versión manual / wiki), `source` = lo que dice la fuente, `note` = ayuda al presentador.
 */
export const SCENES: SceneDef[] = [
  {
    id: '01', title: 'INICIO',
    beats: [
      { name: 'standby', note: 'Pantalla tranquila mientras la gente entra. El primer clic arranca.' },
      { name: 'título', ref: 'manual · portada', note: 'Tercera PoC de Crossplane: esta vez, la herramienta para construir y probar composiciones.' },
      { name: 'kpis', auto: true, ref: 'manual · portada', source: '11/11 errores antes del cluster · ~30 % créditos AI · 4 bugs ocultos',
        note: 'Los tres números que se llevan: menos errores, menos créditos, y bugs que ya teníamos sin saberlo. ~30 % es estimado.' },
    ],
  },
  {
    id: '02', title: 'HOY',
    beats: [
      { name: 'statement', ref: 'manual · contexto', note: 'Migramos de Terraform a Crossplane con ~65 composiciones, muchas hechas con AI.' },
      { name: 'ciclo', ref: 'manual · contexto', source: 'AI escribe → aplicar al cluster → esperar 2–3 min → leer eventos ↺',
        note: 'Cada error se descubre en AWS, después de esperar.' },
      { name: 'dolores', ref: 'manual · contexto', source: 'Lento · caro en créditos · errores invisibles',
        note: 'Invisibles: se despliega "bien" pero sin tags, con mala retención o con campos ignorados.' },
    ],
  },
  {
    id: '03', title: 'LA CLI 2.5',
    beats: [
      { name: 'pregunta', ref: 'manual · qué buscamos', note: '¿Menos errores? ¿más rápido y barato? ¿ayuda a la migración? ¿qué cuesta?' },
      { name: 'capacidades', ref: 'manual · qué trae', source: 'Previsualizar · validar · generar · empaquetar' },
      { name: 'sin actualizar', ref: '00-research', source: 'Desde v2.4 la CLI soporta core v2.3: no hay que actualizar el cluster (v2.3.3)',
        note: 'La mayoría de comandos nuevos son Beta: se fija la versión.' },
    ],
  },
  {
    id: '04', title: 'LA PRUEBA',
    beats: [
      { name: 'caso', ref: 'manual · la prueba', source: '"Necesito exponer una API con los estándares Nequi" · 17 recursos',
        note: 'La AI compone bloques generales que ya existen: API, /health, llave KMS; más logs cifrados y alarmas.' },
      { name: 'escenarios', ref: 'manual · la prueba', source: 'Hoy · CLI 2.2 · CLI 2.5 + compuerta',
        note: 'Mismo requerimiento y mismo contrato de negocio para los tres. Cluster EKS y cuenta AWS reales.' },
      { name: 'compuerta', ref: 'manual · compuerta', source: 'Simula · revisa y valida · reglas de negocio · 2 equipos · recién ahí al cluster',
        note: '~20 segundos en la máquina de la persona o de la AI, sin tocar AWS.' },
      { name: 'quién aporta', ref: 'manual · compuerta / AI + persona',
        note: 'Honestidad: la CLI aporta render y validate; las reglas de negocio y la prueba entre equipos son nuestras.' },
    ],
  },
  {
    id: '05', title: 'MENOS ERRORES',
    beats: [
      { name: 'hoy 0', ref: '02-resultados', source: 'Hoy: 0 de 11 antes del cluster', note: 'Inyectamos 11 errores típicos, uno a uno.' },
      { name: 'cli 2.2 = 6', ref: '02-resultados', source: 'CLI 2.2: 6' },
      { name: 'cli 2.5 = 11', ref: '02-resultados', source: 'CLI 2.5 + compuerta: 11 de 11' },
      { name: 'tipos', ref: '02-resultados · matriz', note: 'El salto no es en esquema (eso ya lo hacía la 2.2): es en negocio, orden y convivencia entre equipos.' },
    ],
  },
  {
    id: '06', title: 'MÁS RÁPIDO, MÁS BARATO',
    beats: [
      { name: 'vuelta', auto: true, ref: '02-resultados', source: 'cluster ~160 s · compuerta ~15 s', note: 'Medido: 127, 144 y 206 s en el cluster.' },
      { name: 'caso completo', ref: '02-resultados', source: 'Hoy ~14 min (3 vueltas) · CLI 2.5 ~5–7 min' },
      { name: 'créditos', ref: '02-resultados', source: '100 % · 77 % · ~30 % · turnos 28/22/11',
        note: 'Lo caro no es escribir: es esperar al cluster. Estimado con datos medidos, no es la factura de Kiro.' },
      { name: 'ojo', ref: '02-resultados', source: 'Un error se escapó al cluster → ~101 %',
        note: 'El ahorro existe solo si la compuerta cubre el tipo de error. Cada error nuevo se vuelve una regla.' },
    ],
  },
  {
    id: '07', title: 'HALLAZGOS',
    beats: [
      { name: '4 bugs', ref: '03-hallazgos', source: 'Roles IAM · log groups · integraciones MOCK · choque entre equipos',
        note: 'Solo revisamos 5 de 34 bloques generales: vale la pena pasar la compuerta por todo el catálogo.' },
      { name: 'migración', ref: '02-resultados · adopción', source: '10/10 claim real · 6/10 sin managementPolicies → crearía una llave nueva',
        note: 'La CLI no reemplaza la skill de adopción: le agrega un paso antes del PR.' },
    ],
  },
  {
    id: '08', title: 'EVIDENCIA',
    beats: [
      { name: 'compuerta', ref: '06-evidence E6' },
      { name: 'matriz', ref: '06-evidence E10' },
      { name: 'eks', ref: '06-evidence E8', note: '17 recursos Ready y la API respondiendo HTTP 200.' },
      { name: 'aws', ref: '06-evidence E9', note: 'Stage con access logs, log group cifrado, evento real y alarmas.' },
    ],
  },
  {
    id: '09', title: 'VEREDICTO',
    beats: [
      { name: 'balance', ref: '04-recomendaciones', note: 'Lo bueno, lo que cuesta (Python en Windows, defaults, Beta) y el ojo.' },
      { name: 'fases', ref: '04-recomendaciones', source: 'Fase 1 compuerta en repos · 2 CI + catálogo · 3 paquetes + skill Kiro · 4 funciones tipadas' },
      { name: 'frase', ref: 'manual · cierre', source: 'Probar antes de desplegar: la AI construye, la compuerta verifica, el cluster confirma.' },
    ],
  },
];
