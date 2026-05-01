---
plan: all
sidebar_position: 2
description: "List, get, and delete connectors for third-party services."
---

# Add a connector

A **connector** in Airbyte Agents is a stored set of credentials for a third-party service plus everything needed to execute operations against it. You create a connector once, then reference it on every subsequent call by its slug (preferred) when the workspace has one connector of that type, or by its `connector_id` when you need to disambiguate.

## Create a connector

The SDK does not expose a connector creation method. Create connectors through either of these interfaces instead:

- **Web app**: Open the [Connectors page](https://app.airbyte.ai/) and follow the guided flow. See [Add a connector (UI)](../ui/add-connector) for a walkthrough.
- **REST API**: `POST /api/v1/integrations/connectors` with the `definition_id` and credentials. See [Add a connector (API)](../api/add-connector) for request examples.

After the connector exists in your workspace, use `connect()` or `Workspace.list_connectors()` in the SDK to work with it.

## List connectors

```python title="agent.py"
async with Workspace() as ws:
    connectors = await ws.list_connectors()
    for info in connectors:
        print(info.id, info.name, info.connector_type)
```

Each `ConnectorInfo` carries `id`, `name`, `connector_type` (the template display name, such as `"GitHub"` or `"Linear"`), `created_at`, and `updated_at`. Use the display name for logging or UI; use the slug you passed to `connect()` when you need to reopen the connector.

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

When multiple connectors of the same type exist in the workspace (for example, two separate Stripe accounts), pass `connector_id` explicitly to `connect()`:

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
