"""MCP tool definitions for Google Docs."""
from __future__ import annotations

import json
import logging
from typing import Any

from google_docs_mcp.docs.documents import batch_update, create_document, get_document
from google_docs_mcp.docs.drive import DocsApiError, list_files, search_files
from google_docs_mcp.tools import sanitize_api_error

logger = logging.getLogger(__name__)

DOCS_MIME_TYPE = "application/vnd.google-apps.document"


def _error(msg: str) -> str:
    return json.dumps({"error": msg})


def register_docs_tools(mcp: Any, get_clients: Any) -> None:
    """Register all document-related MCP tools."""

    @mcp.tool()
    def list_documents_tool(max_results: int = 10, query: str = "") -> str:
        """List Google Docs files."""
        try:
            clients = get_clients()
            files = list_files(
                clients["drive"],
                DOCS_MIME_TYPE,
                query=query,
                max_results=max_results,
            )
            return json.dumps({"documents": files, "count": len(files)})
        except DocsApiError as exc:
            return _error(sanitize_api_error(exc))
        except Exception:
            logger.exception("Unexpected error in list_documents_tool")
            return _error("An internal error occurred. Check server logs for details.")

    @mcp.tool()
    def search_documents_tool(query: str, max_results: int = 10) -> str:
        """Search Google Docs by full text."""
        if not query.strip():
            return _error("query must not be empty")
        try:
            clients = get_clients()
            files = search_files(
                clients["drive"],
                DOCS_MIME_TYPE,
                query=query,
                max_results=max_results,
            )
            return json.dumps({"documents": files, "count": len(files)})
        except DocsApiError as exc:
            return _error(sanitize_api_error(exc))
        except Exception:
            logger.exception("Unexpected error in search_documents_tool")
            return _error("An internal error occurred. Check server logs for details.")

    @mcp.tool()
    def get_document_tool(document_id: str) -> str:
        """Get document content and metadata."""
        if not document_id.strip():
            return _error("document_id must not be empty")
        try:
            clients = get_clients()
            document = get_document(clients["docs"], document_id=document_id)
            return json.dumps(document)
        except DocsApiError as exc:
            return _error(sanitize_api_error(exc))
        except Exception:
            logger.exception("Unexpected error in get_document_tool")
            return _error("An internal error occurred. Check server logs for details.")

    @mcp.tool()
    def create_document_tool(title: str, content: str = "") -> str:
        """Create a new document, optionally with content."""
        if not title.strip():
            return _error("title must not be empty")
        try:
            clients = get_clients()
            created = create_document(clients["docs"], title=title)
            if content:
                batch_update(
                    clients["docs"],
                    document_id=created["documentId"],
                    requests=[
                        {
                            "insertText": {
                                "location": {"index": 1},
                                "text": content,
                            }
                        }
                    ],
                )
            return json.dumps(created)
        except DocsApiError as exc:
            return _error(sanitize_api_error(exc))
        except Exception:
            logger.exception("Unexpected error in create_document_tool")
            return _error("An internal error occurred. Check server logs for details.")

    @mcp.tool()
    def update_document_tool(document_id: str, requests: list[dict[str, Any]]) -> str:
        """Apply Docs API batch update requests to a document."""
        if not document_id.strip():
            return _error("document_id must not be empty")
        if not isinstance(requests, list) or not requests:
            return _error("requests must be a non-empty list")
        try:
            clients = get_clients()
            result = batch_update(
                clients["docs"],
                document_id=document_id,
                requests=requests,
            )
            return json.dumps(result)
        except DocsApiError as exc:
            return _error(sanitize_api_error(exc))
        except Exception:
            logger.exception("Unexpected error in update_document_tool")
            return _error("An internal error occurred. Check server logs for details.")
