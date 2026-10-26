"""Reproduce en pantalla las salidas clave de la PoC para tomar pantallazos (evidencia wiki).

Multiplataforma. Desde la raíz del repo:

    python 06-evidence/replay.py 1      # E1 versiones de CLI
    python 06-evidence/replay.py 2      # E2 errores vistos en el cluster
    python 06-evidence/replay.py 3      # E3 bugs detectados offline
    python 06-evidence/replay.py 4      # E4 verificación de adopción
    python 06-evidence/replay.py 5      # E6 compuerta local antes vs después
    python 06-evidence/replay.py 6      # E7 control plane local (KIND)
    python 06-evidence/replay.py 7      # E8 árbol Ready en EKS + API respondiendo
    python 06-evidence/replay.py 8      # E10 matriz de defectos
"""

import os
import platform
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GENERAL = ROOT.parent / "local-argocd-crossplane-config"
EXE = ".exe" if platform.system() == "Windows" else ""
XP_NEW = ROOT / "tools" / f"crossplane-2.5.0{EXE}"
XP_OLD = ROOT / "tools" / f"crank-2.2.6{EXE}"
FUNCTIONS = ROOT / "03-before-2-cli-2.2" / "functions.yaml"
KMS_COMPOSITION = GENERAL / "platform" / "aws_xrds" / "kms" / "composition.yaml"

CYAN, GREEN, RED, DIM, RESET = "\033[36m", "\033[32m", "\033[31m", "\033[2m", "\033[0m"


def title(text):
    print(f"\n{CYAN}=== {text} ==={RESET}")


def prompt(cmd):
    """Muestra el comando como si se hubiera tecleado (con rutas relativas y sin .exe)."""
    shown = " ".join(str(c) for c in cmd)
    shown = shown.replace(str(ROOT) + os.sep, "").replace(str(ROOT.parent) + os.sep, "../")
    shown = re.sub(r"tools[\\/](crossplane-2\.5\.0|crank-2\.2\.6)(\.exe)?", lambda m: "crossplane" if "2.5" in m.group(1) else "crossplane-2.2", shown)
    print(f"{GREEN}$ {shown.replace(os.sep, '/')}{RESET}")


def run(cmd, stdin=None):
    prompt(cmd)
    out = subprocess.run([str(c) for c in cmd], input=stdin, capture_output=True, text=True, encoding="utf-8", cwd=ROOT)
    text = out.stdout + out.stderr
    print(colorize(text), end="" if text.endswith("\n") else "\n")
    return out.stdout


def colorize(text):
    text = re.sub(r"^(FAIL.*|\[x\].*)$", lambda m: f"{RED}{m.group(1)}{RESET}", text, flags=re.M)
    return re.sub(r"^(PASS.*|\[✓\].*)$", lambda m: f"{GREEN}{m.group(1)}{RESET}", text, flags=re.M)


def adoption(claim):
    rendered = subprocess.run(
        [str(XP_NEW), "composition", "render", str(claim), str(KMS_COMPOSITION), str(FUNCTIONS), "-x"],
        capture_output=True, text=True, encoding="utf-8", cwd=ROOT,
    ).stdout
    prompt([XP_NEW, "composition", "render", claim, KMS_COMPOSITION, FUNCTIONS, "-x", "|", "python", "05-measurements/adoption_checks.py", "-"])
    out = subprocess.run([sys.executable, "05-measurements/adoption_checks.py", "-"], input=rendered,
                         capture_output=True, text=True, encoding="utf-8", cwd=ROOT,
                         env={**os.environ, "PYTHONIOENCODING": "utf-8"})
    print(colorize(out.stdout + out.stderr))


def paso1():
    title("E1 · CLI 2.2.6 (antes) y 2.5.0 (después) contra el core v2.3.3 del cluster")
    run([XP_OLD, "version"])
    run([XP_NEW, "version"])


def paso2():
    title("E2 · Errores que solo aparecieron en el cluster (1.ª corrida: 2,4 min, ~5.200 tokens de eventos)")
    log = ROOT / "05-measurements" / "runs" / "before-1" / "observe-cluster-01.log"
    prompt(["grep", "-E", "'permissionsBoundary|field not declared|not authorized'", "05-measurements/runs/before-1/observe-cluster-01.log"])
    patterns = ["permissionsBoundary", "field not declared", "iam:CreatePolicy", "kms:CreateAlias"]
    for pat in patterns:
        line = next((l.strip() for l in log.read_text(encoding="utf-8-sig").splitlines() if pat in l), "")
        msg = re.search(r"(api error.*?)(\s+\[\]|$)|(cannot apply composed resource.*)", line)
        text = (msg.group(1) or msg.group(3)) if msg else line[:200]
        text = re.sub(r"/\d{10,}", "", text.split(" Go to ")[0])
        print(f"{RED}✗{RESET} {text}")


def paso3():
    title("E3 · CLI 2.5 detecta offline los 2 bugs de las composiciones generales (sin cluster ni AWS)")
    audit = Path("04-after-cli-2.5") / "general-audit"
    run([XP_NEW, "resource", "validate", audit / "providers.yaml", audit / "render-all.yaml"])
    title("Render anidado de aws-iam-role")
    prompt(["grep", "-n", "'no value'", (audit / "render-xiam.yaml")])
    for i, line in enumerate((ROOT / audit / "render-xiam.yaml").read_text(encoding="utf-8-sig").splitlines(), 1):
        if "no value" in line:
            print(f"{RED}{i}:{line}{RESET}")


def paso4():
    title("E4 · Adopción: claim real adopt-kms-test verificado offline")
    adoption(GENERAL / "claims" / "adopt-kms-test" / "claim.yaml")
    title("E4b · Mismo claim sin managementPolicies (error típico al editar): crearía en vez de adoptar")
    adoption(ROOT / "04-after-cli-2.5" / "adoption-demo" / "claim-sin-policies.yaml")


def gate(xr, composition, extensions, label):
    cmd = [sys.executable, "05-measurements/local_gate.py", "--xr", xr, "--composition", composition,
           "--functions", "04-after-cli-2.5/project/examples/functions.yaml",
           "--nested-functions", "04-after-cli-2.5/general-audit/functions-api.yaml",
           "--extensions", extensions, "--contract", "05-measurements/business_checks_api.py",
           "--out", f"05-measurements/gate-out/replay-{label}", "--multi-instance"]
    prompt(["python", *cmd[1:]])
    out = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", cwd=ROOT,
                         env={**os.environ, "PYTHONIOENCODING": "utf-8"})
    text = re.sub(r"(?m)^(.*\bFALLA\b.*|.*RECHAZADA.*)$", lambda m: f"{RED}{m.group(1)}{RESET}", out.stdout)
    print(re.sub(r"(?m)^(.*APROBADA.*)$", lambda m: f"{GREEN}{m.group(1)}{RESET}", text))


def paso5():
    title("E6 · Compuerta local CLI 2.5 sobre la composición de ANTES (ya desplegada): detecta la colisión")
    gate("02-before-1-yaml/api/xr.yaml", "02-before-1-yaml/api/composition.yaml", "03-before-2-cli-2.2/api/extensions-gate", "antes")
    title("E6b · Misma compuerta sobre la composición de DESPUÉS: aprobada en segundos, sin cluster ni AWS")
    gate("04-after-cli-2.5/project/examples/xr.yaml", "04-after-cli-2.5/project/apis/xpoccliapiservices/composition.yaml",
         "04-after-cli-2.5/extensions", "despues")


def paso6():
    title("E7 · Control plane local (crossplane project run): Configuration + funciones + XRD instalados")
    kcfg = Path(os.environ.get("TEMP", "/tmp")) / "poc-kind.kubeconfig"
    for args in (["get", "configurations.pkg.crossplane.io,functions.pkg.crossplane.io"], ["get", "xrd,compositions"],
                 ["get", "xpoccliapiservice,xapigatewayreststack,xkms"]):
        run(["kubectl", "--kubeconfig", kcfg, *args])


def paso7():
    title("E8 · Después en EKS: árbol completo Ready (crossplane resource trace)")
    run([XP_NEW, "resource", "trace", "xpoccliapiservice.poc-cli.platform.nequi.com/poc-cli-api"])
    url = subprocess.run(["kubectl", "get", "xpoccliapiservice.poc-cli.platform.nequi.com", "poc-cli-api", "-o",
                          "jsonpath={.status.invokeUrl}"], capture_output=True, text=True).stdout
    title("E8b · La API responde")
    run(["curl", "-s", "-w", "\nHTTP %{http_code} en %{time_total}s\n", url])


def paso8():
    import csv
    title("E10 · Matriz de detección de defectos (¿dónde se descubre cada error?)")
    with open(ROOT / "05-measurements" / "defects.csv", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    print(f"{'ID':<4} {'Defecto':<62} {'Solo cluster (hoy)':<28} {'CLI 2.2':<14} {'CLI 2.5 + compuerta'}")
    for r in rows:
        cl = r["solo_cluster"].split(":")[0]
        b2 = r["antes2_detecta"]
        a5 = r["despues_detecta"]
        c2 = RED if b2 == "no detectado" else GREEN
        c5 = RED if a5 == "no detectado" else GREEN
        print(f"{r['id']:<4} {r['defecto'][:61]:<62} {cl[:27]:<28} {c2}{b2:<14}{RESET} {c5}{a5}{RESET}")
    d2 = sum(r["antes2_detecta"] != "no detectado" for r in rows)
    d5 = sum(r["despues_detecta"] != "no detectado" for r in rows)
    print(f"\nDetectados antes de tocar el cluster: CLI 2.2 = {d2}/{len(rows)} · CLI 2.5 + compuerta = {d5}/{len(rows)}")


if __name__ == "__main__":
    if platform.system() == "Windows":
        os.system("")  # habilita colores ANSI en consolas Windows
        sys.stdout.reconfigure(encoding="utf-8")
    steps = {"1": paso1, "2": paso2, "3": paso3, "4": paso4, "5": paso5, "6": paso6, "7": paso7, "8": paso8}
    if len(sys.argv) != 2 or sys.argv[1] not in steps:
        print(__doc__)
        sys.exit(2)
    steps[sys.argv[1]]()
