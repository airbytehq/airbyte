---
sidebar_position: 2
---

# Add a connector

A **connector** in Airbyte Agents is a stored set of credentials for a third-party service plus everything needed to execute operations against it. You create a connector once, then reference it on every subsequent call — by its slug (preferred) when the workspace has one connector of that type, or by its `connector_id` when you need to disambiguate.

The `Workspace` class covers every connector operation: create, list, get, and delete.

## Create a connector

Call `create_connector` on an open `Workspace`. Pass the `definition_id` for the connector type (GitHub, HubSpot, and so on) and the credentials in the shape that connector expects.

`create_connector` returns a string `connector_id`. You can ignore it if the workspace only ever has one connector of this type — later calls can resolve the connector by slug. Store the ID if you plan to run multiple connectors of the same type in the same workspace.

### API token connectors

Connectors that authenticate with an API key or personal access token accept a `token` field.

```python title="agent.py"
import asyncio
from airbyte_agent_sdk import Workspace

async def main():
    async with Workspace() as ws:
        await ws.create_connector(
            definition_id="<github_definition_id>",
            name="My GitHub Connector",
            credentials={
                "token": "<github_personal_access_token>",
            },
        )

asyncio.run(main())
```

### OAuth connectors

Connectors that use OAuth accept a `client_id`, `client_secret`, and `refresh_token`. Airbyte uses the refresh token to mint and rotate access tokens automatically at execution time.

```python title="agent.py"
import asyncio
from airbyte_agent_sdk import Workspace

async def main():
    async with Workspace() as ws:
        await ws.create_connector(
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

You can also browse the raw [Airbyte Connector Registry](https://connectors.airbyte.com/files/registries/v0/cloud_registry.json) JSON (large file — approximately 100 MB) and copy `sourceDefinitionId` for the entry you want.

## List connectors

```python title="agent.py"
async with Workspace() as ws:
    connectors = await ws.list_connectors()
    for info in connectors:
        print(info.id, info.name, info.type)
```

## Get a connector

When the workspace has exactly one connector of a given type, resolve it by slug. This is the recommended pattern for most apps — you never hard-code a UUID.

```python title="agent.py"
async with Workspace() as ws:
    stripe = await ws.get_connector(name="stripe")
    try:
        result = await stripe.execute("customers", "list", params={"limit": 10})
    finally:
        await stripe.close()
```

`get_connector(name=...)` raises `ValueError` if zero or more than one connector of that type exists. When multiple connectors of the same type exist in the workspace — for example, two separate Stripe accounts — pass `connector_id` explicitly:

```python title="agent.py"
async with Workspace() as ws:
    stripe_us = await ws.get_connector(connector_id="<us_account_connector_id>")
    stripe_eu = await ws.get_connector(connector_id="<eu_account_connector_id>")
```

`get_connector(name=...)` always returns a generic `HostedExecutor` with `.execute(entity, action, params)`. To get a typed connector with IDE autocompletion and structured method shortcuts (for example, `stripe.customers.list(...)`), call `connect(slug)` for slug resolution or `connect(slug, connector_id=...)` when you need to pin a specific connector. See [Typed connectors and `HostedExecutor`](./execute#typed-connectors-and-hostedexecutor).

## Delete a connector

`delete_connector(connector_id)` takes the connector ID as its first positional argument (or you can pass it by name for clarity). Airbyte removes the stored credentials.

```python title="agent.py"
async with Workspace() as ws:
    await ws.delete_connector(connector_id="<connector_id>")
```
