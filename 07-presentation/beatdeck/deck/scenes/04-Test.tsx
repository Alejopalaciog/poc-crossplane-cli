import { Arrow, NodeBox, Reveal, Scene, useScene, type Rect } from 'beatdeck';

const ROWS = [
  { t: 'Hoy', s: 'AI + YAML → aplicar al cluster y leer eventos' },
  { t: 'CLI 2.2', s: 'previsualizar y validar básico, luego cluster' },
  { t: 'CLI 2.5', s: 'compuerta local completa, luego cluster', hot: true },
];

const GY = 420, GH = 120, GW = 236, GAP = 42;
const GATE: { kind: string; value: string; cap: string; tone?: 'hot' }[] = [
  { kind: '1', value: 'AI escribe', cap: 'la composición' },
  { kind: '2', value: 'Simula', cap: 'el despliegue paso a paso' },
  { kind: '3', value: 'Valida', cap: 'bloques + esquemas AWS' },
  { kind: '4', value: 'Negocio', cap: 'tags, cifrado, naming' },
  { kind: '5', value: '2 equipos', cap: 'sin choques entre sí' },
  { kind: '✓', value: 'Cluster', cap: 'recién ahí', tone: 'hot' },
];
const rect = (i: number): Rect => ({ x: 150 + i * (GW + GAP), y: GY, w: GW, h: GH });

function Test_() {
  const { here, b } = useScene();
  const gate = here && b >= 2;
  return (
    <>
      {/* 4.1 el caso */}
      <Reveal on={here && b === 0} out={here && b > 0} x={156} y={260}><div className="t-eyebrow">El caso</div></Reveal>
      <Reveal on={here && b === 0} out={here && b > 0} x={150} y={320} delay={100}>
        <div className="t-statement" style={{ fontSize: 120 }}>“Necesito exponer una API</div>
        <div className="t-statement" style={{ fontSize: 120, marginTop: 20 }}>con los <span className="mag">estándares Nequi</span>”</div>
        <div style={{ fontSize: 34, color: 'var(--ink-2)', marginTop: 60 }}>API · /health · llave KMS · logs cifrados · alarmas — 17 recursos, EKS y AWS reales</div>
      </Reveal>

      {/* 4.2 tres formas de trabajar */}
      <Reveal on={here && b === 1} out={here && b > 1} x={156} y={250}><div className="t-eyebrow">Mismo requerimiento, tres formas de trabajar</div></Reveal>
      {ROWS.map((r, i) => (
        <Reveal key={r.t} on={here && b === 1} out={here && b > 1} x={150} y={340 + i * 170} delay={i * 160}>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: 50 }}>
            <div className={r.hot ? 'mag' : ''} style={{ fontSize: 76, fontWeight: 800, width: 380 }}>{r.t}</div>
            <div style={{ fontSize: 40, color: r.hot ? 'var(--ink)' : 'var(--ink-2)' }}>{r.s}</div>
          </div>
        </Reveal>
      ))}

      {/* 4.3 la compuerta */}
      <Reveal on={gate} x={150} y={200}>
        <div className="t-statement" style={{ fontSize: 100 }}>Una compuerta local</div>
        <div style={{ fontSize: 36, color: 'var(--ink-2)', marginTop: 18 }}>~20 segundos en la máquina de la persona o de la AI, sin tocar AWS</div>
      </Reveal>
      {GATE.map((g, i) => (
        <NodeBox key={g.value} rect={rect(i)} on={gate} kind={g.kind} value={g.value} tone={g.tone} delay={i * 140} />
      ))}
      {GATE.slice(1).map((g, i) => <Arrow key={g.value} from={rect(i)} to={rect(i + 1)} on={gate} delay={150 + i * 140} gap={4} />)}
      {GATE.map((g, i) => (
        <Reveal key={g.cap} on={gate} x={rect(i).x} y={GY + GH + 20} delay={300 + i * 140}>
          <div style={{ fontSize: 22, color: 'var(--ink-2)', width: GW, lineHeight: 1.3 }}>{g.cap}</div>
        </Reveal>
      ))}

      {/* 4.4 quién aporta qué */}
      {[
        { x: 150, t: 'Lo aporta la CLI', s: 'previsualizar —incluso los bloques internos y funciones privadas— y validar contra los esquemas de AWS' },
        { x: 1000, t: 'Lo aportamos nosotros', s: 'el estándar Nequi como reglas que se ejecutan, y la prueba de convivencia entre equipos' },
      ].map((c, i) => (
        <Reveal key={c.t} on={here && b >= 3} x={c.x} y={720} delay={i * 200}>
          <div style={{ width: 770, borderTop: '2px solid var(--accent)', paddingTop: 22 }}>
            <div style={{ fontSize: 44, fontWeight: 700 }}>{c.t}</div>
            <div style={{ fontSize: 28, color: 'var(--ink-2)', marginTop: 10, lineHeight: 1.35 }}>{c.s}</div>
          </div>
        </Reveal>
      ))}
    </>
  );
}

/** 04 LA PRUEBA — caso, escenarios, compuerta. */
export const Test = () => <Scene index={3}><Test_ /></Scene>;
