"""Google Docs wrapper tests."""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from googleapiclient.errors import HttpError

from google_docs_mcp.docs.documents import (
    batch_update,
    create_document,
    extract_plain_text,
    get_document,
)
from google_docs_mcp.docs.drive import DocsApiError


def _http_error(status: int) -> HttpError:
    resp = MagicMock()
    resp.status = status
    resp.reason = "error"
    return HttpError(resp=resp, content=b"error")


def test_extract_plain_text_from_document():
    document = {
        "body": {
            "content": [
                {
                    "paragraph": {
                        "elements": [
                            {"textRun": {"content": "Hello "}},
                            {"textRun": {"content": "world\n"}},
                        ]
                    }
                }
            ]
        }
    }

    assert extract_plain_text(document) == "Hello world"


def test_get_document_includes_text(mock_clients):
    docs = mock_clients["docs"]
    docs.documents().get.return_value.execute.return_value = {
        "documentId": "doc1",
        "title": "My Doc",
        "revisionId": "rev1",
        "body": {
            "content": [
                {"paragraph": {"elements": [{"textRun": {"content": "Hi\n"}}]}}
            ]
        },
    }

    result = get_document(docs, "doc1")

    assert result["documentId"] == "doc1"
    assert result["text"] == "Hi"


def test_create_document_returns_id_and_title(mock_clients):
    docs = mock_clients["docs"]
    docs.documents().create.return_value.execute.return_value = {
        "documentId": "doc-new",
        "title": "New",
    }

    result = create_document(docs, "New")

    assert result["documentId"] == "doc-new"


def test_batch_update_wraps_http_error(mock_clients):
    docs = mock_clients["docs"]
    docs.documents().batchUpdate.return_value.execute.side_effect = _http_error(400)

    with pytest.raises(DocsApiError):
        batch_update(docs, "doc1", [{"insertText": {}}])
