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
from .parser_screenshot import extract_embedded_screenshot


def _connector_kind(connector_name: str) -> str:
    """Classe un ``connectorName`` Talend dans une catégorie fonctionnelle
    utilisée pour l'affichage (style du lien dans le diagramme).

    Les exports réels utilisent des noms très variés selon les composants
    (ex: ``OUTPUT_1``/``OUTPUT_2`` pour les sorties multiples d'un tMap,
    ``TRIGGER_OUTPUT_1`` pour un enchaînement de tRunJob...) : on classe donc
    par préfixe plutôt que par correspondance exacte.
    """
    name = (connector_name or "").upper()
    if name in ("FLOW", "MAIN") or name.startswith("OUTPUT"):
        return "flow"
    if name.startswith("REJECT") or name.startswith("FILTER"):
        return "reject"
    if name == "ITERATE":
        return "iterate"
    # RUN_IF, OK_IF, ERROR_IF, SUBJOB_OK/ERROR, COMPONENT_OK/ERROR,
    # TRIGGER_OUTPUT_n... : tous des enchaînements de sous-jobs/composants.
    return "trigger"


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
                    kind=_connector_kind(connector),
                )
            )

    context_params = _default_context_parameters(root)

    return Job(
        name=job_name,
        components=components,
        connections=connections,
        context_params=context_params,
        source_kind="item",
    )


def _default_context_parameters(root: ET.Element) -> dict[str, str]:
    """Extrait les paramètres du contexte Talend par défaut du job
    (ex: contexte ``dev``). Un job peut définir plusieurs contextes
    (dev/qualif/prod...) avec les mêmes noms de paramètres : on ne retient
    que celui déclaré comme contexte par défaut, pour éviter les doublons."""
    default_context_name = root.get("defaultContext")
    contexts = [child for child in root if _local(child.tag) == "context"]
    if not contexts:
        return {}

    target = next((c for c in contexts if c.get("name") == default_context_name), contexts[0])

    params: dict[str, str] = {}
    for child in target:
        if _local(child.tag) != "contextParameter":
            continue
        name = child.get("name")
        if name:
            params[name] = child.get("value", "") or ""
    return params


def parse_properties_file(path: str | Path) -> dict[str, str]:
    """Parse un fichier .properties Talend.

    Deux formats sont acceptés :
      - le format XMI utilisé par Talend Studio/Cloud (élément
        ``TalendProperties:Property`` avec des attributs ``label``,
        ``version``, ``description``, ``purpose``, ``status``...) ;
      - un simple format ``clé=valeur`` (pour des métadonnées saisies/
        éditées à la main).
    """
    path = Path(path)
    if not path.exists():
        return {}

    try:
        root = ET.parse(path).getroot()
    except ET.ParseError:
        return _parse_key_value_properties(path)

    for elem in root.iter():
        if _local(elem.tag) == "Property":
            return {
                key: elem.get(key)
                for key in ("label", "version", "description", "purpose", "status")
                if elem.get(key)
            }
    return {}


def _parse_key_value_properties(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
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
    job.embedded_screenshot = extract_embedded_screenshot(item_path)

    return job
