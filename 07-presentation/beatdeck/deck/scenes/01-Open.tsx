import { CountUp, Reveal, Scene, useScene } from 'beatdeck';
import { config } from '../deck.config';

function Open_() {
  const { here, b, entry } = useScene();
  const title = here && b === 1;
  const kpis = here && b === 2;
  return (
    <>
      {/* 1.1 standby: una marca tranquila */}
      <div style={{ position: 'absolute', left: 952, top: 532, width: 16, height: 16, borderRadius: 8, background: 'var(--accent)',
        opacity: here && b === 0 ? 1 : 0, transition: 'opacity 400ms' }} />

      {/* 1.2 título */}
      <Reveal on={title} out={here && b > 1} x={156} y={250}>
        <div className="t-eyebrow">{config.author} · PoC 3</div>
      </Reveal>
      <Reveal on={title} out={here && b > 1} x={150} y={320} delay={120} ms={1100}>
        <div className="t-statement" style={{ fontSize: 190 }}>Crossplane</div>
        <div className="t-statement" style={{ fontSize: 190, marginTop: 18 }}><span className="mag">CLI 2.5</span> en Nequi</div>
      </Reveal>
      <Reveal on={title} out={here && b > 1} x={156} y={780} delay={420}>
        <div className="t-editorial soft" style={{ fontSize: 40 }}>¿Construimos y migramos composiciones más rápido,</div>
        <div className="t-editorial soft" style={{ fontSize: 40 }}>con menos errores y menos créditos de AI?</div>
      </Reveal>

      {/* 1.3 los tres números */}
      {[
        { x: 150, value: 11, prefix: '', suffix: '/11', label: ['errores típicos detectados', 'antes de tocar el cluster'] },
        { x: 760, value: 30, prefix: '~', suffix: ' %', label: ['de los créditos de AI', 'frente al flujo actual*'] },
        { x: 1460, value: 4, prefix: '', suffix: '', label: ['bugs ocultos en bloques', 'que ya usamos'] },
      ].map((k, i) => (
        <Reveal key={k.x} on={kpis} x={k.x} y={330} delay={i * 220}>
          <CountUp className="t-numeral" style={{ fontSize: 190, whiteSpace: 'nowrap' }} value={k.value} prefix={k.prefix} suffix={k.suffix}
            from={kpis ? 0 : undefined} entry={entry} delay={IN(i)} ms={1200} />
          <div style={{ fontSize: 34, color: 'var(--ink-2)', marginTop: 34, lineHeight: 1.3 }}>{k.label[0]}<br />{k.label[1]}</div>
        </Reveal>
      ))}
      <Reveal on={kpis} x={156} y={900} delay={900}>
        <div style={{ fontSize: 22, color: 'var(--ink-3)' }}>* estimado con datos medidos, cuando la validación local cubre el error</div>
      </Reveal>
    </>
  );
}

const IN = (i: number) => 340 + i * 220;

/** 01 INICIO — standby, título, los tres números. */
export const Open = () => <Scene index={0}><Open_ /></Scene>;
