# Slack authentication and configuration

This page documents the authentication and configuration options for the Slack agent connector.

## Authentication

### Open source execution

In open source mode, you provide API credentials directly to the connector.

#### OAuth

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `client_id` | `str` | Yes | Your Slack App's Client ID |
| `client_secret` | `str` | Yes | Your Slack App's Client Secret |
| `access_token` | `str` | Yes | OAuth access token (bot token from oauth.v2.access response) |

```python
from airbyte_agent_slack import SlackConnector
from airbyte_agent_slack.models import SlackOauth20AuthenticationAuthConfig

connector = SlackConnector(
    auth_config=SlackOauth20AuthenticationAuthConfig(
        client_id="<Your Slack App's Client ID>",
        client_secret="<Your Slack App's Client Secret>",
        access_token="<OAuth access token (bot token from oauth.v2.access response)>"
    )
)
```

#### Token

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `access_token` | `str` | Yes | Your Slack Bot Token (xoxb-) or User Token (xoxp-) |

```python
from airbyte_agent_slack import SlackConnector
from airbyte_agent_slack.models import SlackTokenAuthenticationAuthConfig

connector = SlackConnector(
    auth_config=SlackTokenAuthenticationAuthConfig(
        access_token="<Your Slack Bot Token (xoxb-) or User Token (xoxp-)>"
    )
)
```

### Hosted execution

In hosted mode, you first create a connector via the Airbyte API (providing your OAuth or Token credentials), then execute operations using either the Python SDK or API. If you need a step-by-step guide, see the [hosted execution tutorial](https://docs.airbyte.com/ai-agents/quickstarts/tutorial-hosted).

#### OAuth

Create a connector with OAuth credentials:

```bash
curl -X POST 'https://api.airbyte.ai/v1/integrations/sources' \
  -H 'Authorization: Bearer <SCOPED_TOKEN>' \
  -H 'Content-Type: application/json' \
  -d '{
    "workspace_id": "<WORKSPACE_ID>",
    "source_template_id": "<SOURCE_TEMPLATE_ID>",
    "name": "My Slack Connector",
    "credentials": {
      "client_id": "<Your Slack App's Client ID>",
      "client_secret": "<Your Slack App's Client Secret>",
      "access_token": "<OAuth access token (bot token from oauth.v2.access response)>"
    }
  }'
```

#### Token

Create a connector with Token credentials:

```bash
curl -X POST 'https://api.airbyte.ai/v1/integrations/sources' \
  -H 'Authorization: Bearer <SCOPED_TOKEN>' \
  -H 'Content-Type: application/json' \
  -d '{
    "workspace_id": "<WORKSPACE_ID>",
    "source_template_id": "<SOURCE_TEMPLATE_ID>",
    "name": "My Slack Connector",
    "credentials": {
      "access_token": "<Your Slack Bot Token (xoxb-) or User Token (xoxp-)>"
    }
  }'
```

#### Execution

After creating the connector, execute operations using either the Python SDK or API.

**Python SDK**

```python
from airbyte_agent_slack import SlackConnector

connector = SlackConnector(
    external_user_id="<your-scoped-token>",
    airbyte_client_id="<your-client-id>",
    airbyte_client_secret="<your-client-secret>"
)

@agent.tool_plain # assumes you're using Pydantic AI
@SlackConnector.describe
async def slack_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**API**

```bash
curl -X POST 'https://api.airbyte.ai/api/v1/connectors/sources/<connector_id>/execute' \
  -H 'Authorization: Bearer <SCOPED_TOKEN>' \
  -H 'Content-Type: application/json' \
  -d '{"entity": "<entity>", "action": "<action>", "params": {}}'
```


