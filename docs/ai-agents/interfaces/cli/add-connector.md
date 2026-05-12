---
plan: all
sidebar_position: 3
---

# Add a connector

A **connector** in Airbyte Agents is a stored set of credentials for a third-party service plus everything needed to execute operations against it. You create a connector once, then reference it on every subsequent call by its name (preferred) when the workspace has one connector of that type, or by its `id` when you need to disambiguate.

The CLI creates connectors through `connectors create`, which opens a browser tab so you can sign in to the third-party service directly. The CLI itself never touches the credentials.

:::warning Never paste connector credentials into the CLI
The CLI deliberately doesn't accept third-party credentials (API keys, OAuth tokens, passwords) as parameters or on stdin. If an agent or script needs a new connector, it must run `connectors create` and let the browser flow handle the credential exchange. This keeps secrets out of shell history, prompt logs, and agent transcripts.
:::

## Find an available connector template

```bash
airbyte-agent connectors list-available --format table
```

The output lists every connector template the CLI can create. Each row has a name (for example, `hubspot`, `linear`, `stripe`) — that's the value you pass as `name` when you create the connector.

If you already know the connector type, you can skip this step.

## Create a connector

```bash
airbyte-agent connectors create --json '{
  "workspace": "default",
  "name": "hubspot"
}'
```

What happens:

1. The CLI resolves the template by name and mints a short-lived widget token for the web app.
2. It opens a browser tab against the Airbyte web app's credential bridge for that template.
3. You sign in to the third-party service in the browser. The web app captures the credentials and reports completion back to the CLI.
4. The CLI polls the session with exponential backoff and, when the browser flow finishes, creates the connector in your workspace with the captured credentials.

When it returns, the response includes the new connector's `id` and `name`. Use either to reference the connector from [`connectors describe`](./describe-connector), [`connectors execute`](./execute), or [`connectors delete`](./troubleshooting#deleting-a-connector).

You can also pass the source definition ID directly with `--id` if you already have it:

```bash
airbyte-agent connectors create --json '{
  "workspace": "default",
  "id": "<source_definition_id>"
}'
```

## Timeouts and re-tries

The default credential-flow timeout is 180 seconds. If the browser tab idles too long, the CLI returns a `validation_error` and you can re-run the command. Raise the timeout for slow flows:

```bash
AIRBYTE_CREDENTIAL_TIMEOUT=300 airbyte-agent connectors create --json '{...}'
```

If the browser doesn't open automatically (for example, on a headless machine), the CLI prints the URL to stderr so you can open it manually on another device.

## List existing connectors

After creating a connector, confirm it's in the workspace:

```bash
airbyte-agent connectors list --json '{"workspace": "default"}' --format table
```

## Next steps

Once the connector exists, run [`connectors describe`](./describe-connector) to see which entities and actions it exposes — that's the contract for every [`connectors execute`](./execute) call against it.
