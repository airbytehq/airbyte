---
plan: all
sidebar_position: 8
---

# Troubleshooting

Errors from the CLI are returned as JSON on stderr with a stable exit code. The full taxonomy is in the [command reference](./command-reference#exit-codes). This page covers the common ones, plus a few non-error symptoms that come up in day-to-day use.

For every entry: **Symptom → Cause → Fix.**

## Missing settings on a fresh machine

### Symptom

```json
{
  "type": "authentication_error",
  "message": "no credentials found",
  "status_code": 401,
  "retryable": false
}
```

Exit code `2`.

### Cause

Either `~/.airbyte-agent/settings.json` doesn't exist, or it exists but `client_id`, `client_secret`, or `organization_id` is missing. Environment variables are also unset (or only some of the three are set — env-var resolution requires all three).

### Fix

Run `airbyte-agent configure` to prompt for the three values and write the settings file. See [Authenticate](./authenticate) for the alternatives.

## Authentication fails

### Symptom

```json
{
  "type": "authentication_error",
  "message": "invalid client credentials",
  "status_code": 401,
  "retryable": false
}
```

Exit code `2`.

### Cause

Stale or rotated credentials, a `client_id`/`client_secret` from a different organization, or a typo when you ran `configure`.

### Fix

1. Re-read your credentials from **Settings > Profile** in the web app.
2. Re-run `airbyte-agent configure`, or update the env vars.
3. If you switched orgs, also update `AIRBYTE_ORGANIZATION_ID`.

## Workspace not found

### Symptom

```json
{
  "type": "not_found",
  "message": "workspace \"prod\" not found",
  "status_code": 404,
  "hint": "run 'airbyte-agent workspaces list' to see available workspaces"
}
```

Exit code `3`.

### Cause

Typo in the workspace name, or the workspace was deleted.

### Fix

Run `airbyte-agent workspaces list --format table` to see the canonical names, then retry the command with the right one. To stop typing it on every call, persist a default with `airbyte-agent workspaces use --json '{"name": "..."}'` — see [List and set workspaces](./workspaces#set-a-default-workspace).

## Connector not found

### Symptom

```json
{
  "type": "not_found",
  "message": "connector \"gong\" not found in workspace \"default\"",
  "status_code": 404,
  "hint": "run 'airbyte-agent connectors list --json {\"workspace\": \"default\"}' to see available connectors"
}
```

Exit code `3`.

### Cause

The named connector doesn't exist in that workspace. Often this means it lives in a different workspace, or it was created under a different name.

### Fix

```bash
airbyte-agent connectors list --json '{"workspace": "default"}' --format table
```

If the connector genuinely doesn't exist yet, create it with [`connectors create`](./add-connector).

## Destructive delete on a non-TTY machine

### Symptom

```json
{
  "type": "validation_error",
  "message": "destructive operation requires explicit permission on non-TTY",
  "status_code": 400,
  "hint": "set \"allow_destructive\": true in ~/.airbyte-agent/settings.json (or AIRBYTE_ALLOW_DESTRUCTIVE=true)"
}
```

Exit code `4`.

### Cause

`connectors delete` is destructive. On a terminal, it prompts for `"Type 'yes' to confirm:"`. When stdin is piped (an agent harness driving the CLI, a CI job, a script), there's nothing to type, so the command refuses rather than hanging on a prompt that can never resolve.

### Fix

Grant one-time permission. Either:

```bash
AIRBYTE_ALLOW_DESTRUCTIVE=true airbyte-agent connectors delete --json '{"workspace": "default", "name": "old-hubspot"}'
```

…or set `"allow_destructive": true` in `~/.airbyte-agent/settings.json` for a persistent grant. This is intended as a deliberate permission for agent harnesses that have no way to answer a TTY prompt.

## Credential-flow timeout

### Symptom

```json
{
  "type": "validation_error",
  "message": "credential flow timed out after 180 seconds",
  "status_code": 408,
  "retryable": false
}
```

Exit code `4`.

### Cause

[`connectors create`](./add-connector) opens a browser and polls for completion. If you don't finish signing in within 180 seconds (the default), the CLI gives up.

### Fix

Re-run the command and complete the browser flow faster. For slow flows (corporate SSO, MFA prompts, multi-step OAuth), raise the timeout:

```bash
AIRBYTE_CREDENTIAL_TIMEOUT=600 airbyte-agent connectors create --json '{
  "workspace": "default",
  "name": "salesforce"
}'
```

If the browser doesn't open automatically (headless machine, SSH session, restricted environment), the CLI prints the credential-flow URL to stderr. Open it manually on a device that has a browser.

## Large responses

### Symptom

`connectors execute` returns a payload that overflows your terminal, your agent's context window, or your shell pipeline.

### Cause

The default response shape for many connectors includes nested objects and metadata you don't need.

### Fix

Filter the response with both layers of `select_fields` and `--fields`:

```bash
airbyte-agent connectors execute --json '{
  "workspace": "default",
  "name": "hubspot",
  "entity": "contacts",
  "action": "read",
  "select_fields": ["id", "email", "name"]
}' --fields data.id,data.email,data.name
```

`select_fields` (and `exclude_fields`) is API-side — the source connector doesn't emit columns you don't need. `--fields` is client-side — it trims what the CLI prints to stdout. They're complementary. See [Filter the response](./execute#filter-the-response).

For very large responses, also write the output to a file:

```bash
airbyte-agent connectors execute --json '{...}' -o response.json
```

## `--describe` returns no `api` block

### Symptom

Running `--describe` returns the `params` section but the `api` block is empty or missing.

### Cause

The OpenAPI schemas in `--describe` are extracted at build time from the CLI's checked-in specs and only cover routes the CLI maps to a public API endpoint. Some operations (for example, internal helpers) don't have a public OpenAPI counterpart, so there's no API shape to print.

### Fix

No action needed — the `params` section is still authoritative for what the CLI accepts. The missing `api` block only means there's no public REST endpoint to show alongside it.

## Rate limited

### Symptom

```json
{
  "type": "rate_limited",
  "message": "rate limit exceeded",
  "status_code": 429,
  "retryable": true
}
```

### Cause

You (or your agent) made too many requests in a short window.

### Fix

The CLI already retries 429s with exponential backoff (3 attempts, 1s/2s/4s). If you're still hitting the limit, slow down your loop or batch operations. See [Retry behavior](./command-reference#retry-behavior).
