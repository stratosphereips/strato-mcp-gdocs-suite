"""MCP server entry point for Google Docs/Sheets/Slides."""
from __future__ import annotations

import logging
import sys
import threading

from mcp.server.fastmcp import FastMCP

logger = logging.getLogger(__name__)

mcp = FastMCP("GDocs Suite")

_clients = None
_client_lock = threading.Lock()


def _get_clients():
    with _client_lock:
        if _clients is None:
            raise RuntimeError(
                "Google clients not initialised. "
                "Ensure main() completed authentication before tools are called."
            )
        return _clients


def _register_tools() -> None:
    from gdocs_suite_mcp.tools.docs import register_docs_tools
    from gdocs_suite_mcp.tools.sheets import register_sheets_tools
    from gdocs_suite_mcp.tools.slides import register_slides_tools

    register_docs_tools(mcp, _get_clients)
    register_sheets_tools(mcp, _get_clients)
    register_slides_tools(mcp, _get_clients)


def main() -> None:
    """Entry point called by the pyproject.toml script."""
    global _clients

    from gdocs_suite_mcp.auth.oauth import DocsAuthError, get_credentials
    from gdocs_suite_mcp.auth.token_store import FileTokenStore
    from gdocs_suite_mcp.config import ConfigurationError, load_config
    from gdocs_suite_mcp.docs.client import build_clients

    try:
        config = load_config()
    except ConfigurationError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        sys.exit(1)

    token_store = FileTokenStore(config.token_store_path)

    try:
        credentials = get_credentials("default", config, token_store, headless=True)
    except DocsAuthError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        print(
            "\n[ERROR] No valid token found. Run authentication first:\n\n"
            "  docker compose run --rm -p 8082:8082 auth\n",
            file=sys.stderr,
        )
        sys.exit(1)

    with _client_lock:
        _clients = build_clients(credentials)
    logger.info("Google Docs/Sheets/Slides clients initialised successfully")

    _register_tools()
    mcp.run()


def auth_main() -> None:
    """Entry point for the google-docs-auth command."""
    from gdocs_suite_mcp.auth.oauth import DocsAuthError, get_credentials
    from gdocs_suite_mcp.auth.token_store import FileTokenStore
    from gdocs_suite_mcp.config import ConfigurationError, load_config

    try:
        config = load_config()
    except ConfigurationError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        sys.exit(1)

    token_store = FileTokenStore(config.token_store_path)

    try:
        get_credentials("default", config, token_store, headless=False)
        print("Authentication successful. Token saved.", file=sys.stderr)
    except DocsAuthError as exc:
        print(f"Authentication error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
