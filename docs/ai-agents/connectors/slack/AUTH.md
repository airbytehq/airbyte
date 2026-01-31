# Slack authentication and configuration

This page documents the authentication and configuration options for the Slack agent connector.

## Authentication

### Open source execution

In open source mode, you provide API credentials directly to the connector.

#### OAuth

`credentials` fields you need:


| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `client_id` | `str` | Yes | Your Slack App's Client ID |
| `client_secret` | `str` | Yes | Your Slack App's Client Secret |
| `access_token` | `str` | Yes | OAuth access token (bot token from oauth.v2.access response) |

Example request:

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

`credentials` fields you need:

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `api_token` | `str` | Yes | Your Slack Bot Token (xoxb-) or User Token (xoxp-) |

Example request:

```python
from airbyte_agent_slack import SlackConnector
from airbyte_agent_slack.models import SlackTokenAuthenticationAuthConfig

connector = SlackConnector(
    auth_config=SlackTokenAuthenticationAuthConfig(
        api_token="<Your Slack Bot Token (xoxb-) or User Token (xoxp-)>"
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
| `client_id` | `str` | Yes | Your Slack App's Client ID |
| `client_secret` | `str` | Yes | Your Slack App's Client Secret |
| `access_token` | `str` | Yes | OAuth access token (bot token from oauth.v2.access response) |

`replication_config` fields you need:

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `start_date` | `str (date-time)` | Yes | UTC date and time in the format YYYY-MM-DDTHH:mm:ssZ from which to start replicating data. |
| `lookback_window` | `int` | Yes | Number of days to look back when syncing data (0-365). |
| `join_channels` | `bool` | Yes | Whether to automatically join public channels to sync messages. |

Example request:

```bash
curl -X POST "https://api.airbyte.ai/v1/integrations/connectors" \
  -H "Authorization: Bearer <SCOPED_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "external_user_id": "<EXTERNAL_USER_ID>",
    "connector_type": "Slack",
    "name": "My Slack Connector",
    "credentials": {
      "client_id": "<Your Slack App's Client ID>",
      "client_secret": "<Your Slack App's Client Secret>",
      "access_token": "<OAuth access token (bot token from oauth.v2.access response)>"
    },
    "replication_config": {
      "start_date": "<UTC date and time in the format YYYY-MM-DDTHH:mm:ssZ from which to start replicating data.>",
      "lookback_window": "<Number of days to look back when syncing data (0-365).>",
      "join_channels": "<Whether to automatically join public channels to sync messages.>"
    }
  }'
```

#### Token
Create a connector with Token credentials.


`credentials` fields you need:

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `api_token` | `str` | Yes | Your Slack Bot Token (xoxb-) or User Token (xoxp-) |

`replication_config` fields you need:

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `start_date` | `str (date-time)` | Yes | UTC date and time in the format YYYY-MM-DDTHH:mm:ssZ from which to start replicating data. |
| `lookback_window` | `int` | Yes | Number of days to look back when syncing data (0-365). |
| `join_channels` | `bool` | Yes | Whether to automatically join public channels to sync messages. |

Example request:


```bash
curl -X POST "https://api.airbyte.ai/v1/integrations/connectors" \
  -H "Authorization: Bearer <SCOPED_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "external_user_id": "<EXTERNAL_USER_ID>",
    "connector_type": "Slack",
    "name": "My Slack Connector",
    "credentials": {
      "api_token": "<Your Slack Bot Token (xoxb-) or User Token (xoxp-)>"
    },
    "replication_config": {
      "start_date": "<UTC date and time in the format YYYY-MM-DDTHH:mm:ssZ from which to start replicating data.>",
      "lookback_window": "<Number of days to look back when syncing data (0-365).>",
      "join_channels": "<Whether to automatically join public channels to sync messages.>"
    }
  }'
```

#### Execution

After creating the connector, execute operations using either the Python SDK or API.

**Python SDK**

```python
from airbyte_agent_slack import SlackConnector

connector = SlackConnector(
    external_user_id="<your_external_user_id>",
    airbyte_client_id="<your-client-id>",
    airbyte_client_secret="<your-client-secret>"
)

@agent.tool_plain # assumes you're using Pydantic AI
@SlackConnector.tool_utils
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


