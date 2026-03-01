"""Token store tests."""
from __future__ import annotations

from gdocs_suite_mcp.auth.token_store import FileTokenStore


def test_file_token_store_round_trip(tmp_path):
    store = FileTokenStore(tmp_path / "tokens")
    data = {"token": "abc", "refresh_token": "r1"}

    store.save("default", data)
    loaded = store.load("default")

    assert loaded == data


def test_file_token_store_delete(tmp_path):
    store = FileTokenStore(tmp_path / "tokens")
    store.save("default", {"token": "abc"})

    store.delete("default")

    assert store.load("default") is None


def test_file_token_store_invalid_user_id(tmp_path):
    store = FileTokenStore(tmp_path / "tokens")

    try:
        store.save("!!!", {"token": "abc"})
        assert False, "Expected ValueError"
    except ValueError:
        assert True
