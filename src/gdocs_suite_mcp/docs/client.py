"""Google API client builders."""
from __future__ import annotations

from googleapiclient.discovery import Resource, build


def build_clients(credentials) -> dict[str, Resource]:
    """Build docs/sheets/slides/drive clients from one credentials object."""
    return {
        "docs": build("docs", "v1", credentials=credentials),
        "sheets": build("sheets", "v4", credentials=credentials),
        "slides": build("slides", "v1", credentials=credentials),
        "drive": build("drive", "v3", credentials=credentials),
    }
