"""MCP tool integration tests — validation and JSON contracts."""
from __future__ import annotations

import json
from unittest.mock import MagicMock

import pytest


class ToolRecorder:
    def __init__(self):
        self._tools: dict[str, callable] = {}

    def tool(self):
        def decorator(fn):
            self._tools[fn.__name__] = fn
            return fn

        return decorator

    def call(self, name: str, **kwargs):
        return self._tools[name](**kwargs)


class TestDocsTools:
    @pytest.fixture(autouse=True)
    def setup(self, mock_clients):
        from gdocs_suite_mcp.tools.docs import register_docs_tools

        self.recorder = ToolRecorder()
        self.clients = mock_clients
        register_docs_tools(self.recorder, lambda: self.clients)

    def test_list_documents_returns_json(self):
        self.clients["drive"].files().list.return_value.execute.return_value = {
            "files": [{"id": "d1", "name": "Doc"}]
        }
        result = json.loads(self.recorder.call("list_documents_tool"))
        assert result["count"] == 1

    def test_search_documents_rejects_empty_query(self):
        result = json.loads(self.recorder.call("search_documents_tool", query=" "))
        assert "error" in result

    def test_get_document_rejects_empty_id(self):
        result = json.loads(self.recorder.call("get_document_tool", document_id=""))
        assert "error" in result

    def test_create_document_with_content_issues_batch_update(self):
        self.clients["docs"].documents().create.return_value.execute.return_value = {
            "documentId": "d2",
            "title": "Doc 2",
        }
        json.loads(self.recorder.call("create_document_tool", title="Doc 2", content="Hello"))
        assert self.clients["docs"].documents().batchUpdate.called

    def test_update_document_requires_requests(self):
        result = json.loads(
            self.recorder.call("update_document_tool", document_id="d1", requests=[])
        )
        assert "error" in result


class TestSheetsTools:
    @pytest.fixture(autouse=True)
    def setup(self, mock_clients):
        from gdocs_suite_mcp.tools.sheets import register_sheets_tools

        self.recorder = ToolRecorder()
        self.clients = mock_clients
        register_sheets_tools(self.recorder, lambda: self.clients)

    def test_list_spreadsheets_returns_json(self):
        self.clients["drive"].files().list.return_value.execute.return_value = {
            "files": [{"id": "s1", "name": "Sheet"}]
        }
        result = json.loads(self.recorder.call("list_spreadsheets_tool"))
        assert result["count"] == 1

    def test_read_range_requires_inputs(self):
        result = json.loads(self.recorder.call("read_range_tool", spreadsheet_id="", range="A1"))
        assert "error" in result

    def test_write_range_requires_values_list(self):
        result = json.loads(
            self.recorder.call(
                "write_range_tool",
                spreadsheet_id="s1",
                range="Sheet1!A1",
                values="not-a-list",
            )
        )
        assert "error" in result


class TestSlidesTools:
    @pytest.fixture(autouse=True)
    def setup(self, mock_clients):
        from gdocs_suite_mcp.tools.slides import register_slides_tools

        self.recorder = ToolRecorder()
        self.clients = mock_clients
        register_slides_tools(self.recorder, lambda: self.clients)

    def test_list_presentations_returns_json(self):
        self.clients["drive"].files().list.return_value.execute.return_value = {
            "files": [{"id": "p1", "name": "Deck"}]
        }
        result = json.loads(self.recorder.call("list_presentations_tool"))
        assert result["count"] == 1

    def test_get_presentation_rejects_empty_id(self):
        result = json.loads(self.recorder.call("get_presentation_tool", presentation_id=""))
        assert "error" in result
