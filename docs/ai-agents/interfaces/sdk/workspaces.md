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

You don't explicitly create a workspace. The first `create_connector` call against a new `workspace_name` provisions it on the fly.

Other operations do not provision the workspace. `list_connectors()`, `get_connector()`, and `ask()` against a `workspace_name` that hasn't been created yet return an empty result or a 404 — they won't implicitly create it for you. If you need to start from an empty workspace, call `create_connector` first (or add a connector in the Airbyte Agents app).

## Operations that require the API

The SDK doesn't expose every workspace operation. If you need to do any of the following, use the [API](../api/workspaces) instead:

- List every workspace in your organization.
- Update a workspace's status, for example to deactivate one.
- Delete a workspace and its data.
- Read a workspace's metadata, like ID, status, or `created_at`, without opening it.
