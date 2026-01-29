# Google-Drive authentication and configuration

This page documents the authentication and configuration options for the Google-Drive agent connector.

## Authentication

### Open source execution

In open source mode, you provide API credentials directly to the connector.

#### OAuth

`credentials` fields you need:


| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `access_token` | `str` | No | Your Google OAuth2 Access Token (optional, will be obtained via refresh) |
| `refresh_token` | `str` | Yes | Your Google OAuth2 Refresh Token |
| `client_id` | `str` | Yes | Your Google OAuth2 Client ID |
| `client_secret` | `str` | Yes | Your Google OAuth2 Client Secret |

Example request:

```python
from airbyte_agent_google-drive import GoogleDriveConnector
from airbyte_agent_google-drive.models import GoogleDriveAuthConfig

connector = GoogleDriveConnector(
    auth_config=GoogleDriveAuthConfig(
        access_token="<Your Google OAuth2 Access Token (optional, will be obtained via refresh)>",
        refresh_token="<Your Google OAuth2 Refresh Token>",
        client_id="<Your Google OAuth2 Client ID>",
        client_secret="<Your Google OAuth2 Client Secret>"
    )
)
```

#### Token
This authentication method isn't available for this connector.

### Hosted execution

In hosted mode, you first create a connector via the Airbyte API (providing your OAuth or Token credentials), then execute operations using either the Python SDK or API. If you need a step-by-step guide, see the [hosted execution tutorial](https://docs.airbyte.com/ai-agents/quickstarts/tutorial-hosted).

#### OAuth
Create a connector with OAuth credentials.

`credentials` fields you need:


| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `access_token` | `str` | No | Your Google OAuth2 Access Token (optional, will be obtained via refresh) |
| `refresh_token` | `str` | Yes | Your Google OAuth2 Refresh Token |
| `client_id` | `str` | Yes | Your Google OAuth2 Client ID |
| `client_secret` | `str` | Yes | Your Google OAuth2 Client Secret |

Example request:

```bash
curl -X POST "https://api.airbyte.ai/v1/integrations/connectors" \
  -H "Authorization: Bearer <SCOPED_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "external_user_id": "<EXTERNAL_USER_ID>",
    "connector_type": "Google-Drive",
    "name": "My Google-Drive Connector",
    "credentials": {
      "access_token": "<Your Google OAuth2 Access Token (optional, will be obtained via refresh)>",
      "refresh_token": "<Your Google OAuth2 Refresh Token>",
      "client_id": "<Your Google OAuth2 Client ID>",
      "client_secret": "<Your Google OAuth2 Client Secret>"
    }
  }'
```

#### Token
This authentication method isn't available for this connector.

#### Execution

After creating the connector, execute operations using either the Python SDK or API.

**Python SDK**

```python
from airbyte_agent_google-drive import GoogleDriveConnector

connector = GoogleDriveConnector(
    external_user_id="<your_external_user_id>",
    airbyte_client_id="<your-client-id>",
    airbyte_client_secret="<your-client-secret>"
)

@agent.tool_plain # assumes you're using Pydantic AI
@GoogleDriveConnector.tool_utils
async def google-drive_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**API**

```bash
curl -X POST 'https://api.airbyte.ai/api/v1/connectors/sources/<connector_id>/execute' \
  -H 'Authorization: Bearer <SCOPED_TOKEN>' \
  -H 'Content-Type: application/json' \
  -d '{"entity": "<entity>", "action": "<action>", "params": {}}'
```


