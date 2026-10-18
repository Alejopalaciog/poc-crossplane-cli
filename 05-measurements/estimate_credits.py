"""Estimación de créditos de AI (Kiro) por escenario, a partir de datos MEDIDOS en la PoC.

Los créditos de un agente son proporcionales a los tokens que procesa en cada turno:
cada turno re-envía el contexto acumulado (system/steering + archivos + conversación) más
lo nuevo (salida de herramientas). Por eso lo que más pesa NO es escribir la composición,
sino CUÁNTOS TURNOS hace el agente esperando y diagnosticando en el cluster.

Datos medidos (results.csv): iteraciones, segundos de cada ciclo en cluster, tokens de
feedback (eventos/describe vs. salida de la compuerta), tokens de los archivos.
Supuestos (explícitos, ajustables abajo): contexto base, intervalo de sondeo del agente,
turnos de diagnóstico por error en cluster.

Salida: tabla en consola + 05-measurements/credits.json (para las gráficas).
"""

import csv
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
M = ROOT / "05-measurements"

# ---------------- Supuestos (ajustables) ----------------
BASE_CONTEXT = 15_000        # system prompt + steering + skill + requerimiento (tokens por turno)
POLL_EVERY_S = 30            # el agente consulta el cluster cada 30 s mientras espera
POLL_OUTPUT = 150            # tokens de salida de un `kubectl get` de estado
DIAG_TURNS_PER_ERROR = 2     # describe + eventos para encontrar la causa raíz en cluster
DIAG_OUTPUT = 900            # tokens de un describe/eventos útil (medido: 580–1.827)
FIX_OUTPUT_RATIO = 0.25      # una corrección reescribe ~25 % de la composición
CHARS_PER_TOKEN = 4


def tokens_of(path):
    return math.ceil(Path(path).read_text(encoding="utf-8").__len__() / CHARS_PER_TOKEN)


def rows():
    with open(M / "results.csv", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


class Agent:
    """Acumula turnos: cada turno cuesta contexto acumulado + entrada nueva."""

    def __init__(self, name):
        self.name, self.history, self.turns, self.total, self.wait_s = name, 0, 0, 0, 0

    def turn(self, new_tokens, label=""):
        self.turns += 1
        self.total += BASE_CONTEXT + self.history + new_tokens
        self.history += new_tokens

    def cluster_cycle(self, seconds, feedback_tokens, failed):
        self.wait_s += seconds
        self.turn(60, "apply")
        for _ in range(max(1, math.ceil(seconds / POLL_EVERY_S))):
            self.turn(POLL_OUTPUT, "poll")
        if failed:
            self.turn(feedback_tokens, "feedback")
            for _ in range(DIAG_TURNS_PER_ERROR - 1):
                self.turn(DIAG_OUTPUT, "diagnóstico")


def main():
    r = rows()
    comp_before = tokens_of(ROOT / "02-before-1-yaml" / "api" / "composition.yaml")
    xrd_before = tokens_of(ROOT / "02-before-1-yaml" / "api" / "xrd.yaml")
    schema_after = tokens_of(ROOT / "04-after-cli-2.5" / "project" / "apis" / "xpoccliapiservices" / "schema.yaml")
    comp_after = tokens_of(ROOT / "04-after-cli-2.5" / "project" / "apis" / "xpoccliapiservices" / "composition.yaml")
    lookup = next(int(x["output_tokens_est"]) for x in r if x["step"] == "lookup-crd-fields")

    # Ciclos en cluster medidos (caso API)
    b1 = [x for x in r if x["scenario"] == "before-1" and x["step"] == "observe-cluster" and "API" in x["note"]]
    af = [x for x in r if x["scenario"] == "after" and x["step"] == "observe-cluster"]
    gate_it = [x for x in r if x["scenario"] == "after" and x["step"] == "local-gate" and "iteracion" in x["note"]]

    # --- Antes-1: AI + YAML, valida aplicando al cluster ---
    a1 = Agent("Antes-1 (YAML + cluster)")
    a1.turn(lookup, "explain CRDs")
    a1.turn(comp_before + xrd_before, "escribe XRD+composition")
    for i, c in enumerate(b1):
        failed = c["exit_code"] != "0"
        a1.cluster_cycle(float(c["duration_s"]), int(c["output_tokens_est"]), failed)
        if failed:
            a1.turn(int(comp_before * FIX_OUTPUT_RATIO), "corrige")

    # --- Antes-2: + CLI 2.2 render/validate (sin anidado): detecta 1 de los 2 problemas localmente ---
    a2 = Agent("Antes-2 (CLI 2.2 local + cluster)")
    a2.turn(lookup, "explain CRDs")
    a2.turn(comp_before + xrd_before, "escribe")
    a2.turn(400, "render+validate local (falla integrationUri)")
    a2.turn(int(comp_before * FIX_OUTPUT_RATIO), "corrige")
    a2.turn(300, "render+validate OK")
    # el bug de uri:null (composición general) solo aparece en cluster → 2 ciclos
    for c in b1[1:]:
        failed = c["exit_code"] != "0"
        a2.cluster_cycle(float(c["duration_s"]), int(c["output_tokens_est"]), failed)
        if failed:
            a2.turn(int(comp_before * FIX_OUTPUT_RATIO), "corrige")

    # --- Después: CLI 2.5 (SimpleSchema + compuerta local) + 1 despliegue ---
    d = Agent("Después (CLI 2.5 + compuerta)")
    d.turn(schema_after, "escribe SimpleSchema (XRD generado)")
    d.turn(comp_after, "escribe composition")
    for g in gate_it:
        d.turn(int(g["output_tokens_est"]), "compuerta local")
        if g["exit_code"] != "0":
            d.turn(int(comp_after * FIX_OUTPUT_RATIO), "corrige")
    # despliegue: con la compuerta v2 (multi-instancia) basta 1 ciclo; se usa el ciclo exitoso medido
    ok_cycle = next(c for c in af if c["exit_code"] == "0")
    d.cluster_cycle(float(ok_cycle["duration_s"]), 0, False)

    # --- Después tal como ocurrió (compuerta v1: la colisión se vio en cluster) ---
    d_real = Agent("Después medido (compuerta v1)")
    d_real.turn(schema_after, "SimpleSchema")
    d_real.turn(comp_after, "composition")
    for g in gate_it:
        d_real.turn(int(g["output_tokens_est"]), "compuerta")
        if g["exit_code"] != "0":
            d_real.turn(int(comp_after * FIX_OUTPUT_RATIO), "corrige")
    for c in af:
        failed = c["exit_code"] != "0"
        d_real.cluster_cycle(float(c["duration_s"]), int(c["output_tokens_est"]), failed)
        if failed:
            d_real.turn(int(comp_after * FIX_OUTPUT_RATIO), "corrige")

    agents = [a1, a2, d_real, d]
    base = a1.total
    print(f"{'Escenario':<36} {'Turnos':>6} {'Tokens procesados':>18} {'Créditos rel.':>13} {'Espera cluster':>15}")
    out = []
    for a in agents:
        rel = round(100 * a.total / base)
        print(f"{a.name:<36} {a.turns:>6} {a.total:>18,} {rel:>12}% {a.wait_s / 60:>13.1f} min")
        out.append({"escenario": a.name, "turnos": a.turns, "tokens": a.total, "creditos_relativos": rel,
                    "espera_cluster_min": round(a.wait_s / 60, 1)})
    supuestos = {k: v for k, v in globals().items() if k.isupper() and k not in ("ROOT", "M")}
    (M / "credits.json").write_text(json.dumps({"escenarios": out, "supuestos": supuestos}, ensure_ascii=False, indent=2),
                                    encoding="utf-8")
    print("\nSupuestos:", supuestos)


if __name__ == "__main__":
    main()
