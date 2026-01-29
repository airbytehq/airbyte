# Asana authentication and configuration

This page documents the authentication and configuration options for the Asana agent connector.

## Authentication

### Open source execution

In open source mode, you provide API credentials directly to the connector.

#### OAuth

`credentials` fields you need:


| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `access_token` | `str` | No | OAuth access token for API requests |
| `refresh_token` | `str` | Yes | OAuth refresh token for automatic token renewal |
| `client_id` | `str` | Yes | Connected App Consumer Key |
| `client_secret` | `str` | Yes | Connected App Consumer Secret |

Example request:

```python
from airbyte_agent_asana import AsanaConnector
from airbyte_agent_asana.models import AsanaOauth2AuthConfig

connector = AsanaConnector(
    auth_config=AsanaOauth2AuthConfig(
        access_token="<OAuth access token for API requests>",
        refresh_token="<OAuth refresh token for automatic token renewal>",
        client_id="<Connected App Consumer Key>",
        client_secret="<Connected App Consumer Secret>"
    )
)
```

#### Token

`credentials` fields you need:

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `token` | `str` | Yes | Your Asana Personal Access Token. Generate one at https://app.asana.com/0/my-apps |

Example request:

```python
from airbyte_agent_asana import AsanaConnector
from airbyte_agent_asana.models import AsanaPersonalAccessTokenAuthConfig

connector = AsanaConnector(
    auth_config=AsanaPersonalAccessTokenAuthConfig(
        token="<Your Asana Personal Access Token. Generate one at https://app.asana.com/0/my-apps>"
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
| `access_token` | `str` | No | OAuth access token for API requests |
| `refresh_token` | `str` | Yes | OAuth refresh token for automatic token renewal |
| `client_id` | `str` | Yes | Connected App Consumer Key |
| `client_secret` | `str` | Yes | Connected App Consumer Secret |

Example request:

```bash
curl -X POST "https://api.airbyte.ai/v1/integrations/connectors" \
  -H "Authorization: Bearer <SCOPED_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "external_user_id": "<EXTERNAL_USER_ID>",
    "connector_type": "Asana",
    "name": "My Asana Connector",
    "credentials": {
      "access_token": "<OAuth access token for API requests>",
      "refresh_token": "<OAuth refresh token for automatic token renewal>",
      "client_id": "<Connected App Consumer Key>",
      "client_secret": "<Connected App Consumer Secret>"
    }
  }'
```

#### Token
Create a connector with Token credentials.


`credentials` fields you need:

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `token` | `str` | Yes | Your Asana Personal Access Token. Generate one at https://app.asana.com/0/my-apps |

Example request:


```bash
curl -X POST "https://api.airbyte.ai/v1/integrations/connectors" \
  -H "Authorization: Bearer <SCOPED_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "external_user_id": "<EXTERNAL_USER_ID>",
    "connector_type": "Asana",
    "name": "My Asana Connector",
    "credentials": {
      "token": "<Your Asana Personal Access Token. Generate one at https://app.asana.com/0/my-apps>"
    }
  }'
```

#### Execution

After creating the connector, execute operations using either the Python SDK or API.

**Python SDK**

```python
from airbyte_agent_asana import AsanaConnector

connector = AsanaConnector(
    external_user_id="<your_external_user_id>",
    airbyte_client_id="<your-client-id>",
    airbyte_client_secret="<your-client-secret>"
)

@agent.tool_plain # assumes you're using Pydantic AI
@AsanaConnector.tool_utils
async def asana_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**API**

```bash
curl -X POST 'https://api.airbyte.ai/api/v1/connectors/sources/<connector_id>/execute' \
  -H 'Authorization: Bearer <SCOPED_TOKEN>' \
  -H 'Content-Type: application/json' \
  -d '{"entity": "<entity>", "action": "<action>", "params": {}}'
```


