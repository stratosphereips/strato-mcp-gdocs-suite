"""OAuth flow tests."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from google.auth.exceptions import RefreshError
from google.oauth2.credentials import Credentials

from gdocs_suite_mcp.auth.oauth import DocsAuthError, get_credentials


def _expired_credentials() -> Credentials:
    creds = Credentials(
        token="expired",
        refresh_token="refresh",
        token_uri="https://oauth2.googleapis.com/token",
        client_id="client",
        client_secret="secret",
        scopes=["https://www.googleapis.com/auth/documents"],
    )
    creds.expiry = None
    return creds


def test_get_credentials_uses_cached_valid_token(valid_config, tmp_token_store):
    tmp_token_store.save(
        "default",
        {
            "token": "tok",
            "refresh_token": "ref",
            "scopes": ["https://www.googleapis.com/auth/documents"],
        },
    )

    with patch("gdocs_suite_mcp.auth.oauth.Credentials") as creds_cls:
        mock_creds = MagicMock()
        mock_creds.valid = True
        creds_cls.return_value = mock_creds
        result = get_credentials("default", valid_config, tmp_token_store, headless=True)

    assert result is mock_creds


def test_get_credentials_headless_without_token_raises(valid_config, tmp_token_store):
    with pytest.raises(DocsAuthError):
        get_credentials("default", valid_config, tmp_token_store, headless=True)


def test_get_credentials_refreshes_expired_token(valid_config, tmp_token_store):
    tmp_token_store.save(
        "default",
        {
            "token": "expired",
            "refresh_token": "ref",
            "scopes": ["https://www.googleapis.com/auth/documents"],
        },
    )

    with patch("gdocs_suite_mcp.auth.oauth.Credentials") as creds_cls:
        mock_creds = MagicMock()
        mock_creds.valid = False
        mock_creds.expired = True
        mock_creds.refresh_token = "ref"
        mock_creds.refresh.return_value = None
        mock_creds.token = "newtok"
        mock_creds.scopes = ["https://www.googleapis.com/auth/documents"]
        mock_creds.token_uri = "https://oauth2.googleapis.com/token"
        mock_creds.client_id = valid_config.client_id
        creds_cls.return_value = mock_creds

        result = get_credentials("default", valid_config, tmp_token_store, headless=True)

    assert result is mock_creds


def test_get_credentials_refresh_failure_then_headless_raises(valid_config, tmp_token_store):
    tmp_token_store.save(
        "default",
        {
            "token": "expired",
            "refresh_token": "ref",
            "scopes": ["https://www.googleapis.com/auth/documents"],
        },
    )

    with patch("gdocs_suite_mcp.auth.oauth.Credentials") as creds_cls:
        mock_creds = MagicMock()
        mock_creds.valid = False
        mock_creds.expired = True
        mock_creds.refresh_token = "ref"
        mock_creds.refresh.side_effect = RefreshError("bad refresh")
        creds_cls.return_value = mock_creds

        with pytest.raises(DocsAuthError):
            get_credentials("default", valid_config, tmp_token_store, headless=True)


def test_get_credentials_runs_oauth_flow_when_not_headless(valid_config, tmp_token_store):
    flow_creds = MagicMock()
    flow_creds.token = "tok"
    flow_creds.refresh_token = "ref"
    flow_creds.token_uri = "https://oauth2.googleapis.com/token"
    flow_creds.client_id = valid_config.client_id
    flow_creds.scopes = ["https://www.googleapis.com/auth/documents"]

    with patch(
        "gdocs_suite_mcp.auth.oauth.InstalledAppFlow.from_client_config"
    ) as from_config:
        flow = MagicMock()
        flow.run_local_server.return_value = flow_creds
        from_config.return_value = flow

        result = get_credentials("default", valid_config, tmp_token_store, headless=False)

    assert result is flow_creds
    assert tmp_token_store.load("default") is not None
