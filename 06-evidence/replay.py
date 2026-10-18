"""Reproduce en pantalla las salidas clave de la PoC para tomar pantallazos (evidencia wiki).

Multiplataforma (Linux/macOS/Windows con Git Bash). Desde la raíz del repo:

    python 06-evidence/replay.py 1      # E1 versiones de CLI
    python 06-evidence/replay.py 2      # E2 errores vistos en el cluster
    python 06-evidence/replay.py 3      # E3 bugs detectados offline
    python 06-evidence/replay.py 4      # E4 verificación de adopción
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


if __name__ == "__main__":
    if platform.system() == "Windows":
        os.system("")  # habilita colores ANSI en consolas Windows
        sys.stdout.reconfigure(encoding="utf-8")
    steps = {"1": paso1, "2": paso2, "3": paso3, "4": paso4}
    if len(sys.argv) != 2 or sys.argv[1] not in steps:
        print(__doc__)
        sys.exit(2)
    steps[sys.argv[1]]()
