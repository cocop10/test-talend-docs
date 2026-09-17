"""Chargement des métadonnées de flux saisies manuellement en YAML.

Utilisé pour :
  - les jobs dont on n'a pas l'export Talend (.item), uniquement une capture
    d'écran et une description du flux ;
  - compléter/enrichir un job déjà parsé depuis un .item (description
    métier, systèmes source/cible, planning, notes...), en fusionnant les
    deux sources sur le nom du job.

Format attendu d'un fichier YAML (voir jobs/README.md pour un exemple
complet) ::

    name: DWH_Load_Customers
    description: ...
    owner: Equipe Data
    schedule: "Quotidien 02:00"
    source_systems: [CRM Salesforce]
    target_systems: [Data Warehouse - PostgreSQL]
    screenshot: DWH_Load_Customers.png
    components:
      - name: tSalesforceInput_1
        type: tSalesforceInput
        description: Extraction des comptes clients
    connections:
      - from: tSalesforceInput_1
        to: tMap_1
        label: Main
    notes: |
      Point d'attention...
"""

from __future__ import annotations

from pathlib import Path

import yaml

from .models import Component, Connection, Job


def load_manual_job(path: str | Path) -> Job:
    path = Path(path)
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}

    name = data.get("name") or path.stem
    components = [
        Component(
            name=c["name"],
            type=c.get("type", ""),
            description=c.get("description", ""),
        )
        for c in data.get("components", []) or []
    ]
    connections = [
        Connection(
            source=c["from"],
            target=c["to"],
            label=c.get("label", "Main"),
            kind=c.get("kind", "flow"),
        )
        for c in data.get("connections", []) or []
    ]

    return Job(
        name=name,
        description=data.get("description", ""),
        purpose=data.get("purpose", ""),
        owner=data.get("owner", ""),
        version=str(data.get("version", "")),
        schedule=data.get("schedule", ""),
        source_systems=list(data.get("source_systems", []) or []),
        target_systems=list(data.get("target_systems", []) or []),
        context_params=dict(data.get("context_params", {}) or {}),
        components=components,
        connections=connections,
        notes=data.get("notes", ""),
        screenshot=data.get("screenshot"),
        source_kind="manual",
    )


def merge_jobs(base: Job, override: Job) -> Job:
    """Fusionne les métadonnées manuelles (``override``) dans un job déjà
    parsé depuis un .item (``base``). Les champs non vides de ``override``
    gagnent ; les composants/connexions extraits du .item sont conservés
    tels quels s'ils ne sont pas redéfinis manuellement."""
    merged = Job(
        name=override.name or base.name,
        description=override.description or base.description,
        purpose=override.purpose or base.purpose,
        owner=override.owner or base.owner,
        version=override.version or base.version,
        schedule=override.schedule or base.schedule,
        source_systems=override.source_systems or base.source_systems,
        target_systems=override.target_systems or base.target_systems,
        context_params={**base.context_params, **override.context_params},
        components=override.components or base.components,
        connections=override.connections or base.connections,
        notes=override.notes or base.notes,
        screenshot=override.screenshot or base.screenshot,
        embedded_screenshot=override.embedded_screenshot or base.embedded_screenshot,
        source_kind="item+manual",
    )
    return merged
