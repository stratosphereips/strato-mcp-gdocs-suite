# Stratosphere MCP GDocs Suite

A Python MCP server that exposes Google Docs, Google Sheets, Google Slides, and Google Forms as tools for any MCP-compatible AI assistant. Currently supporting **26 tools** across documents, spreadsheets, presentations, and forms.

## Prerequisites

Enable these APIs in your Google Cloud project:
1. Google Docs API
2. Google Sheets API
3. Google Slides API
4. Google Drive API
5. Google Forms API

Then create OAuth credentials:
1. Go to `APIs & Services` -> `OAuth consent screen` and configure it
2. On the OAuth consent screen, go to **Scopes** and add the following scopes:
   - `https://www.googleapis.com/auth/documents`
   - `https://www.googleapis.com/auth/spreadsheets`
   - `https://www.googleapis.com/auth/presentations`
   - `https://www.googleapis.com/auth/drive.readonly`
   - `https://www.googleapis.com/auth/forms.body`
   - `https://www.googleapis.com/auth/forms.responses.readonly`
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

<details>
<summary><strong>Claude Desktop</strong></summary>

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

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

</details>

<details>
<summary><strong>Claude Code</strong></summary>

```bash
claude mcp add --transport stdio google-docs -- \
  docker run --rm -i \
    -v gdocs-suite-mcp-tokens:/tokens \
    --env-file /absolute/path/to/.env \
    gdocs-suite-mcp:latest serve
```

</details>

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
git clone https://github.com/stratosphereips/strato-mcp-gdocs-suite
cd strato-mcp-gdocs-suite
uv venv && source .venv/bin/activate
uv pip install -e .
cp .env.example .env
```

Authenticate once:

```bash
gdocs-suite-auth
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

### Forms

| Tool | Parameters | Description |
|---|---|---|
| `list_forms_tool` | `max_results=10`, `query=""` | List Google Forms files, optionally filtered by name |
| `get_form_tool` | `form_id` | Get form metadata, description, and all items/questions |
| `create_form_tool` | `title`, `description=""` | Create a new form with optional description |
| `add_question_tool` | `form_id`, `question_type`, `title`, `required=False`, `index=None`, `options=None` | Add a question (types: `text`, `paragraph`, `multiple_choice`, `checkbox`, `dropdown`, `scale`, `date`, `time`) |
| `update_form_info_tool` | `form_id`, `title=""`, `description=""` | Update form title and/or description |
| `delete_item_tool` | `form_id`, `item_id` | Delete a question/item by item ID |
| `list_responses_tool` | `form_id`, `max_results=100` | List all responses for a form |
| `get_response_tool` | `form_id`, `response_id` | Get a single response by response ID |
| `move_item_tool` | `form_id`, `original_index`, `new_index` | Move an item to a new position (0-based indices) |
| `add_text_item_tool` | `form_id`, `title`, `description=""`, `index=0` | Add a section header with optional description |
| `add_page_break_tool` | `form_id`, `title=""`, `index=0` | Add a page break to start a new section |
| `update_form_settings_tool` | `form_id`, `email_collection_type=""`, `is_quiz=None` | Set email collection (`DO_NOT_COLLECT`, `VERIFIED`, `RESPONDER_INPUT`) and/or quiz mode |

> **Note:** The Forms tools require two additional OAuth scopes (`forms.body` and `forms.responses.readonly`). If you previously authenticated without these scopes, re-run the auth step: `docker compose run --rm -p 8082:8082 auth`

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
