"""Drive wrapper tests."""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from googleapiclient.errors import HttpError

from google_docs_mcp.docs.drive import DocsApiError, list_files, search_files


def _http_error(status: int) -> HttpError:
    resp = MagicMock()
    resp.status = status
    resp.reason = "error"
    return HttpError(resp=resp, content=b"error")


def test_list_files_builds_query_and_returns_files(mock_clients):
    drive = mock_clients["drive"]
    drive.files().list.return_value.execute.return_value = {
        "files": [{"id": "1", "name": "Doc"}]
    }

    files = list_files(drive, "application/vnd.google-apps.document", query="Report")

    assert len(files) == 1
    called_q = drive.files().list.call_args.kwargs["q"]
    assert "mimeType='application/vnd.google-apps.document'" in called_q
    assert "name contains 'Report'" in called_q


def test_search_files_uses_fulltext(mock_clients):
    drive = mock_clients["drive"]

    search_files(drive, "application/vnd.google-apps.presentation", "roadmap")

    called_q = drive.files().list.call_args.kwargs["q"]
    assert "fullText contains 'roadmap'" in called_q


def test_list_files_wraps_http_error(mock_clients):
    drive = mock_clients["drive"]
    drive.files().list.return_value.execute.side_effect = _http_error(403)

    with pytest.raises(DocsApiError):
        list_files(drive, "application/vnd.google-apps.spreadsheet")
