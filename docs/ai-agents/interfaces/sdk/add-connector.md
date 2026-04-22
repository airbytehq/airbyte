---
sidebar_position: 2
---

# Add a connector

A **connector** in Airbyte Agents is a per-end-user instance that stores one set of credentials for a third-party service and executes operations against it. You create a connector the first time an end user connects their account, then reuse the returned `connector_id` on every subsequent call.

The `Workspace` class covers every connector operation: create, list, get, and delete.

## Create a connector

Call `create_connector` on an open `Workspace`. Pass the `definition_id` for the connector type (GitHub, HubSpot, and so on) and the end user's credentials in the shape that connector expects.

`create_connector` returns a string `connector_id`. Store it in your app database, keyed by your end user.

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
                "token": "<user_github_personal_access_token>",
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

The `definition_id` identifies the connector type. You can look it up two ways:

- Browse the [Airbyte Connector Registry](https://connectors.airbyte.com/files/registries/v0/cloud_registry.json) and copy the `sourceDefinitionId` for your connector.
- Call the API `GET /api/v1/integrations/definitions/sources` to list every available connector type with its definition ID.

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

## Delete a connector

```python title="agent.py"
async with Workspace() as ws:
    await ws.delete_connector("<connector_id>")
```

Delete a connector when an end user disconnects their account. Airbyte removes the stored credentials.
