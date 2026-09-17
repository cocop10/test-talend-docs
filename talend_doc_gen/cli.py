"""Orchestration : parse les jobs (exports Talend + métadonnées manuelles),
associe les captures d'écran, et génère le site de documentation.

Usage::

    python -m talend_doc_gen.cli generate \\
        --items-dir items \\
        --manual-dir jobs \\
        --screenshots-dir screenshots \\
        --out-dir docs
"""

from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path

from .loader_manual import load_manual_job, merge_jobs
from .models import Job
from .parser_item import load_job_from_item
from .parser_screenshot import guess_image_extension
from .parser_zip import extract_item_files
from .render_html import STYLE_CSS, render_index_html, render_job_html
from .render_markdown import render_index_markdown, render_job_markdown
from .screenshots import find_screenshot


def slugify(name: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "-", name).strip("-").lower()
    return slug or "job"


def collect_jobs(items_dir: Path | None, manual_dir: Path | None) -> dict[str, Job]:
    """Parse toutes les sources disponibles et fusionne par nom de job."""
    jobs: dict[str, Job] = {}
    tmp_dirs: list[Path] = []

    if items_dir and items_dir.is_dir():
        item_files = sorted(items_dir.glob("*.item"))
        for zip_path in sorted(items_dir.glob("*.zip")):
            tmp_dir, extracted = extract_item_files(zip_path)
            tmp_dirs.append(tmp_dir)
            item_files += extracted

        for item_path in item_files:
            job = load_job_from_item(item_path)
            jobs[job.name] = job

    if manual_dir and manual_dir.is_dir():
        for yaml_path in sorted(manual_dir.glob("*.yml")) + sorted(manual_dir.glob("*.yaml")):
            manual_job = load_manual_job(yaml_path)
            if manual_job.name in jobs:
                jobs[manual_job.name] = merge_jobs(jobs[manual_job.name], manual_job)
            else:
                jobs[manual_job.name] = manual_job

    for tmp_dir in tmp_dirs:
        shutil.rmtree(tmp_dir, ignore_errors=True)

    return jobs


def generate_docs(
    items_dir: Path | None,
    manual_dir: Path | None,
    screenshots_dir: Path | None,
    out_dir: Path,
    mask_context_values: bool = True,
) -> list[str]:
    jobs = collect_jobs(items_dir, manual_dir)

    jobs_dir = out_dir / "jobs"
    assets_dir = out_dir / "assets"
    screenshots_out_dir = assets_dir / "screenshots"
    for d in (out_dir, jobs_dir, assets_dir, screenshots_out_dir):
        d.mkdir(parents=True, exist_ok=True)

    (assets_dir / "style.css").write_text(STYLE_CSS, encoding="utf-8")

    entries: list[tuple[str, Job]] = []
    for job in jobs.values():
        slug = slugify(job.name)

        # Ordre de priorité pour la capture d'écran d'un job :
        #   1. override manuel explicite (champ `screenshot` du YAML) ;
        #   2. capture intégrée par Talend Studio dans l'export du job
        #      (fichier .screenshot) : toujours à jour et fidèle au canevas
        #      réel, sans rien à faire manuellement ;
        #   3. capture déposée à la main dans screenshots/, nommée d'après
        #      le job (utile quand il n'y a pas d'export .item).
        screenshot_src = None
        if job.screenshot:
            candidate = Path(job.screenshot)
            if candidate.is_absolute():
                if candidate.exists():
                    screenshot_src = candidate
            else:
                for root in (Path("."), manual_dir, screenshots_dir):
                    if root is None:
                        continue
                    resolved = root / candidate
                    if resolved.exists():
                        screenshot_src = resolved
                        break

        screenshot_rel = None
        if screenshot_src is not None:
            dest_name = f"{slug}{screenshot_src.suffix.lower()}"
            shutil.copyfile(screenshot_src, screenshots_out_dir / dest_name)
            screenshot_rel = f"../assets/screenshots/{dest_name}"
        elif job.embedded_screenshot:
            dest_name = f"{slug}{guess_image_extension(job.embedded_screenshot)}"
            (screenshots_out_dir / dest_name).write_bytes(job.embedded_screenshot)
            screenshot_rel = f"../assets/screenshots/{dest_name}"
        elif screenshots_dir:
            screenshot_src = find_screenshot(job.name, screenshots_dir)
            if screenshot_src is not None:
                dest_name = f"{slug}{screenshot_src.suffix.lower()}"
                shutil.copyfile(screenshot_src, screenshots_out_dir / dest_name)
                screenshot_rel = f"../assets/screenshots/{dest_name}"

        (jobs_dir / f"{slug}.md").write_text(
            render_job_markdown(job, screenshot_rel, mask_context_values=mask_context_values),
            encoding="utf-8",
        )
        (jobs_dir / f"{slug}.html").write_text(
            render_job_html(job, screenshot_rel, mask_context_values=mask_context_values),
            encoding="utf-8",
        )
        entries.append((slug, job))

    (out_dir / "index.md").write_text(render_index_markdown(entries), encoding="utf-8")
    (out_dir / "index.html").write_text(render_index_html(entries), encoding="utf-8")

    return [job.name for _, job in entries]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Génère la documentation des flux Talend.")
    sub = parser.add_subparsers(dest="command", required=True)

    gen = sub.add_parser("generate", help="Génère le site de documentation")
    gen.add_argument("--items-dir", type=Path, default=Path("items"))
    gen.add_argument("--manual-dir", type=Path, default=Path("jobs"))
    gen.add_argument("--screenshots-dir", type=Path, default=Path("screenshots"))
    gen.add_argument("--out-dir", type=Path, default=Path("docs"))
    gen.add_argument(
        "--show-context-values",
        action="store_true",
        help=(
            "Affiche les valeurs des paramètres de contexte (hôtes, identifiants, "
            "chemins...) en clair. Par défaut elles sont masquées car souvent "
            "sensibles (mots de passe chiffrés, noms de serveurs internes...). "
            "À utiliser uniquement dans un dépôt privé/de confiance."
        ),
    )

    args = parser.parse_args(argv)

    if args.command == "generate":
        names = generate_docs(
            args.items_dir,
            args.manual_dir,
            args.screenshots_dir,
            args.out_dir,
            mask_context_values=not args.show_context_values,
        )
        print(f"{len(names)} job(s) documenté(s) dans {args.out_dir}/ :")
        for name in sorted(names):
            print(f"  - {name}")
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
