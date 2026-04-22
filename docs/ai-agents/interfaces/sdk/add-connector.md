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

Connectors that authenticate with a single API key or personal access token take one credential field. The exact field name is connector-specific — Linear uses `api_key`, Notion uses `token`, Jira uses `api_token`, and so on. See the connector's page in the [Connectors](../../connectors) reference for the exact field name.

```python title="agent.py"
import asyncio
from airbyte_agent_sdk import Workspace

async def main():
    async with Workspace() as ws:
        await ws.create_connector(
            definition_id="<linear_definition_id>",
            name="My Linear Connector",
            credentials={
                "api_key": "<linear_api_key>",
            },
        )

asyncio.run(main())
```

Some connectors also require non-credential configuration alongside `credentials`. For example, `source-github` requires a `repositories` array of `owner/repo` strings; create fails with a `422` if it's missing. Check the connector's page for any required configuration.

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

The `definition_id` identifies the connector type. The SDK doesn't currently ship a helper for listing definitions, but `Workspace` exposes the `AirbyteCloudClient` it uses under `ws._cloud_client`, and that client already holds a valid bearer token. You can reuse it to hit the definitions endpoint from Python:

```python title="find_definition_id.py"
import asyncio
from airbyte_agent_sdk import Workspace

async def main():
    async with Workspace() as ws:
        token = await ws._cloud_client.get_bearer_token()
        response = await ws._cloud_client._http_client.get(
            f"{ws._cloud_client.API_BASE_URL}/api/v1/integrations/definitions/sources",
            params={"name": "hubspot"},
            headers={"Authorization": f"Bearer {token}"},
        )
        for definition in response.json()["definitions"]:
            print(definition["name"], definition["sourceDefinitionId"])

asyncio.run(main())
```

The response returns `sourceDefinitionId`. The `create_connector` request expects it as `definition_id` — the two names refer to the same UUID.

If you prefer to avoid private attributes, the same endpoint is documented under [Find a `definition_id`](../api/add-connector#find-a-definition_id) on the API side; it takes an application token you mint with `POST /account/applications/token`.

You can also browse the raw [Airbyte Connector Registry](https://connectors.airbyte.com/files/registries/v0/cloud_registry.json) JSON (large file — approximately 100 MB) and copy `sourceDefinitionId` for the entry you want.

## List connectors

```python title="agent.py"
async with Workspace() as ws:
    connectors = await ws.list_connectors()
    for info in connectors:
        print(info.id, info.name, info.connector_type)
```

Each `ConnectorInfo` carries `id`, `name`, `connector_type` (the connector slug, such as `"stripe"` or `"hubspot"`), `created_at`, and `updated_at`.

## Get a connector

For most apps, resolve a connector by passing its slug to `connect()`. `connect()` returns a typed connector (when one is generated) or a generic `HostedExecutor`, and handles slug-to-ID resolution for you when the workspace has exactly one connector of that type. You never hard-code a UUID.

```python title="agent.py"
from airbyte_agent_sdk import connect

stripe = connect("stripe")
try:
    result = await stripe.execute("customers", "list")
finally:
    await stripe.close()
```

When multiple connectors of the same type exist in the workspace — for example, two separate Stripe accounts — pass `connector_id` explicitly to `connect()`:

```python title="agent.py"
stripe_us = connect("stripe", connector_id="<us_account_connector_id>")
stripe_eu = connect("stripe", connector_id="<eu_account_connector_id>")
```

`Workspace` also exposes a lower-level `get_connector(connector_id=...)` method that returns a `HostedExecutor` for a known connector ID. Prefer `connect(slug, ...)` unless you specifically need to resolve a connector from inside an open `Workspace` session.

For typed-connector shortcuts like `stripe.customers.list(...)` and the distinction between typed connectors and `HostedExecutor`, see [Typed connectors and `HostedExecutor`](./execute#typed-connectors-and-hostedexecutor).

## Delete a connector

`delete_connector(connector_id)` takes the connector ID as its first positional argument (or you can pass it by name for clarity). Airbyte removes the stored credentials.

```python title="agent.py"
async with Workspace() as ws:
    await ws.delete_connector(connector_id="<connector_id>")
```
