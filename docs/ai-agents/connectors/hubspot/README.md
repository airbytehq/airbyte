# Hubspot agent connector

HubSpot is a CRM platform that provides tools for marketing, sales, customer service,
and content management. This connector provides access to contacts, companies, deals,
tickets, and custom objects for customer relationship management and sales analytics.


## Example questions

The Hubspot connector is optimized to handle prompts like these.

- Show me all deals from \{company\} this quarter
- What are the top 5 most valuable deals in my pipeline right now?
- List recent tickets from \{customer\} and analyze their support trends
- Search for contacts in the marketing department at \{company\}
- Give me an overview of my sales team's deals in the last 30 days
- Identify the most active companies in our CRM this month
- Compare the number of deals closed by different sales representatives
- Find all tickets related to a specific product issue and summarize their status

## Unsupported questions

The Hubspot connector isn't currently able to handle prompts like these.

- Create a new contact record for \{person\}
- Update the contact information for \{customer\}
- Delete the ticket from last week's support case
- Schedule a follow-up task for this deal
- Send an email to all contacts in the sales pipeline

## Installation

```bash
uv pip install airbyte-agent-hubspot
```

## Usage

```python
from airbyte_agent_hubspot import HubspotConnector, HubspotAuthConfig

connector = HubspotConnector(
  auth_config=HubspotAuthConfig(
    client_id="...",
    client_secret="...",
    refresh_token="...",
    access_token="..."
  )
)
result = await connector.contacts.list()
```


## Full documentation

This connector supports the following entities and actions.

| Entity | Actions |
|--------|---------|
| Contacts | [List](./REFERENCE.md#contacts-list), [Get](./REFERENCE.md#contacts-get), [Api_search](./REFERENCE.md#contacts-api_search) |
| Companies | [List](./REFERENCE.md#companies-list), [Get](./REFERENCE.md#companies-get), [Api_search](./REFERENCE.md#companies-api_search) |
| Deals | [List](./REFERENCE.md#deals-list), [Get](./REFERENCE.md#deals-get), [Api_search](./REFERENCE.md#deals-api_search) |
| Tickets | [List](./REFERENCE.md#tickets-list), [Get](./REFERENCE.md#tickets-get), [Api_search](./REFERENCE.md#tickets-api_search) |
| Schemas | [List](./REFERENCE.md#schemas-list), [Get](./REFERENCE.md#schemas-get) |
| Objects | [List](./REFERENCE.md#objects-list), [Get](./REFERENCE.md#objects-get) |


For detailed documentation on available actions and parameters, see this connector's [full reference documentation](./REFERENCE.md).

For the service's official API docs, see the [Hubspot API reference](https://developers.hubspot.com/docs/api/crm/understanding-the-crm).

## Version information

- **Package version:** 0.15.49
- **Connector version:** 0.1.6
- **Generated with Connector SDK commit SHA:** 1bd5ca37d04d092d9a53eecfcf8d1802ba501ad5