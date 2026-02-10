---
sidebar_position: 0
---

# Open source authentication

When you use agent connectors as open source Python packages, you provide user credentials to the connector in your app. The connector then makes HTTP calls directly to the external API using those credentials. In this case, you don't need to subscribe to Agent Engine, but you are responsible for managing your users' credentials.

- You provide actual API credentials (tokens, keys, OAuth tokens) directly to the connector.
- Connectors make direct HTTP calls to external APIs.
- You are responsible for credential security, rotation, and lifecycle management.
- You can't use the [context store](../context-store).

## Authentication methods

Agent connectors support two main authentication patterns, though the specific methods available vary by connector.

### OAuth credentials

Many connectors support OAuth authentication, which typically requires some combination of the following fields:

| Field | Description |
|-------|-------------|
| `access_token` | OAuth 2.0 access token |
| `refresh_token` | OAuth refresh token for automatic token renewal |
| `client_id` | OAuth application client ID |
| `client_secret` | OAuth application client secret |

Here's an example using OAuth with the HubSpot connector:

```python title="agent.py"
from airbyte_agent_hubspot import HubspotConnector
from airbyte_agent_hubspot.models import HubspotAuthConfig

connector = HubspotConnector(
    auth_config=HubspotAuthConfig(
        client_id="<your_hubspot_client_id>",
        client_secret="<your_hubspot_client_secret>",
        refresh_token="<your_hubspot_refresh_token>"
    )
)
```

### API tokens

Some connectors support simpler token-based authentication using API keys or personal access tokens:

| Field | Description |
|-------|-------------|
| `token` | API key or personal access token |

Here's an example using a personal access token with the GitHub connector:

```python title="agent.py"
from airbyte_agent_github import GithubConnector
from airbyte_agent_github.models import GithubPersonalAccessTokenAuthConfig

connector = GithubConnector(
    auth_config=GithubPersonalAccessTokenAuthConfig(
        token="<your_github_personal_access_token>"
    )
)
```

### Finding connector-specific authentication options

Each connector has its own authentication requirements. See the [reference documentation](../../connectors/) for the connector you want to use.

## Security considerations

When managing credentials locally, follow these best practices:

- **Use environment variables**: Store credentials in environment variables rather than hard coding them in your source code. Use a library like `python-dotenv` to load them from a `.env` file during development. Add `.env` files to your `.gitignore` to prevent accidentally committing secrets to version control.

- **Rotate credentials regularly**: Periodically rotate API keys and tokens.

- **Use least privilege**: Request only the scopes and permissions your agent actually needs.

- **Secure your environment**: Ensure the machine running your agent has appropriate access controls.

## When to use open source mode

Open source authentication is most appropriate when:

- You're developing or testing an agent locally.
- You have a single-user scenario where you control the credentials.
- You need full control over credential storage and don't want to use a cloud service.
- You're building a proof of concept before moving to production.

For production applications with multiple end-users, use [hosted authentication](hosted.md) instead, which provides secure credential management in the Agent Engine.
