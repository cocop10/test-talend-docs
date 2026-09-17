"""Rendu Markdown d'un job (et de l'index) documenté."""

from __future__ import annotations

from .diagram import build_mermaid
from .models import Job

_KIND_LABEL_FR = {
    "flow": "Flux principal",
    "reject": "Rejet",
    "trigger": "Déclencheur (OnSubjobOk/RunIf...)",
    "iterate": "Itération",
}


def _bullet_list(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items) if items else "_Non renseigné_"


_MASKED_VALUE = "•••• (masqué)"


def render_job_markdown(
    job: Job, screenshot_rel_path: str | None, mask_context_values: bool = True
) -> str:
    lines: list[str] = [f"# {job.name}", ""]

    if job.description:
        lines += [job.description, ""]

    meta_rows = [
        ("Propriétaire", job.owner or "_Non renseigné_"),
        ("Version", job.version or "_Non renseigné_"),
        ("Planification", job.schedule or "_Non renseigné_"),
        ("Source du parsing", job.source_kind),
    ]
    lines += ["| Champ | Valeur |", "|---|---|"]
    lines += [f"| {k} | {v} |" for k, v in meta_rows]
    lines.append("")

    if job.purpose:
        lines += ["## Objectif métier", "", job.purpose, ""]

    lines += ["## Systèmes source", "", _bullet_list(job.source_systems), ""]
    lines += ["## Systèmes cible", "", _bullet_list(job.target_systems), ""]

    lines += ["## Schéma du flux", ""]
    if screenshot_rel_path:
        lines += [f"![Capture d'écran du flux {job.name}]({screenshot_rel_path})", ""]
        lines += [
            "<details>",
            "<summary>Diagramme généré automatiquement (Mermaid)</summary>",
            "",
            "```mermaid",
            build_mermaid(job),
            "```",
            "",
            "</details>",
            "",
        ]
    else:
        lines += [
            "_Aucune capture d'écran associée à ce job "
            f"(dépose une image nommée `{job.name}.png` dans le dossier `screenshots/`)._",
            "",
            "```mermaid",
            build_mermaid(job),
            "```",
            "",
        ]

    if job.components:
        lines += ["## Composants", "", "| Nom | Type | Description |", "|---|---|---|"]
        lines += [
            f"| {c.name} | {c.type or '_?_'} | {c.description or '_Non renseigné_'} |"
            for c in job.components
        ]
        lines.append("")

    if job.connections:
        lines += ["## Connexions", "", "| De | Vers | Type | Nature |", "|---|---|---|---|"]
        lines += [
            f"| {c.source} | {c.target} | {c.label} | {_KIND_LABEL_FR.get(c.kind, c.kind)} |"
            for c in job.connections
        ]
        lines.append("")

    if job.context_params:
        lines += ["## Paramètres de contexte", ""]
        if mask_context_values:
            lines.append(
                "_Les valeurs (hôtes, identifiants, chemins...) sont masquées "
                "par défaut car potentiellement sensibles ; seuls les noms de "
                "paramètres sont listés._"
            )
            lines.append("")
        lines += ["| Nom | Valeur |", "|---|---|"]
        lines += [
            f"| {k} | {_MASKED_VALUE if mask_context_values else v} |"
            for k, v in job.context_params.items()
        ]
        lines.append("")

    if job.notes:
        lines += ["## Notes", "", job.notes, ""]

    return "\n".join(lines).rstrip() + "\n"


def render_index_markdown(entries: list[tuple[str, Job]]) -> str:
    lines = ["# Documentation des flux Talend", "", "| Job | Description | Propriétaire | Source |", "|---|---|---|---|"]
    for slug, job in sorted(entries, key=lambda e: e[1].name.lower()):
        description = (job.description or "_Non renseigné_").splitlines()[0]
        lines.append(
            f"| [{job.name}](jobs/{slug}.md) | {description} | {job.owner or '_Non renseigné_'} | {job.source_kind} |"
        )
    lines.append("")
    return "\n".join(lines)
