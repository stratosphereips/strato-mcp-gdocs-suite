"""MCP tool integration tests for Google Forms."""
from __future__ import annotations

import json
from unittest.mock import MagicMock

import pytest
from googleapiclient.errors import HttpError

from gdocs_suite_mcp.docs.drive import DocsApiError


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


class TestFormsTools:
    @pytest.fixture(autouse=True)
    def setup(self, mock_clients):
        from gdocs_suite_mcp.tools.forms import register_forms_tools

        self.recorder = ToolRecorder()
        self.clients = mock_clients
        register_forms_tools(self.recorder, lambda: self.clients)

    def test_list_forms_returns_json(self):
        self.clients["drive"].files().list.return_value.execute.return_value = {
            "files": [{"id": "f1", "name": "Form A"}]
        }
        result = json.loads(self.recorder.call("list_forms_tool"))
        assert result["count"] == 1
        assert result["forms"][0]["name"] == "Form A"

    def test_get_form_returns_metadata(self):
        result = json.loads(self.recorder.call("get_form_tool", form_id="form1"))
        assert result["formId"] == "form1"
        assert result["title"] == "My Form"

    def test_get_form_rejects_empty_id(self):
        result = json.loads(self.recorder.call("get_form_tool", form_id=""))
        assert "error" in result

    def test_create_form_returns_form_id(self):
        result = json.loads(self.recorder.call("create_form_tool", title="New Form"))
        assert result["formId"] == "form-new"

    def test_create_form_rejects_empty_title(self):
        result = json.loads(self.recorder.call("create_form_tool", title=""))
        assert "error" in result

    def test_create_form_with_description_calls_batch_update(self):
        self.recorder.call("create_form_tool", title="Form", description="desc")
        # batchUpdate should have been called once for description
        assert self.clients["forms"].forms().batchUpdate.called

    def test_add_question_text_type(self):
        result = json.loads(
            self.recorder.call(
                "add_question_tool",
                form_id="form1",
                question_type="text",
                title="What is your name?",
            )
        )
        assert result["formId"] == "form1"
        assert result["itemId"] == "item1"

    def test_add_question_rejects_empty_form_id(self):
        result = json.loads(
            self.recorder.call(
                "add_question_tool",
                form_id="",
                question_type="text",
                title="Q",
            )
        )
        assert "error" in result

    def test_update_form_info_updates_title(self):
        result = json.loads(
            self.recorder.call(
                "update_form_info_tool", form_id="form1", title="Updated Title"
            )
        )
        assert result["formId"] == "form1"
        assert "title" in result["updated"]

    def test_update_form_info_rejects_no_fields(self):
        result = json.loads(
            self.recorder.call("update_form_info_tool", form_id="form1")
        )
        assert "error" in result

    def test_delete_item_returns_deleted_id(self):
        result = json.loads(
            self.recorder.call("delete_item_tool", form_id="form1", item_id="item1")
        )
        assert result["deletedItemId"] == "item1"

    def test_delete_item_rejects_empty_item_id(self):
        result = json.loads(
            self.recorder.call("delete_item_tool", form_id="form1", item_id="")
        )
        assert "error" in result

    def test_list_responses_returns_json(self):
        self.clients["forms"].forms().responses().list.return_value.execute.return_value = {
            "responses": [{"responseId": "r1"}]
        }
        result = json.loads(self.recorder.call("list_responses_tool", form_id="form1"))
        assert result["count"] == 1

    def test_list_responses_rejects_empty_form_id(self):
        result = json.loads(self.recorder.call("list_responses_tool", form_id=""))
        assert "error" in result

    def test_get_response_returns_response(self):
        result = json.loads(
            self.recorder.call(
                "get_response_tool", form_id="form1", response_id="resp1"
            )
        )
        assert result["responseId"] == "resp1"

    def test_get_response_rejects_empty_response_id(self):
        result = json.loads(
            self.recorder.call("get_response_tool", form_id="form1", response_id="")
        )
        assert "error" in result

    def test_api_error_returns_error_json(self):
        from unittest.mock import patch

        with patch(
            "gdocs_suite_mcp.tools.forms.get_form",
            side_effect=DocsApiError("HttpError 403"),
        ):
            result = json.loads(self.recorder.call("get_form_tool", form_id="form1"))
            assert "error" in result
            assert "403" in result["error"]
