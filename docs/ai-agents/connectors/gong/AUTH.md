# Gong authentication

This page documents the authentication and configuration options for the Gong agent connector.

## Authentication

### Open source execution

In open source mode, you provide API credentials directly to the connector.

#### OAuth

`credentials` fields you need:


| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `access_token` | `str` | No | Your Gong OAuth2 Access Token. |
| `refresh_token` | `str` | Yes | Your Gong OAuth2 Refresh Token. Note: Gong uses single-use refresh tokens. |
| `client_id` | `str` | No | Your Gong OAuth App Client ID. |
| `client_secret` | `str` | No | Your Gong OAuth App Client Secret. |

Example request:

```python
from airbyte_agent_gong import GongConnector
from airbyte_agent_gong.models import GongOauth20AuthenticationAuthConfig

connector = GongConnector(
    auth_config=GongOauth20AuthenticationAuthConfig(
        access_token="<Your Gong OAuth2 Access Token.>",
        refresh_token="<Your Gong OAuth2 Refresh Token. Note: Gong uses single-use refresh tokens.>",
        client_id="<Your Gong OAuth App Client ID.>",
        client_secret="<Your Gong OAuth App Client Secret.>"
    )
)
```

#### Token

`credentials` fields you need:

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `access_key` | `str` | Yes | Your Gong API Access Key |
| `access_key_secret` | `str` | Yes | Your Gong API Access Key Secret |

Example request:

```python
from airbyte_agent_gong import GongConnector
from airbyte_agent_gong.models import GongAccessKeyAuthenticationAuthConfig

connector = GongConnector(
    auth_config=GongAccessKeyAuthenticationAuthConfig(
        access_key="<Your Gong API Access Key>",
        access_key_secret="<Your Gong API Access Key Secret>"
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
| `access_token` | `str` | No | Your Gong OAuth2 Access Token. |
| `refresh_token` | `str` | Yes | Your Gong OAuth2 Refresh Token. Note: Gong uses single-use refresh tokens. |
| `client_id` | `str` | No | Your Gong OAuth App Client ID. |
| `client_secret` | `str` | No | Your Gong OAuth App Client Secret. |

Example request:

```bash
curl -X POST "https://api.airbyte.ai/api/v1/integrations/connectors" \
  -H "Authorization: Bearer <YOUR_BEARER_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_name": "<CUSTOMER_NAME>",
    "connector_type": "Gong",
    "name": "My Gong Connector",
    "credentials": {
      "access_token": "<Your Gong OAuth2 Access Token.>",
      "refresh_token": "<Your Gong OAuth2 Refresh Token. Note: Gong uses single-use refresh tokens.>",
      "client_id": "<Your Gong OAuth App Client ID.>",
      "client_secret": "<Your Gong OAuth App Client Secret.>"
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
| `connector_type` | `string` | Yes | The connector type (e.g., "Gong") |
| `redirect_url` | `string` | Yes | URL to redirect to after OAuth authorization |

Example request:

```bash
curl -X POST "https://api.airbyte.ai/api/v1/integrations/connectors/oauth/initiate" \
  -H "Authorization: Bearer <YOUR_BEARER_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_name": "<CUSTOMER_NAME>",
    "connector_type": "Gong",
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
Create a connector with Token credentials.


`credentials` fields you need:

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `access_key` | `str` | Yes | Your Gong API Access Key |
| `access_key_secret` | `str` | Yes | Your Gong API Access Key Secret |

Example request:


```bash
curl -X POST "https://api.airbyte.ai/api/v1/integrations/connectors" \
  -H "Authorization: Bearer <YOUR_BEARER_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_name": "<CUSTOMER_NAME>",
    "connector_type": "Gong",
    "name": "My Gong Connector",
    "credentials": {
      "access_key": "<Your Gong API Access Key>",
      "access_key_secret": "<Your Gong API Access Key Secret>"
    }
  }'
```

#### Execution

After creating the connector, execute operations using either the Python SDK or API.
If your Airbyte client can access multiple organizations, include `organization_id` in `AirbyteAuthConfig` and `X-Organization-Id` in raw API calls.

**Python SDK**

```python
from airbyte_agent_gong import GongConnector, AirbyteAuthConfig

connector = GongConnector(
    auth_config=AirbyteAuthConfig(
        customer_name="<your_customer_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

@agent.tool_plain # assumes you're using Pydantic AI
@GongConnector.tool_utils
async def gong_execute(entity: str, action: str, params: dict | None = None):
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


