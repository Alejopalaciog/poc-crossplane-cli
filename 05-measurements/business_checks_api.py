"""Contrato de negocio ejecutable para XPocCliApiService (API Service Platform).

Lee la salida de `crossplane composition render` (YAML multi-documento) y verifica las
reglas API-00..API-10 de 01-requirement/README.md (sección 6). Sin cluster ni AWS.

Uso:
    crossplane composition render xr.yaml composition.yaml [fns] -x | python business_checks_api.py -
    python business_checks_api.py render-output.yaml [--json]

Exit code 0 si todas las reglas pasan, 1 si alguna falla.
"""

import argparse
import json
import sys

import yaml

IDENTITY = ("serviceid", "capacity", "country", "env")
LOW_ENVS = {"dev", "qa", "sbx", "stg"}
XR_CHILDREN = {"XAPIGatewayRestStack", "XAPIGatewayIntegration", "XKMS"}
CREATE_OK = ({"*"}, {"Observe", "Create", "Update", "LateInitialize"})


def load_docs(path):
    stream = sys.stdin if path == "-" else open(path, encoding="utf-8")
    with stream:
        return [d for d in yaml.safe_load_all(stream) if isinstance(d, dict)]


def walk(value, path=""):
    if isinstance(value, dict):
        for k, v in value.items():
            yield from walk(v, f"{path}.{k}" if path else k)
    elif isinstance(value, list):
        for i, v in enumerate(value):
            yield from walk(v, f"{path}[{i}]")
    else:
        yield path, value


def params(doc):
    return (doc.get("spec") or {}).get("parameters") or {}


def fp(doc):
    return (doc.get("spec") or {}).get("forProvider") or {}


def check(docs):
    xr = next((d for d in docs if d.get("kind") == "XPocCliApiService"), None)
    xp = params(xr) if xr else {}
    env = xp.get("env", "")
    children = [d for d in docs if d is not xr]
    kinds = {}
    for c in children:
        kinds.setdefault(c.get("kind"), []).append(c)
    results = []

    def add(rule, ok, detail):
        results.append({"rule": rule, "ok": bool(ok), "detail": detail})

    # API-00 render íntegro
    bad = [f"{d.get('kind')}:{p}" for d in docs for p, v in walk(d) if isinstance(v, str) and "<no value>" in v]
    add("API-00 render íntegro", not bad, ", ".join(bad) or "sin <no value>")

    # API-01 identidad en todos los hijos (XR: parámetros; MR: tags)
    missing = []
    for c in children:
        src = params(c) if c.get("kind") in XR_CHILDREN else (fp(c).get("tags") or {})
        if c.get("kind") in ("XAPIGatewayIntegration", "Deployment"):
            continue  # sin campos de identidad/tags en AWS: heredan de la API y del stage
        missing += [f"{c['kind']}.{k}" for k in IDENTITY if not src.get(k)]
        if src.get("deployment", "jarvis") != "jarvis":
            missing.append(f"{c['kind']}.deployment")
    add("API-01 identidad y tags", children and not missing, ", ".join(missing) or f"{len(children)} hijos OK")

    # API-02 nombres compatibles con guardarraíl IAM (*cbo*)
    names = []
    for k in kinds.get("XKMS", []):
        p = params(k)
        names.append(("alias", f"alias-{p.get('capacity')}-{p.get('country')}-{(p.get('key') or {}).get('name')}-{p.get('env')}"))
    for g in kinds.get("Group", []):
        names.append(("log group", (g["metadata"].get("annotations") or {}).get("crossplane.io/external-name", "")))
    for a in kinds.get("MetricAlarm", []):
        names.append(("alarma", (a["metadata"].get("annotations") or {}).get("crossplane.io/external-name", a["metadata"]["name"])))
    wrong = [f"{t}={n}" for t, n in names if "cbo" not in n]
    add("API-02 guardarraíl 'cbo'", names and not wrong, ", ".join(wrong) or f"{len(names)} nombres OK")

    # API-03 / API-04 log group
    groups = kinds.get("Group", [])
    if groups:
        g = fp(groups[0])
        need = 14 if env in LOW_ENVS else 90
        add("API-03 retención logs", g.get("retentionInDays", 0) >= need, f"{g.get('retentionInDays')} días (mínimo {need} en {env})")
        add("API-04 logs cifrados", bool(g.get("kmsKeyId")), g.get("kmsKeyId") or "sin kmsKeyId")
    else:
        add("API-03 retención logs", False, "log group aún no emitido (¿llave lista?)")
        add("API-04 logs cifrados", False, "log group aún no emitido")

    # API-05 rotación CMK
    kms = kinds.get("XKMS", [])
    rot = bool(kms) and (params(kms[0]).get("key") or {}).get("enableKeyRotation") is True
    add("API-05 rotación CMK", rot, "enableKeyRotation=true" if rot else "sin rotación o sin XKMS")

    # API-06 API regional + clasificación
    api = kinds.get("XAPIGatewayRestStack", [])
    if api:
        p = params(api[0])
        cls = [k for k in ("confidentiality", "integrity", "availability") if not p.get(k)] + ([] if "pci" in p else ["pci"])
        add("API-06 regional + clasificación", p.get("endpointType", "REGIONAL") == "REGIONAL" and not cls,
            f"endpoint={p.get('endpointType', 'REGIONAL')} faltan={cls or 'ninguno'}")
    else:
        add("API-06 regional + clasificación", False, "no hay XAPIGatewayRestStack")

    # API-07 alarmas
    alarms = kinds.get("MetricAlarm", [])
    metrics = {fp(a).get("metricName") for a in alarms}
    dims_ok = all({"ApiName", "Stage"} <= set((fp(a).get("dimensions") or {}).keys()) for a in alarms)
    if alarms or kinds.get("Stage"):
        add("API-07 alarmas 5XX + latencia", {"5XXError", "Latency"} <= metrics and dims_ok, f"métricas={sorted(m for m in metrics if m)} dimensiones={'OK' if dims_ok else 'incompletas'}")
    else:
        add("API-07 alarmas 5XX + latencia", True, "aún no emitidas (esperan el stage) — correcto")

    # API-08 cuenta/región
    pcs, regions = set(), set()
    for c in children:
        if c.get("kind") in XR_CHILDREN:
            pcs.add((params(c).get("providerConfigRef") or {}).get("name"))
            regions.add(params(c).get("region", "us-east-1"))
        else:
            pcs.add((c.get("spec", {}).get("providerConfigRef") or {}).get("name"))
            regions.add(fp(c).get("region"))
    add("API-08 cuenta/región", len(pcs) == 1 and len(regions) == 1, f"providerConfig={pcs} región={regions}")

    # API-09 stage con access logs al log group de la plataforma
    stages = kinds.get("Stage", [])
    if stages:
        als = fp(stages[0]).get("accessLogSettings") or {}
        als = (als[0] if als else {}) if isinstance(als, list) else als
        dest = als.get("destinationArn", "")
        lg = (groups[0]["metadata"].get("annotations") or {}).get("crossplane.io/external-name", "") if groups else "?"
        add("API-09 access logs", dest.endswith(f"log-group:{lg}"), dest or "stage sin accessLogSettings")
    else:
        add("API-09 access logs", True, "stage aún no emitido (espera integración y logs) — correcto")

    # API-10 sin referencias rotas + políticas que permitan crear
    problems = []
    for i in kinds.get("XAPIGatewayIntegration", []):
        p = params(i)
        if not p.get("apiId"):
            problems.append("integración sin apiId")
        if set(p.get("managementPolicies") or ["Observe"]) not in CREATE_OK:
            problems.append(f"integración con managementPolicies={p.get('managementPolicies') or 'default Observe'} (no crearía)")
    for s in stages:
        if not fp(s).get("deploymentId") and not fp(s).get("deploymentIdRef"):
            problems.append("stage sin deployment")
    add("API-10 sin referencias rotas", not problems, ", ".join(problems) or "OK")
    return results


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path", help="salida de render ('-' para stdin)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    results = check(load_docs(args.path))
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        for r in results:
            print(f"{'PASS' if r['ok'] else 'FAIL'}  {r['rule']:<32} {r['detail']}")
        print(f"\n{sum(r['ok'] for r in results)}/{len(results)} reglas de negocio cumplidas")
    sys.exit(0 if all(r["ok"] for r in results) else 1)


if __name__ == "__main__":
    main()
