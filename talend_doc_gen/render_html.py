"""Rendu HTML statique (site consultable dans un navigateur, sans build)."""

from __future__ import annotations

import html

from .diagram import build_mermaid
from .models import Job

_KIND_LABEL_FR = {
    "flow": "Flux principal",
    "reject": "Rejet",
    "trigger": "Déclencheur",
    "iterate": "Itération",
}

_PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<title>{title}</title>
<link rel="stylesheet" href="{css_path}">
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
<script>mermaid.initialize({{ startOnLoad: true, securityLevel: "loose" }});</script>
</head>
<body>
<div class="page">
{body}
</div>
</body>
</html>
"""


def _e(value: str) -> str:
    return html.escape(value, quote=False)


def _table(headers: list[str], rows: list[list[str]]) -> str:
    head = "".join(f"<th>{_e(h)}</th>" for h in headers)
    body = "".join(
        "<tr>" + "".join(f"<td>{_e(cell)}</td>" for cell in row) + "</tr>" for row in rows
    )
    return f'<table class="tbl"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>'


def _bullet_list(items: list[str]) -> str:
    if not items:
        return '<p class="muted">Non renseigné</p>'
    return "<ul>" + "".join(f"<li>{_e(i)}</li>" for i in items) + "</ul>"


def render_job_html(job: Job, screenshot_rel_path: str | None, css_path: str = "../assets/style.css") -> str:
    parts: list[str] = [f'<p><a href="../index.html">&larr; Retour à l\'index</a></p>']
    parts.append(f"<h1>{_e(job.name)}</h1>")

    if job.description:
        parts.append(f"<p>{_e(job.description)}</p>")

    parts.append(
        _table(
            ["Champ", "Valeur"],
            [
                ["Propriétaire", job.owner or "Non renseigné"],
                ["Version", job.version or "Non renseigné"],
                ["Planification", job.schedule or "Non renseigné"],
                ["Source du parsing", job.source_kind],
            ],
        )
    )

    if job.purpose:
        parts.append("<h2>Objectif métier</h2>")
        parts.append(f"<p>{_e(job.purpose)}</p>")

    parts.append("<h2>Systèmes source</h2>")
    parts.append(_bullet_list(job.source_systems))
    parts.append("<h2>Systèmes cible</h2>")
    parts.append(_bullet_list(job.target_systems))

    parts.append("<h2>Schéma du flux</h2>")
    if screenshot_rel_path:
        parts.append(
            f'<img class="screenshot" src="{_e(screenshot_rel_path)}" '
            f'alt="Capture d\'écran du flux {_e(job.name)}">'
        )
        parts.append("<details><summary>Diagramme généré automatiquement</summary>")
        parts.append(f'<pre class="mermaid">{_e(build_mermaid(job))}</pre>')
        parts.append("</details>")
    else:
        parts.append(
            '<p class="muted">Aucune capture d\'écran associée '
            f"(dépose une image nommée <code>{_e(job.name)}.png</code> dans <code>screenshots/</code>).</p>"
        )
        parts.append(f'<pre class="mermaid">{_e(build_mermaid(job))}</pre>')

    if job.components:
        parts.append("<h2>Composants</h2>")
        parts.append(
            _table(
                ["Nom", "Type", "Description"],
                [[c.name, c.type or "?", c.description or "Non renseigné"] for c in job.components],
            )
        )

    if job.connections:
        parts.append("<h2>Connexions</h2>")
        parts.append(
            _table(
                ["De", "Vers", "Type", "Nature"],
                [
                    [c.source, c.target, c.label, _KIND_LABEL_FR.get(c.kind, c.kind)]
                    for c in job.connections
                ],
            )
        )

    if job.context_params:
        parts.append("<h2>Paramètres de contexte</h2>")
        parts.append(_table(["Nom", "Valeur"], [[k, v] for k, v in job.context_params.items()]))

    if job.notes:
        parts.append("<h2>Notes</h2>")
        parts.append(f"<p>{_e(job.notes)}</p>")

    body = "\n".join(parts)
    return _PAGE_TEMPLATE.format(title=_e(job.name), css_path=css_path, body=body)


def render_index_html(entries: list[tuple[str, Job]]) -> str:
    rows = []
    for slug, job in sorted(entries, key=lambda e: e[1].name.lower()):
        description = (job.description or "Non renseigné").splitlines()[0]
        name_cell = f'<a href="jobs/{_e(slug)}.html">{_e(job.name)}</a>'
        rows.append([name_cell, description, job.owner or "Non renseigné", job.source_kind])

    head = "".join(f"<th>{h}</th>" for h in ["Job", "Description", "Propriétaire", "Source"])
    body_rows = "".join(
        "<tr>"
        + f"<td>{row[0]}</td>"
        + "".join(f"<td>{_e(cell)}</td>" for cell in row[1:])
        + "</tr>"
        for row in rows
    )
    table = f'<table class="tbl"><thead><tr>{head}</tr></thead><tbody>{body_rows}</tbody></table>'

    body = f"<h1>Documentation des flux Talend</h1>\n<p>{len(entries)} flux documentés.</p>\n{table}"
    return _PAGE_TEMPLATE.format(title="Documentation des flux Talend", css_path="assets/style.css", body=body)


STYLE_CSS = """
:root {
  color-scheme: light dark;
  --fg: #1b1f24;
  --bg: #ffffff;
  --muted: #6b7280;
  --border: #e2e8f0;
  --accent: #2563eb;
}
@media (prefers-color-scheme: dark) {
  :root { --fg: #e5e7eb; --bg: #0f172a; --muted: #94a3b8; --border: #1f2937; }
}
body { background: var(--bg); color: var(--fg); font-family: -apple-system, Segoe UI, Roboto, sans-serif; }
.page { max-width: 900px; margin: 0 auto; padding: 32px 16px 80px; line-height: 1.5; }
h1, h2 { line-height: 1.25; }
h2 { margin-top: 2em; border-bottom: 1px solid var(--border); padding-bottom: .3em; }
a { color: var(--accent); }
.muted { color: var(--muted); }
.tbl { width: 100%; border-collapse: collapse; margin: 1em 0; }
.tbl th, .tbl td { text-align: left; padding: 6px 10px; border-bottom: 1px solid var(--border); }
.screenshot { max-width: 100%; border: 1px solid var(--border); border-radius: 6px; }
code { background: rgba(127,127,127,.15); padding: 1px 5px; border-radius: 4px; }
details { margin: 1em 0; }
pre.mermaid { background: transparent; }
"""
