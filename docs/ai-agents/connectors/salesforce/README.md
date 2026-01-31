# Salesforce agent connector

Salesforce is a cloud-based CRM platform that helps businesses manage customer
relationships, sales pipelines, and business operations. This connector provides
access to accounts, contacts, leads, opportunities, tasks, events, campaigns, cases,
notes, and attachments for sales analytics and customer relationship management.


## Example questions

The Salesforce connector is optimized to handle prompts like these.

- Show me my top 5 opportunities this month
- List all contacts from \{company\} in the last quarter
- Search for leads in the technology sector with revenue over $10M
- What trends can you identify in my recent sales pipeline?
- Summarize the open cases for my key accounts
- Find upcoming events related to my most important opportunities
- Analyze the performance of my recent marketing campaigns
- Identify the highest value opportunities I'm currently tracking
- Show me the notes and attachments for \{customer\}'s account

## Unsupported questions

The Salesforce connector isn't currently able to handle prompts like these.

- Create a new lead for \{person\}
- Update the status of my sales opportunity
- Schedule a follow-up meeting with \{customer\}
- Delete this old contact record
- Send an email to all contacts in this campaign

## Installation

```bash
uv pip install airbyte-agent-salesforce
```

## Usage

Connectors can run in open source or hosted mode.

### Open source

In open source mode, you provide API credentials directly to the connector.

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

@agent.tool_plain # assumes you're using Pydantic AI
@SalesforceConnector.tool_utils
async def salesforce_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

### Hosted

In hosted mode, API credentials are stored securely in Airbyte Cloud. You provide your Airbyte credentials instead. 

This example assumes you've already authenticated your connector with Airbyte. See [Authentication](AUTH.md) to learn more about authenticating. If you need a step-by-step guide, see the [hosted execution tutorial](https://docs.airbyte.com/ai-agents/quickstarts/tutorial-hosted).

```python
from airbyte_agent_salesforce import SalesforceConnector

connector = SalesforceConnector(
    external_user_id="<your_external_user_id>",
    airbyte_client_id="<your-client-id>",
    airbyte_client_secret="<your-client-secret>"
)

@agent.tool_plain # assumes you're using Pydantic AI
@SalesforceConnector.tool_utils
async def salesforce_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

## Full documentation

### Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Accounts | [List](./REFERENCE.md#accounts-list), [Get](./REFERENCE.md#accounts-get), [API Search](./REFERENCE.md#accounts-api_search) |
| Contacts | [List](./REFERENCE.md#contacts-list), [Get](./REFERENCE.md#contacts-get), [API Search](./REFERENCE.md#contacts-api_search) |
| Leads | [List](./REFERENCE.md#leads-list), [Get](./REFERENCE.md#leads-get), [API Search](./REFERENCE.md#leads-api_search) |
| Opportunities | [List](./REFERENCE.md#opportunities-list), [Get](./REFERENCE.md#opportunities-get), [API Search](./REFERENCE.md#opportunities-api_search) |
| Tasks | [List](./REFERENCE.md#tasks-list), [Get](./REFERENCE.md#tasks-get), [API Search](./REFERENCE.md#tasks-api_search) |
| Events | [List](./REFERENCE.md#events-list), [Get](./REFERENCE.md#events-get), [API Search](./REFERENCE.md#events-api_search) |
| Campaigns | [List](./REFERENCE.md#campaigns-list), [Get](./REFERENCE.md#campaigns-get), [API Search](./REFERENCE.md#campaigns-api_search) |
| Cases | [List](./REFERENCE.md#cases-list), [Get](./REFERENCE.md#cases-get), [API Search](./REFERENCE.md#cases-api_search) |
| Notes | [List](./REFERENCE.md#notes-list), [Get](./REFERENCE.md#notes-get), [API Search](./REFERENCE.md#notes-api_search) |
| Content Versions | [List](./REFERENCE.md#content-versions-list), [Get](./REFERENCE.md#content-versions-get), [Download](./REFERENCE.md#content-versions-download) |
| Attachments | [List](./REFERENCE.md#attachments-list), [Get](./REFERENCE.md#attachments-get), [Download](./REFERENCE.md#attachments-download) |
| Query | [List](./REFERENCE.md#query-list) |


### Authentication and configuration

For all authentication and configuration options, see the connector's [authentication documentation](AUTH.md).

### Salesforce API docs

See the official [Salesforce API reference](https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/intro_rest.htm).

## Version information

- **Package version:** 0.1.66
- **Connector version:** 1.0.8
- **Generated with Connector SDK commit SHA:** b184da3e22ef8521d2eeebf3c96a0fe8da2424f5
- **Changelog:** [View changelog](https://github.com/airbytehq/airbyte-agent-connectors/blob/main/connectors/salesforce/CHANGELOG.md)