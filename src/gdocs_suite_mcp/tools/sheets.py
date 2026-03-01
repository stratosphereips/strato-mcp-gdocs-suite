"""MCP tool definitions for Google Sheets."""
from __future__ import annotations

import json
import logging
from typing import Any

from gdocs_suite_mcp.docs.drive import DocsApiError, list_files
from gdocs_suite_mcp.docs.sheets import (
    append_rows,
    create_spreadsheet,
    get_spreadsheet,
    read_range,
    write_range,
)
from gdocs_suite_mcp.tools import sanitize_api_error

logger = logging.getLogger(__name__)

SHEETS_MIME_TYPE = "application/vnd.google-apps.spreadsheet"


def _error(msg: str) -> str:
    return json.dumps({"error": msg})


def register_sheets_tools(mcp: Any, get_clients: Any) -> None:
    """Register all spreadsheet-related MCP tools."""

    @mcp.tool()
    def list_spreadsheets_tool(max_results: int = 10, query: str = "") -> str:
        """List Google Sheets files."""
        try:
            clients = get_clients()
            files = list_files(
                clients["drive"],
                SHEETS_MIME_TYPE,
                query=query,
                max_results=max_results,
            )
            return json.dumps({"spreadsheets": files, "count": len(files)})
        except DocsApiError as exc:
            return _error(sanitize_api_error(exc))
        except Exception:
            logger.exception("Unexpected error in list_spreadsheets_tool")
            return _error("An internal error occurred. Check server logs for details.")

    @mcp.tool()
    def get_spreadsheet_tool(spreadsheet_id: str) -> str:
        """Get spreadsheet metadata and sheet names."""
        if not spreadsheet_id.strip():
            return _error("spreadsheet_id must not be empty")
        try:
            clients = get_clients()
            spreadsheet = get_spreadsheet(
                clients["sheets"],
                spreadsheet_id=spreadsheet_id,
            )
            return json.dumps(spreadsheet)
        except DocsApiError as exc:
            return _error(sanitize_api_error(exc))
        except Exception:
            logger.exception("Unexpected error in get_spreadsheet_tool")
            return _error("An internal error occurred. Check server logs for details.")

    @mcp.tool()
    def create_spreadsheet_tool(title: str) -> str:
        """Create a new spreadsheet."""
        if not title.strip():
            return _error("title must not be empty")
        try:
            clients = get_clients()
            spreadsheet = create_spreadsheet(clients["sheets"], title=title)
            return json.dumps(spreadsheet)
        except DocsApiError as exc:
            return _error(sanitize_api_error(exc))
        except Exception:
            logger.exception("Unexpected error in create_spreadsheet_tool")
            return _error("An internal error occurred. Check server logs for details.")

    @mcp.tool()
    def read_range_tool(spreadsheet_id: str, range: str) -> str:
        """Read values from a spreadsheet range."""
        if not spreadsheet_id.strip():
            return _error("spreadsheet_id must not be empty")
        if not range.strip():
            return _error("range must not be empty")
        try:
            clients = get_clients()
            values = read_range(clients["sheets"], spreadsheet_id=spreadsheet_id, range_=range)
            return json.dumps({"values": values, "count": len(values)})
        except DocsApiError as exc:
            return _error(sanitize_api_error(exc))
        except Exception:
            logger.exception("Unexpected error in read_range_tool")
            return _error("An internal error occurred. Check server logs for details.")

    @mcp.tool()
    def write_range_tool(spreadsheet_id: str, range: str, values: list[list[Any]]) -> str:
        """Write values to a spreadsheet range."""
        if not spreadsheet_id.strip():
            return _error("spreadsheet_id must not be empty")
        if not range.strip():
            return _error("range must not be empty")
        if not isinstance(values, list):
            return _error("values must be a list of rows")
        try:
            clients = get_clients()
            result = write_range(
                clients["sheets"],
                spreadsheet_id=spreadsheet_id,
                range_=range,
                values=values,
            )
            return json.dumps(result)
        except DocsApiError as exc:
            return _error(sanitize_api_error(exc))
        except Exception:
            logger.exception("Unexpected error in write_range_tool")
            return _error("An internal error occurred. Check server logs for details.")

    @mcp.tool()
    def append_rows_tool(spreadsheet_id: str, range: str, values: list[list[Any]]) -> str:
        """Append rows in a spreadsheet range."""
        if not spreadsheet_id.strip():
            return _error("spreadsheet_id must not be empty")
        if not range.strip():
            return _error("range must not be empty")
        if not isinstance(values, list):
            return _error("values must be a list of rows")
        try:
            clients = get_clients()
            result = append_rows(
                clients["sheets"],
                spreadsheet_id=spreadsheet_id,
                range_=range,
                values=values,
            )
            return json.dumps(result)
        except DocsApiError as exc:
            return _error(sanitize_api_error(exc))
        except Exception:
            logger.exception("Unexpected error in append_rows_tool")
            return _error("An internal error occurred. Check server logs for details.")
