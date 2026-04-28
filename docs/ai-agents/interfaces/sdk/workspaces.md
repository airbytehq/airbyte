---
sidebar_position: 4
---

# Manage workspaces

A **workspace** is a container inside your Airbyte Agents organization that holds a set of connectors and credentials. A token scoped to one workspace can't reach another.

Most apps use the `default` workspace and never think about this again. The `Workspace` class, `connect()`, and `ask()` all default to `workspace_name="default"`. Reach for multiple workspaces only when you actively need to isolate credentials across distinct tenants, teams, or environments.

## Use a specific workspace

To target a workspace other than `default`, pass `workspace_name`. Use a stable identifier that makes sense in your app, such as an internal tenant ID or team slug.

```python title="agent.py"
import asyncio
from airbyte_agent_sdk import Workspace

async def main():
    async with Workspace(workspace_name="acme_corp") as ws:
        connectors = await ws.list_connectors()
        print(connectors)

asyncio.run(main())
```

`connect()` and `ask()` accept the same argument.

```python title="agent.py"
from airbyte_agent_sdk import ask, connect

stripe = connect("stripe", workspace_name="acme_corp")
result = await ask("list my 5 most recent customers", workspace_name="acme_corp")
```

## `async with` vs direct construction

`Workspace` can be used as an async context manager or constructed directly. The context manager form is recommended — it closes the underlying HTTP client when the block exits. If you construct a `Workspace` directly, call `await ws.close()` yourself when you're done with it.

```python title="agent.py"
# Preferred — automatic cleanup
async with Workspace() as ws:
    connectors = await ws.list_connectors()

# Also valid — you own the lifecycle
ws = Workspace()
try:
    connectors = await ws.list_connectors()
finally:
    await ws.close()
```

## Auto-creation

You don't explicitly create a workspace. Airbyte provisions one automatically the first time you mint a scoped or widget token for a new `workspace_name` (see [Authentication](../api/authentication#scoped-token) on the API side). Under the hood, `Workspace()` and `connect()` both mint a scoped token on first use, so opening a `Workspace` is enough.

`list_connectors()`, `get_connector()`, and `ask()` against a `workspace_name` that hasn't been created yet raise `httpx.HTTPStatusError` with a `404` status — they don't return an empty list and they don't implicitly create the workspace. If you want to start from a known-empty workspace, catch the 404 and then call `create_connector` (or open the workspace in the Airbyte Agents app and add a connector there):

```python title="agent.py"
import httpx
from airbyte_agent_sdk import Workspace

async with Workspace(workspace_name="tenant-123") as ws:
    try:
        connectors = await ws.list_connectors()
    except httpx.HTTPStatusError as err:
        if err.response.status_code == 404:
            connectors = []
        else:
            raise
```

<!--
AGENTIC-1140: create_connector doesn't autocreate a workspace — it 404s if
no scoped token has been minted for that workspace_name yet. `Workspace(...)`
mints one on open, so readers who follow the SDK pattern above never hit
this, which is why we don't surface the quirk in the public narrative.
Revisit when autocreate is consistent across endpoints.
-->

## Operations that require the API

The SDK doesn't expose every workspace operation. If you need to do any of the following, use the [API](../api/workspaces) instead:

- List every workspace in your organization.
- Update a workspace's status, for example to deactivate one.
- Delete a workspace and its data.
- Read a workspace's metadata, like ID, status, or `created_at`, without opening it.
