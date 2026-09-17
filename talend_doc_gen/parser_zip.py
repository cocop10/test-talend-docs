"""Support des exports Talend livrés sous forme d'archive .zip.

Talend Studio permet d'exporter un ou plusieurs jobs sous forme de .zip
contenant les fichiers .item/.properties (parfois dans une arborescence de
type ``process/<JobName>/...``). Ce module extrait l'archive dans un dossier
temporaire et retourne la liste des fichiers .item trouvés, prêts à être
passés à :func:`talend_doc_gen.parser_item.load_job_from_item`.
"""

from __future__ import annotations

import tempfile
import zipfile
from pathlib import Path


def extract_item_files(zip_path: str | Path) -> tuple[Path, list[Path]]:
    """Extrait un .zip Talend dans un dossier temporaire.

    Retourne le dossier temporaire (à nettoyer par l'appelant si besoin) et
    la liste des fichiers .item trouvés dans l'archive.
    """
    zip_path = Path(zip_path)
    extract_dir = Path(tempfile.mkdtemp(prefix="talend_doc_gen_"))
    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(extract_dir)
    item_files = sorted(extract_dir.rglob("*.item"))
    return extract_dir, item_files
