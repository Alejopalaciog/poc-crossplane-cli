import { Reveal, Scene, useScene } from 'beatdeck';

const CAPS = [
  { x: 150, y: 300, t: 'Previsualizar', s: 'render: qué crearía en AWS, sin desplegar' },
  { x: 1000, y: 300, t: 'Validar', s: 'validate: contra los esquemas reales de AWS' },
  { x: 150, y: 560, t: 'Generar', s: 'XRD desde un esquema simple · funciones Python/Go' },
  { x: 1000, y: 560, t: 'Empaquetar', s: 'paquete versionado y Crossplane local en un comando' },
];

function Cli_() {
  const { here, b } = useScene();
  const caps = here && b >= 1;
  return (
    <>
      {/* 3.1 pregunta */}
      <Reveal on={here && b === 0} out={here && b > 0} x={150} y={270}>
        <div className="t-statement" style={{ fontSize: 150 }}>¿Y si pudiéramos</div>
        <div className="t-statement" style={{ fontSize: 150, marginTop: 20 }}>probar <span className="mag">antes</span></div>
        <div className="t-statement" style={{ fontSize: 150, marginTop: 20 }}>de desplegar?</div>
      </Reveal>

      {/* 3.2 qué trae la CLI 2.5 */}
      <Reveal on={caps} x={156} y={200}><div className="t-eyebrow">Qué trae la CLI 2.5</div></Reveal>
      {CAPS.map((c, i) => (
        <Reveal key={c.t} on={caps} x={c.x} y={c.y} delay={i * 160}>
          <div className="t-statement" style={{ fontSize: 96 }}>{c.t}</div>
          <div style={{ fontSize: 30, color: 'var(--ink-2)', marginTop: 16, width: 720 }}>{c.s}</div>
        </Reveal>
      ))}

      {/* 3.3 sin actualizar el cluster */}
      <Reveal on={here && b >= 2} x={150} y={850}>
        <div style={{ borderLeft: '6px solid var(--accent)', paddingLeft: 26 }}>
          <div style={{ fontSize: 44, fontWeight: 700 }}>Funciona con nuestro Crossplane v2.3.3: <span className="mag">no hay que actualizar el cluster.</span></div>
          <div style={{ fontSize: 24, color: 'var(--ink-3)', marginTop: 8 }}>v2.3 may-2026 · v2.4 jun independiente del core · v2.5 ago · comandos nuevos en Beta</div>
        </div>
      </Reveal>
    </>
  );
}

/** 03 LA CLI 2.5 — la pregunta y lo que trae. */
export const Cli = () => <Scene index={2}><Cli_ /></Scene>;
