# Open source authentication

When you use agent connectors as open source Python packages, you manage credentials locally and provide them directly to the connector. This approach gives you full control over credential storage and is ideal for development, testing, and single-user scenarios.

## How it works

In open source mode, you install agent connectors as Python packages and provide API credentials directly when initializing the connector. The connector then makes HTTP calls directly to the external API using those credentials.

Key characteristics of open source authentication:

- You provide actual API credentials (tokens, keys, OAuth tokens) directly to the connector.
- Credentials are stored and managed locally by you.
- Connectors make direct HTTP calls to external APIs.
- You are responsible for credential security, rotation, and lifecycle management.

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

```python
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

```python
from airbyte_agent_github import GithubConnector
from airbyte_agent_github.models import GithubPersonalAccessTokenAuthConfig

connector = GithubConnector(
    auth_config=GithubPersonalAccessTokenAuthConfig(
        token="<your_github_personal_access_token>"
    )
)
```

### Finding connector-specific authentication options

Each connector has its own authentication requirements. See the [connector reference documentation](../../connectors/) for details on the authentication methods and required fields for each connector.

## Security considerations

When managing credentials locally, follow these best practices:

- **Use environment variables**: Store credentials in environment variables rather than hardcoding them in your source code. Use a library like `python-dotenv` to load them from a `.env` file during development.

- **Never commit credentials**: Add `.env` files to your `.gitignore` to prevent accidentally committing secrets to version control.

- **Rotate credentials regularly**: Periodically rotate API keys and tokens, especially if you suspect they may have been exposed.

- **Use least privilege**: Request only the scopes and permissions your application actually needs.

- **Secure your environment**: Ensure the machine running your agent has appropriate access controls.

## When to use open source mode

Open source authentication is most appropriate when:

- You're developing or testing an agent locally.
- You have a single-user scenario where you control the credentials.
- You need full control over credential storage and don't want to use a cloud service.
- You're building a proof of concept before moving to production.

For production B2B applications with multiple end-users, consider using [hosted authentication](hosted.md) instead, which provides centralized credential management and enhanced security.
