---
sidebar_position: 2
---

# Add a connector

<!--
BLOCKS MERGE until AGENTIC-1133 ships.

The published airbyte-agent-sdk (as of 0.1.55) raises TypeError from
Workspace.create_connector and Workspace.get_connector(name=...) because
Workspace passes `customer_name=` to AirbyteCloudClient, which expects
`workspace_name=`. Every snippet on this page depends on that call path.
Confirm the fix ships and the docs' pinned SDK version includes it before
merging.
-->

A **connector** in Airbyte Agents is a stored set of credentials for a third-party service plus everything needed to execute operations against it. You create a connector once, then reference it on every subsequent call — by its slug (preferred) when the workspace has one connector of that type, or by its `connector_id` when you need to disambiguate.

The `Workspace` class covers every connector operation: create, list, get, and delete.

## Create a connector

Call `create_connector` on an open `Workspace`. Pass the `definition_id` for the connector type (GitHub, HubSpot, and so on) and the credentials in the shape that connector expects.

`create_connector` returns a string `connector_id`. You can ignore it if the workspace only ever has one connector of this type — later calls can resolve the connector by slug. Store the ID if you plan to run multiple connectors of the same type in the same workspace.

### API token connectors

Connectors that authenticate with a single API key or personal access token take one credential field. The exact field name is connector-specific — GitHub uses `personal_access_token`, Linear uses `api_key`, Notion uses `token`, and so on. See the connector's page in the [Connectors](../../connectors) reference for the exact field name.

```python title="agent.py"
import asyncio
from airbyte_agent_sdk import Workspace

async def main():
    async with Workspace() as ws:
        await ws.create_connector(
            definition_id="<github_definition_id>",
            name="My GitHub Connector",
            credentials={
                "option_title": "PAT Credentials",
                "personal_access_token": "<github_pat>",
            },
            replication_config={"repositories": ["airbytehq/airbyte"]},
        )

asyncio.run(main())
```

Some connectors also require non-credential configuration alongside `credentials`. Pass those fields as `replication_config` — not alongside `credentials`. GitHub, for example, requires a `repositories` array of `owner/repo` strings; the create call above fails with a `422` without it. Check the connector's page for any required configuration.

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

The `definition_id` identifies the connector type. Look it up once from the public `GET /api/v1/integrations/definitions/sources` endpoint and paste the value into your `create_connector` call. See [Find a `definition_id`](../api/add-connector#find-a-definition_id) on the API side for the exact request, including the `?name=github` filter you can use to fetch a single entry. The endpoint returns `sourceDefinitionId`; the SDK accepts it as `definition_id` — both names refer to the same UUID.

## List connectors

```python title="agent.py"
async with Workspace() as ws:
    connectors = await ws.list_connectors()
    for info in connectors:
        print(info.id, info.name, info.connector_type)
```

Each `ConnectorInfo` carries `id`, `name`, `connector_type` (the template display name, such as `"GitHub"` or `"Linear"`), `created_at`, and `updated_at`. Use the display name for logging or UI; use the slug you passed to `connect()` or `create_connector` when you need to reopen the connector.

## Get a connector

For most apps, resolve a connector by passing its slug to `connect()`. `connect()` returns a typed connector (when one is generated) or a generic `HostedExecutor`, and handles slug-to-ID resolution for you when the workspace has exactly one connector of that type. You never hard-code a UUID.

```python title="agent.py"
from airbyte_agent_sdk import connect

stripe = connect("stripe")
try:
    result = await stripe.execute("customers", "list", params={"limit": 10})
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
