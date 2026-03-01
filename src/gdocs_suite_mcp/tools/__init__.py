"""Shared utilities for MCP tool modules."""
from __future__ import annotations

import logging
import re

from gdocs_suite_mcp.docs.drive import DocsApiError

logger = logging.getLogger(__name__)

_HTTP_STATUS_RE = re.compile(r"HttpError\s+(\d{3})")


def sanitize_api_error(exc: DocsApiError) -> str:
    """Return a safe, client-facing error string for a DocsApiError."""
    logger.warning("Google API error: %s", exc)
    match = _HTTP_STATUS_RE.search(str(exc))
    if match:
        return f"Google API error ({match.group(1)})"
    return "Google API request failed"
