"""Modèle de données commun, alimenté soit par le parsing d'un export
Talend (.item), soit par des métadonnées saisies manuellement (YAML)."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Component:
    name: str  # identifiant unique dans le job, ex: tFileInputDelimited_1
    type: str  # type de composant Talend, ex: tFileInputDelimited
    description: str = ""

    @property
    def display_label(self) -> str:
        return f"{self.name}\n({self.type})" if self.type else self.name


@dataclass
class Connection:
    source: str
    target: str
    label: str = "Main"
    kind: str = "flow"  # flow | reject | trigger | iterate


@dataclass
class Job:
    name: str
    description: str = ""
    purpose: str = ""
    owner: str = ""
    version: str = ""
    schedule: str = ""
    source_systems: list[str] = field(default_factory=list)
    target_systems: list[str] = field(default_factory=list)
    context_params: dict[str, str] = field(default_factory=dict)
    components: list[Component] = field(default_factory=list)
    connections: list[Connection] = field(default_factory=list)
    notes: str = ""
    screenshot: str | None = None  # chemin relatif vers la capture d'écran
    embedded_screenshot: bytes | None = None  # capture extraite du .screenshot Talend
    source_kind: str = "manual"  # "item" | "manual" | "item+manual"

    def component_by_name(self, name: str) -> Component | None:
        for c in self.components:
            if c.name == name:
                return c
        return None
