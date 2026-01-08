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

```python
from airbyte_agent_salesforce import SalesforceConnector, SalesforceAuthConfig

connector = SalesforceConnector(
  auth_config=SalesforceAuthConfig(
    refresh_token="...",
    client_id="...",
    client_secret="..."
  )
)
result = await connector.accounts.list()
```


## Full documentation

This connector supports the following entities and actions.

| Entity | Actions |
|--------|---------|
| Accounts | [List](./REFERENCE.md#accounts-list), [Get](./REFERENCE.md#accounts-get), [Search](./REFERENCE.md#accounts-search) |
| Contacts | [List](./REFERENCE.md#contacts-list), [Get](./REFERENCE.md#contacts-get), [Search](./REFERENCE.md#contacts-search) |
| Leads | [List](./REFERENCE.md#leads-list), [Get](./REFERENCE.md#leads-get), [Search](./REFERENCE.md#leads-search) |
| Opportunities | [List](./REFERENCE.md#opportunities-list), [Get](./REFERENCE.md#opportunities-get), [Search](./REFERENCE.md#opportunities-search) |
| Tasks | [List](./REFERENCE.md#tasks-list), [Get](./REFERENCE.md#tasks-get), [Search](./REFERENCE.md#tasks-search) |
| Events | [List](./REFERENCE.md#events-list), [Get](./REFERENCE.md#events-get), [Search](./REFERENCE.md#events-search) |
| Campaigns | [List](./REFERENCE.md#campaigns-list), [Get](./REFERENCE.md#campaigns-get), [Search](./REFERENCE.md#campaigns-search) |
| Cases | [List](./REFERENCE.md#cases-list), [Get](./REFERENCE.md#cases-get), [Search](./REFERENCE.md#cases-search) |
| Notes | [List](./REFERENCE.md#notes-list), [Get](./REFERENCE.md#notes-get), [Search](./REFERENCE.md#notes-search) |
| Content Versions | [List](./REFERENCE.md#content-versions-list), [Get](./REFERENCE.md#content-versions-get), [Download](./REFERENCE.md#content-versions-download) |
| Attachments | [List](./REFERENCE.md#attachments-list), [Get](./REFERENCE.md#attachments-get), [Download](./REFERENCE.md#attachments-download) |
| Query | [List](./REFERENCE.md#query-list) |


For detailed documentation on available actions and parameters, see this connector's [full reference documentation](./REFERENCE.md).

For the service's official API docs, see the [Salesforce API reference](https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/intro_rest.htm).

## Version information

- **Package version:** 0.1.22
- **Connector version:** 1.0.4
- **Generated with Connector SDK commit SHA:** d023e05f2b7a1ddabf81fab7640c64de1e0aa6a1