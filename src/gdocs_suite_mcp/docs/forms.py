"""Google Forms API wrappers."""
from __future__ import annotations

from typing import Any

from googleapiclient.discovery import Resource
from googleapiclient.errors import HttpError

from gdocs_suite_mcp.docs.drive import DocsApiError, list_files

FORMS_MIME_TYPE = "application/vnd.google-apps.form"


def list_forms(
    drive_client: Resource,
    max_results: int = 10,
    query: str = "",
) -> list[dict[str, Any]]:
    """List Google Forms via Drive API."""
    try:
        return list_files(drive_client, FORMS_MIME_TYPE, query=query, max_results=max_results)
    except DocsApiError:
        raise


def get_form(forms_client: Resource, form_id: str) -> dict[str, Any]:
    """Get form metadata, description, and all items/questions."""
    try:
        form = forms_client.forms().get(formId=form_id).execute()
        items = []
        for item in form.get("items", []):
            entry: dict[str, Any] = {
                "itemId": item.get("itemId"),
                "title": item.get("title", ""),
            }
            for q_type in (
                "questionItem",
                "questionGroupItem",
                "imageItem",
                "videoItem",
                "pageBreakItem",
                "textItem",
            ):
                if q_type in item:
                    entry["type"] = q_type
                    q = item[q_type].get("question", {})
                    if q:
                        entry["required"] = q.get("required", False)
                        for answer_type in (
                            "choiceQuestion",
                            "textQuestion",
                            "scaleQuestion",
                            "dateQuestion",
                            "timeQuestion",
                            "rowQuestion",
                        ):
                            if answer_type in q:
                                entry["questionType"] = answer_type
                                entry["questionDetails"] = q[answer_type]
                    break
            items.append(entry)
        info = form.get("info", {})
        return {
            "formId": form.get("formId"),
            "title": info.get("title", ""),
            "description": info.get("description", ""),
            "responderUri": form.get("responderUri", ""),
            "linkedSheetId": form.get("linkedSheetId", ""),
            "itemCount": len(items),
            "items": items,
        }
    except HttpError as exc:
        raise DocsApiError(f"Failed to get form {form_id!r}: {exc}") from exc


def create_form(
    forms_client: Resource,
    title: str,
    description: str = "",
) -> dict[str, Any]:
    """Create a new Google Form."""
    try:
        result = forms_client.forms().create(body={"info": {"title": title}}).execute()
        form_id = result.get("formId")
        if description:
            forms_client.forms().batchUpdate(
                formId=form_id,
                body={
                    "requests": [
                        {
                            "updateFormInfo": {
                                "info": {"description": description},
                                "updateMask": "description",
                            }
                        }
                    ]
                },
            ).execute()
        return {
            "formId": form_id,
            "title": result.get("info", {}).get("title", title),
            "responderUri": result.get("responderUri", ""),
        }
    except HttpError as exc:
        raise DocsApiError(f"Failed to create form: {exc}") from exc


_QUESTION_TYPE_MAP = {
    "text": {"textQuestion": {"paragraph": False}},
    "paragraph": {"textQuestion": {"paragraph": True}},
    "multiple_choice": {"choiceQuestion": {"type": "RADIO", "options": []}},
    "checkbox": {"choiceQuestion": {"type": "CHECKBOX", "options": []}},
    "dropdown": {"choiceQuestion": {"type": "DROP_DOWN", "options": []}},
    "scale": {"scaleQuestion": {"low": 1, "high": 5}},
    "date": {"dateQuestion": {}},
    "time": {"timeQuestion": {}},
}


def add_question(
    forms_client: Resource,
    form_id: str,
    question_type: str,
    title: str,
    required: bool = False,
    index: int | None = None,
    options: list[str] | None = None,
    description: str = "",
) -> dict[str, Any]:
    """Add a question to a form."""
    if question_type not in _QUESTION_TYPE_MAP:
        raise DocsApiError(
            f"Unsupported question_type {question_type!r}. "
            f"Choose from: {', '.join(_QUESTION_TYPE_MAP)}"
        )
    question_body = dict(_QUESTION_TYPE_MAP[question_type])
    if question_type in ("multiple_choice", "checkbox", "dropdown") and options:
        question_body["choiceQuestion"] = dict(question_body["choiceQuestion"])
        question_body["choiceQuestion"]["options"] = [{"value": o} for o in options]

    item: dict[str, Any] = {"title": title}
    if description:
        item["description"] = description
    item["questionItem"] = {
        "question": {
            "required": required,
            **question_body,
        }
    }
    create_item: dict[str, Any] = {
        "item": item,
        "location": {"index": index if index is not None else 0},
    }

    try:
        result = forms_client.forms().batchUpdate(
            formId=form_id,
            body={"requests": [{"createItem": create_item}]},
        ).execute()
        replies = result.get("replies", [{}])
        item_id = replies[0].get("createItem", {}).get("itemId", "") if replies else ""
        return {"formId": form_id, "itemId": item_id, "title": title}
    except HttpError as exc:
        raise DocsApiError(f"Failed to add question to form {form_id!r}: {exc}") from exc


def update_form_info(
    forms_client: Resource,
    form_id: str,
    title: str = "",
    description: str = "",
) -> dict[str, Any]:
    """Update form title and/or description."""
    if not title and not description:
        raise DocsApiError("At least one of title or description must be provided")
    info: dict[str, Any] = {}
    mask_fields = []
    if title:
        info["title"] = title
        mask_fields.append("title")
    if description:
        info["description"] = description
        mask_fields.append("description")
    try:
        forms_client.forms().batchUpdate(
            formId=form_id,
            body={
                "requests": [
                    {
                        "updateFormInfo": {
                            "info": info,
                            "updateMask": ",".join(mask_fields),
                        }
                    }
                ]
            },
        ).execute()
        return {"formId": form_id, "updated": mask_fields}
    except HttpError as exc:
        raise DocsApiError(f"Failed to update form info {form_id!r}: {exc}") from exc


def delete_item(
    forms_client: Resource,
    form_id: str,
    item_id: str,
) -> dict[str, Any]:
    """Delete a question/item by item ID.

    Looks up the item's index from the form first, then deletes by index
    (the Forms API deleteItem requires a location index, not an item ID).
    """
    try:
        form = forms_client.forms().get(formId=form_id).execute()
    except HttpError as exc:
        raise DocsApiError(
            f"Failed to fetch form {form_id!r} to resolve item index: {exc}"
        ) from exc

    items = form.get("items", [])
    index = next(
        (i for i, item in enumerate(items) if item.get("itemId") == item_id), None
    )
    if index is None:
        raise DocsApiError(
            f"Item {item_id!r} not found in form {form_id!r}"
        )

    try:
        forms_client.forms().batchUpdate(
            formId=form_id,
            body={
                "requests": [{"deleteItem": {"location": {"index": index}}}]
            },
        ).execute()
        return {"formId": form_id, "deletedItemId": item_id, "deletedIndex": index}
    except HttpError as exc:
        raise DocsApiError(
            f"Failed to delete item {item_id!r} from form {form_id!r}: {exc}"
        ) from exc


def list_responses(
    forms_client: Resource,
    form_id: str,
    max_results: int = 100,
) -> list[dict[str, Any]]:
    """List all responses for a form."""
    try:
        result = (
            forms_client.forms()
            .responses()
            .list(formId=form_id, pageSize=min(max(1, max_results), 5000))
            .execute()
        )
        return result.get("responses", [])
    except HttpError as exc:
        raise DocsApiError(f"Failed to list responses for form {form_id!r}: {exc}") from exc


def get_response(
    forms_client: Resource,
    form_id: str,
    response_id: str,
) -> dict[str, Any]:
    """Get a single response by response ID."""
    try:
        return (
            forms_client.forms()
            .responses()
            .get(formId=form_id, responseId=response_id)
            .execute()
        )
    except HttpError as exc:
        raise DocsApiError(
            f"Failed to get response {response_id!r} from form {form_id!r}: {exc}"
        ) from exc


def move_item(
    forms_client: Resource,
    form_id: str,
    original_index: int,
    new_index: int,
) -> dict[str, Any]:
    """Move an item from original_index to new_index."""
    try:
        forms_client.forms().batchUpdate(
            formId=form_id,
            body={
                "requests": [
                    {
                        "moveItem": {
                            "originalLocation": {"index": original_index},
                            "newLocation": {"index": new_index},
                        }
                    }
                ]
            },
        ).execute()
        return {"formId": form_id, "movedFrom": original_index, "movedTo": new_index}
    except HttpError as exc:
        raise DocsApiError(f"Failed to move item in form {form_id!r}: {exc}") from exc


def add_text_item(
    forms_client: Resource,
    form_id: str,
    title: str,
    description: str = "",
    index: int = 0,
) -> dict[str, Any]:
    """Add a text/section-header item to a form."""
    item: dict[str, Any] = {"title": title, "textItem": {}}
    if description:
        item["description"] = description
    try:
        result = forms_client.forms().batchUpdate(
            formId=form_id,
            body={
                "requests": [
                    {"createItem": {"item": item, "location": {"index": index}}}
                ]
            },
        ).execute()
        replies = result.get("replies", [{}])
        item_id = replies[0].get("createItem", {}).get("itemId", "") if replies else ""
        return {"formId": form_id, "itemId": item_id, "title": title}
    except HttpError as exc:
        raise DocsApiError(f"Failed to add text item to form {form_id!r}: {exc}") from exc


def add_page_break(
    forms_client: Resource,
    form_id: str,
    title: str = "",
    index: int = 0,
) -> dict[str, Any]:
    """Add a page break to a form."""
    item: dict[str, Any] = {"pageBreakItem": {}}
    if title:
        item["title"] = title
    try:
        result = forms_client.forms().batchUpdate(
            formId=form_id,
            body={
                "requests": [
                    {"createItem": {"item": item, "location": {"index": index}}}
                ]
            },
        ).execute()
        replies = result.get("replies", [{}])
        item_id = replies[0].get("createItem", {}).get("itemId", "") if replies else ""
        return {"formId": form_id, "itemId": item_id, "title": title}
    except HttpError as exc:
        raise DocsApiError(f"Failed to add page break to form {form_id!r}: {exc}") from exc


_VALID_EMAIL_COLLECTION = {"DO_NOT_COLLECT", "VERIFIED", "RESPONDER_INPUT"}


def update_form_settings(
    forms_client: Resource,
    form_id: str,
    email_collection_type: str = "",
    is_quiz: bool | None = None,
) -> dict[str, Any]:
    """Update form settings: email collection type and/or quiz mode."""
    if email_collection_type and email_collection_type not in _VALID_EMAIL_COLLECTION:
        raise DocsApiError(
            f"Invalid email_collection_type {email_collection_type!r}. "
            f"Choose from: {', '.join(sorted(_VALID_EMAIL_COLLECTION))}"
        )
    settings: dict[str, Any] = {}
    mask_fields = []
    if email_collection_type:
        settings["emailCollectionType"] = email_collection_type
        mask_fields.append("emailCollectionType")
    if is_quiz is not None:
        settings["quizSettings"] = {"isQuiz": is_quiz}
        mask_fields.append("quizSettings")
    if not mask_fields:
        raise DocsApiError(
            "At least one of email_collection_type or is_quiz must be provided"
        )
    try:
        forms_client.forms().batchUpdate(
            formId=form_id,
            body={
                "requests": [
                    {
                        "updateSettings": {
                            "settings": settings,
                            "updateMask": ",".join(mask_fields),
                        }
                    }
                ]
            },
        ).execute()
        return {"formId": form_id, "updated": mask_fields}
    except HttpError as exc:
        raise DocsApiError(
            f"Failed to update settings for form {form_id!r}: {exc}"
        ) from exc
