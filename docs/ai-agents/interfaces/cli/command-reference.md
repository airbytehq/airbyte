---
plan: all
sidebar_position: 7
---

# Command reference

Every command on the CLI follows the same shape:

```bash
airbyte-agent <resource> <operation> [flags]
```

Run `airbyte-agent --help` to list resources, `airbyte-agent <resource> --help` to list operations, and `airbyte-agent <resource> <operation> --describe` to print the parameter schema and the underlying OpenAPI request and response shapes without executing the call. This page summarizes that surface in one place.

:::note Single source of truth
If anything on this page disagrees with `--describe` output, `--describe` wins. Run it whenever you need the canonical parameter list for a command.
:::

## Common flags

These flags are available on every operation.

| Flag | Description | Default |
| --- | --- | --- |
| `--json` | Inline JSON parameters. Pass `@filename` to load from a file. Mutually exclusive with per-parameter flags. | — |
| `--format` | Output format: `json` or `table`. | `json` |
| `--describe` | Print the operation's parameter schema (plus OpenAPI shape) and exit without executing. | `false` |
| `--output`, `-o` | Write stdout to a file instead of the terminal. | — |
| `--verbose`, `-v` | Enable debug logging on stderr. | `false` |
| `--fields` | Client-side response filter. Comma-separated dot paths (for example, `data.id,data.name`). Errors are not filtered. | — |

Per-parameter flags are generated from each operation's schema. Snake_case parameter names become kebab-case flags — for example, `select_fields` is exposed as `--select-fields`.

## `organizations`

### `organizations list`

List the organizations you belong to.

```bash
airbyte-agent organizations list
airbyte-agent organizations list --format table --fields id,organization_name
```

No required parameters.

## `workspaces`

### `workspaces list`

List or filter workspaces in the current organization. Paginates automatically.

```bash
airbyte-agent workspaces list --json '{"name_contains": "prod", "status": "active", "limit": 10}'
```

| Param | Type | Required | Description |
| --- | --- | --- | --- |
| `name_contains` | string | no | Filter by case-insensitive substring match against `name`. |
| `status` | string | no | Filter by workspace status (for example, `active`). |
| `limit` | integer | no | Cap the result count. |

### `workspaces use`

Persist a default workspace name to `~/.airbyte-agent/settings.json`. Subsequent commands that take a `workspace` parameter without receiving one fall back to this value.

```bash
airbyte-agent workspaces use --json '{"name": "Production"}'
```

| Param | Type | Required | Description |
| --- | --- | --- | --- |
| `name` | string | yes | Workspace name (case-insensitive match). The canonical-cased name is what gets persisted. |

## `connectors`

### `connectors list`

List connectors in a workspace.

```bash
airbyte-agent connectors list --json '{"workspace": "default"}'
```

| Param | Type | Required | Description |
| --- | --- | --- | --- |
| `workspace` | string | yes | Workspace name. Falls back to the default set by `workspaces use`. |

### `connectors list-available`

List the connector templates you can create from. No required parameters.

```bash
airbyte-agent connectors list-available --format table
```

### `connectors describe`

Return a connector's entities, actions, and parameter schemas. See [Describe a connector](./describe-connector).

```bash
airbyte-agent connectors describe --json '{"workspace": "default", "name": "hubspot"}'
airbyte-agent connectors describe --id <connector_id>
```

| Param | Type | Required | Description |
| --- | --- | --- | --- |
| `name` | string | one of `name`+`workspace` or `id` | Connector name. Requires `workspace`. |
| `workspace` | string | with `name` | Workspace the connector lives in. |
| `id` | string | one of `name`+`workspace` or `id` | Connector ID (UUID). |

### `connectors create`

Create a new connector through the browser credential flow. See [Add a connector](./add-connector).

```bash
airbyte-agent connectors create --json '{"workspace": "default", "name": "hubspot"}'
```

| Param | Type | Required | Description |
| --- | --- | --- | --- |
| `workspace` | string | yes | Workspace to create the connector in. |
| `name` | string | one of `name` or `id` | Connector template name (for example, `hubspot`). |
| `id` | string | one of `name` or `id` | Source definition ID. Alternative to `name`. |

### `connectors execute`

Run an action against an entity on a connector. See [Execute operations](./execute).

```bash
airbyte-agent connectors execute --json '{
  "workspace": "default",
  "name": "hubspot",
  "entity": "contacts",
  "action": "read",
  "select_fields": ["id", "email"]
}'
```

| Param | Type | Required | Description |
| --- | --- | --- | --- |
| `name` | string | one of `name`+`workspace` or `id` | Connector name. Requires `workspace`. |
| `workspace` | string | with `name` | Workspace the connector lives in. |
| `id` | string | one of `name`+`workspace` or `id` | Connector ID (UUID). |
| `entity` | string | yes | Entity to act on (for example, `contacts`). |
| `action` | string | yes | Action to run (for example, `read`, `context_store_search`, `get`). |
| `params` | object | no | Action-specific arguments. Shape depends on entity and action — run `connectors describe` for the schema. |
| `select_fields` | string[] | no | Allowlist of fields the source connector should return. |
| `exclude_fields` | string[] | no | Blocklist of fields the source connector should omit. `select_fields` wins if both are passed. |

### `connectors delete`

Delete a connector. Destructive — prompts for `"Type 'yes' to confirm:"` on a TTY.

```bash
airbyte-agent connectors delete --json '{"workspace": "default", "name": "old-hubspot"}'
```

| Param | Type | Required | Description |
| --- | --- | --- | --- |
| `name` | string | one of `name`+`workspace` or `id` | Connector name. Requires `workspace`. |
| `workspace` | string | with `name` | Workspace the connector lives in. |
| `id` | string | one of `name`+`workspace` or `id` | Connector ID (UUID). |

Without a TTY (piped input from an agent harness, for example), the prompt can't run. The command refuses with a `validation_error` whose hint tells you to grant one-time permission by setting `"allow_destructive": true` in `~/.airbyte-agent/settings.json` (or `AIRBYTE_ALLOW_DESTRUCTIVE=true` for a single invocation). See [Troubleshooting](./troubleshooting#cant-confirm-destructive-delete-on-a-non-tty-machine).

## Exit codes

All errors are returned as JSON on stderr, with a stable exit code:

| Code | Meaning | Typical HTTP status |
| --- | --- | --- |
| `0` | Success. | 2xx |
| `1` | General error. | 500, others |
| `2` | Authentication error. | 401, 403 |
| `3` | Not found. | 404 |
| `4` | Validation error. | 400, 422 |

## Retry behavior

The HTTP client retries transient failures automatically:

- **Retryable:** 429 (rate limit), 502, 503, 504.
- **Not retryable:** 400, 401, 403, 404, 422.
- **Strategy:** Up to 3 retries with exponential backoff (1s, 2s, 4s).
- **Per-request timeout:** 30 seconds.

For long-running operations that exceed 30 seconds, run them via a job (for example, the [HTTP API](../api/execute) async endpoints) and poll for the result.

## Environment variables

| Variable | Description | Default |
| --- | --- | --- |
| `AIRBYTE_CLIENT_ID` | OAuth client ID. | (required) |
| `AIRBYTE_CLIENT_SECRET` | OAuth client secret. | (required) |
| `AIRBYTE_ORGANIZATION_ID` | Organization ID. | (required) |
| `AIRBYTE_WORKSPACE` | Default workspace name when commands don't pass `workspace`. | `default` |
| `AIRBYTE_API_HOST` | API base URL. | `https://api.airbyte.ai` |
| `AIRBYTE_WEBAPP_URL` | Web app URL for the [`connectors create`](./add-connector) browser flow. | `https://app.airbyte.ai` |
| `AIRBYTE_CREDENTIAL_TIMEOUT` | Credential-flow timeout in seconds. | `180` |
| `AIRBYTE_ALLOW_DESTRUCTIVE` | When truthy (`1`/`true`/`yes`/`on`), skip the interactive confirmation prompt on destructive commands. | (settings file) |
| `AIRBYTE_TELEMETRY_MODE` | Set to `disabled` to turn off telemetry emission. | (settings file) |
| `AIRBYTE_EXECUTION_CONTEXT` | Self-reported invocation context. Common values: `mcp`, `agent`, `direct`. | `direct` |

The full env var matrix, including internal-user flags, lives in the [CLI repo README](https://github.com/airbytehq/airbyte-agent-cli/blob/main/README.md).
