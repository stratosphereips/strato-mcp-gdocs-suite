"""Google Slides API wrappers."""
from __future__ import annotations

from typing import Any

from googleapiclient.discovery import Resource
from googleapiclient.errors import HttpError

from gdocs_suite_mcp.docs.drive import DocsApiError


def _extract_slide_titles(presentation: dict[str, Any]) -> list[str]:
    titles: list[str] = []
    for slide in presentation.get("slides", []):
        for element in slide.get("pageElements", []):
            shape = element.get("shape", {})
            text = shape.get("text", {})
            text_elements = text.get("textElements", [])
            content = "".join(
                te.get("textRun", {}).get("content", "") for te in text_elements
            ).strip()
            if content:
                titles.append(content)
                break
    return titles


def get_presentation(slides_client: Resource, presentation_id: str) -> dict[str, Any]:
    """Get presentation metadata and inferred slide titles."""
    try:
        presentation = (
            slides_client.presentations()
            .get(presentationId=presentation_id)
            .execute()
        )
        return {
            "presentationId": presentation.get("presentationId"),
            "title": presentation.get("title"),
            "slideCount": len(presentation.get("slides", [])),
            "slideTitles": _extract_slide_titles(presentation),
            "raw": presentation,
        }
    except HttpError as exc:
        raise DocsApiError(
            f"Failed to get presentation {presentation_id!r}: {exc}"
        ) from exc


def create_presentation(slides_client: Resource, title: str) -> dict[str, Any]:
    """Create a new presentation."""
    try:
        presentation = (
            slides_client.presentations()
            .create(body={"title": title})
            .execute()
        )
        return {
            "presentationId": presentation.get("presentationId"),
            "title": presentation.get("title", title),
        }
    except HttpError as exc:
        raise DocsApiError(f"Failed to create presentation: {exc}") from exc
