"""Verificación offline de un claim de ADOPCIÓN (flujo Terraform -> Crossplane).

Se ejecuta sobre la salida de `crossplane composition render` ANTES de llevar el claim
a Git/ArgoCD. Complementa las skills de tscbo_developerkit_Tool (discover / gap /
preflight), que trabajan sobre el estado del cluster DESPUÉS del apply.

Reglas (las mismas "reglas de oro" de adoption-conventions.md, verificables sin cluster):
  AD-01  Ningún managed resource lleva Delete ni "*" en managementPolicies
  AD-02  Todos los managed resources heredan la política del claim (propagación en cadena)
  AD-03  Todo managed resource tiene crossplane.io/external-name (no intentará crear)
  AD-04  Ningún campo quedó con "<no value>" (render go-template fallido, no solo tags)
  AD-05  deployment=jarvis en los tags de cada recurso

Uso:
    crossplane composition render claim.yaml composition.yaml fns.yaml -x | python adoption_checks.py -
"""

import json
import sys

import yaml


def walk(value, path=""):
    if isinstance(value, dict):
        for k, v in value.items():
            yield from walk(v, f"{path}.{k}" if path else k)
    elif isinstance(value, list):
        for i, v in enumerate(value):
            yield from walk(v, f"{path}[{i}]")
    else:
        yield path, value


def main():
    src = sys.stdin if sys.argv[1] == "-" else open(sys.argv[1], encoding="utf-8")
    docs = [d for d in yaml.safe_load_all(src) if isinstance(d, dict)]
    claim = next((d for d in docs if "crossplane.io/composite" not in (d.get("metadata", {}).get("labels") or {})), docs[0])
    claim_policy = (claim.get("spec", {}).get("parameters") or {}).get("managementPolicies")
    mrs = [d for d in docs if d is not claim and ".m.upbound.io/" in d.get("apiVersion", "")]

    results = []
    for mr in mrs:
        name = f"{mr['kind']}/{mr['metadata']['name']}"
        pol = mr.get("spec", {}).get("managementPolicies")
        ext = (mr["metadata"].get("annotations") or {}).get("crossplane.io/external-name")
        tags = (mr.get("spec", {}).get("forProvider") or {}).get("tags") or {}
        no_value = [p for p, v in walk(mr) if isinstance(v, str) and "<no value>" in v]
        results += [
            ("AD-01 sin Delete", name, bool(pol) and "Delete" not in pol and "*" not in pol, f"policies={pol}"),
            ("AD-02 propagación", name, pol == claim_policy, f"claim={claim_policy} mr={pol}"),
            ("AD-03 external-name", name, bool(ext), ext or "SIN external-name -> intentará CREAR"),
            ("AD-04 render íntegro", name, not no_value, ", ".join(no_value) or "ok"),
            ("AD-05 deployment=jarvis", name, tags.get("deployment") == "jarvis" or not tags, f"deployment={tags.get('deployment')}"),
        ]

    for rule, name, ok, detail in results:
        print(f"{'PASS' if ok else 'FAIL'}  {rule:<24} {name:<55} {detail}")
    failed = [r for r in results if not r[2]]
    print(f"\n{len(results) - len(failed)}/{len(results)} verificaciones OK sobre {len(mrs)} managed resources")
    if "--json" in sys.argv:
        print(json.dumps([dict(zip(("rule", "resource", "ok", "detail"), r)) for r in results], ensure_ascii=False))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
