---
plan: all
sidebar_position: 6
---

# Use the CLI with AI agents

AI agents can call `airbyte-agent` as a shell tool. The CLI gives agents a consistent command model, JSON input and output, and runtime schema discovery.

## Install the bundled skill

The CLI repository includes an agent skill at [`skills/airbyte-agent/`](https://github.com/airbytehq/airbyte-agent-cli/tree/main/skills/airbyte-agent). The install script installs it by default:

```bash
curl -fsSL https://airbyte.ai/install.sh | bash
```

To install only the binary, set:

```bash
AIRBYTE_AGENT_SKIP_SKILLS=1 curl -fsSL https://airbyte.ai/install.sh | bash
```

To install the skill to a custom directory, set `AIRBYTE_AGENT_SKILLS_DIR`.

If your harness supports the `skills` CLI, you can also install from GitHub:

```bash
npx skills add airbytehq/airbyte-agent-cli
```

## Rules for agents

### Read the command schema first

Before calling an unfamiliar operation, run:

```bash
airbyte-agent schema <resource> <operation>
```

If the command returns `not_supported`, fall back to:

```bash
airbyte-agent <resource> <operation> --help
```

### Use JSON input

Agents should pass parameters as one JSON payload:

```bash
airbyte-agent connectors list --json '{"workspace": "default"}'
```

Don't mix `--json` with per-parameter flags. The CLI rejects that combination.

### Describe before execute

Run `connectors describe` before executing:

```bash
airbyte-agent connectors describe --json '{
  "workspace": "default",
  "name": "GitHub"
}'
```

Use the returned schema to choose `entity`, `action`, `params`, and response fields. Don't infer them from another connector.

### Keep responses small

For `connectors execute`, include `select_fields` or `exclude_fields` in the JSON payload whenever you know which fields you need. Also use `--fields` to trim stdout for the agent's next step.

```bash
airbyte-agent connectors execute --json '{
  "workspace": "default",
  "name": "GitHub",
  "entity": "issues",
  "action": "context_store_search",
  "select_fields": ["id", "title", "state"],
  "params": {
    "limit": 10
  }
}' --fields data.id,data.title
```

### Never ask for third-party connector secrets in chat

If a task needs a new connector, run:

```bash
airbyte-agent connectors create --json '{"workspace": "default", "name": "GitHub"}'
```

The user enters credentials in the browser. The agent should not collect or echo third-party API keys, OAuth tokens, passwords, or one-time codes.

### Parse stderr JSON on failures

The CLI writes machine-readable errors to stderr. Branch on the JSON `type` field first, then use the exit code as a coarse fallback.

Common error types include:

- `auth_error` or `unauthorized`: run `airbyte-agent login`, then retry.
- `not_found`: list the relevant resource and correct the ID or name.
- `validation_error`: fix the payload shape or required fields.
- `rate_limited`: retry later with backoff.
- `not_supported`: use `--help` instead of `schema` for that internal operation.

## Agent workflow

A safe workflow for an agent is:

1. Check authentication with `airbyte-agent login show`.
2. List workspaces or use the saved default workspace.
3. List connectors in the workspace.
4. Describe the connector.
5. Execute the smallest action that answers the user's request.
6. Filter outputs with API-side field selection and `--fields`.
