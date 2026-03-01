# Stratosphere MCP GDocs Suite

A Python MCP server that exposes Google Docs, Google Sheets, and Google Slides as tools for any MCP-compatible AI assistant. Currently supporting **14 tools** across documents, spreadsheets, and presentations.

## Prerequisites

Enable these APIs in your Google Cloud project:
1. Google Docs API
2. Google Sheets API
3. Google Slides API
4. Google Drive API

Then create OAuth credentials:
1. Go to `APIs & Services` -> `OAuth consent screen` and configure it
2. On the OAuth consent screen, go to **Scopes** and add the following scopes:
   - `https://www.googleapis.com/auth/documents`
   - `https://www.googleapis.com/auth/spreadsheets`
   - `https://www.googleapis.com/auth/presentations`
   - `https://www.googleapis.com/auth/drive.readonly`
3. Go to `APIs & Services` -> `Credentials` -> `Create credentials` -> `OAuth client ID` -> `Desktop app`
4. Copy the `Client ID` and `Client Secret`

## Quick start (Docker)

### Step 1: Build

```bash
docker compose build
```

### Step 2: Configure

```bash
cp .env.example .env
# Fill in GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET
```

### Step 3: Authenticate (once)

```bash
docker compose run --rm -p 8082:8082 auth
```

### Step 4: Register with your AI assistant

**Claude Desktop** (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "google-docs": {
      "command": "docker",
      "args": [
        "run", "--rm", "-i",
        "-v", "gdocs-suite-mcp-tokens:/tokens",
        "--env-file", "/absolute/path/to/.env",
        "gdocs-suite-mcp:latest",
        "serve"
      ]
    }
  }
}
```

**Claude Code:**

```bash
claude mcp add --transport stdio google-docs -- \
  docker run --rm -i \
    -v gdocs-suite-mcp-tokens:/tokens \
    --env-file /absolute/path/to/.env \
    gdocs-suite-mcp:latest serve
```

<details>
<summary><strong>Gemini CLI</strong></summary>

Add to `~/.gemini/settings.json` (or `.gemini/settings.json` for project-level):

```json
{
  "mcpServers": {
    "gdocs-suite": {
      "command": "docker",
      "args": [
        "run", "--rm", "-i",
        "-v", "gdocs-suite-mcp-tokens:/tokens",
        "--env-file", "/absolute/path/to/.env",
        "gdocs-suite-mcp:latest",
        "serve"
      ]
    }
  }
}
```

</details>

<details>
<summary><strong>OpenAI Codex CLI</strong></summary>

Add to `~/.codex/config.toml` (or `.codex/config.toml` for project-level):

```toml
[mcp_servers.gdocs-suite]
command = "docker"
args = ["run", "--rm", "-i", "-v", "gdocs-suite-mcp-tokens:/tokens", "--env-file", "/absolute/path/to/.env", "gdocs-suite-mcp:latest", "serve"]
enabled = true
```

</details>

## Alternative: local install

```bash
git clone https://github.com/stratosphereips/strato-mcp-google-docs
cd strato-mcp-google-docs
uv venv && source .venv/bin/activate
uv pip install -e .
cp .env.example .env
```

Authenticate once:

```bash
google-docs-auth
```

Start MCP server:

```bash
gdocs-suite-mcp
```

## Available Tools

### Documents

| Tool | Parameters | Description |
|---|---|---|
| `list_documents_tool` | `max_results=10`, `query=""` | List Google Docs files, optionally filtered by name |
| `search_documents_tool` | `query`, `max_results=10` | Full-text search across document content |
| `get_document_tool` | `document_id` | Get document metadata and extracted plain text |
| `create_document_tool` | `title`, `content=""` | Create a document with optional initial text |
| `update_document_tool` | `document_id`, `requests` | Apply raw [Docs API batchUpdate](https://developers.google.com/docs/api/reference/rest/v1/documents/batchUpdate) requests |

### Spreadsheets

| Tool | Parameters | Description |
|---|---|---|
| `list_spreadsheets_tool` | `max_results=10`, `query=""` | List Google Sheets files, optionally filtered by name |
| `get_spreadsheet_tool` | `spreadsheet_id` | Get spreadsheet metadata and sheet names |
| `create_spreadsheet_tool` | `title` | Create a new spreadsheet |
| `read_range_tool` | `spreadsheet_id`, `range` | Read cell values from an A1-notation range (e.g. `Sheet1!A1:C10`) |
| `write_range_tool` | `spreadsheet_id`, `range`, `values` | Write a 2D list of values to a range |
| `append_rows_tool` | `spreadsheet_id`, `range`, `values` | Append rows below the last row with data in the range |

### Presentations

| Tool | Parameters | Description |
|---|---|---|
| `list_presentations_tool` | `max_results=10`, `query=""` | List Google Slides files, optionally filtered by name |
| `get_presentation_tool` | `presentation_id` | Get presentation metadata, slide count, and slide titles |
| `create_presentation_tool` | `title` | Create a new presentation |

## Configuration reference

| Variable | Required | Default | Description |
|---|---|---|---|
| `GOOGLE_CLIENT_ID` | Yes | - | OAuth client ID |
| `GOOGLE_CLIENT_SECRET` | Yes | - | OAuth client secret |
| `GOOGLE_REDIRECT_URI` | No | `http://localhost:8082` | OAuth redirect URI |
| `TOKEN_STORE_PATH` | No | `~/.config/gdocs-suite-mcp/` (local) / `/tokens` (Docker) | Token storage directory |
| `GOOGLE_SCOPES` | No | docs + sheets + slides + drive.readonly | Comma-separated OAuth scopes |
| `LOG_LEVEL` | No | `WARNING` | Log level (stderr only) |

## Development

```bash
uv pip install -e ".[dev]"
uv run pytest
```
