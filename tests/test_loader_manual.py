from pathlib import Path

import pytest

from talend_doc_gen.loader_manual import load_manual_job, merge_jobs
from talend_doc_gen.parser_item import load_job_from_item

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture()
def manual_yaml(tmp_path: Path) -> Path:
    content = """
    name: CRM_Export_Prospects
    description: Exporte les prospects qualifiés du CRM vers le fichier de campagne marketing.
    owner: Equipe Marketing Ops
    schedule: "Hebdomadaire - lundi 06:00"
    source_systems: [CRM Salesforce]
    target_systems: [Outil Emailing]
    screenshot: CRM_Export_Prospects.png
    components:
      - name: tSalesforceInput_1
        type: tSalesforceInput
        description: Extraction des prospects qualifiés
      - name: tFileOutputDelimited_1
        type: tFileOutputDelimited
        description: Génération du fichier de campagne
    connections:
      - from: tSalesforceInput_1
        to: tFileOutputDelimited_1
        label: Main
    notes: |
      Vérifier le filtre de qualification avant chaque campagne.
    """
    path = tmp_path / "CRM_Export_Prospects.yaml"
    path.write_text(content, encoding="utf-8")
    return path


def test_load_manual_job(manual_yaml: Path):
    job = load_manual_job(manual_yaml)

    assert job.name == "CRM_Export_Prospects"
    assert job.owner == "Equipe Marketing Ops"
    assert job.source_systems == ["CRM Salesforce"]
    assert len(job.components) == 2
    assert job.connections[0].source == "tSalesforceInput_1"
    assert job.screenshot == "CRM_Export_Prospects.png"
    assert job.source_kind == "manual"


def test_merge_jobs_prefers_manual_overrides():
    base = load_job_from_item(FIXTURES / "DWH_Load_Clients_0.1.item")
    from talend_doc_gen.models import Job

    override = Job(
        name="DWH_Load_Clients",
        owner="",
        schedule="Quotidien 02:00",
        source_systems=["CRM"],
        notes="Attention aux doublons.",
    )

    merged = merge_jobs(base, override)

    assert merged.schedule == "Quotidien 02:00"
    assert merged.source_systems == ["CRM"]
    # Le owner vient toujours du .item/.properties car non redéfini manuellement
    assert merged.owner == base.owner
    # Les composants parsés depuis le .item sont conservés
    assert len(merged.components) == len(base.components)
    assert merged.source_kind == "item+manual"
