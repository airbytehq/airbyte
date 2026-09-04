---
plan: all
sidebar_position: 8
---

# Troubleshoot the CLI

Use the JSON error on stderr as the primary signal. Exit codes are useful, but the `type`, `message`, and `hint` fields usually tell you what to fix.

## `no credentials configured`

The CLI couldn't resolve credentials from the environment or settings file.

Fix:

```bash
airbyte-agent login
```

For CI or headless use, set all three required environment variables:

```bash
export AIRBYTE_CLIENT_ID="<client-id>"
export AIRBYTE_CLIENT_SECRET="<client-secret>"
export AIRBYTE_ORGANIZATION_ID="<organization-id>"
```

Setting only one or two of those variables isn't enough. The CLI falls back to `$HOME/.airbyte-agent/settings.json` unless all three are present.

## `settings file does not exist`

Commands such as `workspaces use`, `organizations use`, and `login show` read or update `$HOME/.airbyte-agent/settings.json`.

Fix:

```bash
airbyte-agent login
```

## Connector or workspace not found

List the relevant resource and copy the exact name or ID:

```bash
airbyte-agent workspaces list --fields id,name
airbyte-agent connectors list --json '{"workspace": "default"}' --fields id,name
```

Use connector `id` when names are ambiguous.

## `schema` returns `not_supported`

Some operations use internal routes without published schemas. Use command help instead:

```bash
airbyte-agent organizations list --help
```

A `schema` response for an internal operation can look like this:

```json
{
  "type": "not_supported",
  "message": "Schema is not available for organizations list. Use --help for command details."
}
```

## `--json cannot be combined with parameter flags`

Pass input either as one JSON payload or as individual flags, not both.

Use JSON:

```bash
airbyte-agent connectors describe --json '{"workspace": "default", "name": "GitHub"}'
```

Or use flags:

```bash
airbyte-agent connectors describe --workspace default --name GitHub
```

## Browser credential flow times out

`connectors create` waits 180 seconds by default. Increase the timeout:

```bash
AIRBYTE_CREDENTIAL_TIMEOUT=300 airbyte-agent connectors create --json '{
  "workspace": "default",
  "name": "GitHub"
}'
```

If the browser doesn't open, copy the `credentials_url` printed to stderr and open it manually. If the command times out, no connector was created; re-run `connectors create` to start a new browser credential session.

## Delete prompts in non-interactive runs

`connectors delete` prompts for confirmation unless destructive operations are allowed.

For a one-off non-interactive run:

```bash
AIRBYTE_ALLOW_DESTRUCTIVE=true airbyte-agent connectors delete --json '{
  "id": "<connector-id>"
}'
```

Only use this when the connector should be deleted.

## Large outputs

Use API-side field selection and client-side filtering together:

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
}' --fields result.id,result.title
```

For list and search actions where long text fields are truncated, pass `"skip_truncation": true` in the JSON payload when you need full values.
