from talend_doc_gen.diagram import build_mermaid
from talend_doc_gen.models import Component, Connection, Job


def test_build_mermaid_includes_nodes_and_edges():
    job = Job(
        name="Demo",
        components=[
            Component(name="tFileInputDelimited_1", type="tFileInputDelimited"),
            Component(name="tMap_1", type="tMap"),
        ],
        connections=[
            Connection(source="tFileInputDelimited_1", target="tMap_1", label="Main", kind="flow"),
        ],
    )

    diagram = build_mermaid(job)

    assert diagram.startswith("flowchart LR")
    assert "tFileInputDelimited_1" in diagram
    assert "tMap_1" in diagram
    assert "-->|Main|" in diagram


def test_build_mermaid_handles_empty_job():
    diagram = build_mermaid(Job(name="Vide"))
    assert "Aucun composant" in diagram


def test_build_mermaid_sanitizes_ids():
    job = Job(
        name="Demo",
        components=[Component(name="t-Weird.Name 1", type="tMap")],
    )
    diagram = build_mermaid(job)
    assert "t-Weird.Name 1" not in diagram.splitlines()[1].split("[")[0]
