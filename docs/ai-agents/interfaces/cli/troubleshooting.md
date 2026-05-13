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
  "type": "auth_error",
  "message": "no credentials configured: set AIRBYTE_CLIENT_ID and AIRBYTE_CLIENT_SECRET environment variables, or create ~/.airbyte-agent/credentials",
  "status_code": 401,
  "retryable": false
}
```

Exit code `2`.

### Cause

Either `~/.airbyte-agent/settings.json` doesn't exist, or it exists but `client_id`, `client_secret`, or `organization_id` is missing. Environment variables are also unset, or only some of `AIRBYTE_CLIENT_ID`, `AIRBYTE_CLIENT_SECRET`, and `AIRBYTE_ORGANIZATION_ID` are set (env-var resolution requires all three).

The error text refers to a legacy `~/.airbyte-agent/credentials` path and only the two OAuth env vars. The current settings file is `~/.airbyte-agent/settings.json` and resolution requires the organization ID as well. The fix below is what to actually do.

### Fix

Run `airbyte-agent configure` to prompt for the three values and write the settings file. See [Authenticate](./authenticate) for the alternatives.

## Authentication fails

### Symptom

```json
{
  "type": "unauthorized",
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

Run `airbyte-agent workspaces list` to see the canonical names, then retry the command with the right one. To stop typing it on every call, persist a default with `airbyte-agent workspaces use --json '{"name": "..."}'`. See [List and set workspaces](./workspaces#set-a-default-workspace).

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
airbyte-agent connectors list --json '{"workspace": "default"}'
```

If the connector genuinely doesn't exist yet, create it with [`connectors create`](./add-connector).

## Destructive delete on a non-TTY machine

### Symptom

```json
{
  "type": "validation_error",
  "message": "destructive action requires confirmation but no TTY is available",
  "status_code": 400,
  "hint": "set \"allow_destructive\": true in ~/.airbyte-agent/settings.json (or AIRBYTE_ALLOW_DESTRUCTIVE=true) to allow non-interactive destructive operations"
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

[`connectors create`](./add-connector) returns successfully (exit code `0`) and prints a result object to stdout with an `error` field:

```json
{
  "error": "timeout",
  "message": "Credential flow timed out after 3m0s",
  "session_id": "<session-uuid>"
}
```

This is not a structured CLI error (`type` / `status_code` / exit code 4). It's the success-path payload of the create command, indicating the polling loop expired before the browser flow completed.

### Cause

`connectors create` opens a browser and polls for completion. If you don't finish signing in within 180 seconds (the default), the polling loop exits and returns the timeout result.

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

`select_fields` (and `exclude_fields`) is API-side; the source connector doesn't emit columns you don't need. `--fields` is client-side; it trims what the CLI prints to stdout. They're complementary. See [Filter the response](./execute#filter-the-response).

For very large responses, also write the output to a file:

```bash
airbyte-agent connectors execute --json '{...}' -o response.json
```

## `--describe` returns no `api` block or `not_supported`

### Symptom

One of two things happens when you run `--describe` (or the equivalent `airbyte-agent schema <resource> <operation>`):

1. The response includes `params` but the `api` block is empty or missing.
2. The response is an error on stderr with exit code `3`:

   ```json
   {
     "type": "not_supported",
     "message": "no published schema for \"list\"; run `airbyte-agent organizations list --help` for argument details"
   }
   ```

### Cause

The OpenAPI schemas in `--describe` are extracted at build time from the CLI's checked-in specs and only cover routes the CLI maps to a public API endpoint.

- Case 1 happens when the operation maps to a route that exists in the public spec but isn't bundled, leaving `params` populated but `api` empty.
- Case 2 happens when the operation maps to an internal-only route (any path starting with `/api/v1/internal/`). The schema lookup deliberately refuses these. Today this affects `organizations list`; the same shape applies to any future operation backed by an internal route.

### Fix

For case 1, no action needed. `params` is authoritative for what the CLI accepts. The missing `api` block only means there's no public REST endpoint to show alongside it.

For case 2, run `airbyte-agent <resource> <operation> --help` instead. The Cobra-generated help text lists the flags the CLI exposes.

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
