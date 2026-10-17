"""Contrato de negocio ejecutable para XPocCliLambdaService.

Lee la salida de `crossplane composition render` (YAML multi-documento) y
verifica las reglas BR-01..BR-10 de 01-requirement/README.md sobre los XRs
compuestos. No necesita cluster ni AWS.

Uso:
    crossplane composition render xr.yaml composition.yaml | python business_checks.py -
    python business_checks.py render-output.yaml [--json]

Exit code 0 si todas las reglas pasan, 1 si alguna falla.
"""

import argparse
import json
import sys

import yaml

REQUIRED_TAGS = ("serviceid", "capacity", "country", "env")
LOW_ENVS = {"dev", "qa", "sbx", "stg"}
PLATFORM_KINDS = {"XKMS", "XCLOUDWATCH", "XIAM", "XSecurityGroup", "XLambda"}


def load_docs(path):
    stream = sys.stdin if path == "-" else open(path, encoding="utf-8")
    with stream:
        return [d for d in yaml.safe_load_all(stream) if isinstance(d, dict)]


def params(doc):
    return (doc.get("spec") or {}).get("parameters") or {}


def check(docs):
    xr = next((d for d in docs if d.get("kind") == "XPocCliLambdaService"), None)
    children = [d for d in docs if d.get("kind") in PLATFORM_KINDS]
    by_kind = {}
    for c in children:
        by_kind.setdefault(c["kind"], []).append(c)
    xr_params = params(xr) if xr else {}
    env = xr_params.get("env", "")
    results = []

    def add(rule, ok, detail):
        results.append({"rule": rule, "ok": bool(ok), "detail": detail})

    # BR-01 tags/identidad en todos los hijos
    missing = []
    for c in children:
        p = params(c)
        for t in REQUIRED_TAGS:
            if not p.get(t):
                missing.append(f"{c['kind']}.{t}")
        if p.get("deployment", "jarvis") != "jarvis":
            missing.append(f"{c['kind']}.deployment")
    add("BR-01 identidad y tags", not missing and children, ", ".join(missing) or f"{len(children)} hijos OK")

    # BR-02 naming estándar
    bad = [c["kind"] for c in children if c["kind"] != "XKMS" and params(c).get("standardName") is False]
    add("BR-02 naming estándar", not bad, ", ".join(bad) or "standardName en todos")

    # BR-03 / BR-04 log group
    cw = by_kind.get("XCLOUDWATCH", [])
    if not cw:
        add("BR-03 retención logs", False, "no hay XCLOUDWATCH")
        add("BR-04 logs cifrados", False, "no hay XCLOUDWATCH")
    else:
        lg = params(cw[0]).get("logGroup") or {}
        ret = lg.get("retentionInDays", 0)
        need = 14 if env in LOW_ENVS else 90
        add("BR-03 retención logs", ret >= need, f"{ret} días (mínimo {need} en {env or '?'})")
        add("BR-04 logs cifrados", bool(lg.get("kmsKeyId")), lg.get("kmsKeyId") or "sin kmsKeyId (¿llave aún no lista?)")

    # BR-05 rotación KMS
    kms = by_kind.get("XKMS", [])
    rot = bool(kms) and (params(kms[0]).get("key") or {}).get("enableKeyRotation") is True
    add("BR-05 rotación CMK", rot, "enableKeyRotation=true" if rot else "sin rotación o sin XKMS")

    # BR-06 mínimo privilegio IAM
    iam = by_kind.get("XIAM", [])
    if not iam:
        add("BR-06 mínimo privilegio", False, "no hay XIAM")
    else:
        p = params(iam[0])
        problems = []
        trust = json.loads((p.get("role") or {}).get("assumeRolePolicy") or "{}")
        principals = {
            s.get("Principal", {}).get("Service")
            for s in trust.get("Statement", [])
        }
        if principals != {"lambda.amazonaws.com"}:
            problems.append(f"trust={principals}")
        for pol in p.get("policies") or []:
            doc = json.loads(pol.get("policy") or "{}")
            for s in doc.get("Statement", []):
                res = s.get("Resource")
                res = res if isinstance(res, list) else [res]
                if "*" in res:
                    problems.append(f"{pol.get('name')}: Resource '*'")
        add("BR-06 mínimo privilegio", not problems, ", ".join(problems) or "trust lambda + recursos acotados")

    # BR-07 guardarraíles de costo
    lam = by_kind.get("XLambda", [])
    lp = (xr_params.get("lambda") or {})
    mem, tout = lp.get("memorySize", 128), lp.get("timeout", 15)
    if lam:
        mem, tout = params(lam[0]).get("memorySize", mem), params(lam[0]).get("timeout", tout)
    add("BR-07 guardarraíles costo", 128 <= mem <= 1024 and tout <= 60, f"memoria={mem}MB timeout={tout}s")

    # BR-08 providerConfig y región consistentes
    pcs = {(params(c).get("providerConfigRef") or {}).get("name") for c in children}
    regions = {params(c).get("region", "us-east-1") for c in children}
    add("BR-08 cuenta/región", len(pcs) == 1 and len(regions) == 1, f"providerConfig={pcs} región={regions}")

    # BR-09 VPC / SG
    vpc_on = (xr_params.get("vpc") or {}).get("enabled", False)
    sgs = by_kind.get("XSecurityGroup", [])
    if not vpc_on:
        add("BR-09 red", not sgs, "sin VPC y sin SG" if not sgs else "SG creado sin VPC")
    else:
        open_ingress = [
            r for sg in sgs for r in params(sg).get("ingressRules") or []
            if "0.0.0.0/0" in (r.get("cidrBlocks") or [])
        ]
        add("BR-09 red", sgs and not open_ingress, f"{len(sgs)} SG, ingress abierto={len(open_ingress)}")

    # BR-10 sin referencias rotas
    if lam:
        role_arn = params(lam[0]).get("roleArn", "")
        add("BR-10 sin referencias rotas", role_arn.startswith("arn:aws:iam::"), f"roleArn={role_arn or 'VACÍO'}")
    else:
        add("BR-10 sin referencias rotas", True, "XLambda aún no emitida (espera roleArn) — correcto")

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
            print(f"{'PASS' if r['ok'] else 'FAIL'}  {r['rule']:<28} {r['detail']}")
        passed = sum(r["ok"] for r in results)
        print(f"\n{passed}/{len(results)} reglas de negocio cumplidas")
    sys.exit(0 if all(r["ok"] for r in results) else 1)


if __name__ == "__main__":
    main()
