import { defineDeck } from 'beatdeck';
import '../themes/nequi.css';
import { config } from './deck.config';
import { SCENES } from './scenes';
import { Open } from './scenes/01-Open';
import { Today } from './scenes/02-Today';
import { Cli } from './scenes/03-Cli';
import { Test } from './scenes/04-Test';
import { Errors } from './scenes/05-Errors';
import { Speed } from './scenes/06-Speed';
import { Findings } from './scenes/07-Findings';
import { Evidence } from './scenes/08-Evidence';
import { Verdict } from './scenes/09-Verdict';

/** Todas las capas del escenario, de atrás hacia adelante. Todas quedan montadas; cada una se muestra en su escena. */
function Stage() {
  return (
    <>
      <Open />
      <Today />
      <Cli />
      <Test />
      <Errors />
      <Speed />
      <Findings />
      <Evidence />
      <Verdict />
    </>
  );
}

export default defineDeck({
  id: 'crossplane-cli-2-5-en-nequi',
  title: config.title,
  lang: 'es',
  scenes: SCENES,
  Stage,
  fonts: ['400 100px "Poppins"', '700 100px "Poppins"', '800 100px "Poppins"', '400 32px "JetBrains Mono Variable"'],
  qrUrl: config.qrUrl,
});
