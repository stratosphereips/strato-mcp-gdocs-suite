"""MCP tool definitions for Google Slides."""
from __future__ import annotations

import json
import logging
from typing import Any

from gdocs_suite_mcp.docs.drive import DocsApiError, list_files
from gdocs_suite_mcp.docs.slides import create_presentation, get_presentation
from gdocs_suite_mcp.tools import sanitize_api_error

logger = logging.getLogger(__name__)

SLIDES_MIME_TYPE = "application/vnd.google-apps.presentation"


def _error(msg: str) -> str:
    return json.dumps({"error": msg})


def register_slides_tools(mcp: Any, get_clients: Any) -> None:
    """Register all presentation-related MCP tools."""

    @mcp.tool()
    def list_presentations_tool(max_results: int = 10, query: str = "") -> str:
        """List Google Slides files."""
        try:
            clients = get_clients()
            files = list_files(
                clients["drive"],
                SLIDES_MIME_TYPE,
                query=query,
                max_results=max_results,
            )
            return json.dumps({"presentations": files, "count": len(files)})
        except DocsApiError as exc:
            return _error(sanitize_api_error(exc))
        except Exception:
            logger.exception("Unexpected error in list_presentations_tool")
            return _error("An internal error occurred. Check server logs for details.")

    @mcp.tool()
    def get_presentation_tool(presentation_id: str) -> str:
        """Get presentation metadata and slide titles."""
        if not presentation_id.strip():
            return _error("presentation_id must not be empty")
        try:
            clients = get_clients()
            presentation = get_presentation(
                clients["slides"],
                presentation_id=presentation_id,
            )
            return json.dumps(presentation)
        except DocsApiError as exc:
            return _error(sanitize_api_error(exc))
        except Exception:
            logger.exception("Unexpected error in get_presentation_tool")
            return _error("An internal error occurred. Check server logs for details.")

    @mcp.tool()
    def create_presentation_tool(title: str) -> str:
        """Create a new presentation."""
        if not title.strip():
            return _error("title must not be empty")
        try:
            clients = get_clients()
            presentation = create_presentation(clients["slides"], title=title)
            return json.dumps(presentation)
        except DocsApiError as exc:
            return _error(sanitize_api_error(exc))
        except Exception:
            logger.exception("Unexpected error in create_presentation_tool")
            return _error("An internal error occurred. Check server logs for details.")
