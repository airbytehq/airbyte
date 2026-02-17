# Gmail authentication

This page documents the authentication and configuration options for the Gmail agent connector.

## Authentication

### Open source execution

In open source mode, you provide API credentials directly to the connector.

#### OAuth

`credentials` fields you need:


| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `access_token` | `str` | No | Your Google OAuth2 Access Token (optional, will be obtained via refresh) |
| `refresh_token` | `str` | Yes | Your Google OAuth2 Refresh Token |
| `client_id` | `str` | No | Your Google OAuth2 Client ID |
| `client_secret` | `str` | No | Your Google OAuth2 Client Secret |

Example request:

```python
from airbyte_agent_gmail import GmailConnector
from airbyte_agent_gmail.models import GmailAuthConfig

connector = GmailConnector(
    auth_config=GmailAuthConfig(
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
| `client_id` | `str` | No | Your Google OAuth2 Client ID |
| `client_secret` | `str` | No | Your Google OAuth2 Client Secret |

`replication_config` fields you need:

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `include_spam_and_trash` | `bool` | No | Include messages from SPAM and TRASH in the results. Defaults to false. |

Example request:

```bash
curl -X POST "https://api.airbyte.ai/api/v1/integrations/connectors" \
  -H "Authorization: Bearer <YOUR_BEARER_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "external_user_id": "<EXTERNAL_USER_ID>",
    "connector_type": "Gmail",
    "name": "My Gmail Connector",
    "credentials": {
      "access_token": "<Your Google OAuth2 Access Token (optional, will be obtained via refresh)>",
      "refresh_token": "<Your Google OAuth2 Refresh Token>",
      "client_id": "<Your Google OAuth2 Client ID>",
      "client_secret": "<Your Google OAuth2 Client Secret>"
    },
    "replication_config": {
      "include_spam_and_trash": "<Include messages from SPAM and TRASH in the results. Defaults to false.>"
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
| `connector_type` | `string` | Yes | The connector type (e.g., "Gmail") |
| `redirect_url` | `string` | Yes | URL to redirect to after OAuth authorization |

Example request:

```bash
curl -X POST "https://api.airbyte.ai/api/v1/integrations/connectors/oauth/initiate" \
  -H "Authorization: Bearer <YOUR_BEARER_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "external_user_id": "<EXTERNAL_USER_ID>",
    "connector_type": "Gmail",
    "redirect_url": "https://yourapp.com/oauth/callback"
  }'
```

Redirect your user to the `consent_url` from the response. After they authorize, they'll be redirected back to your app with a `secret_id` query parameter.

**Step 2: Create a connector with the secret ID**

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `external_user_id` | `string` | Yes | Your unique identifier for the end user |
| `connector_type` | `string` | Yes | The connector type (e.g., "Gmail") |
| `name` | `string` | Yes | A name for this connector instance |
| `server_side_oauth_secret_id` | `string` | Yes | The secret_id from the OAuth callback |
| `replication_config.include_spam_and_trash` | `bool` | No | Include messages from SPAM and TRASH in the results. Defaults to false. |

Example request:

```bash
curl -X POST "https://api.airbyte.ai/api/v1/integrations/connectors" \
  -H "Authorization: Bearer <YOUR_BEARER_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "external_user_id": "<EXTERNAL_USER_ID>",
    "connector_type": "Gmail",
    "name": "My Gmail Connector",
    "server_side_oauth_secret_id": "<secret_id_from_callback>",
    "replication_config": {
      "include_spam_and_trash": "<Include messages from SPAM and TRASH in the results. Defaults to false.>"
    }
  }'
```

#### Token
This authentication method isn't available for this connector.

#### Execution

After creating the connector, execute operations using either the Python SDK or API.

**Python SDK**

```python
from airbyte_agent_gmail import GmailConnector, AirbyteAuthConfig

connector = GmailConnector(
    auth_config=AirbyteAuthConfig(
        external_user_id="<your_external_user_id>",
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

@agent.tool_plain # assumes you're using Pydantic AI
@GmailConnector.tool_utils
async def gmail_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**API**

```bash
curl -X POST 'https://api.airbyte.ai/api/v1/integrations/connectors/<connector_id>/execute' \
  -H 'Authorization: Bearer <YOUR_BEARER_TOKEN>' \
  -H 'Content-Type: application/json' \
  -d '{"entity": "<entity>", "action": "<action>", "params": {}}'
```


