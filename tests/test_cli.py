import base64
import shutil
from pathlib import Path

from talend_doc_gen.cli import generate_docs

FIXTURES = Path(__file__).parent / "fixtures"

# Le plus petit PNG valide possible (1x1 pixel transparent), pour que le
# rendu .docx (qui inspecte réellement le contenu de l'image) l'accepte.
_TINY_PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
)


def test_generate_docs_end_to_end(tmp_path: Path):
    items_dir = tmp_path / "items"
    manual_dir = tmp_path / "jobs"
    screenshots_dir = tmp_path / "screenshots"
    out_dir = tmp_path / "docs"
    items_dir.mkdir()
    manual_dir.mkdir()
    screenshots_dir.mkdir()

    shutil.copyfile(FIXTURES / "DWH_Load_Clients_0.1.item", items_dir / "DWH_Load_Clients_0.1.item")
    shutil.copyfile(
        FIXTURES / "DWH_Load_Clients_0.1.properties", items_dir / "DWH_Load_Clients_0.1.properties"
    )

    manual_yaml = manual_dir / "CRM_Export_Prospects.yaml"
    manual_yaml.write_text(
        """
name: CRM_Export_Prospects
description: Exporte les prospects qualifiés vers l'outil emailing.
owner: Equipe Marketing Ops
components:
  - name: tSalesforceInput_1
    type: tSalesforceInput
  - name: tFileOutputDelimited_1
    type: tFileOutputDelimited
connections:
  - from: tSalesforceInput_1
    to: tFileOutputDelimited_1
""",
        encoding="utf-8",
    )
    (screenshots_dir / "CRM_Export_Prospects.png").write_bytes(_TINY_PNG)

    names = generate_docs(items_dir, manual_dir, screenshots_dir, out_dir)

    assert set(names) == {"DWH_Load_Clients", "CRM_Export_Prospects"}
    assert (out_dir / "index.md").exists()
    assert (out_dir / "index.html").exists()
    assert (out_dir / "assets" / "style.css").exists()
    assert (out_dir / "jobs" / "dwh-load-clients.md").exists()
    assert (out_dir / "jobs" / "crm-export-prospects.html").exists()
    assert (out_dir / "assets" / "screenshots" / "crm-export-prospects.png").exists()
    assert (out_dir / "word" / "dwh-load-clients.docx").exists()
    assert (out_dir / "word" / "crm-export-prospects.docx").exists()

    dwh_md = (out_dir / "jobs" / "dwh-load-clients.md").read_text(encoding="utf-8")
    assert "Aucune capture d'écran associée" in dwh_md
    assert "```mermaid" in dwh_md

    crm_html = (out_dir / "jobs" / "crm-export-prospects.html").read_text(encoding="utf-8")
    assert "assets/screenshots/crm-export-prospects.png" in crm_html
