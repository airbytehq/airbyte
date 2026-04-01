# Amazon-Seller-Partner authentication

This page documents the authentication and configuration options for the Amazon-Seller-Partner agent connector.

## Authentication

### Open source execution

In open source mode, you provide API credentials directly to the connector.

#### OAuth

`credentials` fields you need:


| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `lwa_app_id` | `str` | Yes | Your Login with Amazon Client ID. |
| `lwa_client_secret` | `str` | Yes | Your Login with Amazon Client Secret. |
| `refresh_token` | `str` | Yes | The Refresh Token obtained via the OAuth authorization flow. |
| `access_token` | `str` | No | Access token (optional if refresh_token is provided). |

Example request:

```python
from airbyte_agent_amazon_seller_partner import AmazonSellerPartnerConnector
from airbyte_agent_amazon_seller_partner.models import AmazonSellerPartnerAuthConfig

connector = AmazonSellerPartnerConnector(
    auth_config=AmazonSellerPartnerAuthConfig(
        lwa_app_id="<Your Login with Amazon Client ID.>",
        lwa_client_secret="<Your Login with Amazon Client Secret.>",
        refresh_token="<The Refresh Token obtained via the OAuth authorization flow.>",
        access_token="<Access token (optional if refresh_token is provided).>"
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
| `lwa_app_id` | `str` | Yes | Your Login with Amazon Client ID. |
| `lwa_client_secret` | `str` | Yes | Your Login with Amazon Client Secret. |
| `refresh_token` | `str` | Yes | The Refresh Token obtained via the OAuth authorization flow. |
| `access_token` | `str` | No | Access token (optional if refresh_token is provided). |

`replication_config` fields you need:

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `replication_start_date` | `str (date-time)` | Yes | UTC date and time in the format 2017-01-25T00:00:00Z. Any data before this date will not be replicated. |

Example request:

```bash
curl -X POST "https://api.airbyte.ai/api/v1/integrations/connectors" \
  -H "Authorization: Bearer <YOUR_BEARER_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_name": "<CUSTOMER_NAME>",
    "connector_type": "Amazon-Seller-Partner",
    "name": "My Amazon-Seller-Partner Connector",
    "credentials": {
      "lwa_app_id": "<Your Login with Amazon Client ID.>",
      "lwa_client_secret": "<Your Login with Amazon Client Secret.>",
      "refresh_token": "<The Refresh Token obtained via the OAuth authorization flow.>",
      "access_token": "<Access token (optional if refresh_token is provided).>"
    },
    "replication_config": {
      "replication_start_date": "<UTC date and time in the format 2017-01-25T00:00:00Z. Any data before this date will not be replicated.>"
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
| `connector_type` | `string` | Yes | The connector type (e.g., "Amazon-Seller-Partner") |
| `redirect_url` | `string` | Yes | URL to redirect to after OAuth authorization |

Example request:

```bash
curl -X POST "https://api.airbyte.ai/api/v1/integrations/connectors/oauth/initiate" \
  -H "Authorization: Bearer <YOUR_BEARER_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_name": "<CUSTOMER_NAME>",
    "connector_type": "Amazon-Seller-Partner",
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
from airbyte_agent_amazon_seller_partner import AmazonSellerPartnerConnector, AirbyteAuthConfig

connector = AmazonSellerPartnerConnector(
    auth_config=AirbyteAuthConfig(
        customer_name="<your_customer_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

@agent.tool_plain # assumes you're using Pydantic AI
@AmazonSellerPartnerConnector.tool_utils
async def amazon_seller_partner_execute(entity: str, action: str, params: dict | None = None):
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


## Configuration

The Amazon-Seller-Partner connector requires the following configuration variables. These variables are used to construct the base API URL. Pass them via the `config` parameter when initializing the connector.

| Variable | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `region` | `string` | Yes | na | The SP-API endpoint URL based on seller region:
- NA (North America: US, CA, MX, BR): https://sellingpartnerapi-na.amazon.com
- EU (Europe/Middle East/Africa/India): https://sellingpartnerapi-eu.amazon.com
- FE (Far East: JP, AU, SG): https://sellingpartnerapi-fe.amazon.com
 |
