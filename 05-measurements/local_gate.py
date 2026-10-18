"""Compuerta local de calidad para composiciones Crossplane (CLI 2.5), sin cluster ni AWS.

1. Simula la reconciliación: renderiza en pasadas sucesivas; en cada pasada marca lo
   emitido como "observado" (Ready + IDs/ARNs ficticios) para que se ejecuten las
   etapas que esperan dependencias. Termina cuando el conjunto de recursos se estabiliza.
2. Render anidado: cada XR hijo se renderiza con su composición general (mismo método).
3. `crossplane resource validate` de TODO lo emitido contra providers + XRDs.
4. Contrato de negocio (opcional) sobre el render de la plataforma.

Salida compacta (pensada para que la lea una persona o un agente AI con pocos créditos).

Uso:
  python local_gate.py --xr X --composition C --functions F --extensions DIR \
      [--general-dir DIR] [--nested-functions F2] [--contract business_checks_api.py] [--out DIR]
"""

import argparse
import os
import platform
import subprocess
import sys
import time
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
XP = ROOT / "tools" / ("crossplane-2.5.0.exe" if platform.system() == "Windows" else "crossplane-2.5.0")

# XR general -> carpeta de su composición en el repo de composiciones generales
GENERAL = {
    "XAPIGatewayRestStack": "apigateway-rest",
    "XAPIGatewayIntegration": "apigateway-integration",
    "XAPIGatewayDeployment": "apigateway-deployment",
    "XKMS": "kms",
    "XIAM": "iam",
    "XCLOUDWATCH": "cloudwatch",
    "XLambda": "lambda",
    "XSecurityGroup": "securitygroup",
}
FAKE_ATPROVIDER = {
    "id": "fake0id001", "arn": "arn:aws:fake:us-east-1:000000000000:fake/fake",
    "restApiId": "fakeapi001", "rootResourceId": "fakeroot01", "keyArn": "arn:aws:kms:us-east-1:000000000000:key/fake",
    "roleArn": "arn:aws:iam::000000000000:role/fake", "securityGroupId": "sg-fake0001",
    "executionArn": "arn:aws:execute-api:us-east-1:000000000000:fakeapi001", "invokeUrl": "https://fake",
    "logGroupName": "/fake", "lambdaFunctionArn": "arn:aws:lambda:us-east-1:000000000000:function:fake",
    "deploymentId": "fakedep001", "stageId": "fakestage1", "name": "fake",
}


def load(text):
    return [d for d in yaml.safe_load_all(text) if isinstance(d, dict)]


def render(xr, composition, functions, observed, workdir):
    cmd = [str(XP), "composition", "render", str(xr), str(composition), str(functions), "-x"]
    if observed:
        cmd += ["-o", str(observed)]
    out = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", cwd=workdir)
    return out.returncode, out.stdout, out.stderr.strip()


def as_observed(doc):
    md = doc.get("metadata", {})
    obs = {
        "apiVersion": doc["apiVersion"], "kind": doc["kind"],
        "metadata": {k: v for k, v in md.items() if k in ("name", "namespace", "annotations", "labels")},
        "status": {
            "conditions": [
                {"type": "Ready", "status": "True", "reason": "Available", "lastTransitionTime": "2026-01-01T00:00:00Z"},
                {"type": "Synced", "status": "True", "reason": "ReconcileSuccess", "lastTransitionTime": "2026-01-01T00:00:00Z"},
            ],
            "atProvider": dict(FAKE_ATPROVIDER),
        },
    }
    if "spec" in doc:
        obs["spec"] = doc["spec"]
    return obs


def simulate(xr, composition, functions, workdir, tmp, label, max_passes=8):
    """Devuelve (ok, docs_finales, pasadas, error)."""
    observed_file = tmp / f"{label}-observed.yaml"
    observed_file.unlink(missing_ok=True)
    previous = None
    for n in range(1, max_passes + 1):
        rc, out, err = render(xr, composition, functions, observed_file if observed_file.exists() else None, workdir)
        if rc != 0:
            return False, [], n, err.splitlines()[-1] if err else f"render rc={rc}"
        docs = load(out)
        composed = [d for d in docs[1:] if d.get("apiVersion") != "render.crossplane.io/v1beta1"]
        key = sorted(f"{d['kind']}/{d['metadata'].get('name')}" for d in composed)
        if key == previous:
            return True, docs, n, ""
        previous = key
        observed_file.write_text(yaml.safe_dump_all([as_observed(d) for d in composed], sort_keys=False), encoding="utf-8")
    return True, docs, max_passes, "no convergió (revisar dependencias circulares)"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--xr", required=True)
    ap.add_argument("--composition", required=True)
    ap.add_argument("--functions", required=True)
    ap.add_argument("--extensions", required=True, help="dir con providers.yaml + XRDs")
    ap.add_argument("--general-dir", default=str(ROOT.parent / "local-argocd-crossplane-config" / "platform" / "aws_xrds"))
    ap.add_argument("--nested-functions", help="functions para composiciones generales (incluye privadas)")
    ap.add_argument("--contract", help="script de contrato de negocio")
    ap.add_argument("--out", default=str(ROOT / "05-measurements" / "gate-out"))
    args = ap.parse_args()

    workdir = Path.cwd()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    rows, failed = [], False

    def row(stage, ok, detail, secs):
        nonlocal failed
        failed |= not ok
        rows.append((stage, ok, detail, secs))

    # 1. Plataforma
    t = time.time()
    ok, docs, passes, err = simulate(Path(args.xr), Path(args.composition), Path(args.functions), workdir, out, "platform")
    platform_docs = docs
    row("render plataforma (simulado)", ok, f"{passes} pasadas, {max(len(docs) - 1, 0)} recursos" if ok else err, time.time() - t)
    (out / "platform-render.yaml").write_text(yaml.safe_dump_all(docs, sort_keys=False), encoding="utf-8")
    all_docs = list(docs[1:])

    # 2. Render anidado de cada XR general
    for child in [d for d in docs[1:] if d.get("kind") in GENERAL]:
        comp = Path(args.general_dir) / GENERAL[child["kind"]] / "composition.yaml"
        xr_file = out / f"child-{child['kind'].lower()}.yaml"
        clean = {k: child[k] for k in ("apiVersion", "kind", "spec") if k in child}
        clean["metadata"] = {"name": child["metadata"]["name"], "labels": child["metadata"].get("labels", {})}
        xr_file.write_text(yaml.safe_dump(clean, sort_keys=False), encoding="utf-8")
        t = time.time()
        okc, cdocs, cpasses, cerr = simulate(xr_file, comp, Path(args.nested_functions or args.functions), workdir, out, child["kind"].lower())
        row(f"render anidado {child['kind']}", okc, f"{cpasses} pasadas, {max(len(cdocs) - 1, 0)} recursos" if okc else cerr, time.time() - t)
        all_docs += cdocs[1:]
        nv = [f"{d['kind']}/{d['metadata']['name']}" for d in cdocs if "<no value>" in yaml.safe_dump(d)]
        if nv:
            row(f"integridad {child['kind']}", False, "'<no value>' en " + ", ".join(nv), 0)

    # 3. Validación de esquemas de todo lo emitido
    bundle = out / "all-rendered.yaml"
    to_validate = [platform_docs[0]] + [d for d in all_docs if d.get("apiVersion") != "render.crossplane.io/v1beta1"] if platform_docs else []
    bundle.write_text(yaml.safe_dump_all(to_validate, sort_keys=False), encoding="utf-8")
    if len(to_validate) < 2:
        row("validate esquemas (providers + XRDs)", False, "no hay recursos renderizados para validar", 0)
    else:
        t = time.time()
        v = subprocess.run([str(XP), "resource", "validate", args.extensions, str(bundle)],
                           capture_output=True, text=True, encoding="utf-8", cwd=workdir)
        errors = [l for l in (v.stdout + v.stderr).splitlines() if l.startswith("[x]")]
        summary = next((l for l in v.stdout.splitlines() if l.startswith("Total")), "")
        detail = summary if not errors else summary + "\n      " + "\n      ".join(e[:260] for e in errors)
        row("validate esquemas (providers + XRDs)", v.returncode == 0, detail, time.time() - t)

    # 4. Contrato de negocio
    if args.contract and platform_docs:
        t = time.time()
        c = subprocess.run([sys.executable, args.contract, str(out / "platform-render.yaml")], capture_output=True, text=True,
                           encoding="utf-8", env={**os.environ, "PYTHONIOENCODING": "utf-8"})
        fails = [l for l in c.stdout.splitlines() if l.startswith("FAIL")]
        last = [l for l in c.stdout.splitlines() if "reglas" in l]
        row("contrato de negocio", c.returncode == 0, (last[-1] if last else "") + ("".join("\n      " + f for f in fails)), time.time() - t)

    print(f"{'ETAPA':<40} {'RESULT':<6} {'SEG':>6}  DETALLE")
    for stage, ok, detail, secs in rows:
        print(f"{stage:<40} {'OK' if ok else 'FALLA':<6} {secs:6.1f}  {detail}")
    print(f"\nCompuerta local: {'APROBADA' if not failed else 'RECHAZADA'} en {time.time() - t0:.1f} s (sin cluster ni AWS)")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
