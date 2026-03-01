"""Google Slides wrapper tests."""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from googleapiclient.errors import HttpError

from gdocs_suite_mcp.docs.drive import DocsApiError
from gdocs_suite_mcp.docs.slides import create_presentation, get_presentation


def _http_error(status: int) -> HttpError:
    resp = MagicMock()
    resp.status = status
    resp.reason = "error"
    return HttpError(resp=resp, content=b"error")


def test_get_presentation_extracts_slide_titles(mock_clients):
    slides = mock_clients["slides"]
    slides.presentations().get.return_value.execute.return_value = {
        "presentationId": "p1",
        "title": "Deck",
        "slides": [
            {
                "pageElements": [
                    {
                        "shape": {
                            "text": {
                                "textElements": [
                                    {"textRun": {"content": "Title Slide\n"}}
                                ]
                            }
                        }
                    }
                ]
            }
        ],
    }

    result = get_presentation(slides, "p1")

    assert result["slideCount"] == 1
    assert result["slideTitles"] == ["Title Slide"]


def test_create_presentation_returns_id(mock_clients):
    slides = mock_clients["slides"]

    result = create_presentation(slides, "QBR")

    assert result["presentationId"] == "pres-new"


def test_get_presentation_wraps_http_error(mock_clients):
    slides = mock_clients["slides"]
    slides.presentations().get.return_value.execute.side_effect = _http_error(404)

    with pytest.raises(DocsApiError):
        get_presentation(slides, "missing")
