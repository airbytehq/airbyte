# Sentry authentication

This page documents the authentication and configuration options for the Sentry agent connector.

## Authentication

### Open source execution

In open source mode, you provide API credentials directly to the connector.

#### OAuth
This authentication method isn't available for this connector.

#### Token

`credentials` fields you need:

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `auth_token` | `str` | Yes | Sentry authentication token. Log into Sentry and create one at Settings \> Account \> API \> Auth Tokens. |

Example request:

```python
from airbyte_agent_sentry import SentryConnector
from airbyte_agent_sentry.models import SentryAuthConfig

connector = SentryConnector(
    auth_config=SentryAuthConfig(
        auth_token="<Sentry authentication token. Log into Sentry and create one at Settings > Account > API > Auth Tokens.>"
    )
)
```

### Hosted execution

In hosted mode, you first create a connector via the Airbyte API (providing your OAuth or Token credentials), then execute operations using either the Python SDK or API. If you need a step-by-step guide, see the [hosted execution tutorial](https://docs.airbyte.com/ai-agents/quickstarts/tutorial-hosted).

#### OAuth
This authentication method isn't available for this connector.

#### Bring your own OAuth flow
This authentication method isn't available for this connector.

#### Token
Create a connector with Token credentials.


`credentials` fields you need:

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `auth_token` | `str` | Yes | Sentry authentication token. Log into Sentry and create one at Settings \> Account \> API \> Auth Tokens. |

`replication_config` fields you need:

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `organization` | `str` | Yes | The slug of the organization to replicate data from. |
| `project` | `str` | Yes | The slug of the project to replicate data from. |

Example request:


```bash
curl -X POST "https://api.airbyte.ai/api/v1/integrations/connectors" \
  -H "Authorization: Bearer <YOUR_BEARER_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_name": "<CUSTOMER_NAME>",
    "connector_type": "Sentry",
    "name": "My Sentry Connector",
    "credentials": {
      "auth_token": "<Sentry authentication token. Log into Sentry and create one at Settings > Account > API > Auth Tokens.>"
    },
    "replication_config": {
      "organization": "<The slug of the organization to replicate data from.>",
      "project": "<The slug of the project to replicate data from.>"
    }
  }'
```

#### Execution

After creating the connector, execute operations using either the Python SDK or API.
If your Airbyte client can access multiple organizations, include `organization_id` in `AirbyteAuthConfig` and `X-Organization-Id` in raw API calls.

**Python SDK**

```python
from airbyte_agent_sentry import SentryConnector, AirbyteAuthConfig

connector = SentryConnector(
    auth_config=AirbyteAuthConfig(
        customer_name="<your_customer_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

@agent.tool_plain # assumes you're using Pydantic AI
@SentryConnector.tool_utils
async def sentry_execute(entity: str, action: str, params: dict | None = None):
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

The Sentry connector requires the following configuration variables. These variables are used to construct the base API URL. Pass them via the `config` parameter when initializing the connector.

| Variable | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `hostname` | `string` | Yes | sentry.io | Host name of Sentry API server. For self-hosted instances, specify your host name here. Otherwise, leave as sentry.io. |
