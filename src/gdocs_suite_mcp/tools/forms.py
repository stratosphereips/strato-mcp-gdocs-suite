"""MCP tool definitions for Google Forms."""
from __future__ import annotations

import json
import logging
from typing import Any

from gdocs_suite_mcp.docs.drive import DocsApiError
from gdocs_suite_mcp.docs.forms import (
    add_page_break,
    add_question,
    add_text_item,
    create_form,
    delete_item,
    get_form,
    get_response,
    list_forms,
    list_responses,
    move_item,
    update_form_info,
    update_form_settings,
)
from gdocs_suite_mcp.tools import sanitize_api_error

logger = logging.getLogger(__name__)


def _error(msg: str) -> str:
    return json.dumps({"error": msg})


def register_forms_tools(mcp: Any, get_clients: Any) -> None:
    """Register all Forms-related MCP tools."""

    @mcp.tool()
    def list_forms_tool(max_results: int = 10, query: str = "") -> str:
        """List Google Forms files."""
        try:
            clients = get_clients()
            files = list_forms(clients["drive"], max_results=max_results, query=query)
            return json.dumps({"forms": files, "count": len(files)})
        except DocsApiError as exc:
            return _error(sanitize_api_error(exc))
        except Exception:
            logger.exception("Unexpected error in list_forms_tool")
            return _error("An internal error occurred. Check server logs for details.")

    @mcp.tool()
    def get_form_tool(form_id: str) -> str:
        """Get form metadata, description, and all items/questions."""
        if not form_id.strip():
            return _error("form_id must not be empty")
        try:
            clients = get_clients()
            form = get_form(clients["forms"], form_id=form_id)
            return json.dumps(form)
        except DocsApiError as exc:
            return _error(sanitize_api_error(exc))
        except Exception:
            logger.exception("Unexpected error in get_form_tool")
            return _error("An internal error occurred. Check server logs for details.")

    @mcp.tool()
    def create_form_tool(title: str, description: str = "") -> str:
        """Create a new Google Form with a title and optional description."""
        if not title.strip():
            return _error("title must not be empty")
        try:
            clients = get_clients()
            result = create_form(clients["forms"], title=title, description=description)
            return json.dumps(result)
        except DocsApiError as exc:
            return _error(sanitize_api_error(exc))
        except Exception:
            logger.exception("Unexpected error in create_form_tool")
            return _error("An internal error occurred. Check server logs for details.")

    @mcp.tool()
    def add_question_tool(
        form_id: str,
        question_type: str,
        title: str,
        required: bool = False,
        index: int | None = None,
        options: list[str] | None = None,
        description: str = "",
    ) -> str:
        """Add a question to a form.

        question_type must be one of: text, paragraph, multiple_choice,
        checkbox, dropdown, scale, date, time.
        options is used for multiple_choice, checkbox, and dropdown types.
        description is the help text shown below the question title.
        """
        if not form_id.strip():
            return _error("form_id must not be empty")
        if not title.strip():
            return _error("title must not be empty")
        if not question_type.strip():
            return _error("question_type must not be empty")
        try:
            clients = get_clients()
            result = add_question(
                clients["forms"],
                form_id=form_id,
                question_type=question_type,
                title=title,
                required=required,
                index=index,
                options=options,
                description=description,
            )
            return json.dumps(result)
        except DocsApiError as exc:
            return _error(sanitize_api_error(exc))
        except Exception:
            logger.exception("Unexpected error in add_question_tool")
            return _error("An internal error occurred. Check server logs for details.")

    @mcp.tool()
    def update_form_info_tool(
        form_id: str, title: str = "", description: str = ""
    ) -> str:
        """Update a form's title and/or description."""
        if not form_id.strip():
            return _error("form_id must not be empty")
        if not title.strip() and not description.strip():
            return _error("At least one of title or description must be provided")
        try:
            clients = get_clients()
            result = update_form_info(
                clients["forms"],
                form_id=form_id,
                title=title,
                description=description,
            )
            return json.dumps(result)
        except DocsApiError as exc:
            return _error(sanitize_api_error(exc))
        except Exception:
            logger.exception("Unexpected error in update_form_info_tool")
            return _error("An internal error occurred. Check server logs for details.")

    @mcp.tool()
    def delete_item_tool(form_id: str, item_id: str) -> str:
        """Delete a question/item from a form by item ID."""
        if not form_id.strip():
            return _error("form_id must not be empty")
        if not item_id.strip():
            return _error("item_id must not be empty")
        try:
            clients = get_clients()
            result = delete_item(clients["forms"], form_id=form_id, item_id=item_id)
            return json.dumps(result)
        except DocsApiError as exc:
            return _error(sanitize_api_error(exc))
        except Exception:
            logger.exception("Unexpected error in delete_item_tool")
            return _error("An internal error occurred. Check server logs for details.")

    @mcp.tool()
    def list_responses_tool(form_id: str, max_results: int = 100) -> str:
        """List all responses for a form."""
        if not form_id.strip():
            return _error("form_id must not be empty")
        try:
            clients = get_clients()
            responses = list_responses(
                clients["forms"], form_id=form_id, max_results=max_results
            )
            return json.dumps({"responses": responses, "count": len(responses)})
        except DocsApiError as exc:
            return _error(sanitize_api_error(exc))
        except Exception:
            logger.exception("Unexpected error in list_responses_tool")
            return _error("An internal error occurred. Check server logs for details.")

    @mcp.tool()
    def get_response_tool(form_id: str, response_id: str) -> str:
        """Get a single form response by response ID."""
        if not form_id.strip():
            return _error("form_id must not be empty")
        if not response_id.strip():
            return _error("response_id must not be empty")
        try:
            clients = get_clients()
            response = get_response(
                clients["forms"], form_id=form_id, response_id=response_id
            )
            return json.dumps(response)
        except DocsApiError as exc:
            return _error(sanitize_api_error(exc))
        except Exception:
            logger.exception("Unexpected error in get_response_tool")
            return _error("An internal error occurred. Check server logs for details.")

    @mcp.tool()
    def move_item_tool(form_id: str, original_index: int, new_index: int) -> str:
        """Move a form item from original_index to new_index.

        Both indices are 0-based positions in the form's item list.
        Use get_form_tool to see current item order and indices.
        """
        if not form_id.strip():
            return _error("form_id must not be empty")
        try:
            clients = get_clients()
            result = move_item(
                clients["forms"],
                form_id=form_id,
                original_index=original_index,
                new_index=new_index,
            )
            return json.dumps(result)
        except DocsApiError as exc:
            return _error(sanitize_api_error(exc))
        except Exception:
            logger.exception("Unexpected error in move_item_tool")
            return _error("An internal error occurred. Check server logs for details.")

    @mcp.tool()
    def add_text_item_tool(
        form_id: str, title: str, description: str = "", index: int = 0
    ) -> str:
        """Add a section header (text item) to a form.

        Text items display a title and optional description — useful for
        grouping questions under named sections.
        index is the 0-based position to insert the item at.
        """
        if not form_id.strip():
            return _error("form_id must not be empty")
        if not title.strip():
            return _error("title must not be empty")
        try:
            clients = get_clients()
            result = add_text_item(
                clients["forms"],
                form_id=form_id,
                title=title,
                description=description,
                index=index,
            )
            return json.dumps(result)
        except DocsApiError as exc:
            return _error(sanitize_api_error(exc))
        except Exception:
            logger.exception("Unexpected error in add_text_item_tool")
            return _error("An internal error occurred. Check server logs for details.")

    @mcp.tool()
    def add_page_break_tool(
        form_id: str, title: str = "", index: int = 0
    ) -> str:
        """Add a page break to a form, starting a new section/page.

        An optional title is displayed at the top of the new page.
        index is the 0-based position to insert the page break at.
        """
        if not form_id.strip():
            return _error("form_id must not be empty")
        try:
            clients = get_clients()
            result = add_page_break(
                clients["forms"],
                form_id=form_id,
                title=title,
                index=index,
            )
            return json.dumps(result)
        except DocsApiError as exc:
            return _error(sanitize_api_error(exc))
        except Exception:
            logger.exception("Unexpected error in add_page_break_tool")
            return _error("An internal error occurred. Check server logs for details.")

    @mcp.tool()
    def update_form_settings_tool(
        form_id: str,
        email_collection_type: str = "",
        is_quiz: bool | None = None,
    ) -> str:
        """Update form settings.

        email_collection_type controls email collection:
          - DO_NOT_COLLECT: do not collect email addresses
          - VERIFIED: collect verified Google account email automatically
          - RESPONDER_INPUT: ask respondents to enter their email

        is_quiz: set to true to enable quiz/grading mode, false to disable.

        At least one of the two must be provided.
        """
        if not form_id.strip():
            return _error("form_id must not be empty")
        if not email_collection_type.strip() and is_quiz is None:
            return _error(
                "At least one of email_collection_type or is_quiz must be provided"
            )
        try:
            clients = get_clients()
            result = update_form_settings(
                clients["forms"],
                form_id=form_id,
                email_collection_type=email_collection_type,
                is_quiz=is_quiz,
            )
            return json.dumps(result)
        except DocsApiError as exc:
            return _error(sanitize_api_error(exc))
        except Exception:
            logger.exception("Unexpected error in update_form_settings_tool")
            return _error("An internal error occurred. Check server logs for details.")
