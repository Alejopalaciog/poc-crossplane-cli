import { Reveal, Scene, useScene } from 'beatdeck';
import gate from '../assets/5.png';
import matrix from '../assets/8.png';
import trace from '../assets/7.png';
import stage from '../assets/aws2.png';
import logs from '../assets/aws4.png';
import event from '../assets/aws5.png';
import alarms from '../assets/aws6.png';
import { Shot } from '../ui';

const TITLES = [
  'La misma compuerta: rechaza "antes", aprueba "después"',
  'Matriz de detección: CLI 2.2 = 6/11 · CLI 2.5 + compuerta = 11/11',
  'Desplegado en EKS: 17 recursos Ready y la API responde HTTP 200',
  'En AWS: access logs, cifrado con llave propia, evento real y alarmas',
];

function Evidence_() {
  const { here, b } = useScene();
  const at = (k: number) => here && b === k;
  const past = (k: number) => here && b > k;
  return (
    <>
      <Reveal on={here} x={156} y={110}><div className="t-eyebrow">Evidencia · capturas reales de la PoC</div></Reveal>
      {TITLES.map((t, k) => (
        <Reveal key={t} on={at(k)} out={past(k)} x={150} y={160}>
          <div className="t-editorial" style={{ fontSize: 50 }}>{t}</div>
        </Reveal>
      ))}

      <Shot src={gate} on={at(0)} out={past(0)} x={150} y={270} w={1620} h={720} />
      <Shot src={matrix} on={at(1)} out={past(1)} x={150} y={270} w={1620} h={560} />
      <Shot src={trace} on={at(2)} out={past(2)} x={360} y={270} w={1200} h={720} />

      <Shot src={stage} on={at(3)} x={150} y={270} w={790} h={360} caption="Stage con access logs activos" />
      <Shot src={logs} on={at(3)} x={980} y={270} w={790} h={360} caption="Log group: retención y llave KMS" delay={150} />
      <Shot src={event} on={at(3)} x={150} y={700} w={790} h={300} delay={300} />
      <Shot src={alarms} on={at(3)} x={980} y={700} w={790} h={300} delay={450} />
    </>
  );
}

/** 08 EVIDENCIA — capturas reales: compuerta, matriz, EKS, AWS. */
export const Evidence = () => <Scene index={7}><Evidence_ /></Scene>;
