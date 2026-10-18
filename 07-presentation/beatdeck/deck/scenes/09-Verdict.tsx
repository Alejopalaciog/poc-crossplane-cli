import { Reveal, Scene, useScene } from 'beatdeck';
import { config } from '../deck.config';

const COLS = [
  { x: 150, t: 'Lo bueno', c: 'var(--ok)', items: ['Errores detectados en segundos, sin cluster', 'Estándares de negocio ejecutables', 'Sin actualizar el cluster', 'Encontró bugs reales escondidos'] },
  { x: 700, t: 'Lo que cuesta', c: 'var(--warning)', items: ['Funciones Python no compilan en Windows (sí en WSL)', 'Defaults que no calzan con nuestro estándar', 'Bloques generales deben publicarse como paquete', 'Docker obligatorio · comandos en Beta'] },
  { x: 1250, t: 'Ojo', c: 'var(--fault)', items: ['La compuerta solo ve lo que cubre', 'Permisos reales de AWS solo se ven en el cluster', 'El cluster sigue siendo la verificación final'] },
];

const PHASES = [
  { n: '1', w: 'Sprint actual', t: 'CLI 2.5 + compuerta local en los repos', s: 'paso obligatorio antes de cada PR · corregir los 4 bugs' },
  { n: '2', w: 'Siguiente sprint', t: 'Compuerta en Azure Pipelines y en todo el catálogo', s: 'paso offline en la skill de migración Terraform → Crossplane' },
  { n: '3', w: 'Trimestre', t: 'Bloques generales como paquete + skill de Kiro', s: 'dependencias claras, autocompletado, menos créditos' },
  { n: '4', w: 'Evaluación', t: 'Funciones tipadas para composiciones grandes', s: 'cuando el equipo trabaje en WSL / devcontainer o en CI' },
];

function Verdict_() {
  const { here, b } = useScene();
  const bal = here && b === 0;
  const road = here && b === 1;
  const end = here && b === 2;
  return (
    <>
      {/* 9.1 balance */}
      <Reveal on={bal} out={here && b > 0} x={156} y={160}><div className="t-eyebrow">Balance</div></Reveal>
      {COLS.map((col, i) => (
        <Reveal key={col.t} on={bal} out={here && b > 0} x={col.x} y={230} delay={i * 180}>
          <div style={{ width: 500, borderTop: `4px solid ${col.c}`, paddingTop: 24 }}>
            <div style={{ fontSize: 60, fontWeight: 800 }}>{col.t}</div>
            {col.items.map((it) => (
              <div key={it} style={{ fontSize: 30, color: 'var(--ink-2)', marginTop: 26, lineHeight: 1.3 }}>{it}</div>
            ))}
          </div>
        </Reveal>
      ))}

      {/* 9.2 fases */}
      <Reveal on={road} out={here && b > 1} x={156} y={130}><div className="t-eyebrow">Veredicto: sí, por fases</div></Reveal>
      {PHASES.map((p, i) => (
        <Reveal key={p.n} on={road} out={here && b > 1} x={150} y={200 + i * 200} delay={i * 170}>
          <div style={{ display: 'flex', gap: 46, alignItems: 'flex-start' }}>
            <div className="t-numeral" style={{ fontSize: 150, width: 110 }}>{p.n}</div>
            <div style={{ paddingTop: 6 }}>
              <div className="t-meta" style={{ fontSize: 22, color: 'var(--accent-strong)' }}>{p.w}</div>
              <div style={{ fontSize: 50, fontWeight: 700, marginTop: 4 }}>{p.t}</div>
              <div style={{ fontSize: 28, color: 'var(--ink-2)', marginTop: 4 }}>{p.s}</div>
            </div>
          </div>
        </Reveal>
      ))}

      {/* 9.3 frase final */}
      <Reveal on={end} x={156} y={220}><div className="t-eyebrow">En una frase</div></Reveal>
      <Reveal on={end} x={150} y={300} delay={100}>
        <div className="t-statement mag" style={{ fontSize: 130 }}>Probar antes de desplegar.</div>
      </Reveal>
      {['La AI construye,', 'la compuerta verifica,', 'el cluster confirma.'].map((l, i) => (
        <Reveal key={l} on={end} x={150} y={470 + i * 120} delay={400 + i * 250}>
          <div className="t-statement" style={{ fontSize: 100 }}>{l}</div>
        </Reveal>
      ))}
      <Reveal on={end} x={156} y={940} delay={1300}>
        <div className="t-meta" style={{ fontSize: 22 }}>{config.author} · repo poc-crossplane-cli · wiki 08-wiki</div>
      </Reveal>
    </>
  );
}

/** 09 VEREDICTO — balance, fases, frase final. */
export const Verdict = () => <Scene index={8}><Verdict_ /></Scene>;
