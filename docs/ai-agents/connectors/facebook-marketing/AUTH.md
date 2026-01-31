# Facebook-Marketing authentication and configuration

This page documents the authentication and configuration options for the Facebook-Marketing agent connector.

## Authentication

### Open source execution

In open source mode, you provide API credentials directly to the connector.

#### OAuth

`credentials` fields you need:


| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `access_token` | `str` | No | Facebook OAuth2 Access Token |
| `client_id` | `str` | Yes | Facebook App Client ID |
| `client_secret` | `str` | Yes | Facebook App Client Secret |
| `account_id` | `str` | Yes | Facebook Ad Account ID (without act_ prefix) |

Example request:

```python
from airbyte_agent_facebook-marketing import FacebookMarketingConnector
from airbyte_agent_facebook-marketing.models import FacebookMarketingAuthConfig

connector = FacebookMarketingConnector(
    auth_config=FacebookMarketingAuthConfig(
        access_token="<Facebook OAuth2 Access Token>",
        client_id="<Facebook App Client ID>",
        client_secret="<Facebook App Client Secret>",
        account_id="<Facebook Ad Account ID (without act_ prefix)>"
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
| `access_token` | `str` | No | Facebook OAuth2 Access Token |
| `client_id` | `str` | Yes | Facebook App Client ID |
| `client_secret` | `str` | Yes | Facebook App Client Secret |
| `account_id` | `str` | Yes | Facebook Ad Account ID (without act_ prefix) |

Example request:

```bash
curl -X POST "https://api.airbyte.ai/v1/integrations/connectors" \
  -H "Authorization: Bearer <SCOPED_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "external_user_id": "<EXTERNAL_USER_ID>",
    "connector_type": "Facebook-Marketing",
    "name": "My Facebook-Marketing Connector",
    "credentials": {
      "access_token": "<Facebook OAuth2 Access Token>",
      "client_id": "<Facebook App Client ID>",
      "client_secret": "<Facebook App Client Secret>",
      "account_id": "<Facebook Ad Account ID (without act_ prefix)>"
    }
  }'
```

#### Token
This authentication method isn't available for this connector.

#### Execution

After creating the connector, execute operations using either the Python SDK or API.

**Python SDK**

```python
from airbyte_agent_facebook-marketing import FacebookMarketingConnector

connector = FacebookMarketingConnector(
    external_user_id="<your_external_user_id>",
    airbyte_client_id="<your-client-id>",
    airbyte_client_secret="<your-client-secret>"
)

@agent.tool_plain # assumes you're using Pydantic AI
@FacebookMarketingConnector.tool_utils
async def facebook-marketing_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**API**

```bash
curl -X POST 'https://api.airbyte.ai/api/v1/connectors/sources/<connector_id>/execute' \
  -H 'Authorization: Bearer <SCOPED_TOKEN>' \
  -H 'Content-Type: application/json' \
  -d '{"entity": "<entity>", "action": "<action>", "params": {}}'
```


