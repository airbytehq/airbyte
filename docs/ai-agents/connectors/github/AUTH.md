# Github authentication and configuration

This page documents the authentication and configuration options for the Github agent connector.

## Authentication

### Open source execution

In open source mode, you provide API credentials directly to the connector.

#### OAuth

`credentials` fields you need:


| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `access_token` | `str` | Yes | OAuth 2.0 access token |

Example request:

```python
from airbyte_agent_github import GithubConnector
from airbyte_agent_github.models import GithubOauth2AuthConfig

connector = GithubConnector(
    auth_config=GithubOauth2AuthConfig(
        access_token="<OAuth 2.0 access token>"
    )
)
```

#### Token

`credentials` fields you need:

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `token` | `str` | Yes | GitHub personal access token (fine-grained or classic) |

Example request:

```python
from airbyte_agent_github import GithubConnector
from airbyte_agent_github.models import GithubPersonalAccessTokenAuthConfig

connector = GithubConnector(
    auth_config=GithubPersonalAccessTokenAuthConfig(
        token="<GitHub personal access token (fine-grained or classic)>"
    )
)
```

### Hosted execution

In hosted mode, you first create a connector via the Airbyte API (providing your OAuth or Token credentials), then execute operations using either the Python SDK or API. If you need a step-by-step guide, see the [hosted execution tutorial](https://docs.airbyte.com/ai-agents/quickstarts/tutorial-hosted).

#### OAuth
Create a connector with OAuth credentials.

`credentials` fields you need:


| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `access_token` | `str` | Yes | OAuth 2.0 access token |

Example request:

```bash
curl -X POST "https://api.airbyte.ai/v1/integrations/connectors" \
  -H "Authorization: Bearer <SCOPED_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "external_user_id": "<EXTERNAL_USER_ID>",
    "connector_type": "Github",
    "name": "My Github Connector",
    "credentials": {
      "access_token": "<OAuth 2.0 access token>"
    }
  }'
```



#### Bring your own OAuth flow
To implement your own OAuth flow, use Airbyte's server-side OAuth API endpoints. For a complete guide, see [Implement your own OAuth flow](https://docs.airbyte.com/ai-agents/quickstarts/tutorial-server-side-oauth).

**Step 1: Initiate the OAuth flow**

Request a consent URL for your user.

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `external_user_id` | `string` | Yes | Your unique identifier for the end user |
| `connector_type` | `string` | Yes | The connector type (e.g., "Github") |
| `redirect_url` | `string` | Yes | URL to redirect to after OAuth authorization |

Example request:

```bash
curl -X POST "https://api.airbyte.ai/v1/integrations/connectors/oauth/initiate" \
  -H "Authorization: Bearer <BEARER_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "external_user_id": "<EXTERNAL_USER_ID>",
    "connector_type": "Github",
    "redirect_url": "https://yourapp.com/oauth/callback"
  }'
```

Redirect your user to the `consent_url` from the response. After they authorize, they'll be redirected back to your app with a `secret_id` query parameter.

**Step 2: Create a connector with the secret ID**

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `external_user_id` | `string` | Yes | Your unique identifier for the end user |
| `connector_type` | `string` | Yes | The connector type (e.g., "Github") |
| `name` | `string` | Yes | A name for this connector instance |
| `server_side_oauth_secret_id` | `string` | Yes | The secret_id from the OAuth callback |

Example request:

```bash
curl -X POST "https://api.airbyte.ai/v1/integrations/connectors" \
  -H "Authorization: Bearer <BEARER_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "external_user_id": "<EXTERNAL_USER_ID>",
    "connector_type": "Github",
    "name": "My Github Connector",
    "server_side_oauth_secret_id": "<secret_id_from_callback>"
  }'
```

#### Token
Create a connector with Token credentials.


`credentials` fields you need:

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `token` | `str` | Yes | GitHub personal access token (fine-grained or classic) |

Example request:


```bash
curl -X POST "https://api.airbyte.ai/v1/integrations/connectors" \
  -H "Authorization: Bearer <SCOPED_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "external_user_id": "<EXTERNAL_USER_ID>",
    "connector_type": "Github",
    "name": "My Github Connector",
    "credentials": {
      "token": "<GitHub personal access token (fine-grained or classic)>"
    }
  }'
```

#### Execution

After creating the connector, execute operations using either the Python SDK or API.

**Python SDK**

```python
from airbyte_agent_github import GithubConnector

connector = GithubConnector(
    external_user_id="<your_external_user_id>",
    airbyte_client_id="<your-client-id>",
    airbyte_client_secret="<your-client-secret>"
)

@agent.tool_plain # assumes you're using Pydantic AI
@GithubConnector.tool_utils
async def github_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**API**

```bash
curl -X POST 'https://api.airbyte.ai/api/v1/connectors/sources/<connector_id>/execute' \
  -H 'Authorization: Bearer <SCOPED_TOKEN>' \
  -H 'Content-Type: application/json' \
  -d '{"entity": "<entity>", "action": "<action>", "params": {}}'
```


