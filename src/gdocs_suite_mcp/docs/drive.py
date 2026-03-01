"""Google Drive wrappers used for Docs/Sheets/Slides file listing and search."""
from __future__ import annotations

from typing import Any

from googleapiclient.discovery import Resource
from googleapiclient.errors import HttpError


class DocsApiError(Exception):
    """Raised when a Google Workspace API call fails."""


def _safe_max_results(max_results: int) -> int:
    return min(max(1, max_results), 100)


def _escape_query_value(value: str) -> str:
    return value.replace("'", "\\'")


def list_files(
    drive_client: Resource,
    mime_type: str,
    query: str = "",
    max_results: int = 10,
) -> list[dict[str, Any]]:
    """List files by MIME type, optionally filtered by name substring."""
    try:
        clauses = [f"mimeType='{mime_type}'", "trashed=false"]
        if query.strip():
            clauses.append(f"name contains '{_escape_query_value(query.strip())}'")

        result = (
            drive_client.files()
            .list(
                q=" and ".join(clauses),
                pageSize=_safe_max_results(max_results),
                fields=(
                    "files(id,name,mimeType,webViewLink,modifiedTime,createdTime,owners)"
                ),
                orderBy="modifiedTime desc",
            )
            .execute()
        )
        return result.get("files", [])
    except HttpError as exc:
        raise DocsApiError(f"Failed to list files: {exc}") from exc


def search_files(
    drive_client: Resource,
    mime_type: str,
    query: str,
    max_results: int = 10,
) -> list[dict[str, Any]]:
    """Search files by full text within files of a given MIME type."""
    try:
        q = (
            f"mimeType='{mime_type}' and trashed=false and "
            f"fullText contains '{_escape_query_value(query.strip())}'"
        )
        result = (
            drive_client.files()
            .list(
                q=q,
                pageSize=_safe_max_results(max_results),
                fields=(
                    "files(id,name,mimeType,webViewLink,modifiedTime,createdTime,owners)"
                ),
                orderBy="modifiedTime desc",
            )
            .execute()
        )
        return result.get("files", [])
    except HttpError as exc:
        raise DocsApiError(f"Failed to search files: {exc}") from exc
