# Facebook-Marketing authentication and configuration

This page documents the authentication and configuration options for the Facebook-Marketing agent connector.

## Authentication

### Open source execution

In open source mode, you provide API credentials directly to the connector.

#### OAuth

`credentials` fields you need:


| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `access_token` | `str` | Yes | Facebook OAuth2 Access Token |
| `client_id` | `str` | No | Facebook App Client ID |
| `client_secret` | `str` | No | Facebook App Client Secret |

Example request:

```python
from airbyte_agent_facebook_marketing import FacebookMarketingConnector
from airbyte_agent_facebook_marketing.models import FacebookMarketingOauth20AuthenticationAuthConfig

connector = FacebookMarketingConnector(
    auth_config=FacebookMarketingOauth20AuthenticationAuthConfig(
        access_token="<Facebook OAuth2 Access Token>",
        client_id="<Facebook App Client ID>",
        client_secret="<Facebook App Client Secret>"
    )
)
```

#### Token

`credentials` fields you need:

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `account_key` | `str` | Yes | Facebook long-lived access token for Service Account authentication |

Example request:

```python
from airbyte_agent_facebook_marketing import FacebookMarketingConnector
from airbyte_agent_facebook_marketing.models import FacebookMarketingServiceAccountKeyAuthenticationAuthConfig

connector = FacebookMarketingConnector(
    auth_config=FacebookMarketingServiceAccountKeyAuthenticationAuthConfig(
        account_key="<Facebook long-lived access token for Service Account authentication>"
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
| `access_token` | `str` | Yes | Facebook OAuth2 Access Token |
| `client_id` | `str` | No | Facebook App Client ID |
| `client_secret` | `str` | No | Facebook App Client Secret |

`replication_config` fields you need:

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `account_ids` | `str` | Yes | The Facebook Ad account ID(s) to pull data from. The Ad account ID number is in the account dropdown menu or in your browser's address bar of your Meta Ads Manager. |

Example request:

```bash
curl -X POST "https://api.airbyte.ai/api/v1/integrations/connectors" \
  -H "Authorization: Bearer <YOUR_BEARER_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "external_user_id": "<EXTERNAL_USER_ID>",
    "connector_type": "Facebook-Marketing",
    "name": "My Facebook-Marketing Connector",
    "credentials": {
      "access_token": "<Facebook OAuth2 Access Token>",
      "client_id": "<Facebook App Client ID>",
      "client_secret": "<Facebook App Client Secret>"
    },
    "replication_config": {
      "account_ids": "<The Facebook Ad account ID(s) to pull data from. The Ad account ID number is in the account dropdown menu or in your browser's address bar of your Meta Ads Manager.>"
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
| `connector_type` | `string` | Yes | The connector type (e.g., "Facebook-Marketing") |
| `redirect_url` | `string` | Yes | URL to redirect to after OAuth authorization |

Example request:

```bash
curl -X POST "https://api.airbyte.ai/api/v1/integrations/connectors/oauth/initiate" \
  -H "Authorization: Bearer <YOUR_BEARER_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "external_user_id": "<EXTERNAL_USER_ID>",
    "connector_type": "Facebook-Marketing",
    "redirect_url": "https://yourapp.com/oauth/callback"
  }'
```

Redirect your user to the `consent_url` from the response. After they authorize, they'll be redirected back to your app with a `secret_id` query parameter.

**Step 2: Create a connector with the secret ID**

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `external_user_id` | `string` | Yes | Your unique identifier for the end user |
| `connector_type` | `string` | Yes | The connector type (e.g., "Facebook-Marketing") |
| `name` | `string` | Yes | A name for this connector instance |
| `server_side_oauth_secret_id` | `string` | Yes | The secret_id from the OAuth callback |
| `replication_config.account_ids` | `str` | Yes | The Facebook Ad account ID(s) to pull data from. The Ad account ID number is in the account dropdown menu or in your browser's address bar of your Meta Ads Manager. |

Example request:

```bash
curl -X POST "https://api.airbyte.ai/api/v1/integrations/connectors" \
  -H "Authorization: Bearer <YOUR_BEARER_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "external_user_id": "<EXTERNAL_USER_ID>",
    "connector_type": "Facebook-Marketing",
    "name": "My Facebook-Marketing Connector",
    "server_side_oauth_secret_id": "<secret_id_from_callback>",
    "replication_config": {
      "account_ids": "<The Facebook Ad account ID(s) to pull data from. The Ad account ID number is in the account dropdown menu or in your browser's address bar of your Meta Ads Manager.>"
    }
  }'
```

#### Token
Create a connector with Token credentials.


`credentials` fields you need:

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `account_key` | `str` | Yes | Facebook long-lived access token for Service Account authentication |

`replication_config` fields you need:

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `account_ids` | `str` | Yes | The Facebook Ad account ID(s) to pull data from. The Ad account ID number is in the account dropdown menu or in your browser's address bar of your Meta Ads Manager. |

Example request:


```bash
curl -X POST "https://api.airbyte.ai/api/v1/integrations/connectors" \
  -H "Authorization: Bearer <YOUR_BEARER_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "external_user_id": "<EXTERNAL_USER_ID>",
    "connector_type": "Facebook-Marketing",
    "name": "My Facebook-Marketing Connector",
    "credentials": {
      "account_key": "<Facebook long-lived access token for Service Account authentication>"
    },
    "replication_config": {
      "account_ids": "<The Facebook Ad account ID(s) to pull data from. The Ad account ID number is in the account dropdown menu or in your browser's address bar of your Meta Ads Manager.>"
    }
  }'
```

#### Execution

After creating the connector, execute operations using either the Python SDK or API.

**Python SDK**

```python
from airbyte_agent_facebook_marketing import FacebookMarketingConnector, AirbyteAuthConfig

connector = FacebookMarketingConnector(
    auth_config=AirbyteAuthConfig(
        external_user_id="<your_external_user_id>",
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

@agent.tool_plain # assumes you're using Pydantic AI
@FacebookMarketingConnector.tool_utils
async def facebook_marketing_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**API**

```bash
curl -X POST 'https://api.airbyte.ai/api/v1/integrations/connectors/<connector_id>/execute' \
  -H 'Authorization: Bearer <YOUR_BEARER_TOKEN>' \
  -H 'Content-Type: application/json' \
  -d '{"entity": "<entity>", "action": "<action>", "params": {}}'
```


