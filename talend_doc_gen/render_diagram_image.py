"""Rendu d'un diagramme Mermaid en image PNG.

Utilisé pour les formats qui ne savent pas afficher du Mermaid nativement
(Word, PDF...). La page HTML/Markdown, elle, le rend directement dans le
navigateur (voir :mod:`render_html`) et n'a pas besoin de ce module.

Nécessite le paquet optionnel ``playwright`` avec un navigateur Chromium
installé (``pip install playwright && playwright install chromium``). En
son absence — ou si le rendu échoue pour une autre raison (pas de sandbox
graphique disponible, etc.) — :func:`render_mermaid_to_png` retourne
``False`` : les appelants doivent prévoir un repli (le code Mermaid brut,
par exemple), la génération de la doc ne doit jamais échouer pour autant.
"""

from __future__ import annotations

from pathlib import Path

_MERMAID_JS_PATH = Path(__file__).parent / "assets" / "mermaid.min.js"

_HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  html, body {{ margin: 0; padding: 0; background: #ffffff; }}
  #graph {{ display: inline-block; padding: 20px; }}
</style>
<script>{mermaid_js}</script>
</head>
<body>
<div id="graph" class="mermaid">{diagram}</div>
<script>
  mermaid.initialize({{ startOnLoad: true, securityLevel: "loose" }});
</script>
</body>
</html>
"""

# Emplacement(s) où chercher un exécutable Chromium en repli quand
# `playwright install` n'a pas pu être relancé pour la version installée
# (utile dans des environnements avec un navigateur pré-installé à un
# chemin non standard).
_FALLBACK_CHROMIUM_EXECUTABLES = [
    "/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
]


def render_mermaid_to_png(diagram: str, out_path: str | Path, scale: int = 2) -> bool:
    """Rend ``diagram`` (code Mermaid) en PNG dans ``out_path``.

    Retourne ``True`` en cas de succès, ``False`` sinon (jamais d'exception :
    c'est un rendu « best effort »).
    """
    if not _MERMAID_JS_PATH.exists():
        return False

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return False

    mermaid_js = _MERMAID_JS_PATH.read_text(encoding="utf-8")
    html = _HTML_TEMPLATE.format(mermaid_js=mermaid_js, diagram=diagram)

    try:
        with sync_playwright() as p:
            browser = None
            for kwargs in ({}, *({"executable_path": exe} for exe in _FALLBACK_CHROMIUM_EXECUTABLES)):
                try:
                    browser = p.chromium.launch(**kwargs)
                    break
                except Exception:
                    continue
            if browser is None:
                return False

            try:
                page = browser.new_page(device_scale_factor=scale)
                page.set_content(html)
                page.wait_for_selector("#graph svg", timeout=10_000)
                page.query_selector("#graph").screenshot(path=str(out_path))
                return True
            finally:
                browser.close()
    except Exception:
        return False
