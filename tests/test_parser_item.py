from pathlib import Path

from talend_doc_gen.parser_item import load_job_from_item, parse_item_file, parse_properties_file

FIXTURES = Path(__file__).parent / "fixtures"


def test_parse_item_file_extracts_components_and_connections():
    job = parse_item_file(FIXTURES / "DWH_Load_Clients_0.1.item")

    assert job.name == "DWH_Load_Clients"
    component_names = [c.name for c in job.components]
    assert component_names == [
        "tFileInputDelimited_1",
        "tMap_1",
        "tDBOutput_1",
        "tLogRow_1",
    ]
    assert job.component_by_name("tMap_1").type == "tMap"
    assert "Nettoyage" in job.component_by_name("tMap_1").description

    assert len(job.connections) == 3
    flow_connections = [c for c in job.connections if c.kind == "flow"]
    reject_connections = [c for c in job.connections if c.kind == "reject"]
    assert len(flow_connections) == 2
    assert len(reject_connections) == 1
    assert reject_connections[0].source == "tMap_1"
    assert reject_connections[0].target == "tLogRow_1"


def test_parse_properties_file():
    props = parse_properties_file(FIXTURES / "DWH_Load_Clients_0.1.properties")
    assert props["label"] == "DWH_Load_Clients"
    assert props["author"] == "corentin.poirier"
    assert props["version"] == "0.1"


def test_load_job_from_item_merges_properties():
    job = load_job_from_item(FIXTURES / "DWH_Load_Clients_0.1.item")

    assert job.name == "DWH_Load_Clients"
    assert job.owner == "corentin.poirier"
    assert job.version == "0.1"
    assert "entrepôt" in job.description
    assert job.source_kind == "item"
