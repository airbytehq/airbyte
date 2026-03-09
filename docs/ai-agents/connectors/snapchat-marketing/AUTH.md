# Snapchat-Marketing authentication

This page documents the authentication and configuration options for the Snapchat-Marketing agent connector.

## Authentication

### Open source execution

In open source mode, you provide API credentials directly to the connector.

#### OAuth
This authentication method isn't available for this connector.

#### Token

`credentials` fields you need:

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `client_id` | `str` | Yes | The Client ID of your Snapchat developer application |
| `client_secret` | `str` | Yes | The Client Secret of your Snapchat developer application |
| `refresh_token` | `str` | Yes | Refresh Token to renew the expired Access Token |

Example request:

```python
from airbyte_agent_snapchat_marketing import SnapchatMarketingConnector
from airbyte_agent_snapchat_marketing.models import SnapchatMarketingAuthConfig

connector = SnapchatMarketingConnector(
    auth_config=SnapchatMarketingAuthConfig(
        client_id="<The Client ID of your Snapchat developer application>",
        client_secret="<The Client Secret of your Snapchat developer application>",
        refresh_token="<Refresh Token to renew the expired Access Token>"
    )
)
```

### Hosted execution

In hosted mode, you first create a connector via the Airbyte API (providing your OAuth or Token credentials), then execute operations using either the Python SDK or API. If you need a step-by-step guide, see the [hosted execution tutorial](https://docs.airbyte.com/ai-agents/quickstarts/tutorial-hosted).

#### OAuth
This authentication method isn't available for this connector.

#### Bring your own OAuth flow
This authentication method isn't available for this connector.

#### Token
Create a connector with Token credentials.


`credentials` fields you need:

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `client_id` | `str` | Yes | The Client ID of your Snapchat developer application |
| `client_secret` | `str` | Yes | The Client Secret of your Snapchat developer application |
| `refresh_token` | `str` | Yes | Refresh Token to renew the expired Access Token |

`replication_config` fields you need:

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `start_date` | `str (date)` | Yes | Date in YYYY-MM-DD format. Data before this date will not be replicated. |

Example request:


```bash
curl -X POST "https://api.airbyte.ai/api/v1/integrations/connectors" \
  -H "Authorization: Bearer <YOUR_BEARER_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_name": "<CUSTOMER_NAME>",
    "connector_type": "Snapchat-Marketing",
    "name": "My Snapchat-Marketing Connector",
    "credentials": {
      "client_id": "<The Client ID of your Snapchat developer application>",
      "client_secret": "<The Client Secret of your Snapchat developer application>",
      "refresh_token": "<Refresh Token to renew the expired Access Token>"
    },
    "replication_config": {
      "start_date": "<Date in YYYY-MM-DD format. Data before this date will not be replicated.>"
    }
  }'
```

#### Execution

After creating the connector, execute operations using either the Python SDK or API.
If your Airbyte client can access multiple organizations, include `organization_id` in `AirbyteAuthConfig` and `X-Organization-Id` in raw API calls.

**Python SDK**

```python
from airbyte_agent_snapchat_marketing import SnapchatMarketingConnector, AirbyteAuthConfig

connector = SnapchatMarketingConnector(
    auth_config=AirbyteAuthConfig(
        customer_name="<your_customer_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

@agent.tool_plain # assumes you're using Pydantic AI
@SnapchatMarketingConnector.tool_utils
async def snapchat_marketing_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**API**

```bash
curl -X POST 'https://api.airbyte.ai/api/v1/integrations/connectors/<connector_id>/execute' \
  -H 'Authorization: Bearer <YOUR_BEARER_TOKEN>' \
  -H 'X-Organization-Id: <YOUR_ORGANIZATION_ID>' \
  -H 'Content-Type: application/json' \
  -d '{"entity": "<entity>", "action": "<action>", "params": {}}'
```


