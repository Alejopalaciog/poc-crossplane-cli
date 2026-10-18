import { Reveal, Scene, useScene } from 'beatdeck';
import { BarRow } from '../ui';

function Errors_() {
  const { here, b } = useScene();
  return (
    <>
      <Reveal on={here} x={156} y={150}><div className="t-eyebrow">Menos errores · 11 errores típicos inyectados</div></Reveal>
      <Reveal on={here} x={150} y={200} delay={100}>
        <div className="t-statement" style={{ fontSize: 100 }}>Detectados antes</div>
        <div className="t-statement" style={{ fontSize: 100, marginTop: 14 }}>de tocar el cluster</div>
      </Reveal>

      <BarRow on={here && b >= 0} y={490} label="Hoy" sub="solo cluster" pct={0} value="0" />
      <BarRow on={here && b >= 1} y={610} label="CLI 2.2" sub="render + validate" pct={54.5} value="6" />
      <BarRow on={here && b >= 2} y={730} label="CLI 2.5" sub="+ compuerta" pct={100} value="11" hot />

      {[
        { x: 150, t: '3 invisibles hoy', s: 'sin tag de costeo, retención de 1 día, campo ignorado' },
        { x: 720, t: 'Choques entre equipos', s: 'mismo endpoint en el mismo espacio' },
        { x: 1290, t: 'Errores de orden', s: 'un recurso antes que su dependencia' },
      ].map((c, i) => (
        <Reveal key={c.t} on={here && b >= 3} x={c.x} y={880} delay={i * 160}>
          <div style={{ fontSize: 38, fontWeight: 700 }}><span className="mag">●</span> {c.t}</div>
          <div style={{ fontSize: 24, color: 'var(--ink-2)', marginTop: 4, width: 520 }}>{c.s}</div>
        </Reveal>
      ))}
    </>
  );
}

/** 05 MENOS ERRORES — 0 / 6 / 11, una barra por beat; qué tipo de errores cambia. */
export const Errors = () => <Scene index={4}><Errors_ /></Scene>;
