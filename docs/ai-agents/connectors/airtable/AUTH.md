# Airtable authentication and configuration

This page documents the authentication and configuration options for the Airtable agent connector.

## Authentication

### Open source execution

In open source mode, you provide API credentials directly to the connector.

#### OAuth
This authentication method isn't available for this connector.

#### Token

`credentials` fields you need:

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `personal_access_token` | `str` | Yes | Airtable Personal Access Token. See https://airtable.com/developers/web/guides/personal-access-tokens |

Example request:

```python
from airbyte_agent_airtable import AirtableConnector
from airbyte_agent_airtable.models import AirtableAuthConfig

connector = AirtableConnector(
    auth_config=AirtableAuthConfig(
        personal_access_token="<Airtable Personal Access Token. See https://airtable.com/developers/web/guides/personal-access-tokens>"
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
| `personal_access_token` | `str` | Yes | Airtable Personal Access Token. See https://airtable.com/developers/web/guides/personal-access-tokens |

Example request:


```bash
curl -X POST "https://api.airbyte.ai/v1/integrations/connectors" \
  -H "Authorization: Bearer <SCOPED_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "external_user_id": "<EXTERNAL_USER_ID>",
    "connector_type": "Airtable",
    "name": "My Airtable Connector",
    "credentials": {
      "personal_access_token": "<Airtable Personal Access Token. See https://airtable.com/developers/web/guides/personal-access-tokens>"
    }
  }'
```

#### Execution

After creating the connector, execute operations using either the Python SDK or API.

**Python SDK**

```python
from airbyte_agent_airtable import AirtableConnector

connector = AirtableConnector(
    external_user_id="<your_external_user_id>",
    airbyte_client_id="<your-client-id>",
    airbyte_client_secret="<your-client-secret>"
)

@agent.tool_plain # assumes you're using Pydantic AI
@AirtableConnector.tool_utils
async def airtable_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**API**

```bash
curl -X POST 'https://api.airbyte.ai/api/v1/connectors/sources/<connector_id>/execute' \
  -H 'Authorization: Bearer <SCOPED_TOKEN>' \
  -H 'Content-Type: application/json' \
  -d '{"entity": "<entity>", "action": "<action>", "params": {}}'
```


