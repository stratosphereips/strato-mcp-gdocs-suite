"""Google Sheets API wrappers."""
from __future__ import annotations

from typing import Any

from googleapiclient.discovery import Resource
from googleapiclient.errors import HttpError

from gdocs_suite_mcp.docs.drive import DocsApiError


def get_spreadsheet(sheets_client: Resource, spreadsheet_id: str) -> dict[str, Any]:
    """Get spreadsheet metadata and list of sheet names."""
    try:
        spreadsheet = (
            sheets_client.spreadsheets()
            .get(spreadsheetId=spreadsheet_id)
            .execute()
        )
        return {
            "spreadsheetId": spreadsheet.get("spreadsheetId"),
            "title": spreadsheet.get("properties", {}).get("title"),
            "sheets": [
                s.get("properties", {}).get("title")
                for s in spreadsheet.get("sheets", [])
                if s.get("properties", {}).get("title")
            ],
            "raw": spreadsheet,
        }
    except HttpError as exc:
        raise DocsApiError(f"Failed to get spreadsheet {spreadsheet_id!r}: {exc}") from exc


def create_spreadsheet(sheets_client: Resource, title: str) -> dict[str, Any]:
    """Create a new spreadsheet."""
    try:
        spreadsheet = (
            sheets_client.spreadsheets()
            .create(body={"properties": {"title": title}})
            .execute()
        )
        return {
            "spreadsheetId": spreadsheet.get("spreadsheetId"),
            "title": spreadsheet.get("properties", {}).get("title", title),
        }
    except HttpError as exc:
        raise DocsApiError(f"Failed to create spreadsheet: {exc}") from exc


def read_range(
    sheets_client: Resource,
    spreadsheet_id: str,
    range_: str,
    value_render_option: str = "FORMATTED_VALUE",
) -> list[list[Any]]:
    """Read values from a spreadsheet range."""
    try:
        result = (
            sheets_client.spreadsheets()
            .values()
            .get(
                spreadsheetId=spreadsheet_id,
                range=range_,
                valueRenderOption=value_render_option,
            )
            .execute()
        )
        return result.get("values", [])
    except HttpError as exc:
        raise DocsApiError(
            f"Failed to read range {range_!r} in spreadsheet {spreadsheet_id!r}: {exc}"
        ) from exc


def write_range(
    sheets_client: Resource,
    spreadsheet_id: str,
    range_: str,
    values: list[list[Any]],
    value_input_option: str = "USER_ENTERED",
) -> dict[str, Any]:
    """Write values to a spreadsheet range."""
    try:
        return (
            sheets_client.spreadsheets()
            .values()
            .update(
                spreadsheetId=spreadsheet_id,
                range=range_,
                valueInputOption=value_input_option,
                body={"values": values},
            )
            .execute()
        )
    except HttpError as exc:
        raise DocsApiError(
            f"Failed to write range {range_!r} in spreadsheet {spreadsheet_id!r}: {exc}"
        ) from exc


def append_rows(
    sheets_client: Resource,
    spreadsheet_id: str,
    range_: str,
    values: list[list[Any]],
) -> dict[str, Any]:
    """Append rows to a spreadsheet range."""
    try:
        return (
            sheets_client.spreadsheets()
            .values()
            .append(
                spreadsheetId=spreadsheet_id,
                range=range_,
                valueInputOption="USER_ENTERED",
                insertDataOption="INSERT_ROWS",
                body={"values": values},
            )
            .execute()
        )
    except HttpError as exc:
        raise DocsApiError(
            f"Failed to append rows to range {range_!r} in spreadsheet {spreadsheet_id!r}: {exc}"
        ) from exc
