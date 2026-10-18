import { Arrow, NodeBox, Reveal, Scene, useScene, type Rect } from 'beatdeck';

const Y = 470, H = 120;
const NODES: { r: Rect; kind: string; value: string; tone?: 'ghost' | 'hot' }[] = [
  { r: { x: 150, y: Y, w: 330, h: H }, kind: 'paso 1', value: 'AI escribe' },
  { r: { x: 560, y: Y, w: 400, h: H }, kind: 'paso 2', value: 'Aplicar al cluster' },
  { r: { x: 1040, y: Y, w: 340, h: H }, kind: 'paso 3', value: 'Esperar 2–3 min' },
  { r: { x: 1460, y: Y, w: 310, h: H }, kind: 'paso 4', value: 'Leer eventos', tone: 'ghost' },
];

function Today_() {
  const { here, b } = useScene();
  const cycle = here && b >= 1;
  const pains = here && b >= 2;
  return (
    <>
      {/* 2.1 statement */}
      <Reveal on={here && b === 0} out={here && b > 0} x={150} y={250}>
        <div className="t-statement" style={{ fontSize: 150 }}>Hoy, para saber</div>
        <div className="t-statement" style={{ fontSize: 150, marginTop: 20 }}>si algo funciona,</div>
        <div className="t-statement mag" style={{ fontSize: 150, marginTop: 20 }}>hay que desplegarlo.</div>
      </Reveal>

      {/* 2.2 el ciclo */}
      <Reveal on={cycle} x={156} y={300}><div className="t-eyebrow">El ciclo de hoy</div></Reveal>
      <Reveal on={cycle} x={150} y={340} delay={100}>
        <div className="t-editorial" style={{ fontSize: 56 }}>Cada error se descubre en AWS, después de esperar.</div>
      </Reveal>
      {NODES.map((n, i) => (
        <NodeBox key={n.value} rect={n.r} on={cycle} kind={n.kind} value={n.value} tone={n.tone} delay={i * 160} />
      ))}
      {NODES.slice(1).map((n, i) => (
        <Arrow key={n.value} from={NODES[i].r} to={n.r} on={cycle} delay={200 + i * 160} />
      ))}
      <Arrow from={{ x: 1615, y: Y + H + 8 }} to={{ x: 760, y: Y + H + 8 }} on={cycle} tone="hot" flow
        label="↺ corregir y volver a aplicar" ly={44} delay={900} />

      {/* 2.3 los dolores */}
      {[
        { x: 150, t: 'Lento', s: 'minutos por vuelta, en el cluster compartido' },
        { x: 720, t: 'Caro', s: 'la AI gasta créditos esperando y leyendo eventos' },
        { x: 1290, t: 'Invisible', s: 'algunos errores no fallan: quedan desplegados' },
      ].map((p, i) => (
        <Reveal key={p.t} on={pains} x={p.x} y={790} delay={i * 180}>
          <div style={{ fontSize: 60, fontWeight: 800 }} className="mag">{p.t}</div>
          <div style={{ fontSize: 26, color: 'var(--ink-2)', width: 480, marginTop: 6, lineHeight: 1.3 }}>{p.s}</div>
        </Reveal>
      ))}
    </>
  );
}

/** 02 HOY — desplegar para saber; el ciclo; lento, caro, invisible. */
export const Today = () => <Scene index={1}><Today_ /></Scene>;
