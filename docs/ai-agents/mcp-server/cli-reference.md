---
sidebar_label: "Command line tool reference"
sidebar_position: 4
---

# Command line reference

All commands use `uv run adp <command>`. Use `--help` on any command for full options.

### Global flags

| Flag | Description |
| --- | --- |
| `--config-dir`, `-d` | Config directory (default: `~/.airbyte_agent_mcp`). Can also be set with the `AIRBYTE_CONFIG_DIR` environment variable. |
| `--org` | Organization ID to use, overriding the default set by `adp login`. |

## `adp connectors list-oss`

List available open source connectors from the Airbyte registry.

```bash
uv run adp connectors list-oss
uv run adp connectors list-oss --pattern salesforce
```

| Flag              | Description               |
| ----------------- | ------------------------- |
| `--pattern`, `-p` | Filter connectors by name |

## `adp connectors list-cloud`

List connectors configured in your Agent Engine organization. Requires [`adp login`](#adp-login) first.

```bash
uv run adp connectors list-cloud
uv run adp connectors list-cloud --customer acme
```

| Flag             | Description             |
| ---------------- | ----------------------- |
| `--customer`, `-c` | Filter by customer name |
| `--customer-id`  | Filter by customer ID   |

## `adp connectors configure`

Generate a connector configuration file by inspecting the connector's authentication requirements.

```bash
uv run adp connectors configure --package airbyte-agent-gong
uv run adp connectors configure --connector-id <your-connector-id>
```

| Flag                   | Description                                          |
| ---------------------- | ---------------------------------------------------- |
| `--package`            | PyPI package name, local path, or `git+https://` URL |
| `--connector-id`, `-c` | Agent Engine connector ID                            |
| `--version`, `-v`      | Package version (PyPI only)                          |
| `--filename`, `-f`      | Output file path (auto-generated if not specified)     |
| `--overwrite`, `-o`    | Overwrite the output file if it already exists        |

## `adp login`

Save Agent Engine credentials to the global config directory. Prompts for your Client ID and Secret, then stores them for subsequent commands.

```bash
uv run adp login <organization-id>
```

| Flag                | Description                                  |
| ------------------- | -------------------------------------------- |
| `<organization-id>` | Your Agent Engine organization ID (required) |

## `adp orgs`

Manage logged-in organizations.

```bash
uv run adp orgs list
uv run adp orgs default
uv run adp orgs default <org-id>
```

| Subcommand         | Description                      |
| ------------------ | -------------------------------- |
| `list`             | List all logged-in organizations |
| `default`          | Show the default organization    |
| `default <org-id>` | Set the default organization     |

## `adp mcp serve`

Start the MCP server with a connector configuration.

```bash
uv run adp mcp serve connector-gong-package.yaml
uv run adp mcp serve connector-gong-package.yaml --transport http --port 8080
```

| Flag                | Default     | Description                            |
| ------------------- | ----------- | -------------------------------------- |
| `--transport`, `-t` | `stdio`     | Transport protocol (`stdio` or `http`) |
| `--host`, `-h`      | `127.0.0.1` | Host to bind to (HTTP only)            |
| `--port`, `-p`      | `8000`      | Port to bind to (HTTP only)            |

## `adp mcp add-to`

Register the MCP server with an agent. Supported targets: `claude-code`, `claude-desktop`, `cursor`, `codex`.

```bash
uv run adp mcp add-to claude-code connector-gong-package.yaml
uv run adp mcp add-to cursor connector-gong-package.yaml --scope project
```

| Flag            | Default | Description                                                    |
| --------------- | ------- | -------------------------------------------------------------- |
| `--name`, `-n`  | Auto    | Name for the MCP server (default: `airbyte-<connector>`)       |
| `--scope`, `-s` | `user`  | Configuration scope: `user` or `project` (Claude Code, Cursor)  |

## `adp chat`

Chat with connector data using natural language in the terminal. Uses Claude and requires an `ANTHROPIC_API_KEY` environment variable. Pass a prompt argument for one-shot mode, or omit it to start an interactive REPL.

```bash
uv run adp chat connector-gong-package.yaml "show me 5 recent calls"
uv run adp chat connector-gong-package.yaml
```

| Flag            | Default           | Description                                  |
| --------------- | ----------------- | -------------------------------------------- |
| `--model`, `-m` | `claude-opus-4-6` | Anthropic model to use                       |
| `--quiet`, `-q` | `false`           | Only show the final answer (hide tool calls)  |
