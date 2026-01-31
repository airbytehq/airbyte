# Jira authentication and configuration

This page documents the authentication and configuration options for the Jira agent connector.

## Authentication

### Open source execution

In open source mode, you provide API credentials directly to the connector.

#### OAuth
This authentication method isn't available for this connector.

#### Token

`credentials` fields you need:

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `username` | `str` | Yes | Your Atlassian account email address |
| `password` | `str` | Yes | Your Jira API token from https://id.atlassian.com/manage-profile/security/api-tokens |

Example request:

```python
from airbyte_agent_jira import JiraConnector
from airbyte_agent_jira.models import JiraAuthConfig

connector = JiraConnector(
    auth_config=JiraAuthConfig(
        username="<Your Atlassian account email address>",
        password="<Your Jira API token from https://id.atlassian.com/manage-profile/security/api-tokens>"
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
| `username` | `str` | Yes | Your Atlassian account email address |
| `password` | `str` | Yes | Your Jira API token from https://id.atlassian.com/manage-profile/security/api-tokens |

Example request:


```bash
curl -X POST "https://api.airbyte.ai/v1/integrations/connectors" \
  -H "Authorization: Bearer <SCOPED_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "external_user_id": "<EXTERNAL_USER_ID>",
    "connector_type": "Jira",
    "name": "My Jira Connector",
    "credentials": {
      "username": "<Your Atlassian account email address>",
      "password": "<Your Jira API token from https://id.atlassian.com/manage-profile/security/api-tokens>"
    }
  }'
```

#### Execution

After creating the connector, execute operations using either the Python SDK or API.

**Python SDK**

```python
from airbyte_agent_jira import JiraConnector

connector = JiraConnector(
    external_user_id="<your_external_user_id>",
    airbyte_client_id="<your-client-id>",
    airbyte_client_secret="<your-client-secret>"
)

@agent.tool_plain # assumes you're using Pydantic AI
@JiraConnector.tool_utils
async def jira_execute(entity: str, action: str, params: dict | None = None):
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

The Jira connector requires the following configuration variables. These variables are used to construct the base API URL. Pass them via the `config` parameter when initializing the connector.

| Variable | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `subdomain` | `string` | Yes | \{subdomain\} | Your Jira Cloud subdomain |
