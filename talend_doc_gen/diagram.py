"""Génération d'un schéma Mermaid (flowchart) à partir d'un ``Job``.

Ce diagramme sert de complément à la capture d'écran Talend (toujours plus
fidèle au canevas réel) : il permet d'avoir un schéma consultable et
« lisible » même sans screenshot, et reste à jour automatiquement quand le
job est reparsé depuis son export .item.
"""

from __future__ import annotations

import re

from .models import Job

_KIND_ARROW = {
    "flow": "-->",
    "reject": "-.->",
    "trigger": "==>",
    "iterate": "-.->",
}


def _safe_id(name: str) -> str:
    """Mermaid n'accepte pas tous les caractères dans les identifiants de
    nœud ; on les normalise sans risquer de collisions."""
    return re.sub(r"[^A-Za-z0-9_]", "_", name)


def build_mermaid(job: Job, direction: str = "LR") -> str:
    lines = [f"flowchart {direction}"]

    for component in job.components:
        node_id = _safe_id(component.name)
        label = component.name
        if component.type and component.type != component.name:
            label = f"{component.name}<br/><i>{component.type}</i>"
        lines.append(f'    {node_id}["{label}"]')

    for conn in job.connections:
        arrow = _KIND_ARROW.get(conn.kind, "-->")
        source_id = _safe_id(conn.source)
        target_id = _safe_id(conn.target)
        label = f"|{conn.label}|" if conn.label else ""
        lines.append(f"    {source_id} {arrow}{label} {target_id}")

    if len(lines) == 1:
        lines.append('    empty["Aucun composant détecté"]')

    return "\n".join(lines)
