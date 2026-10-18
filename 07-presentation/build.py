"""Genera 07-presentation/presentacion-manual.html (autocontenido) a partir de template.html.

Reemplaza {{img:archivo.png}} por la imagen de 06-evidence/img/ en base64, igual que la
presentación de las PoC anteriores (un solo archivo para compartir).

Uso: python 07-presentation/build.py
"""

import base64
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
IMG = HERE.parent / "06-evidence" / "img"


def inline(match):
    path = IMG / match.group(1)
    data = base64.b64encode(path.read_bytes()).decode()
    return f"data:image/png;base64,{data}"


html = re.sub(r"\{\{img:([^}]+)\}\}", inline, (HERE / "template.html").read_text(encoding="utf-8"))
(HERE / "presentacion-manual.html").write_text(html, encoding="utf-8")
print(f"presentacion-manual.html: {len(html) / 1024 / 1024:.1f} MB")
