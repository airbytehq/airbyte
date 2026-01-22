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
@SalesforceConnector.describe
async def salesforce_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

### Hosted

In hosted mode, API credentials are stored securely in Airbyte Cloud. You provide your Airbyte credentials instead. 

This example assumes you've already authenticated your connector with Airbyte. See [Authentication](AUTH.md) to learn more about authenticating. If you need a step-by-step guide, see the [hosted execution tutorial](https://docs.airbyte.com/ai-agents/quickstarts/tutorial-hosted).

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

## Full documentation

This connector supports the following entities and actions.

| Entity | Actions |
|--------|---------|
| Accounts | [List](./REFERENCE.md#accounts-list), [Get](./REFERENCE.md#accounts-get), [Api_search](./REFERENCE.md#accounts-api_search) |
| Contacts | [List](./REFERENCE.md#contacts-list), [Get](./REFERENCE.md#contacts-get), [Api_search](./REFERENCE.md#contacts-api_search) |
| Leads | [List](./REFERENCE.md#leads-list), [Get](./REFERENCE.md#leads-get), [Api_search](./REFERENCE.md#leads-api_search) |
| Opportunities | [List](./REFERENCE.md#opportunities-list), [Get](./REFERENCE.md#opportunities-get), [Api_search](./REFERENCE.md#opportunities-api_search) |
| Tasks | [List](./REFERENCE.md#tasks-list), [Get](./REFERENCE.md#tasks-get), [Api_search](./REFERENCE.md#tasks-api_search) |
| Events | [List](./REFERENCE.md#events-list), [Get](./REFERENCE.md#events-get), [Api_search](./REFERENCE.md#events-api_search) |
| Campaigns | [List](./REFERENCE.md#campaigns-list), [Get](./REFERENCE.md#campaigns-get), [Api_search](./REFERENCE.md#campaigns-api_search) |
| Cases | [List](./REFERENCE.md#cases-list), [Get](./REFERENCE.md#cases-get), [Api_search](./REFERENCE.md#cases-api_search) |
| Notes | [List](./REFERENCE.md#notes-list), [Get](./REFERENCE.md#notes-get), [Api_search](./REFERENCE.md#notes-api_search) |
| Content Versions | [List](./REFERENCE.md#content-versions-list), [Get](./REFERENCE.md#content-versions-get), [Download](./REFERENCE.md#content-versions-download) |
| Attachments | [List](./REFERENCE.md#attachments-list), [Get](./REFERENCE.md#attachments-get), [Download](./REFERENCE.md#attachments-download) |
| Query | [List](./REFERENCE.md#query-list) |


For all authentication options, see the connector's [authentication documentation](AUTH.md).

For detailed documentation on available actions and parameters, see this connector's [full reference documentation](./REFERENCE.md).

For the service's official API docs, see the [Salesforce API reference](https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/intro_rest.htm).

## Version information

- **Package version:** 0.1.48
- **Connector version:** 1.0.5
- **Generated with Connector SDK commit SHA:** 49e6dfe93fc406c8d2ed525372608fa2766ebece