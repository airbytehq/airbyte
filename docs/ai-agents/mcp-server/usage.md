---
sidebar_label: "Usage"
sidebar_position: 3
---

# Use the MCP server

This page covers the MCP tools that the server exposes, field selection and exclusion, downloads, transport modes, and the terminal chat interface.

## MCP tools reference

When you register the MCP server with your agent, it exposes the following tools. Your agent discovers and calls these tools automatically based on your prompts.

### `execute`

The primary tool. Executes an operation on a connector entity.

| Parameter | Type | Description |
| --- | --- | --- |
| `entity` | string | Entity name (e.g., `users`, `calls`, `issues`) |
| `action` | string | Operation to perform: `list`, `get`, `search`, or `download` |
| `params` | object or string | Operation parameters (varies by entity and action) |
| `select_fields` | list of strings | Fields to include in the response (allowlist) |
| `exclude_fields` | list of strings | Fields to remove from the response (blocklist) |
| `skip_truncation` | boolean | Disable long-text truncation for list/search responses |

The `search` action is available in [hosted mode](configuration#hosted-mode) and supports filtering, sorting, and pagination. The `list` action returns all records and is available in both modes.

### `connector_info`

Returns connector metadata including the connector name, version, and a list of available entities with their supported actions and parameters. Call this tool to discover what data the connector can access.

### `entity_schema`

Returns the JSON schema for a specific entity. Call this tool to understand the structure of an entity's data before querying it.

| Parameter | Type | Description |
| --- | --- | --- |
| `entity` | string | Entity name to get the schema for |

### `get_instructions`

Returns the built-in instructions for using the MCP server effectively, including best practices for action selection, field selection, query sizing, and date range handling.

### `current_datetime`

Returns the current date and time in ISO 8601 format (UTC). Agents should call this before any time-based query to get accurate date references.

## Field selection and exclusion

Every `execute` call should include either `select_fields` or `exclude_fields` to control what data is returned. This reduces token usage and improves response quality.

### `select_fields` (allowlist)

Returns only the specified fields:

```
select_fields=["id", "title", "started", "primaryUserId"]
```

### `exclude_fields` (blocklist)

Returns all fields except the specified ones:

```
exclude_fields=["content", "interaction", "parties", "context"]
```

If you provide both, `select_fields` takes priority and `exclude_fields` is ignored.

### Dot notation for nested fields

Both `select_fields` and `exclude_fields` support dot notation to target nested fields:

```
select_fields=["id", "title", "content.topics", "content.brief"]
exclude_fields=["content.trackers", "interaction.speakers"]
```

## Downloads

Some entities support a `download` action for binary content like call recordings. The MCP server saves downloaded files to a local directory and returns metadata about the saved file:

```json
{
  "download": {
    "file_path": "/path/to/call_audio_abc123.mp3",
    "size_bytes": 1048576,
    "entity": "call_audio",
    "message": "File downloaded and saved to: /path/to/call_audio_abc123.mp3 (1,048,576 bytes)."
  }
}
```

The file extension is detected automatically from the file content.

## Transport modes

### stdio (default)

The default transport mode. The MCP server communicates over standard input/output, which is how most AI coding tools expect to interact with MCP servers. This is what `adp mcp add-to` configures.

### HTTP

For integrations that need an HTTP endpoint:

```bash
uv run adp mcp serve connector-gong-package.yaml --transport http --port 8080
```

| Flag | Default | Description |
| --- | --- | --- |
| `--transport`, `-t` | `stdio` | Transport protocol (`stdio` or `http`) |
| `--host`, `-h` | `127.0.0.1` | Host to bind to |
| `--port`, `-p` | `8000` | Port to bind to |

## Terminal chat

The `adp chat` command lets you interact with your connector data using natural language in the terminal, powered by Claude. This requires an `ANTHROPIC_API_KEY` environment variable.

### One-shot mode

Pass a prompt as an argument to get a single response:

```bash
uv run adp chat connector-gong-package.yaml "show me 5 recent calls"
```

Use `--quiet` to hide tool call details and show only the final answer:

```bash
uv run adp chat connector-gong-package.yaml "show me 5 recent calls" --quiet
```

You can also use an aggregate configuration:

```bash
uv run adp chat connectors.yaml "show me 5 users from each system"
```

### Interactive REPL

Omit the prompt to start an interactive session:

```bash
uv run adp chat connector-gong-package.yaml
```

Use `--model` to specify a different Anthropic model:

```bash
uv run adp chat connector-gong-package.yaml --model claude-sonnet-4-20250514
```

## Troubleshooting

### Long text fields are truncated

For `list` and `search` results, the MCP server truncates text fields longer than 200 characters to reduce token usage. Truncated fields are marked with `[truncated]`. To get the full value:

1. Use the `get` action with the record ID.
2. If `get` is not available, retry the original query with `skip_truncation=true` and tight `select_fields` and `limit`.

### Search returns no results

If `search` returns no results but you expect data:

- The search index may lag behind by hours. Try `list` with date boundary parameters instead.
- Try `fuzzy` matching instead of `like` in your filter (e.g., `{"fuzzy": {"name": "search term"}}`).

### Date range queries miss recent data

When querying date ranges that include today, the search index may not have the latest records. Issue both a `search` call and a `list` call with date boundary parameters, then merge results and deduplicate by ID.
