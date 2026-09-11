---
plan: all
sidebar_position: 7
---

# Command reference

Run `airbyte-agent --help` to list top-level commands, `airbyte-agent <resource> --help` to list operations, and `airbyte-agent <resource> <operation> --help` for operation flags.

Run `airbyte-agent schema <resource> <operation>` to print the CLI parameter schema plus OpenAPI request and response schemas when a published API schema exists.

> Schema output wins. If this page disagrees with `airbyte-agent schema <resource> <operation>`, trust the `schema` output. For internal operations without a published schema, use `--help`.

## Common flags

Resource operations share these flags:

- **`--json`**: Input parameters as inline JSON or `@filename`. Mutually exclusive with per-parameter flags.
- **`--fields`**: Filter the JSON response to comma-separated dotted paths.
- **`--output`, `-o`**: Write stdout to a file.
- **`--verbose`, `-v`**: Print debug logging to stderr.

Per-parameter flags are generated from the operation schema. Snake_case parameter names become kebab-case flags. For example, `select_fields` becomes `--select-fields`.

## Top-level commands

- **`airbyte-agent login`**: Browser login. Writes credentials to `$HOME/.airbyte-agent/settings.json`.
- **`airbyte-agent login --manual`**: Prompt-based login for headless machines.
- **`airbyte-agent login --org-id <uuid>`**: Browser login that skips the multi-organization picker.
- **`airbyte-agent login show`**: Print saved settings with `client_secret` obfuscated.
- **`airbyte-agent schema <resource> <operation>`**: Print the operation schema without making an API call.
- **`airbyte-agent version`**: Print the CLI version.
- **`airbyte-agent completion <shell>`**: Generate shell completion for `bash`, `zsh`, `fish`, or `powershell`.

## `organizations`

### `organizations list`

List organizations for the authenticated account:

```bash
airbyte-agent organizations list
```

No parameters.

### `organizations use`

Save the default organization:

```bash
airbyte-agent organizations use --json '{"id": "<organization-id>"}'
```

Parameters:

- **`id`** (string, required: Yes): Organization UUID. Must belong to the authenticated account.

## `workspaces`

### `workspaces list`

List workspaces:

```bash
airbyte-agent workspaces list
```

Parameters:

- **`name_contains`** (string, required: No): Filter by name substring.
- **`status`** (string, required: No): Filter by status.
- **`limit`** (integer, required: No): Maximum total rows to return.

### `workspaces use`

Save the default workspace:

```bash
airbyte-agent workspaces use --json '{"name": "default"}'
```

Parameters:

- **`name`** (string, required: Yes): Workspace name. The CLI verifies it exists before saving.

## `connectors`

### `connectors list-available`

List connectors available to your organization:

```bash
airbyte-agent connectors list-available --fields id,name,connector_name
```

No CLI input parameters. `airbyte-agent schema connectors list-available` currently reports an empty params object, so don't pass filters in `--json` or as per-parameter flags.

### `connectors create`

Create a connector through a browser credential flow:

```bash
airbyte-agent connectors create --json '{
  "workspace": "default",
  "name": "GitHub"
}'
```

Parameters:

- **`id`** (string, required: No): Connector ID. Use this or `name`.
- **`name`** (string, required: No): Connector display name, such as `GitHub`. Use this or `id`.
- **`workspace`** (string, required: No): Workspace name. Defaults to the saved workspace, then `default`.

### `connectors list`

List configured connectors in a workspace:

```bash
airbyte-agent connectors list --json '{"workspace": "default"}'
```

Parameters:

- **`workspace`** (string, required: No): Workspace name. Defaults to the saved workspace, then `default`.

The command enriches connector rows with `context_store_status` and `context_store_entity_count` when the credentials endpoint is available.

### `connectors describe`

Get connector details and schema:

```bash
airbyte-agent connectors describe --json '{
  "workspace": "default",
  "name": "GitHub"
}'
```

Parameters:

- **`id`** (string, required: No): Connector ID. Use this or `name` with `workspace`.
- **`name`** (string, required: No): Connector name. Requires `workspace` or a saved default workspace.
- **`workspace`** (string, required: No): Workspace name. Defaults to the saved workspace, then `default`, when used with `name`.

### `connectors execute`

Execute an action:

```bash
airbyte-agent connectors execute --json '{
  "workspace": "default",
  "name": "GitHub",
  "entity": "issues",
  "action": "context_store_search",
  "select_fields": ["id", "title"],
  "params": {
    "limit": 10
  }
}'
```

Parameters:

- **`id`** (string, required: No): Connector ID. Use this or `name` with `workspace`.
- **`name`** (string, required: No): Connector name. Requires `workspace` or a saved default workspace.
- **`workspace`** (string, required: No): Workspace name. Required when using `name` unless a default workspace is saved.
- **`entity`** (string, required: Yes): Entity name from `connectors describe`.
- **`action`** (string, required: Yes): Action name from `connectors describe`.
- **`params`** (object, required: No): Action-specific parameters.
- **`select_fields`** (array, required: No): Fields to include in the response.
- **`exclude_fields`** (array, required: No): Fields to exclude from the response.
- **`skip_truncation`** (boolean, required: No): Disable automatic truncation of long text fields in list and search responses. This maps to `--skip-truncation` when using per-parameter flags.

### `connectors update`

Open the browser URL for editing an existing connector. The CLI doesn't edit connector configuration directly:

```bash
airbyte-agent connectors update --json '{
  "workspace": "default",
  "name": "GitHub"
}'
```

Parameters:

- **`id`** (string, required: No): Connector ID. Use this or `name` with `workspace`.
- **`name`** (string, required: No): Connector name. Requires `workspace` or a saved default workspace.
- **`workspace`** (string, required: No): Workspace name. Defaults to the saved workspace, then `default`, when used with `name`.

The command returns a URL, the connector ID, a message that connectors can't be edited through the CLI, and `browser_opened`. It only opens the browser after an exact `yes` confirmation. In non-interactive contexts, use the returned URL if the prompt isn't answered.

### `connectors delete`

Delete a connector:

```bash
airbyte-agent connectors delete --json '{
  "workspace": "default",
  "name": "GitHub"
}'
```

Parameters:

- **`id`** (string, required: No): Connector ID. Use this or `name` with `workspace`.
- **`name`** (string, required: No): Connector name. Requires `workspace` or a saved default workspace.
- **`workspace`** (string, required: No): Workspace name. Defaults to the saved workspace, then `default`, when used with `name`.

Unless `AIRBYTE_ALLOW_DESTRUCTIVE` or `allow_destructive` is true, the command prompts for confirmation before deleting.

## Exit codes

- **`0`**: Success.
- **`1`**: General error. Some token-exchange and authentication failures currently return `1` with a JSON error such as `token exchange failed (status 401)`.
- **`2`**: Authentication or authorization error when the CLI can classify it before returning.
- **`3`**: Not found.
- **`4`**: Validation error.

On failure, read the JSON error written to stderr. The `type`, `status_code`, and `message` fields are more specific than the exit code and are safer for scripts to branch on.
