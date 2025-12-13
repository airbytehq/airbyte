# Airbyte Hubspot AI Connector

HubSpot is a CRM platform that provides tools for marketing, sales, customer service,
and content management. This connector provides access to contacts, companies, deals,
tickets, and custom objects for customer relationship management and sales analytics.


## Example Questions

- Show me all deals from [Company] this quarter
- What are the top 5 most valuable deals in my pipeline right now?
- List recent tickets from [customerX] and analyze their support trends
- Search for contacts in the marketing department at [Company]
- Give me an overview of my sales team's deals in the last 30 days
- Identify the most active companies in our CRM this month
- Compare the number of deals closed by different sales representatives
- Find all tickets related to a specific product issue and summarize their status

## Unsupported Questions

- Create a new contact record for [personX]
- Update the contact information for [customerY]
- Delete the ticket from last week's support case
- Schedule a follow-up task for this deal
- Send an email to all contacts in the sales pipeline

## Installation

```bash
uv pip install airbyte-ai-hubspot
```

## Usage

```python
from airbyte_ai_hubspot import HubspotConnector, HubspotAuthConfig

connector = HubspotConnector(
  auth_config=HubspotAuthConfig(
    client_id="...",
    client_secret="...",
    refresh_token="...",
    access_token="..."
  )
)
result = connector.contacts.list()
```

## Documentation

| Entity | Actions |
|--------|---------|
| Contacts | [List](./REFERENCE.md#contacts-list), [Get](./REFERENCE.md#contacts-get), [Search](./REFERENCE.md#contacts-search) |
| Companies | [List](./REFERENCE.md#companies-list), [Get](./REFERENCE.md#companies-get), [Search](./REFERENCE.md#companies-search) |
| Deals | [List](./REFERENCE.md#deals-list), [Get](./REFERENCE.md#deals-get), [Search](./REFERENCE.md#deals-search) |
| Tickets | [List](./REFERENCE.md#tickets-list), [Get](./REFERENCE.md#tickets-get), [Search](./REFERENCE.md#tickets-search) |
| Schemas | [List](./REFERENCE.md#schemas-list), [Get](./REFERENCE.md#schemas-get) |
| Objects | [List](./REFERENCE.md#objects-list), [Get](./REFERENCE.md#objects-get) |


For detailed documentation on available actions and parameters, see [REFERENCE.md](./REFERENCE.md).

For the service's official API docs, see [Hubspot API Reference](https://developers.hubspot.com/docs/api/crm/understanding-the-crm).

## Version Information

**Package Version:** 0.15.10

**Connector Version:** 0.1.2

**Generated with connector-sdk:** 4d366cb586482b57efd0c680b3523bbfe48f2180