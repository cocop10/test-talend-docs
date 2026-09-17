"""Parsing des exports de jobs Talend Studio (fichiers .item / .properties).

Un job Talend exporté se compose généralement de deux fichiers portant le
même nom : ``MonJob_0.1.item`` (XML décrivant les composants et connexions
du canevas) et ``MonJob_0.1.properties`` (métadonnées : description, auteur,
version...). Ce module sait lire l'un, l'autre, ou les deux.

Le format XML réel varie selon les versions de Talend, aussi ce parser reste
tolérant : il ignore les espaces de noms et ne s'appuie que sur les
attributs/éléments qui existent réellement dans le fichier fourni.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

from .models import Component, Connection, Job

# Mapping du nom de connecteur Talend -> catégorie fonctionnelle utilisée
# pour l'affichage (couleur/style du lien dans le diagramme).
_CONNECTOR_KIND = {
    "FLOW": "flow",
    "MAIN": "flow",
    "REJECT": "reject",
    "FILTER": "reject",
    "ITERATE": "iterate",
    "RUN_IF": "trigger",
    "OK_IF": "trigger",
    "ERROR_IF": "trigger",
    "SUBJOB_OK": "trigger",
    "SUBJOB_ERROR": "trigger",
    "ON_COMPONENT_OK": "trigger",
    "ON_COMPONENT_ERROR": "trigger",
}


def _local(tag: str) -> str:
    """Retire le préfixe d'espace de nom éventuel d'un tag XML."""
    return tag.rsplit("}", 1)[-1]


def _element_parameters(node: ET.Element) -> dict[str, str]:
    params: dict[str, str] = {}
    for child in node:
        if _local(child.tag) != "elementParameter":
            continue
        name = child.get("name")
        value = child.get("value")
        if name is not None and value is not None:
            params[name] = value
    return params


def parse_item_file(path: str | Path) -> Job:
    """Parse un fichier .item Talend et retourne un ``Job`` partiel.

    Seules les informations présentes sur le canevas (composants,
    connexions) sont extraites ; les métadonnées descriptives viennent en
    général du fichier .properties associé (voir :func:`parse_properties_file`
    et :func:`load_job_from_item`).
    """
    path = Path(path)
    tree = ET.parse(path)
    root = tree.getroot()

    job_name = path.stem
    # Les exports Talend suffixent parfois le nom par la version, ex:
    # "MonJob_0.1" -> on retire le suffixe numérique de version si présent.
    parts = job_name.rsplit("_", 1)
    if len(parts) == 2 and parts[1].replace(".", "").isdigit():
        job_name = parts[0]

    components: list[Component] = []
    connections: list[Connection] = []

    for elem in root.iter():
        tag = _local(elem.tag)
        if tag == "node":
            comp_type = elem.get("componentName", "")
            params = _element_parameters(elem)
            unique_name = params.get("UNIQUE_NAME") or comp_type
            description = params.get("COMPONENT_DESCRIPTION", "") or ""
            components.append(
                Component(name=unique_name, type=comp_type, description=description)
            )
        elif tag == "connection":
            source = elem.get("source")
            target = elem.get("target")
            if not source or not target:
                continue
            connector = elem.get("connectorName", "FLOW")
            link_label = elem.get("label") or connector.title()
            connections.append(
                Connection(
                    source=source,
                    target=target,
                    label=link_label,
                    kind=_CONNECTOR_KIND.get(connector, "flow"),
                )
            )

    return Job(
        name=job_name,
        components=components,
        connections=connections,
        source_kind="item",
    )


def parse_properties_file(path: str | Path) -> dict[str, str]:
    """Parse un fichier .properties Talend (format ``clé=valeur``)."""
    path = Path(path)
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw_line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        values[key.strip()] = value.strip()
    return values


def load_job_from_item(item_path: str | Path) -> Job:
    """Charge un job complet à partir d'un fichier .item, en complétant
    avec le fichier .properties de même nom s'il existe."""
    item_path = Path(item_path)
    job = parse_item_file(item_path)

    props_path = item_path.with_suffix(".properties")
    props = parse_properties_file(props_path)

    if props.get("label"):
        job.name = props["label"]
    job.description = props.get("description", "")
    job.purpose = props.get("purpose", "")
    job.owner = props.get("author", "")
    job.version = props.get("version", "")

    return job
