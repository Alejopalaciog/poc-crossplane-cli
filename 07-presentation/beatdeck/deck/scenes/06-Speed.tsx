import { CountUp, Reveal, Scene, useScene } from 'beatdeck';
import { BarRow } from '../ui';

function Speed_() {
  const { here, b, entry } = useScene();
  const lap = here && b === 0;
  const whole = here && b === 1;
  const credits = here && b >= 2;
  return (
    <>
      <Reveal on={here && b <= 1} out={here && b > 1} x={156} y={170}><div className="t-eyebrow">Más rápido</div></Reveal>

      {/* 6.1 una vuelta */}
      <Reveal on={lap} out={here && b > 0} x={150} y={300}>
        <CountUp className="t-numeral" style={{ fontSize: 230, color: 'var(--ink-2)' }} value={160} prefix="~" suffix=" s"
          from={lap ? 0 : undefined} entry={entry} delay={340} ms={1400} />
        <div style={{ fontSize: 36, color: 'var(--ink-2)', marginTop: 40 }}>una vuelta en el cluster</div>
        <div style={{ fontSize: 24, color: 'var(--ink-3)', marginTop: 8 }}>medido: 127, 144 y 206 s</div>
      </Reveal>
      <Reveal on={lap} out={here && b > 0} x={1000} y={300} delay={300}>
        <CountUp className="t-numeral" style={{ fontSize: 230 }} value={15} prefix="~" suffix=" s"
          from={lap ? 0 : undefined} entry={entry} delay={640} ms={900} />
        <div style={{ fontSize: 36, marginTop: 40 }}>una vuelta en la compuerta local</div>
        <div style={{ fontSize: 24, color: 'var(--ink-3)', marginTop: 8 }}>15–30 s · 100 s la primera vez, descargando imágenes</div>
      </Reveal>

      {/* 6.2 el caso completo */}
      <Reveal on={whole} out={here && b > 1} x={150} y={300}>
        <div className="t-numeral" style={{ fontSize: 180, color: 'var(--ink-2)', whiteSpace: 'nowrap' }}>~14 min</div>
        <div style={{ fontSize: 36, color: 'var(--ink-2)', marginTop: 40 }}>hoy: 3 vueltas en el cluster</div>
      </Reveal>
      <Reveal on={whole} out={here && b > 1} x={1000} y={300} delay={250}>
        <div className="t-numeral" style={{ fontSize: 180, whiteSpace: 'nowrap' }}>~5–7 min</div>
        <div style={{ fontSize: 36, marginTop: 40 }}>CLI 2.5: 2 vueltas locales + 1 despliegue</div>
      </Reveal>

      {/* 6.3 créditos */}
      <Reveal on={credits} x={156} y={150}><div className="t-eyebrow">Menos créditos de AI · estimado</div></Reveal>
      <Reveal on={credits} x={150} y={200} delay={100}>
        <div className="t-statement" style={{ fontSize: 96 }}>Lo caro no es escribir:</div>
        <div className="t-statement mag" style={{ fontSize: 96, marginTop: 14 }}>es esperar al cluster.</div>
      </Reveal>
      <BarRow on={credits} y={480} label="Hoy" sub="28 turnos de la AI" pct={100} value="100 %" />
      <BarRow on={credits} y={600} label="CLI 2.2" sub="22 turnos" pct={77} value="77 %" delay={200} />
      <BarRow on={credits} y={720} label="CLI 2.5" sub="11 turnos" pct={30} value="~30 %" hot delay={400} />

      {/* 6.4 ojo */}
      <Reveal on={here && b >= 3} x={150} y={860}>
        <div style={{ borderLeft: '6px solid var(--warning)', paddingLeft: 26, width: 1620 }}>
          <div style={{ fontSize: 34, fontWeight: 700 }}>Ojo: cuando un error se escapó al cluster, el costo volvió a ~101 %.</div>
          <div style={{ fontSize: 26, color: 'var(--ink-2)', marginTop: 6 }}>El ahorro existe solo si la compuerta cubre el tipo de error: cada error nuevo se vuelve una regla.</div>
        </div>
      </Reveal>
    </>
  );
}

/** 06 MÁS RÁPIDO, MÁS BARATO — vuelta, caso completo, créditos, ojo. */
export const Speed = () => <Scene index={5}><Speed_ /></Scene>;
