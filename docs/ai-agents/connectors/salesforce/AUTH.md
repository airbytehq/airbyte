# Salesforce authentication and configuration

This page documents the authentication and configuration options for the Salesforce agent connector.

## Authentication

### Open source execution

In open source mode, you provide API credentials directly to the connector.

#### OAuth

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `refresh_token` | `str` | Yes | OAuth refresh token for automatic token renewal |
| `client_id` | `str` | Yes | Connected App Consumer Key |
| `client_secret` | `str` | Yes | Connected App Consumer Secret |

```python
from airbyte_agent_salesforce import SalesforceConnector
from airbyte_agent_salesforce.models import SalesforceAuthConfig

connector = SalesforceConnector(
    auth_config=SalesforceAuthConfig(
        refresh_token="<OAuth refresh token for automatic token renewal>",
        client_id="<Connected App Consumer Key>",
        client_secret="<Connected App Consumer Secret>"
    )
)
```

#### Token
This authentication method is not available for this connector.

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
    "name": "My Salesforce Connector",
    "credentials": {
      "refresh_token": "<OAuth refresh token for automatic token renewal>",
      "client_id": "<Connected App Consumer Key>",
      "client_secret": "<Connected App Consumer Secret>"
    }
  }'
```

#### Token
This authentication method is not available for this connector.

#### Execution

After creating the connector, execute operations using either the Python SDK or API.

**Python SDK**

```python
from airbyte_agent_salesforce import SalesforceConnector

connector = SalesforceConnector(
    external_user_id="<your-scoped-token>",
    airbyte_client_id="<your-client-id>",
    airbyte_client_secret="<your-client-secret>"
)

@agent.tool_plain # assumes you're using Pydantic AI
@SalesforceConnector.describe
async def salesforce_execute(entity: str, action: str, params: dict | None = None):
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

The Salesforce connector requires the following configuration variables. These variables are used to construct the base API URL. Pass them via the `config` parameter when initializing the connector.

| Variable | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `instance_url` | `string` | Yes | https://login.salesforce.com | Your Salesforce instance URL (e.g., https://na1.salesforce.com) |
