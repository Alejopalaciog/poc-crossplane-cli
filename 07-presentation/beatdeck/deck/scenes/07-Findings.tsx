import { Reveal, Scene, useScene } from 'beatdeck';
import { Item } from '../ui';

const BUGS = [
  { t: 'Roles IAM', s: 'envía un valor vacío a AWS: no se puede crear un rol sin boundary' },
  { t: 'Log groups', s: 'usa un campo que no existe: no se pueden crear log groups nuevos' },
  { t: 'Integraciones', s: 'no soporta integraciones de prueba (MOCK)' },
  { t: 'Choque entre equipos', s: 'dos APIs con el mismo endpoint en el mismo espacio colisionan' },
];

const ROLES = [
  { t: 'Equipos de producto', s: 'ven qué recursos AWS crearía su solicitud antes de pedirla' },
  { t: 'Revisores de PR', s: 'revisan un resultado claro, no cientos de líneas de plantilla' },
  { t: 'Seguridad y gobierno', s: 'estándares que se ejecutan en cada cambio, no un documento' },
  { t: 'Plataforma / SRE', s: 'árbol completo de recursos y auditoría de los bloques generales' },
  { t: 'Migración', s: 'menos riesgo de recrear o borrar recursos existentes' },
  { t: 'Agentes AI', s: 'feedback corto y claro: menos turnos, menos créditos' },
];

function Findings_() {
  const { here, b } = useScene();
  const bugs = here && b === 0;
  const adopt = here && b === 1;
  const adoptOut = here && b > 1;
  const roles = here && b >= 2;
  return (
    <>
      {/* 7.1 bugs ocultos */}
      <Reveal on={bugs} out={here && b > 0} x={156} y={150}><div className="t-eyebrow">Hallazgo inesperado</div></Reveal>
      <Reveal on={bugs} out={here && b > 0} x={150} y={200} delay={100}>
        <div className="t-statement" style={{ fontSize: 130 }}><span className="mag">4 bugs ocultos</span></div>
        <div className="t-editorial" style={{ fontSize: 52, marginTop: 20 }}>en bloques generales que ya usamos — y la CLI 2.5 los encuentra sin desplegar</div>
      </Reveal>
      {BUGS.map((g, i) => (
        <Item key={g.t} on={bugs} x={i % 2 ? 1000 : 150} y={530 + Math.floor(i / 2) * 170} title={g.t} text={g.s} delay={300 + i * 150} />
      ))}
      <Reveal on={bugs} out={here && b > 0} x={150} y={900} delay={900}>
        <div style={{ fontSize: 24, color: 'var(--ink-3)' }}>Solo se revisaron 5 de 34 bloques generales: vale la pena pasar la compuerta por todo el catálogo.</div>
      </Reveal>

      {/* 7.2 migración */}
      <Reveal on={adopt} out={adoptOut}x={156} y={150}><div className="t-eyebrow">Migración Terraform → Crossplane</div></Reveal>
      <Reveal on={adopt} out={adoptOut}x={150} y={200} delay={100}>
        <div className="t-statement" style={{ fontSize: 110 }}>Evita el error más caro:</div>
        <div className="t-statement mag" style={{ fontSize: 110, marginTop: 14 }}>crear en vez de adoptar.</div>
      </Reveal>
      <Reveal on={adopt} out={adoptOut}x={150} y={520} delay={300}>
        <div className="t-numeral" style={{ fontSize: 190, color: 'var(--ok)' }}>10/10</div>
        <div style={{ fontSize: 32, color: 'var(--ink-2)', marginTop: 30 }}>claim real de adopción: correcto</div>
      </Reveal>
      <Reveal on={adopt} out={adoptOut}x={750} y={520} delay={550}>
        <div className="t-numeral" style={{ fontSize: 190, color: 'var(--fault)' }}>6/10</div>
        <div style={{ fontSize: 32, color: 'var(--ink-2)', marginTop: 30, width: 600, lineHeight: 1.3 }}>si la AI olvida una línea, <b style={{ color: 'var(--ink)' }}>crearía una llave nueva</b> con permiso de borrar</div>
      </Reveal>
      <Reveal on={adopt} out={adoptOut}x={1380} y={540} delay={800}>
        <div style={{ width: 390, borderLeft: '2px solid var(--accent)', paddingLeft: 24 }}>
          <div style={{ fontSize: 30, fontWeight: 700 }}>Detectado offline, en ~4 s, antes del PR</div>
          <div style={{ fontSize: 24, color: 'var(--ink-2)', marginTop: 10, lineHeight: 1.35 }}>La CLI no reemplaza la skill de adopción: le agrega un paso antes de desplegar.</div>
        </div>
      </Reveal>

      {/* 7.3 valor por rol */}
      <Reveal on={roles} x={156} y={150}><div className="t-eyebrow">No solo para quien crea composiciones</div></Reveal>
      <Reveal on={roles} x={150} y={200} delay={100}>
        <div className="t-statement" style={{ fontSize: 110 }}>Valor por <span className="mag">rol</span></div>
      </Reveal>
      {ROLES.map((r, i) => (
        <Item key={r.t} on={roles} x={150 + (i % 3) * 560} y={420 + Math.floor(i / 3) * 260} w={500}
          title={r.t} text={r.s} tone={i === ROLES.length - 1 ? 'var(--accent-strong)' : 'var(--accent)'} delay={250 + i * 120} />
      ))}
    </>
  );
}

/** 07 HALLAZGOS — bugs ocultos y migración. */
export const Findings = () => <Scene index={6}><Findings_ /></Scene>;
