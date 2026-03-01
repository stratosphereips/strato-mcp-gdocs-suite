"""Google Sheets wrapper tests."""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from googleapiclient.errors import HttpError

from gdocs_suite_mcp.docs.drive import DocsApiError
from gdocs_suite_mcp.docs.sheets import (
    append_rows,
    create_spreadsheet,
    get_spreadsheet,
    read_range,
    write_range,
)


def _http_error(status: int) -> HttpError:
    resp = MagicMock()
    resp.status = status
    resp.reason = "error"
    return HttpError(resp=resp, content=b"error")


def test_get_spreadsheet_returns_sheet_names(mock_clients):
    sheets = mock_clients["sheets"]

    result = get_spreadsheet(sheets, "sheet1")

    assert result["spreadsheetId"] == "sheet1"
    assert "Sheet1" in result["sheets"]


def test_create_spreadsheet_returns_metadata(mock_clients):
    sheets = mock_clients["sheets"]

    result = create_spreadsheet(sheets, "Budget")

    assert result["spreadsheetId"] == "sheet-new"


def test_read_write_append_range(mock_clients):
    sheets = mock_clients["sheets"]

    values = read_range(sheets, "sheet1", "Sheet1!A1:A1")
    assert values == [["A1"]]

    write_result = write_range(sheets, "sheet1", "Sheet1!A1", [["x"]])
    assert write_result["updatedRows"] == 1

    append_result = append_rows(sheets, "sheet1", "Sheet1!A1", [["y"]])
    assert append_result["updates"]["updatedRows"] == 1


def test_read_range_wraps_http_error(mock_clients):
    sheets = mock_clients["sheets"]
    sheets.spreadsheets().values().get.return_value.execute.side_effect = _http_error(403)

    with pytest.raises(DocsApiError):
        read_range(sheets, "sheet1", "Sheet1!A1")
