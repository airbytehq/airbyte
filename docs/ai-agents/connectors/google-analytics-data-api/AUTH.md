# Google-Analytics-Data-Api authentication

This page documents the authentication and configuration options for the Google-Analytics-Data-Api agent connector.

## Authentication

### Open source execution

In open source mode, you provide API credentials directly to the connector.

#### OAuth

`credentials` fields you need:


| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `client_id` | `str` | Yes | OAuth 2.0 Client ID from Google Cloud Console |
| `client_secret` | `str` | Yes | OAuth 2.0 Client Secret from Google Cloud Console |
| `refresh_token` | `str` | Yes | OAuth 2.0 Refresh Token for obtaining new access tokens |

Example request:

```python
from airbyte_agent_google_analytics_data_api import GoogleAnalyticsDataApiConnector
from airbyte_agent_google_analytics_data_api.models import GoogleAnalyticsDataApiAuthConfig

connector = GoogleAnalyticsDataApiConnector(
    auth_config=GoogleAnalyticsDataApiAuthConfig(
        client_id="<OAuth 2.0 Client ID from Google Cloud Console>",
        client_secret="<OAuth 2.0 Client Secret from Google Cloud Console>",
        refresh_token="<OAuth 2.0 Refresh Token for obtaining new access tokens>"
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
| `client_id` | `str` | Yes | OAuth 2.0 Client ID from Google Cloud Console |
| `client_secret` | `str` | Yes | OAuth 2.0 Client Secret from Google Cloud Console |
| `refresh_token` | `str` | Yes | OAuth 2.0 Refresh Token for obtaining new access tokens |

`replication_config` fields you need:

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `property_ids` | `str` | Yes | A list of GA4 Property IDs to replicate data from. |

Example request:

```bash
curl -X POST "https://api.airbyte.ai/api/v1/integrations/connectors" \
  -H "Authorization: Bearer <YOUR_BEARER_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_name": "<CUSTOMER_NAME>",
    "connector_type": "Google-Analytics-Data-Api",
    "name": "My Google-Analytics-Data-Api Connector",
    "credentials": {
      "client_id": "<OAuth 2.0 Client ID from Google Cloud Console>",
      "client_secret": "<OAuth 2.0 Client Secret from Google Cloud Console>",
      "refresh_token": "<OAuth 2.0 Refresh Token for obtaining new access tokens>"
    },
    "replication_config": {
      "property_ids": "<A list of GA4 Property IDs to replicate data from.>"
    }
  }'
```



#### Bring your own OAuth flow
To implement your own OAuth flow, use Airbyte's server-side OAuth API endpoints. For a complete guide, see [Implement your own OAuth flow](https://docs.airbyte.com/ai-agents/quickstarts/tutorial-server-side-oauth).

**Step 1: Initiate the OAuth flow**

Request a consent URL for your user.

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `customer_name` | `string` | Yes | Your unique identifier for the customer |
| `connector_type` | `string` | Yes | The connector type (e.g., "Google-Analytics-Data-Api") |
| `redirect_url` | `string` | Yes | URL to redirect to after OAuth authorization |

Example request:

```bash
curl -X POST "https://api.airbyte.ai/api/v1/integrations/connectors/oauth/initiate" \
  -H "Authorization: Bearer <YOUR_BEARER_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_name": "<CUSTOMER_NAME>",
    "connector_type": "Google-Analytics-Data-Api",
    "redirect_url": "https://yourapp.com/oauth/callback"
  }'
```

Redirect your user to the `consent_url` from the response. After they authorize, they'll be redirected back to your app with a `secret_id` query parameter.

**Step 2: Create a connector with the secret ID**

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `customer_name` | `string` | Yes | Your unique identifier for the customer |
| `connector_type` | `string` | Yes | The connector type (e.g., "Google-Analytics-Data-Api") |
| `name` | `string` | Yes | A name for this connector instance |
| `server_side_oauth_secret_id` | `string` | Yes | The secret_id from the OAuth callback |
| `replication_config.property_ids` | `str` | Yes | A list of GA4 Property IDs to replicate data from. |

Example request:

```bash
curl -X POST "https://api.airbyte.ai/api/v1/integrations/connectors" \
  -H "Authorization: Bearer <YOUR_BEARER_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_name": "<CUSTOMER_NAME>",
    "connector_type": "Google-Analytics-Data-Api",
    "name": "My Google-Analytics-Data-Api Connector",
    "server_side_oauth_secret_id": "<secret_id_from_callback>",
    "replication_config": {
      "property_ids": "<A list of GA4 Property IDs to replicate data from.>"
    }
  }'
```

#### Token
This authentication method isn't available for this connector.

#### Execution

After creating the connector, execute operations using either the Python SDK or API.
If your Airbyte client can access multiple organizations, include `organization_id` in `AirbyteAuthConfig` and `X-Organization-Id` in raw API calls.

**Python SDK**

```python
from airbyte_agent_google_analytics_data_api import GoogleAnalyticsDataApiConnector, AirbyteAuthConfig

connector = GoogleAnalyticsDataApiConnector(
    auth_config=AirbyteAuthConfig(
        customer_name="<your_customer_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

@agent.tool_plain # assumes you're using Pydantic AI
@GoogleAnalyticsDataApiConnector.tool_utils
async def google_analytics_data_api_execute(entity: str, action: str, params: dict | None = None):
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


