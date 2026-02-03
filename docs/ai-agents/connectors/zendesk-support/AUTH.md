# Zendesk-Support authentication and configuration

This page documents the authentication and configuration options for the Zendesk-Support agent connector.

## Authentication

### Open source execution

In open source mode, you provide API credentials directly to the connector.

#### OAuth

`credentials` fields you need:


| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `access_token` | `str` | Yes | OAuth 2.0 access token |
| `refresh_token` | `str` | No | OAuth 2.0 refresh token (optional) |

Example request:

```python
from airbyte_agent_zendesk-support import ZendeskSupportConnector
from airbyte_agent_zendesk-support.models import ZendeskSupportOauth20AuthConfig

connector = ZendeskSupportConnector(
    auth_config=ZendeskSupportOauth20AuthConfig(
        access_token="<OAuth 2.0 access token>",
        refresh_token="<OAuth 2.0 refresh token (optional)>"
    )
)
```

#### Token

`credentials` fields you need:

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `email` | `str` | Yes | Your Zendesk account email address |
| `api_token` | `str` | Yes | Your Zendesk API token from Admin Center |

Example request:

```python
from airbyte_agent_zendesk-support import ZendeskSupportConnector
from airbyte_agent_zendesk-support.models import ZendeskSupportApiTokenAuthConfig

connector = ZendeskSupportConnector(
    auth_config=ZendeskSupportApiTokenAuthConfig(
        email="<Your Zendesk account email address>",
        api_token="<Your Zendesk API token from Admin Center>"
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
| `access_token` | `str` | Yes | OAuth 2.0 access token |
| `refresh_token` | `str` | No | OAuth 2.0 refresh token (optional) |

Example request:

```bash
curl -X POST "https://api.airbyte.ai/v1/integrations/connectors" \
  -H "Authorization: Bearer <SCOPED_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "external_user_id": "<EXTERNAL_USER_ID>",
    "connector_type": "Zendesk-Support",
    "name": "My Zendesk-Support Connector",
    "credentials": {
      "access_token": "<OAuth 2.0 access token>",
      "refresh_token": "<OAuth 2.0 refresh token (optional)>"
    }
  }'
```

#### Token
Create a connector with Token credentials.


`credentials` fields you need:

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `email` | `str` | Yes | Your Zendesk account email address |
| `api_token` | `str` | Yes | Your Zendesk API token from Admin Center |

Example request:


```bash
curl -X POST "https://api.airbyte.ai/v1/integrations/connectors" \
  -H "Authorization: Bearer <SCOPED_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "external_user_id": "<EXTERNAL_USER_ID>",
    "connector_type": "Zendesk-Support",
    "name": "My Zendesk-Support Connector",
    "credentials": {
      "email": "<Your Zendesk account email address>",
      "api_token": "<Your Zendesk API token from Admin Center>"
    }
  }'
```

#### Execution

After creating the connector, execute operations using either the Python SDK or API.

**Python SDK**

```python
from airbyte_agent_zendesk-support import ZendeskSupportConnector

connector = ZendeskSupportConnector(
    external_user_id="<your_external_user_id>",
    airbyte_client_id="<your-client-id>",
    airbyte_client_secret="<your-client-secret>"
)

@agent.tool_plain # assumes you're using Pydantic AI
@ZendeskSupportConnector.tool_utils
async def zendesk-support_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**API**

```bash
curl -X POST 'https://api.airbyte.ai/api/v1/connectors/sources/<connector_id>/execute' \
  -H 'Authorization: Bearer <SCOPED_TOKEN>' \
  -H 'Content-Type: application/json' \
  -d '{"entity": "<entity>", "action": "<action>", "params": {}}'
```


## Configuration

The Zendesk-Support connector requires the following configuration variables. These variables are used to construct the base API URL. Pass them via the `config` parameter when initializing the connector.

| Variable | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `subdomain` | `string` | Yes | your-subdomain | Your Zendesk subdomain |
