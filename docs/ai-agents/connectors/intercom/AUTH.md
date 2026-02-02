# Intercom authentication and configuration

This page documents the authentication and configuration options for the Intercom agent connector.

## Authentication

### Open source execution

In open source mode, you provide API credentials directly to the connector.

#### OAuth
This authentication method isn't available for this connector.

#### Token

`credentials` fields you need:

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `access_token` | `str` | Yes | Your Intercom API Access Token |

Example request:

```python
from airbyte_agent_intercom import IntercomConnector
from airbyte_agent_intercom.models import IntercomAuthConfig

connector = IntercomConnector(
    auth_config=IntercomAuthConfig(
        access_token="<Your Intercom API Access Token>"
    )
)
```

### Hosted execution

In hosted mode, you first create a connector via the Airbyte API (providing your OAuth or Token credentials), then execute operations using either the Python SDK or API. If you need a step-by-step guide, see the [hosted execution tutorial](https://docs.airbyte.com/ai-agents/quickstarts/tutorial-hosted).

#### OAuth
This authentication method isn't available for this connector.

#### Token
Create a connector with Token credentials.


`credentials` fields you need:

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `access_token` | `str` | Yes | Your Intercom API Access Token |

`replication_config` fields you need:

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `start_date` | `str (date-time)` | Yes | UTC date and time in the format YYYY-MM-DDTHH:mm:ssZ from which to start replicating data. |

Example request:


```bash
curl -X POST "https://api.airbyte.ai/v1/integrations/connectors" \
  -H "Authorization: Bearer <SCOPED_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "external_user_id": "<EXTERNAL_USER_ID>",
    "connector_type": "Intercom",
    "name": "My Intercom Connector",
    "credentials": {
      "access_token": "<Your Intercom API Access Token>"
    },
    "replication_config": {
      "start_date": "<UTC date and time in the format YYYY-MM-DDTHH:mm:ssZ from which to start replicating data.>"
    }
  }'
```

#### Execution

After creating the connector, execute operations using either the Python SDK or API.

**Python SDK**

```python
from airbyte_agent_intercom import IntercomConnector

connector = IntercomConnector(
    external_user_id="<your_external_user_id>",
    airbyte_client_id="<your-client-id>",
    airbyte_client_secret="<your-client-secret>"
)

@agent.tool_plain # assumes you're using Pydantic AI
@IntercomConnector.tool_utils
async def intercom_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**API**

```bash
curl -X POST 'https://api.airbyte.ai/api/v1/connectors/sources/<connector_id>/execute' \
  -H 'Authorization: Bearer <SCOPED_TOKEN>' \
  -H 'Content-Type: application/json' \
  -d '{"entity": "<entity>", "action": "<action>", "params": {}}'
```


