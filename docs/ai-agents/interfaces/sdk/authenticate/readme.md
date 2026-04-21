---
sidebar_position: 2
---

# Authenticate

When you subscribe to Airbyte Agents, Airbyte stores your end users' credentials for you. Your Python code authenticates with Airbyte Cloud using your Airbyte client ID and client secret, and the SDK proxies requests through Airbyte — so your application never sees the third-party tokens.

If you're using agent connectors as open source Python packages and managing credentials yourself, see [Open source](./open-source).

For the HTTP equivalent of this flow, see [Airbyte Agents authentication](../../api/authenticate) in the API section.

## Configure Airbyte credentials

Set your Airbyte client credentials as environment variables. The SDK picks them up automatically.

```bash title=".env"
AIRBYTE_CLIENT_ID=<your_client_id>
AIRBYTE_CLIENT_SECRET=<your_client_secret>
```

You can copy these from the [Profile page](https://app.airbyte.ai/profile) in the Airbyte Agents web app. See [Manage your user profile](../../../admin/profile) for details.

To configure credentials explicitly instead of via environment variables, call `airbyte_agent_sdk.configure()` once at startup:

```python title="agent.py"
import airbyte_agent_sdk

airbyte_agent_sdk.configure(
    client_id="<your_client_id>",
    client_secret="<your_client_secret>",
    workspace_name="<your_workspace_name>",
)
```

The SDK uses `workspace_name` to scope connector lookups and creation. If you omit it, the SDK uses `"default"`.

## Use an existing connector

When an end user has already authenticated a connector (for example, through the [Authentication Module](../../api/authentication-module) or the [web app](../../ui)), call `connect()` with the connector slug. The SDK looks up the connector in your workspace and returns a typed, ready-to-use instance.

```python title="agent.py"
from airbyte_agent_sdk import connect

github = connect("github", workspace_name="<your_workspace_name>")
result = await github.execute("issues", "list", {"owner": "airbytehq", "repo": "airbyte"})
```

To operate against many connectors in a workspace, use `Workspace` instead:

```python title="agent.py"
from airbyte_agent_sdk import Workspace

async with Workspace(workspace_name="<your_workspace_name>") as ws:
    connectors = await ws.list_connectors()
    github = await ws.get_connector(name="github")
    result = await github.execute("issues", "list", {"owner": "airbytehq", "repo": "airbyte"})
```

## Create a connector

You don't have to pre-configure connectors through the web app or API before using the SDK. Your Python code can create them on demand, which is useful when you want to provision connectors programmatically during onboarding or from an automated workflow.

Each typed connector exposes an async `create()` classmethod that provisions the source on Airbyte Cloud and returns a ready-to-use instance. The `airbyte_config` parameter carries your Airbyte client credentials and workspace name, and the `auth_config` parameter carries the end user's third-party credentials.

### With API tokens

For connectors that accept token-based authentication, pass the end user's credentials in `auth_config`. Airbyte stores them securely and returns a configured connector.

```python title="agent.py"
from airbyte_agent_sdk.types import AirbyteAuthConfig
from airbyte_agent_sdk.connectors.github import GithubConnector, GithubAuthConfig

airbyte_config = AirbyteAuthConfig(
    airbyte_client_id="<your_client_id>",
    airbyte_client_secret="<your_client_secret>",
    workspace_name="<your_workspace_name>",
)

github = await GithubConnector.create(
    airbyte_config=airbyte_config,
    auth_config=GithubAuthConfig(access_token="<user_github_personal_access_token>"),
    name="My GitHub Connector",
)
```

To create a connector without importing the typed class, call `Workspace.create_connector(definition_id=..., credentials=...)` instead. It returns the new connector ID, which you can pass to `connect()` or `Workspace.get_connector()`.

### With OAuth credentials

For connectors that support OAuth, pass the client ID, client secret, and refresh token in `auth_config`. Airbyte handles access token refresh for you.

```python title="agent.py"
from airbyte_agent_sdk.connectors.hubspot import HubspotConnector, HubspotAuthConfig

hubspot = await HubspotConnector.create(
    airbyte_config=airbyte_config,
    auth_config=HubspotAuthConfig(
        client_id="<hubspot_client_id>",
        client_secret="<hubspot_client_secret>",
        refresh_token="<hubspot_refresh_token>",
    ),
    name="My HubSpot Connector",
)
```

### With your own OAuth flow

If you want end users to complete OAuth without handling tokens yourself, call `<Connector>.get_consent_url()` to generate a consent URL and redirect the user to it. After the user grants access, Airbyte creates the source automatically and redirects back to your `redirect_url` with a `connector_id` query parameter.

```python title="agent.py"
consent_url = await HubspotConnector.get_consent_url(
    airbyte_config=airbyte_config,
    redirect_url="https://myapp.com/oauth/callback",
    name="My HubSpot Connector",
)
# Redirect the user to consent_url.
# After consent, the user arrives at: https://myapp.com/oauth/callback?connector_id=...
```

If you already completed OAuth out of band and have a server-side OAuth secret ID, pass it to `create()` via `server_side_oauth_secret_id` instead of `auth_config`. See [Build your own OAuth flow](../../api/build-your-own) for the end-to-end walkthrough.

## Delete a connector

To remove a connector from a workspace, use `Workspace.delete_connector`.

```python title="agent.py"
async with Workspace(workspace_name="<your_workspace_name>") as ws:
    await ws.delete_connector(connector_id="<connector_id>")
```

## Security considerations

- **Only use client credentials on your backend**. Never expose `AIRBYTE_CLIENT_ID` and `AIRBYTE_CLIENT_SECRET` in client-side code.
- **Let Airbyte manage end-user tokens**. When your agent calls `execute()`, Airbyte refreshes access tokens automatically so you don't have to rotate them yourself.
- **Scope tokens per end user**. For user-scoped operations, generate a Scoped Token instead of using an application token directly. See [Token types](../../api/#token-types).

## When to use hosted authentication

Hosted authentication is the right choice when:

- You're building a production application with multiple end users.
- You need centralized credential management without storing third-party tokens yourself.
- You want Airbyte to handle credential lifecycle management, including token refresh.
- Security and compliance are priorities for your application.

For development, testing, or single-user scenarios where you prefer to manage credentials yourself, use [open source authentication](./open-source) instead.
