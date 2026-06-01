---
plan: all
sidebar_position: 2
---

# Add a connector

A connector stores credentials and configuration for a third-party service in an Airbyte Agents workspace. Create a connector once, then reference it by `id` when you describe it or execute actions.

`connectors create` opens a browser flow for third-party credential entry. Manual login can avoid the browser for CLI authentication, but connector credential setup still requires the browser widget. The CLI doesn't accept third-party API keys, OAuth tokens, passwords, or other connector credentials as command parameters.

:::warning

Never paste third-party credentials into the CLI. Use `connectors create` and complete credential entry in the browser. This keeps secrets out of shell history, logs, and agent transcripts.

:::

## Find an available connector

List the connectors available to your organization:

```bash
airbyte-agent connectors list-available --fields id,name,connector_name
```

Use the display `name` or returned `id` with `connectors create`. Name matching is case-insensitive. After creation, prefer the configured connector `id`; the configured connector `name` may differ from the available connector display name.

## Create a connector

Create by connector name:

```bash
airbyte-agent connectors create --json '{
  "workspace": "default",
  "name": "GitHub"
}'
```

Create by connector ID:

```bash
airbyte-agent connectors create --json '{
  "workspace": "default",
  "id": "<connector-id>"
}'
```

What happens:

1. The CLI resolves the connector.
2. It creates a short-lived browser credential session.
3. It prints a `credentials_url` JSON object to stderr and opens your browser.
4. You complete the third-party credential flow in the browser.
5. The CLI polls for completion, creates the connector, and prints the connector response to stdout.

In an interactive terminal, stderr and stdout appear together. For agents or logs, redirect stderr separately so you can distinguish the initial browser-session payload from the final connector response:

```bash
airbyte-agent connectors create --json '{"workspace":"default","name":"GitHub"}' \
  >connector-response.json \
  2>credential-session.json
```

Initial stderr payload:

```json
{
  "credentials_url": "https://app.airbyte.ai/widget-bridge?...",
  "session_id": "...",
  "message": "Opening browser to complete credential setup. Waiting for credentials..."
}
```

Final stdout payload after credentials complete:

```json
{
  "status": "success",
  "result": {
    "id": "...",
    "name": "GitHub - default"
  }
}
```

When the command returns, save the connector `id`. Use it with [`connectors describe`](./describe-connector), [`connectors execute`](./execute), or [`connectors delete`](./command-reference#connectors-delete). To change connector credentials or configuration, use [`connectors update`](./command-reference#connectors-update) to open the web edit URL; the CLI doesn't edit connector configuration directly.

## Credential-flow timeout

By default, `connectors create` waits 180 seconds for you to finish the browser flow. Increase the timeout for slower flows:

```bash
AIRBYTE_CREDENTIAL_TIMEOUT=300 airbyte-agent connectors create --json '{
  "workspace": "default",
  "name": "GitHub"
}'
```

If the timeout expires, the credential session didn't complete and no connector was created. The command returns JSON that indicates the credential session timed out and includes the `session_id`. Re-run `connectors create` to start a new credential flow.

## If the browser doesn't open

The CLI prints the credential URL to stderr before it tries to open the browser:

```json
{
  "credentials_url": "https://app.airbyte.ai/widget-bridge?...",
  "session_id": "...",
  "message": "Opening browser to complete credential setup. Waiting for credentials..."
}
```

Open `credentials_url` manually in a browser where you can sign in to the third-party service.

## Confirm the connector exists

List configured connectors:

```bash
airbyte-agent connectors list --json '{"workspace": "default"}' --fields id,name,context_store_status,context_store_entity_count
```

`context_store_status` describes indexing for search-style actions. `null` is expected for direct/API-only connectors or connectors that haven't started indexing. Timeout values such as `FIRST_PULL_PREVIEW_TIMEOUT` mean indexing didn't finish in the expected window. Direct actions such as `get`, `list`, or provider-native `api_search` can still work before context-store indexing is ready, when the connector exposes those actions.

Next, run [`connectors describe`](./describe-connector) to inspect the connector's entities, actions, and parameter schemas.
