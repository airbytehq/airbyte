# Hubspot authentication and configuration

This page documents the authentication and configuration options for the Hubspot agent connector.

## Authentication

### Open source execution

In open source mode, you provide API credentials directly to the connector.

#### OAuth

`credentials` fields you need:


| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `client_id` | `str` | Yes | Your HubSpot OAuth2 Client ID |
| `client_secret` | `str` | Yes | Your HubSpot OAuth2 Client Secret |
| `refresh_token` | `str` | Yes | Your HubSpot OAuth2 Refresh Token |
| `access_token` | `str` | No | Your HubSpot OAuth2 Access Token (optional if refresh_token is provided) |

Example request:

```python
from airbyte_agent_hubspot import HubspotConnector
from airbyte_agent_hubspot.models import HubspotAuthConfig

connector = HubspotConnector(
    auth_config=HubspotAuthConfig(
        client_id="<Your HubSpot OAuth2 Client ID>",
        client_secret="<Your HubSpot OAuth2 Client Secret>",
        refresh_token="<Your HubSpot OAuth2 Refresh Token>",
        access_token="<Your HubSpot OAuth2 Access Token (optional if refresh_token is provided)>"
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
| `client_id` | `str` | Yes | Your HubSpot OAuth2 Client ID |
| `client_secret` | `str` | Yes | Your HubSpot OAuth2 Client Secret |
| `refresh_token` | `str` | Yes | Your HubSpot OAuth2 Refresh Token |
| `access_token` | `str` | No | Your HubSpot OAuth2 Access Token (optional if refresh_token is provided) |

Example request:

```bash
curl -X POST "https://api.airbyte.ai/v1/integrations/connectors" \
  -H "Authorization: Bearer <SCOPED_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "external_user_id": "<EXTERNAL_USER_ID>",
    "connector_type": "Hubspot",
    "name": "My Hubspot Connector",
    "credentials": {
      "client_id": "<Your HubSpot OAuth2 Client ID>",
      "client_secret": "<Your HubSpot OAuth2 Client Secret>",
      "refresh_token": "<Your HubSpot OAuth2 Refresh Token>",
      "access_token": "<Your HubSpot OAuth2 Access Token (optional if refresh_token is provided)>"
    }
  }'
```

#### Token
This authentication method isn't available for this connector.

#### Execution

After creating the connector, execute operations using either the Python SDK or API.

**Python SDK**

```python
from airbyte_agent_hubspot import HubspotConnector

connector = HubspotConnector(
    external_user_id="<your_external_user_id>",
    airbyte_client_id="<your-client-id>",
    airbyte_client_secret="<your-client-secret>"
)

@agent.tool_plain # assumes you're using Pydantic AI
@HubspotConnector.tool_utils
async def hubspot_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**API**

```bash
curl -X POST 'https://api.airbyte.ai/api/v1/connectors/sources/<connector_id>/execute' \
  -H 'Authorization: Bearer <SCOPED_TOKEN>' \
  -H 'Content-Type: application/json' \
  -d '{"entity": "<entity>", "action": "<action>", "params": {}}'
```


