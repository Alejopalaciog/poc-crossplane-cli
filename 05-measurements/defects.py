"""Matriz de detección de defectos: ¿en qué momento se detecta cada error típico?

Inyecta 10 defectos (uno a la vez) sobre la composición/XR aprobados del caso API y mide:
  - Antes-2  : CLI 2.2 → render (con observados fijos) + beta validate (solo nivel plataforma)
  - Después  : compuerta local CLI 2.5 (render simulado + anidado + validate + contrato)
La columna "solo cluster" (Antes-1) no se ejecuta 10 veces en AWS: se documenta con base en el
comportamiento de Kubernetes/Crossplane y en los errores reales vistos en esta PoC.

Salida: 05-measurements/defects.csv y tabla en consola.
"""

import csv
import os
import platform
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXE = ".exe" if platform.system() == "Windows" else ""
PY = sys.executable
PROJ = ROOT / "04-after-cli-2.5" / "project"
COMP = PROJ / "apis" / "xpoccliapiservices" / "composition.yaml"
XR = PROJ / "examples" / "xr.yaml"
WORK = ROOT / "05-measurements" / "gate-out" / "defects"

# (id, descripción, tipo, archivo, buscar, reemplazar, detección "solo cluster", base de esa afirmación)
DEFECTS = [
    ("D01", "Campo con nombre errado en un bloque general (endpointTypes)", "Esquema", "comp",
     "endpointType: REGIONAL", "endpointTypes: REGIONAL",
     "Nunca: el API server poda el campo desconocido en silencio y se usa el default",
     "Poda de campos desconocidos en CRDs estructurales"),
    ("D02", "Tipo errado en recurso AWS (threshold texto)", "Esquema", "comp",
     "threshold: {{ $a.threshold }}", 'threshold: "{{ $a.threshold }} ms"',
     "Runtime (minutos): 'cannot apply composed resource' en eventos",
     "Mismo patrón que el error real 'field not declared' de aws-cloudwatch"),
    ("D03", "Falta un campo requerido del bloque general (confidentiality)", "Esquema", "comp",
     "                confidentiality: {{ $c.confidentiality }}\n", "",
     "Runtime (~1 min): '... is invalid: Required value'",
     "Visto en la iteración 1 de Antes-1 (integrationUri)"),
    ("D04", "Valor fuera de catálogo en la solicitud (country: colombia)", "Esquema", "xr",
     "country: co", "country: colombia",
     "Inmediato al aplicar el XR (validación del XRD en el API server)",
     "Validación OpenAPI del XRD"),
    ("D05", "Plantilla go-template rota (falta {{- end }})", "Sintaxis", "comp",
     "            {{- end }}\n\n    # ============================================================\n    # Step 3",
     "\n    # ============================================================\n    # Step 3",
     "Runtime: la composición se acepta y falla al reconciliar (función)",
     "kubectl apply no ejecuta las plantillas"),
    ("D06", "Falta el tag serviceid en el stage", "Negocio", "comp",
     '{{- $tags := merge (dict "serviceid" $p.serviceid "capacity"', '{{- $tags := merge (dict "capacity"',
     "Nunca: se despliega sin el tag (gobierno/costeo)",
     "AWS no exige tags"),
    ("D07", "Retención de logs de 1 día", "Negocio", "comp",
     "{{- $retention := 14 }}", "{{- $retention := 1 }}",
     "Nunca: se despliega con 1 día de retención",
     "Valor válido para AWS"),
    ("D08", "Nombre de alarma sin 'cbo' (guardarraíl IAM)", "Negocio/Entorno", "comp",
     "crossplane.io/external-name: alarm-{{ $base }}-{{ $a.id }}", "crossplane.io/external-name: alerta-api-{{ $a.id }}",
     "Runtime (minutos): AccessDenied de AWS",
     "Visto en la 1.ª corrida (iam:CreatePolicy / kms:CreateAlias)"),
    ("D09", "apiVersion errada en un bloque general (v1alpha2)", "Esquema", "comp",
     "apiVersion: aws.platform.nequi.com/v1alpha1\n            kind: XKMS", "apiVersion: aws.platform.nequi.com/v1alpha2\n            kind: XKMS",
     "Runtime: 'no matches for kind' al componer",
     "Discovery del API server"),
    ("D10", "Stage emitido sin esperar el deployment (referencia rota)", "Lógica", "comp",
     "{{- if and $deploymentId $logsReady }}", "{{- if $logsReady }}",
     "Runtime (minutos): error de AWS por deploymentId vacío",
     "AWS rechaza CreateStage sin deployment"),
    ("D11", "Claves de recursos no únicas por instancia (colisión entre APIs)", "Lógica/Multi-equipo", "comp",
     "                  health-{{ $p.functionality }}:\n                    parentId: {{ $rootId }}\n"
     "                    pathPart: health\n                apiResources:\n"
     "                  health-get-{{ $p.functionality }}:\n                    resourceId: \"@health-{{ $p.functionality }}\"",
     "                  health:\n                    parentId: {{ $rootId }}\n"
     "                    pathPart: health\n                apiResources:\n"
     "                  health-get:\n                    resourceId: \"@health\"",
     "Runtime (minutos): 'Only one reference can have Controller set to true' cuando un 2.º equipo despliega",
     "Visto en esta PoC al desplegar Después junto a Antes-1"),
]


def run(cmd, cwd=ROOT):
    t = time.time()
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", cwd=cwd,
                       env={**os.environ, "PYTHONIOENCODING": "utf-8"})
    return p.returncode, p.stdout + p.stderr, time.time() - t


def before2(comp, xr):
    """CLI 2.2: render con observados fijos + beta validate (sin anidado ni contrato)."""
    crank = ROOT / "tools" / f"crank-2.2.6{EXE}"
    rc, out, t1 = run([str(crank), "render", str(xr), str(comp), str(ROOT / "03-before-2-cli-2.2" / "functions.yaml"),
                       "-o", str(PROJ / "examples" / "observed.yaml"), "-x"])
    if rc != 0:
        return "render", t1, out.strip().splitlines()[-1][:160]
    f = WORK / "b2-render.yaml"
    f.write_text(out, encoding="utf-8")
    rc, vout, t2 = run([str(crank), "beta", "validate", str(ROOT / "04-after-cli-2.5" / "extensions"), str(f)])
    errs = [l for l in vout.splitlines() if l.startswith("[x]") or "could not find" in l]
    return ("validate" if rc != 0 or errs else "no detectado"), t1 + t2, (errs[0][:160] if errs else "")


def after(comp, xr):
    rc, out, t = run([PY, str(ROOT / "05-measurements" / "local_gate.py"), "--xr", str(xr), "--composition", str(comp),
                      "--functions", str(PROJ / "examples" / "functions.yaml"),
                      "--nested-functions", str(ROOT / "04-after-cli-2.5" / "general-audit" / "functions-api.yaml"),
                      "--extensions", str(ROOT / "04-after-cli-2.5" / "extensions"),
                      "--contract", str(ROOT / "05-measurements" / "business_checks_api.py"), "--out", str(WORK / "gate"),
                      "--multi-instance"])
    fails = [l for l in out.splitlines() if " FALLA " in l]
    if rc == 0:
        return "no detectado", t, ""
    stage = fails[0].split("  ")[0].strip() if fails else "compuerta"
    detail = next((l.strip() for l in out.splitlines() if l.strip().startswith(("[x]", "FAIL"))), fails[0] if fails else "")
    return stage, t, re.sub(r"\s+", " ", detail)[:160]


def main():
    WORK.mkdir(parents=True, exist_ok=True)
    base_comp, base_xr = COMP.read_text(encoding="utf-8"), XR.read_text(encoding="utf-8")
    rows = []
    for did, desc, kind, target, find, repl, cluster, basis in DEFECTS:
        comp_txt, xr_txt = base_comp, base_xr
        if target == "comp":
            assert find in comp_txt, f"{did}: patrón no encontrado"
            comp_txt = comp_txt.replace(find, repl, 1)
        else:
            assert find in xr_txt, f"{did}: patrón no encontrado"
            xr_txt = xr_txt.replace(find, repl, 1)
        comp_f, xr_f = WORK / f"{did}-composition.yaml", WORK / f"{did}-xr.yaml"
        comp_f.write_text(comp_txt, encoding="utf-8")
        xr_f.write_text(xr_txt, encoding="utf-8")
        b2, b2t, b2d = before2(comp_f, xr_f)
        a, at, ad = after(comp_f, xr_f)
        rows.append({"id": did, "defecto": desc, "tipo": kind, "solo_cluster": cluster, "base_cluster": basis,
                     "antes2_detecta": b2, "antes2_seg": round(b2t, 1), "antes2_detalle": b2d,
                     "despues_detecta": a, "despues_seg": round(at, 1), "despues_detalle": ad})
        print(f"{did} | 2.2: {b2:<14} ({b2t:5.1f}s) | 2.5: {a:<40} ({at:5.1f}s) | {desc}")
    with open(ROOT / "05-measurements" / "defects.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    d2 = sum(r["antes2_detecta"] != "no detectado" for r in rows)
    d5 = sum(r["despues_detecta"] != "no detectado" for r in rows)
    print(f"\nDetectados antes del cluster: CLI 2.2 = {d2}/{len(rows)} · CLI 2.5 + compuerta = {d5}/{len(rows)}")


if __name__ == "__main__":
    main()
