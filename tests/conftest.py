"""Shared pytest fixtures."""
from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest


@pytest.fixture(autouse=True)
def _no_load_dotenv(monkeypatch):
    monkeypatch.setattr("google_docs_mcp.config.load_dotenv", lambda **_: None)


from google_docs_mcp.auth.token_store import FileTokenStore
from google_docs_mcp.config import Config


@pytest.fixture()
def valid_config() -> Config:
    return Config(
        client_id="test-client-id",
        client_secret="test-client-secret",
        redirect_uri="http://localhost:8082",
        token_store_path=Path("/tmp/test-tokens"),
        scopes=[
            "https://www.googleapis.com/auth/documents",
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/presentations",
            "https://www.googleapis.com/auth/drive.readonly",
        ],
    )


@pytest.fixture()
def tmp_token_store(tmp_path: Path) -> FileTokenStore:
    return FileTokenStore(tmp_path / "tokens")


@pytest.fixture()
def sample_token_data() -> dict[str, Any]:
    return {
        "token": "ya29.test_access_token",
        "refresh_token": "1//test_refresh_token",
        "token_uri": "https://oauth2.googleapis.com/token",
        "client_id": "test-client-id",
        "client_secret": "test-client-secret",
        "scopes": ["https://www.googleapis.com/auth/documents"],
    }


@pytest.fixture()
def mock_clients() -> dict[str, MagicMock]:
    docs_client = MagicMock()
    docs_client.documents().get.return_value.execute.return_value = {
        "documentId": "doc1",
        "title": "Doc 1",
        "body": {"content": []},
    }
    docs_client.documents().create.return_value.execute.return_value = {
        "documentId": "doc-new",
        "title": "New Doc",
    }
    docs_client.documents().batchUpdate.return_value.execute.return_value = {
        "replies": []
    }

    sheets_client = MagicMock()
    sheets_client.spreadsheets().get.return_value.execute.return_value = {
        "spreadsheetId": "sheet1",
        "properties": {"title": "Budget"},
        "sheets": [{"properties": {"title": "Sheet1"}}],
    }
    sheets_client.spreadsheets().create.return_value.execute.return_value = {
        "spreadsheetId": "sheet-new",
        "properties": {"title": "New Sheet"},
    }
    sheets_client.spreadsheets().values().get.return_value.execute.return_value = {
        "values": [["A1"]]
    }
    sheets_client.spreadsheets().values().update.return_value.execute.return_value = {
        "updatedRows": 1
    }
    sheets_client.spreadsheets().values().append.return_value.execute.return_value = {
        "updates": {"updatedRows": 1}
    }

    slides_client = MagicMock()
    slides_client.presentations().get.return_value.execute.return_value = {
        "presentationId": "pres1",
        "title": "Deck",
        "slides": [],
    }
    slides_client.presentations().create.return_value.execute.return_value = {
        "presentationId": "pres-new",
        "title": "New Deck",
    }

    drive_client = MagicMock()
    drive_client.files().list.return_value.execute.return_value = {"files": []}

    return {
        "docs": docs_client,
        "sheets": sheets_client,
        "slides": slides_client,
        "drive": drive_client,
    }
