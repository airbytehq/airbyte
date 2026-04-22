---
sidebar_position: 2
---

# Add a connector

A **connector** in Airbyte Agents is a stored set of credentials for a third-party service plus everything needed to execute operations against it. You create a connector once, then reuse the returned `connector_id` on every subsequent call.

The `Workspace` class covers every connector operation: create, list, get, and delete.

## Create a connector

Call `create_connector` on an open `Workspace`. Pass the `definition_id` for the connector type (GitHub, HubSpot, and so on) and the credentials in the shape that connector expects.

`create_connector` returns a string `connector_id`. Store it somewhere you can retrieve it later.

### API token connectors

Connectors that authenticate with an API key or personal access token accept a `token` field.

```python title="agent.py"
import asyncio
from airbyte_agent_sdk import Workspace

async def main():
    async with Workspace() as ws:
        connector_id = await ws.create_connector(
            definition_id="<github_definition_id>",
            name="My GitHub Connector",
            credentials={
                "token": "<github_personal_access_token>",
            },
        )
        print(connector_id)

asyncio.run(main())
```

### OAuth connectors

Connectors that use OAuth accept a `client_id`, `client_secret`, and `refresh_token`. Airbyte uses the refresh token to mint and rotate access tokens automatically at execution time.

```python title="agent.py"
import asyncio
from airbyte_agent_sdk import Workspace

async def main():
    async with Workspace() as ws:
        connector_id = await ws.create_connector(
            definition_id="<hubspot_definition_id>",
            name="My HubSpot Connector",
            credentials={
                "client_id": "<hubspot_client_id>",
                "client_secret": "<hubspot_client_secret>",
                "refresh_token": "<hubspot_refresh_token>",
            },
        )

asyncio.run(main())
```

Each connector defines its own credential shape. See the connector's page in the [Connectors](../../connectors) reference for the exact field names.

### Find a `definition_id`

The `definition_id` identifies the connector type. The fastest way to look one up is to call the definitions endpoint and filter by connector name:

```bash
curl -s 'https://api.airbyte.ai/api/v1/integrations/definitions/sources' \
  -H 'Authorization: Bearer <application_token>' \
  | jq '.definitions[] | select(.name | test("hubspot"; "i")) | {name, id: .sourceDefinitionId}'
```

See [Make your first request](../api/#make-your-first-request) for token details.

You can also browse the raw [Airbyte Connector Registry](https://connectors.airbyte.com/files/registries/v0/cloud_registry.json) JSON and copy `sourceDefinitionId` for the entry you want.

## List connectors

```python title="agent.py"
async with Workspace() as ws:
    connectors = await ws.list_connectors()
    for info in connectors:
        print(info.id, info.name, info.type)
```

## Get a connector

When you already have the `connector_id`, you don't need to list or look it up. Pass it straight to `connect()`. See [Execute operations](./execute).

When you don't have the ID but you know there's exactly one connector of a given type in the workspace, resolve by name:

```python title="agent.py"
async with Workspace() as ws:
    stripe = await ws.get_connector(name="stripe")
    try:
        result = await stripe.execute("customers", "list", params={"limit": 10})
    finally:
        await stripe.close()
```

`get_connector(name=...)` raises `ValueError` if zero or more than one connector of that type exists. Use `connector_id` explicitly when multiple connectors of the same type might exist.

`get_connector(name=...)` always returns a generic `HostedExecutor` with `.execute(entity, action, params)`. To get a typed connector with IDE autocompletion and structured method shortcuts (for example, `stripe.customers.list(...)`), call `connect(slug, connector_id=...)` with the ID you stored. See [Typed connectors and `HostedExecutor`](./execute#typed-connectors-and-hostedexecutor).

## Delete a connector

`delete_connector(connector_id)` takes the connector ID as its first positional argument (or you can pass it by name for clarity). Airbyte removes the stored credentials.

```python title="agent.py"
async with Workspace() as ws:
    await ws.delete_connector(connector_id="<connector_id>")
```
