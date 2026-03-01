"""Google Docs API wrappers."""
from __future__ import annotations

from typing import Any

from googleapiclient.discovery import Resource
from googleapiclient.errors import HttpError

from google_docs_mcp.docs.drive import DocsApiError


def extract_plain_text(document: dict[str, Any]) -> str:
    """Extract plain text from a Docs API document resource."""
    chunks: list[str] = []
    for content in document.get("body", {}).get("content", []):
        paragraph = content.get("paragraph")
        if not paragraph:
            continue
        for element in paragraph.get("elements", []):
            text_run = element.get("textRun")
            if text_run and "content" in text_run:
                chunks.append(text_run["content"])
    return "".join(chunks).strip()


def get_document(docs_client: Resource, document_id: str) -> dict[str, Any]:
    """Get a document and include extracted plain text."""
    try:
        doc = docs_client.documents().get(documentId=document_id).execute()
        return {
            "documentId": doc.get("documentId"),
            "title": doc.get("title"),
            "revisionId": doc.get("revisionId"),
            "text": extract_plain_text(doc),
            "raw": doc,
        }
    except HttpError as exc:
        raise DocsApiError(f"Failed to get document {document_id!r}: {exc}") from exc


def create_document(docs_client: Resource, title: str) -> dict[str, Any]:
    """Create a new Google Doc."""
    try:
        result = docs_client.documents().create(body={"title": title}).execute()
        return {
            "documentId": result.get("documentId"),
            "title": result.get("title", title),
        }
    except HttpError as exc:
        raise DocsApiError(f"Failed to create document: {exc}") from exc


def batch_update(
    docs_client: Resource,
    document_id: str,
    requests: list[dict[str, Any]],
) -> dict[str, Any]:
    """Run a batchUpdate request against a Google Doc."""
    try:
        return (
            docs_client.documents()
            .batchUpdate(documentId=document_id, body={"requests": requests})
            .execute()
        )
    except HttpError as exc:
        raise DocsApiError(f"Failed to update document {document_id!r}: {exc}") from exc
