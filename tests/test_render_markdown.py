from talend_doc_gen.models import Component, Connection, Job
from talend_doc_gen.render_html import render_job_html
from talend_doc_gen.render_markdown import render_index_markdown, render_job_markdown


def make_job() -> Job:
    return Job(
        name="Demo_Job",
        description="Un job de démonstration.",
        owner="Equipe Data",
        schedule="Quotidien",
        source_systems=["CRM"],
        target_systems=["DWH"],
        components=[
            Component(name="tFileInputDelimited_1", type="tFileInputDelimited", description="Lit le CSV"),
            Component(name="tDBOutput_1", type="tDBOutput", description="Ecrit en base"),
        ],
        connections=[
            Connection(source="tFileInputDelimited_1", target="tDBOutput_1", label="Main", kind="flow"),
        ],
        notes="Attention aux doublons.",
    )


def test_render_job_markdown_with_screenshot():
    job = make_job()
    md = render_job_markdown(job, "../assets/screenshots/demo_job.png")

    assert "# Demo_Job" in md
    assert "![Capture d'écran du flux Demo_Job](../assets/screenshots/demo_job.png)" in md
    assert "```mermaid" in md
    assert "tFileInputDelimited_1" in md
    assert "Attention aux doublons." in md


def test_render_job_markdown_without_screenshot_still_has_diagram():
    job = make_job()
    md = render_job_markdown(job, None)

    assert "Aucune capture d'écran associée" in md
    assert "```mermaid" in md


def test_render_index_markdown_lists_jobs():
    job = make_job()
    md = render_index_markdown([("demo-job", job)])

    assert "[Demo_Job](jobs/demo-job.md)" in md
    assert "Equipe Data" in md


def test_render_job_html_contains_table_and_diagram():
    job = make_job()
    htm = render_job_html(job, "../assets/screenshots/demo_job.png")

    assert "<h1>Demo_Job</h1>" in htm
    assert 'src="../assets/screenshots/demo_job.png"' in htm
    assert 'class="mermaid"' in htm
    assert "tDBOutput_1" in htm
