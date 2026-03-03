# Google-Ads authentication

This page documents the authentication and configuration options for the Google-Ads agent connector.

## Authentication

### Open source execution

In open source mode, you provide API credentials directly to the connector.

#### OAuth

`credentials` fields you need:


| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `client_id` | `str` | Yes | OAuth2 client ID from Google Cloud Console |
| `client_secret` | `str` | Yes | OAuth2 client secret from Google Cloud Console |
| `refresh_token` | `str` | Yes | OAuth2 refresh token |
| `developer_token` | `str` | Yes | Google Ads API developer token |

Example request:

```python
from airbyte_agent_google_ads import GoogleAdsConnector
from airbyte_agent_google_ads.models import GoogleAdsAuthConfig

connector = GoogleAdsConnector(
    auth_config=GoogleAdsAuthConfig(
        client_id="<OAuth2 client ID from Google Cloud Console>",
        client_secret="<OAuth2 client secret from Google Cloud Console>",
        refresh_token="<OAuth2 refresh token>",
        developer_token="<Google Ads API developer token>"
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
| `client_id` | `str` | Yes | OAuth2 client ID from Google Cloud Console |
| `client_secret` | `str` | Yes | OAuth2 client secret from Google Cloud Console |
| `refresh_token` | `str` | Yes | OAuth2 refresh token |
| `developer_token` | `str` | Yes | Google Ads API developer token |

`replication_config` fields you need:

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `customer_id` | `str` | Yes | Comma-separated list of Google Ads customer IDs (10 digits each, no dashes). |
| `start_date` | `str (date)` | No | UTC date in YYYY-MM-DD format from which to start replicating data. Defaults to 2 years ago if not specified. |
| `conversion_window_days` | `int` | No | Number of days for the conversion attribution window. Default is 14. (default: `14`) |

Example request:

```bash
curl -X POST "https://api.airbyte.ai/api/v1/integrations/connectors" \
  -H "Authorization: Bearer <YOUR_BEARER_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_name": "<CUSTOMER_NAME>",
    "connector_type": "Google-Ads",
    "name": "My Google-Ads Connector",
    "credentials": {
      "client_id": "<OAuth2 client ID from Google Cloud Console>",
      "client_secret": "<OAuth2 client secret from Google Cloud Console>",
      "refresh_token": "<OAuth2 refresh token>",
      "developer_token": "<Google Ads API developer token>"
    },
    "replication_config": {
      "customer_id": "<Comma-separated list of Google Ads customer IDs (10 digits each, no dashes).>",
      "start_date": "<UTC date in YYYY-MM-DD format from which to start replicating data. Defaults to 2 years ago if not specified.>",
      "conversion_window_days": "<Number of days for the conversion attribution window. Default is 14.>"
    }
  }'
```



#### Bring your own OAuth flow
To implement your own OAuth flow, use Airbyte's server-side OAuth API endpoints. For a complete guide, see [Build your own OAuth flow](https://docs.airbyte.com/ai-agents/platform/authenticate/build-auth/build-your-own).

##### Step 1: Initiate the OAuth flow

Request a consent URL for your user.

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `customer_name` | `string` | Yes | Your unique identifier for the customer |
| `connector_type` | `string` | Yes | The connector type (e.g., "Google-Ads") |
| `redirect_url` | `string` | Yes | URL to redirect to after OAuth authorization |

Example request:

```bash
curl -X POST "https://api.airbyte.ai/api/v1/integrations/connectors/oauth/initiate" \
  -H "Authorization: Bearer <YOUR_BEARER_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_name": "<CUSTOMER_NAME>",
    "connector_type": "Google-Ads",
    "redirect_url": "https://yourapp.com/oauth/callback"
  }'
```

Redirect your user to the `consent_url` from the response.

##### Step 2: Handle the callback

After the user authorizes access, Airbyte automatically creates the connector and redirects them to your `redirect_url` with a `connector_id` query parameter. You don't need to make a separate API call to create the connector.

```text
https://yourapp.com/oauth/callback?connector_id=<connector_id>
```

Extract the `connector_id` from the callback URL and store it for future operations. For error handling and a complete implementation example, see [Build your own OAuth flow](https://docs.airbyte.com/ai-agents/platform/authenticate/build-auth/build-your-own#part-3-handle-the-callback).

#### Token
This authentication method isn't available for this connector.

#### Execution

After creating the connector, execute operations using either the Python SDK or API.
If your Airbyte client can access multiple organizations, include `organization_id` in `AirbyteAuthConfig` and `X-Organization-Id` in raw API calls.

**Python SDK**

```python
from airbyte_agent_google_ads import GoogleAdsConnector, AirbyteAuthConfig

connector = GoogleAdsConnector(
    auth_config=AirbyteAuthConfig(
        customer_name="<your_customer_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

@agent.tool_plain # assumes you're using Pydantic AI
@GoogleAdsConnector.tool_utils
async def google_ads_execute(entity: str, action: str, params: dict | None = None):
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


