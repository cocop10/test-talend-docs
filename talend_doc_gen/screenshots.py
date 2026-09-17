"""Association automatique d'une capture d'écran à un job.

Convention : déposer dans le dossier des captures un fichier dont le nom
(sans extension) correspond au nom du job, insensible à la casse et aux
espaces/underscores/tirets (ex: job "DWH Load Customers" <-> fichier
``dwh_load_customers.png``). Formats acceptés : png, jpg, jpeg, gif, webp.
"""

from __future__ import annotations

from pathlib import Path

_EXTENSIONS = (".png", ".jpg", ".jpeg", ".gif", ".webp")


def _normalize(name: str) -> str:
    return "".join(ch.lower() for ch in name if ch.isalnum())


def find_screenshot(job_name: str, screenshots_dir: str | Path) -> Path | None:
    screenshots_dir = Path(screenshots_dir)
    if not screenshots_dir.is_dir():
        return None

    target = _normalize(job_name)
    for candidate in sorted(screenshots_dir.iterdir()):
        if candidate.suffix.lower() not in _EXTENSIONS:
            continue
        if _normalize(candidate.stem) == target:
            return candidate
    return None
