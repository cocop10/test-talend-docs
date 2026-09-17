"""Extraction de la capture d'écran du canevas, intégrée par Talend Studio
dans l'export d'un job.

Talend exporte, en plus du ``.item``/``.properties``, un fichier
``<job>_<version>.screenshot`` : un XMI ``talendfile:ScreenshotsMap`` dont
l'attribut ``value`` contient l'image du canevas encodée en base64. Quand ce
fichier est présent, il n'y a donc rien à capturer manuellement : la
capture est utilisée automatiquement.
"""

from __future__ import annotations

import base64
from pathlib import Path

_PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
_JPEG_MAGIC = b"\xff\xd8"


def guess_image_extension(data: bytes) -> str:
    if data.startswith(_PNG_MAGIC):
        return ".png"
    if data.startswith(_JPEG_MAGIC):
        return ".jpg"
    return ".png"


def extract_embedded_screenshot(item_path: str | Path) -> bytes | None:
    """Retourne les octets de l'image embarquée dans le fichier
    ``.screenshot`` associé à ``item_path``, ou ``None`` s'il est absent."""
    item_path = Path(item_path)
    screenshot_path = item_path.with_suffix(".screenshot")
    if not screenshot_path.exists():
        return None

    text = screenshot_path.read_text(encoding="utf-8", errors="replace")
    marker = 'value="'
    start = text.find(marker)
    if start == -1:
        return None
    start += len(marker)
    end = text.find('"', start)
    if end == -1:
        return None
    encoded = text[start:end]

    try:
        return base64.b64decode(encoded)
    except (ValueError, TypeError):
        return None
