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

## Canonical agent sequence

Use this order when an agent needs to create or use a connector:

```bash
airbyte-agent login show
airbyte-agent workspaces list --fields id,name
airbyte-agent schema connectors create
airbyte-agent connectors list-available --fields id,name,connector_name
airbyte-agent connectors create --json '{"workspace":"default","name":"GitHub"}'
airbyte-agent connectors list --json '{"workspace":"default"}' --fields id,name,context_store_status
airbyte-agent connectors describe --json '{"id":"<connector-id>"}' --fields id,name,entities,schema.result.describe
airbyte-agent schema connectors execute
airbyte-agent connectors execute --json @request.json
```

After `connectors create`, always run `connectors list` and capture the exact configured connector `id` and `name`. The available connector `name` from `list-available` is a display name like `GitHub`; the configured connector `name` may include workspace-specific text. Use the returned `id` for `describe`, `execute`, and `delete` wherever supported.

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

Run `connectors describe` before executing. Prefer the configured connector `id` captured from `connectors list`:

```bash
airbyte-agent connectors describe --json '{"id":"<connector-id>"}' --fields id,name,entities,schema.result.describe
```

Use the returned schema to choose `entity`, `action`, `params`, and response fields. Don't infer them from another connector. Some connectors, including GitHub, return a large describe payload; use `--fields` first, then inspect only the entity and action you need.

### Keep responses small

`connectors execute` writes `{"status":"success","result": ...}` on success. For object results, filter under `result.<field>`. For array results, use the row fields under `result.<field>`; the CLI applies the field path to each row.

For `connectors execute`, include `select_fields` or `exclude_fields` in the JSON payload whenever you know which fields you need. Also use `--fields` to trim stdout for the agent's next step.

```bash
airbyte-agent connectors execute --json '{
  "id": "<connector-id>",
  "entity": "pull_requests",
  "action": "api_search",
  "select_fields": ["id", "number", "title", "state"],
  "params": {
    "query": "repo:airbytehq/airbyte type:pr is:open docs"
  }
}' --fields result.number,result.title,result.state
```

### Keep connector credentials in the browser widget

Manual login can avoid the browser for CLI authentication, but connector credential setup still requires the browser widget. If a task needs a new connector, run:

```bash
airbyte-agent connectors create --json '{"workspace": "default", "name": "GitHub"}'
```

Connector credential requirements are discovered inside the browser widget. The widget may require OAuth, a personal access token, an API key, 2FA, or connector-specific fields. For GitHub, OAuth is the default path, but PAT authentication is also available in the widget. Use repository names in `owner/repo` format, such as `airbytehq/airbyte`.

Do not pass third-party connector credentials as CLI JSON params. The user enters connector secrets in the browser widget so they stay out of shell history, logs, and agent transcripts.

Stop and ask the user for help if the widget hits 2FA, a missing OAuth session, an inaccessible third-party account, or repeated credential timeouts. Do not guess credentials, ask for secrets in chat, or retry indefinitely.

### Start with read-only smoke tests

Prefer read-only actions before attempting writes. For a GitHub connector, good smoke tests are:

- `repositories.get` for a known repository. Split repository format `owner/repo`, such as `airbytehq/airbyte`, into `owner` and `repo` params.
- `pull_requests.api_search` for a narrow PR search. Include repository scope in the GitHub search query, such as `repo:airbytehq/airbyte type:pr is:open`.
- `users.get` for a known GitHub username.

Example repository read:

```bash
airbyte-agent connectors execute --json '{
  "id": "<connector-id>",
  "entity": "repositories",
  "action": "get",
  "params": {
    "owner": "airbytehq",
    "repo": "airbyte"
  },
  "select_fields": ["id", "name"]
}' --fields result.id,result.name
```

Example user read:

```bash
airbyte-agent connectors execute --json '{
  "id": "<connector-id>",
  "entity": "users",
  "action": "get",
  "params": {
    "username": "airbytehq"
  },
  "select_fields": ["id", "login"]
}' --fields result.id,result.login
```

Example PR search:

```bash
airbyte-agent connectors execute --json '{
  "id": "<connector-id>",
  "entity": "pull_requests",
  "action": "api_search",
  "params": {
    "query": "repo:airbytehq/airbyte type:pr is:open docs"
  },
  "select_fields": ["number", "title", "state"]
}' --fields result.number,result.title,result.state
```

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
3. If a connector is missing, create it through the browser widget.
4. Immediately list connectors in the workspace and capture the exact configured connector `id` and `name`.
5. Describe the connector by `id` with `--fields` to keep the schema output focused.
6. Run a read-only execute smoke test first.
7. Execute the smallest action that answers the user's request.
8. Filter outputs with API-side field selection and `--fields`.
