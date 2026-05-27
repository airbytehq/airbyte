---
plan: all
sidebar_position: 2
---

# Add a connector

A connector stores credentials and configuration for a third-party service in an Airbyte Agents workspace. Create a connector once, then reference it by `name` and `workspace`, or by `id`, when you describe it or execute actions.

`connectors create` opens a browser flow for third-party credential entry. The CLI doesn't accept third-party API keys, OAuth tokens, passwords, or other connector credentials as command parameters.

> Never paste third-party credentials into the CLI. Use `connectors create` and complete credential entry in the browser. This keeps secrets out of shell history, logs, and agent transcripts.

## Find an available connector

List the connector types available to your organization:

```bash
airbyte-agent connectors list-available --fields id,name,connector_name
```

Use the display `name` or returned `id` with `connectors create`. Name matching is case-insensitive.

## Create a connector

Create by connector name:

```bash
airbyte-agent connectors create --json '{
  "workspace": "default",
  "name": "GitHub"
}'
```

Create by connector type ID:

```bash
airbyte-agent connectors create --json '{
  "workspace": "default",
  "id": "<connector-type-id>"
}'
```

What happens:

1. The CLI resolves the connector type.
2. It creates a short-lived browser credential session.
3. It prints a `credentials_url` JSON object to stderr and opens your browser.
4. You complete the third-party credential flow in the browser.
5. The CLI polls for completion, creates the connector, and prints the connector response to stdout.

When the command returns, save the connector `id` or `name`. Use it with [`connectors describe`](./describe-connector), [`connectors execute`](./execute), [`connectors update`](./command-reference#connectors-update), or [`connectors delete`](./command-reference#connectors-delete).

## Credential-flow timeout

By default, `connectors create` waits 180 seconds for you to finish the browser flow. Increase the timeout for slower flows:

```bash
AIRBYTE_CREDENTIAL_TIMEOUT=300 airbyte-agent connectors create --json '{
  "workspace": "default",
  "name": "GitHub"
}'
```

If the timeout expires, the command prints a success-shaped JSON payload with `error: "timeout"` and the `session_id`. Re-run the command to start a new flow.

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
airbyte-agent connectors list --json '{"workspace": "default"}' --fields id,name,context_store_status
```

Next, run [`connectors describe`](./describe-connector) to inspect the connector's entities, actions, and parameter schemas.
