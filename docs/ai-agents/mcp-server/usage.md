---
sidebar_label: "Advanced use"
sidebar_position: 3
---

# Advanced use of the MCP server

This page covers the MCP tools that the server exposes, field selection and exclusion, downloads, transport modes, and the terminal chat interface.

## MCP tools reference

When you register the MCP server with your agent, it exposes the following tools. Your agent discovers and calls these tools automatically based on your prompts.

The `execute`, `connector_info`, and `entity_schema` tools are registered with a connector name prefix (for example, `github__execute`, `gong__connector_info`). The `get_instructions` and `current_datetime` tools are shared across all connectors and have no prefix.

### `execute`

The primary tool. Executes an operation on a connector entity.

| Parameter         | Type             | Description                                                                                                                                                                                                                                                       |
| ----------------- | ---------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `entity`          | string           | Entity name, like `users`, `calls`, or `issues`.                                                                                                                                                                                                                   |
| `action`          | string           | Operation to perform: `list`, `get`, `search`, or `download`. The `search` action is available in [hosted mode](configuration#hosted-mode) and supports filtering, sorting, and pagination. The `list` action returns all records and is available in both modes.   |
| `params`          | object or string | Operation parameters (varies by entity and action).                                                                                                                                                                                                                |
| `select_fields`    | list of strings  | Fields to include in the response.                                                                                                                                                                                                                  |
| `exclude_fields`   | list of strings  | Fields to remove from the response.                                                                                                                                                                                                                 |
| `skip_truncation` | boolean          | Disable long-text truncation for list/search responses.                                                                                                                                                                                                            |

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

```text
select_fields=["id", "title", "started", "primaryUserId"]
```

### `exclude_fields` (blocklist)

Returns all fields except the specified ones:

```text
exclude_fields=["content", "interaction", "parties", "context"]
```

If you provide both, `select_fields` takes priority and `exclude_fields` is ignored.

### Dot notation for nested fields

Both `select_fields` and `exclude_fields` support dot notation to target nested fields:

```text
select_fields=["id", "title", "content.topics", "content.brief"]
exclude_fields=["content.trackers", "interaction.speakers"]
```

## Downloads

Some entities support a `download` action for binary content like call recordings. The MCP server saves downloaded files to a local directory and returns metadata about the saved file:

```json
{
  "download": {
    "file_path": "~/.airbyte_agent_mcp/downloads/call_audio_a1b2c3d4e5f6.mp3",
    "size_bytes": 1048576,
    "entity": "call_audio",
    "message": "File downloaded and saved to: ~/.airbyte_agent_mcp/downloads/call_audio_a1b2c3d4e5f6.mp3 (1,048,576 bytes)."
  }
}
```

Files are saved to `~/.airbyte_agent_mcp/downloads/` (or `~/.airbyte_agent_mcp/orgs/<org-id>/downloads/` in hosted mode). The file name is generated from the entity name and a random identifier, and the extension is detected automatically from the file content.

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

The `adp chat` command is a lightweight terminal agent for querying your connector data with natural language. It uses Claude to interpret your questions, call the MCP server tools, and return formatted answers without needing an IDE integration. This is useful for testing your connector setup or running ad-hoc data queries.

`adp chat` requires an `ANTHROPIC_API_KEY` environment variable and only supports Anthropic models. The default model is `claude-opus-4-6`. Use `--model` to select a different Anthropic model.

### One-shot mode

Pass a prompt as an argument to get a single response. Tool call progress is written to stderr, so you can pipe the final answer to a file:

```bash
uv run adp chat connector-gong-package.yaml "show me 5 recent calls"
```

Use `--quiet` to hide tool call details and show only the final answer.

```bash
uv run adp chat connector-gong-package.yaml "show me 5 recent calls" --quiet
```

You can also use an aggregate configuration.

```bash
uv run adp chat connectors.yaml "show me 5 users from each system"
```

### Interactive REPL

Omit the prompt to start an interactive session. The REPL maintains conversation history across turns, so you can ask follow-up questions.

```bash
uv run adp chat connector-gong-package.yaml
```

Type `exit`, `quit`, or press Ctrl-C to end the session.
