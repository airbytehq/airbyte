---
plan: all
sidebar_position: 7
---

# Command reference

Every command on the CLI follows the same shape:

```bash
airbyte-agent <resource> <operation> [flags]
```

Run `airbyte-agent --help` to list resources, `airbyte-agent <resource> --help` to list operations, and `airbyte-agent <resource> <operation> --describe` to print the parameter schema (plus the underlying OpenAPI request and response shapes when the operation maps to a public API route) without executing the call. This page summarizes that surface in one place.

:::note Single source of truth
If anything on this page disagrees with `--describe` output, `--describe` wins. Run it whenever you need the canonical parameter list for a command.
:::

## Common flags

These flags are exposed on every resource operation:

| Flag | Description | Default |
| --- | --- | --- |
| `--json` | Inline JSON parameters. Pass `@filename` to load from a file. Mutually exclusive with per-parameter flags. | (none) |
| `--format` | Output format: `json` or `table`. `table` works best on operations whose response is a flat array of records; responses wrapped in `{ "data": [...], "meta": {...} }` render with the array under a `DATA` column. When in doubt, stick with `json` and use `--fields` to trim it. | `json` |
| `--describe` | Print the operation's parameter schema (and OpenAPI shape, when the operation maps to a public API route) and exit without executing. Operations backed by internal-only routes return `{"type": "not_supported", ...}` on stderr with exit code `3`; use `--help` instead. | `false` |
| `--output`, `-o` | Write stdout to a file instead of the terminal. | (none) |
| `--verbose`, `-v` | Enable debug logging on stderr. | `false` |
| `--fields` | Client-side response filter. Comma-separated dot paths (for example, `organizations.id,organizations.organization_name`). Errors are not filtered. | (none) |

Per-parameter flags are generated from each operation's schema. Snake_case parameter names become kebab-case flags. For example, `select_fields` is exposed as `--select-fields`.

The flags above don't all apply to the top-level commands (`configure`, `configure show`, `version`, `schema`). `--json` in particular isn't a valid flag on those: `airbyte-agent version --json '{}'` exits `1` because the flag is unknown to that command.

`--fields`, `--format`, and `--output` (`-o`) are silently accepted on top-level commands but don't do anything. `version --format table` still prints JSON, `version --fields version` still prints every field, and `version -o out.json` exits `0` without writing `out.json`. Treat top-level commands as JSON-to-stdout only, and use shell tools (`jq`, redirection) if you need to post-process the result.

## Top-level commands

A few commands live at the top level rather than under a resource:

| Command | Description |
| --- | --- |
| `airbyte-agent configure` | Prompt for `client_id`, `client_secret`, `organization_id`, and a default workspace, then write `~/.airbyte-agent/settings.json` with `0600` permissions. See [Authenticate](./authenticate). |
| `airbyte-agent configure show` | Print the saved settings (with `client_secret` obfuscated). Useful for `--verbose` debugging and for sharing a redacted dump in bug reports. |
| `airbyte-agent version` | Print version, commit, and build date as JSON. |
| `airbyte-agent schema <resource> <operation>` | Equivalent to `<resource> <operation> --describe`, but discoverable as a top-level command. Returns `{"type": "not_supported", ...}` (exit `3`) for operations backed by internal-only API routes. |
| `airbyte-agent completion <shell>` | Cobra-generated shell-completion script for `bash`, `zsh`, `fish`, or `powershell`. Pipe the output into your shell's completion directory. Run `airbyte-agent completion --help` for installation steps. |

## `organizations`

### `organizations list`

List the organizations you belong to.

```bash
airbyte-agent organizations list
airbyte-agent organizations list --fields organizations.id,organizations.organization_name
```

The response is wrapped under an `organizations` key (`{"organizations": [...], "is_instance_admin": ...}`), so `--fields` paths start with `organizations.` rather than `data.`.

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

Requires an existing `~/.airbyte-agent/settings.json`. Run `airbyte-agent configure` first on a fresh machine; `workspaces use` doesn't bootstrap a settings file from environment variables alone.

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

List the connectors you can create. No required parameters.

```bash
airbyte-agent connectors list-available
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
| `name` | string | one of `name` or `id` | Connector name (for example, `hubspot`). |
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
| `params` | object | no | Action-specific arguments. Shape depends on entity and action; run `connectors describe` for the schema. |
| `select_fields` | string[] | no | Allowlist of fields the source connector should return. |
| `exclude_fields` | string[] | no | Blocklist of fields the source connector should omit. `select_fields` wins if both are passed. |

### `connectors delete`

Delete a connector. This is destructive, so on a TTY it prompts for `"Type 'yes' to confirm:"`.

```bash
airbyte-agent connectors delete --json '{"workspace": "default", "name": "old-hubspot"}'
```

| Param | Type | Required | Description |
| --- | --- | --- | --- |
| `name` | string | one of `name`+`workspace` or `id` | Connector name. Requires `workspace`. |
| `workspace` | string | with `name` | Workspace the connector lives in. |
| `id` | string | one of `name`+`workspace` or `id` | Connector ID (UUID). |

If you type something other than `yes` (or just press Enter), the command exits `4` with `"destructive action cancelled by user"`. Without a TTY (piped input from an agent harness, for example), the prompt can't run at all and the command refuses with `"destructive action requires confirmation but no TTY is available"`. Grant one-time permission to skip the prompt by setting `"allow_destructive": true` in `~/.airbyte-agent/settings.json` (or `AIRBYTE_ALLOW_DESTRUCTIVE=true` for a single invocation). See [Troubleshooting](./troubleshooting#destructive-delete-refused).

## Exit codes

All errors are returned as JSON on stderr, with a stable exit code:

| Code | Meaning | Typical HTTP status |
| --- | --- | --- |
| `0` | Success. | 2xx |
| `1` | General error. | 500, others |
| `2` | Authentication error. | 401, 403 |
| `3` | Not found. | 404 |
| `4` | Validation error. | 400, 422 |

The mapping above is the contract for **server-side** failures: anything the API returns with a recognized HTTP status maps to a typed exit code. **Client-side** validation (malformed inputs, bad UUIDs, unknown flags, unreachable hosts) may exit `1` with `{"type": "error", ...}` even when the underlying problem is auth- or validation-shaped. Don't dispatch on exit code alone: agents and scripts should parse the stderr JSON and branch on the `type` field. See [Rules for agents](./using-with-ai-agents#rules-for-agents).

## Retry behavior

The HTTP client retries transient failures automatically:

- **Retryable:** 429 (rate limit), 502, 503, 504.
- **Not retryable:** 400, 401, 403, 404, 422.
- **Strategy:** Up to 3 retries with exponential backoff (1s, 2s, 4s).
- **Per-request timeout:** 30 seconds.

For long-running operations that exceed 30 seconds, run them via a job (for example, the [Agent API](../api/execute) async endpoints) and poll for the result.

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
