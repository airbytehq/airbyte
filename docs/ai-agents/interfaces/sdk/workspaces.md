---
sidebar_position: 4
---

# Manage workspaces

A **workspace** is an end user's isolated container inside your Airbyte Agents organization. Each workspace has its own connectors and credentials. A token scoped to one workspace can't reach another, which is how Airbyte Agents keeps each end user's data separate in multi-tenant apps.

Most apps use the `default` workspace and never think about this again. The `Workspace` class, `connect()`, and `ask()` all default to `workspace_name="default"`. Only split into multiple workspaces when you actively need per-end-user isolation inside a single Airbyte Agents organization.

## Use a specific workspace

To target a workspace other than `default`, pass `workspace_name`. Use a stable identifier for your end user, such as your internal user ID or company slug.

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

stripe = connect("stripe", workspace_name="acme_corp", connector_id="<connector_id>")
result = await ask("list my 5 most recent customers", workspace_name="acme_corp")
```

## Auto-creation

The SDK creates a workspace on first reference. You don't explicitly create one. The first `create_connector` or `ask()` call against a new `workspace_name` provisions it on the fly.

## Use the API for

The SDK doesn't expose every workspace operation. If you need to do any of the following, use the [API](../api/workspaces) instead:

- List every workspace in your organization.
- Update a workspace's status, for example to deactivate one.
- Delete a workspace and its data.
- Read a workspace's metadata, like ID, status, or `created_at`, without opening it.
