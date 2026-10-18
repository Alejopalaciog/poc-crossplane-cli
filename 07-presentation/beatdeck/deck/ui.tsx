import { EASE, IN_DELAY, Reveal } from 'beatdeck';

/** Fila de barra horizontal (una serie, magnitud): etiqueta · pista · valor. La barra crece al aparecer. */
export function BarRow({ on, y, label, sub, pct, value, hot = false, delay = 0 }: {
  on: boolean; y: number; label: string; sub?: string; pct: number; value: React.ReactNode; hot?: boolean; delay?: number;
}) {
  const d = IN_DELAY + delay;
  return (
    <>
      <Reveal on={on} x={150} y={y - 6} delay={delay}>
        <div style={{ fontSize: 44, fontWeight: 700, lineHeight: 1 }}>{label}</div>
        {sub && <div style={{ fontSize: 24, color: 'var(--ink-2)', marginTop: 8 }}>{sub}</div>}
      </Reveal>
      <div style={{ position: 'absolute', left: 600, top: y, width: 980, height: 44, background: 'rgba(255,255,255,0.08)',
        borderRadius: 4, opacity: on ? 1 : 0, transition: `opacity 400ms ${EASE} ${on ? d : 0}ms` }}>
        <div style={{ height: '100%', width: on ? `${pct}%` : '0%', borderRadius: '0 4px 4px 0',
          background: hot ? 'var(--accent)' : 'rgba(255,233,245,0.42)',
          transition: on ? `width 1100ms ${EASE} ${d + 150}ms` : 'width 200ms' }} />
      </div>
      <Reveal on={on} x={1620} y={y - 18} delay={delay + 300}>
        <div className="t-numeral" style={{ fontSize: 80, color: hot ? 'var(--accent-strong)' : 'var(--ink)' }}>{value}</div>
      </Reveal>
    </>
  );
}

/** Captura real (evidencia), encajada en una caja fija del escenario. */
export function Shot({ src, on, out, x, y, w, h, caption, delay = 0 }: {
  src: string; on: boolean; out?: boolean; x: number; y: number; w: number; h: number; caption?: string; delay?: number;
}) {
  return (
    <Reveal on={on} out={out} x={x} y={y} delay={delay}>
      <div style={{ width: w, height: h, border: '1px solid var(--hair-strong)', borderRadius: 10, background: '#0d000d',
        display: 'flex', alignItems: 'center', justifyContent: 'center', overflow: 'hidden', padding: 10 }}>
        <img src={src} alt={caption ?? ''} style={{ maxWidth: '100%', maxHeight: '100%', objectFit: 'contain', display: 'block' }} />
      </div>
      {caption && <div style={{ fontSize: 26, color: 'var(--ink-2)', marginTop: 14, width: w }}>{caption}</div>}
    </Reveal>
  );
}

/** Ítem con punto de acento: título + texto. */
export function Item({ on, x, y, title, text, w = 760, tone = 'var(--accent)', delay = 0 }: {
  on: boolean; x: number; y: number; title: string; text?: string; w?: number; tone?: string; delay?: number;
}) {
  return (
    <Reveal on={on} x={x} y={y} delay={delay}>
      <div style={{ width: w, display: 'flex', gap: 22 }}>
        <div style={{ flex: 'none', width: 16, height: 16, borderRadius: 8, background: tone, marginTop: 14 }} />
        <div>
          <div style={{ fontSize: 40, fontWeight: 700, lineHeight: 1.15 }}>{title}</div>
          {text && <div style={{ fontSize: 28, color: 'var(--ink-2)', marginTop: 6, lineHeight: 1.3 }}>{text}</div>}
        </div>
      </div>
    </Reveal>
  );
}
