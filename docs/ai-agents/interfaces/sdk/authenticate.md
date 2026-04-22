---
sidebar_position: 1
---

# Authenticate

The SDK authenticates with Airbyte Agents using an Airbyte `client_id` and `client_secret`. Once the SDK has these, it handles the rest: fetching tokens, refreshing them before they expire, and attaching them to every request. You never manage tokens yourself.

## Get your credentials

1. Sign in to [app.airbyte.ai](https://app.airbyte.ai/).
2. Open the [Profile page](https://app.airbyte.ai/profile) and copy your `AIRBYTE_CLIENT_ID` and `AIRBYTE_CLIENT_SECRET`.

For details, see [Manage your user profile](../../admin/profile).

## Provide credentials

The SDK accepts credentials three ways. Pick whichever fits your app. The SDK resolves them in the order **explicit keyword arguments → `configure()` → environment variables**.

### Environment variables

Recommended for most apps. Set `AIRBYTE_CLIENT_ID` and `AIRBYTE_CLIENT_SECRET`, and the SDK picks them up automatically from every entry point.

```bash title=".env"
AIRBYTE_CLIENT_ID=<your_client_id>
AIRBYTE_CLIENT_SECRET=<your_client_secret>
```

```python title="agent.py"
import asyncio
from airbyte_agent_sdk import Workspace

async def main():
    async with Workspace() as ws:
        connectors = await ws.list_connectors()
        print(connectors)

asyncio.run(main())
```

### Explicit keyword arguments

Pass credentials directly to `Workspace`, `connect()`, `ask()`, or `ask_sync()`. Useful when you rotate credentials per request or run against multiple Airbyte organizations from the same process.

```python title="agent.py"
import asyncio
from airbyte_agent_sdk import connect

async def main():
    stripe = connect(
        "stripe",
        client_id="<your_client_id>",
        client_secret="<your_client_secret>",
    )
    try:
        result = await stripe.execute("customers", "list", params={"limit": 10})
        for row in result.data:
            print(row)
    finally:
        await stripe.close()

asyncio.run(main())
```

### Global `configure()` call

Call `configure()` once at startup to set process-wide defaults. This is helpful in notebooks where `connect()` and `ask()` are called repeatedly and you don't want to repeat credentials.

```python title="notebook.ipynb"
from airbyte_agent_sdk import configure, connect

configure(
    client_id="<your_client_id>",
    client_secret="<your_client_secret>",
)

stripe = connect("stripe")
```

`configure()` accepts the following keyword arguments (all must be passed by name):

| Argument          | Type          | Default     | Description                                                                  |
| ----------------- | ------------- | ----------- | ---------------------------------------------------------------------------- |
| `client_id`       | `str`         | —           | Airbyte `client_id`. Required.                                               |
| `client_secret`   | `str`         | —           | Airbyte `client_secret`. Required.                                           |
| `organization_id` | `str \| None` | `None`      | Organization to target when your account belongs to multiple organizations.  |
| `workspace_name`  | `str`         | `"default"` | Default workspace for `connect()`, `ask()`, and `Workspace()` calls.         |

Explicit keyword arguments always override `configure()`, and `configure()` always overrides environment variables.

## Token refresh

The SDK obtains a short-lived token on first use and refreshes it automatically before it expires. You don't need to track expirations or request new tokens yourself.

## Multiple organizations

If your Airbyte account belongs to multiple organizations, pass `organization_id` to route requests to the right one.

```python title="agent.py"
from airbyte_agent_sdk import Workspace

async with Workspace(organization_id="<organization_id>") as ws:
    ...
```

If you belong to a single organization, you can omit `organization_id`.

## Security

- Never commit `AIRBYTE_CLIENT_ID` or `AIRBYTE_CLIENT_SECRET` to version control. Use a `.env` file and add it to `.gitignore`.
- Keep Airbyte credentials server-side. The SDK is designed for backend use.
- Rotate credentials periodically from the [Profile page](https://app.airbyte.ai/profile).
