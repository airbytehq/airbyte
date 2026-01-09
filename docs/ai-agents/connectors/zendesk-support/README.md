# Zendesk-Support agent connector

Zendesk Support is a customer service platform that helps businesses manage support
tickets, customer interactions, and help center content. This connector provides
access to tickets, users, organizations, groups, comments, attachments, automations,
triggers, macros, views, satisfaction ratings, SLA policies, and help center articles
for customer support analytics and service performance insights.


## Example questions

The Zendesk-Support connector is optimized to handle prompts like these.

- Show me the tickets assigned to me last week
- What are the top 5 support issues our organization has faced this month?
- List all unresolved tickets for \{customer\}
- Analyze the satisfaction ratings for our support team in the last 30 days
- Compare ticket resolution times across different support groups
- Show me the details of recent tickets tagged with \{tag\}
- Identify the most common ticket fields used in our support workflow
- Summarize the performance of our SLA policies this quarter

## Unsupported questions

The Zendesk-Support connector isn't currently able to handle prompts like these.

- Create a new support ticket for \{customer\}
- Update the priority of this ticket
- Assign this ticket to \{team_member\}
- Delete these old support tickets
- Send an automatic response to \{customer\}

## Installation

```bash
uv pip install airbyte-agent-zendesk-support
```

## Usage

This connector supports multiple authentication methods:

### OAuth 2.0

```python
from airbyte_agent_zendesk_support import ZendeskSupportConnector
from airbyte_agent_zendesk_support.models import ZendeskSupportOauth20AuthConfig

connector = ZendeskSupportConnector(
  auth_config=ZendeskSupportOauth20AuthConfig(
    access_token="...",
    refresh_token="..."
  )
)
result = await connector.tickets.list()
```

### API Token

```python
from airbyte_agent_zendesk_support import ZendeskSupportConnector
from airbyte_agent_zendesk_support.models import ZendeskSupportApiTokenAuthConfig

connector = ZendeskSupportConnector(
  auth_config=ZendeskSupportApiTokenAuthConfig(
    email="...",
    api_token="..."
  )
)
result = await connector.tickets.list()
```


## Full documentation

This connector supports the following entities and actions.

| Entity | Actions |
|--------|---------|
| Tickets | [List](./REFERENCE.md#tickets-list), [Get](./REFERENCE.md#tickets-get) |
| Users | [List](./REFERENCE.md#users-list), [Get](./REFERENCE.md#users-get) |
| Organizations | [List](./REFERENCE.md#organizations-list), [Get](./REFERENCE.md#organizations-get) |
| Groups | [List](./REFERENCE.md#groups-list), [Get](./REFERENCE.md#groups-get) |
| Ticket Comments | [List](./REFERENCE.md#ticket-comments-list) |
| Attachments | [Get](./REFERENCE.md#attachments-get), [Download](./REFERENCE.md#attachments-download) |
| Ticket Audits | [List](./REFERENCE.md#ticket-audits-list), [List](./REFERENCE.md#ticket-audits-list) |
| Ticket Metrics | [List](./REFERENCE.md#ticket-metrics-list) |
| Ticket Fields | [List](./REFERENCE.md#ticket-fields-list), [Get](./REFERENCE.md#ticket-fields-get) |
| Brands | [List](./REFERENCE.md#brands-list), [Get](./REFERENCE.md#brands-get) |
| Views | [List](./REFERENCE.md#views-list), [Get](./REFERENCE.md#views-get) |
| Macros | [List](./REFERENCE.md#macros-list), [Get](./REFERENCE.md#macros-get) |
| Triggers | [List](./REFERENCE.md#triggers-list), [Get](./REFERENCE.md#triggers-get) |
| Automations | [List](./REFERENCE.md#automations-list), [Get](./REFERENCE.md#automations-get) |
| Tags | [List](./REFERENCE.md#tags-list) |
| Satisfaction Ratings | [List](./REFERENCE.md#satisfaction-ratings-list), [Get](./REFERENCE.md#satisfaction-ratings-get) |
| Group Memberships | [List](./REFERENCE.md#group-memberships-list) |
| Organization Memberships | [List](./REFERENCE.md#organization-memberships-list) |
| Sla Policies | [List](./REFERENCE.md#sla-policies-list), [Get](./REFERENCE.md#sla-policies-get) |
| Ticket Forms | [List](./REFERENCE.md#ticket-forms-list), [Get](./REFERENCE.md#ticket-forms-get) |
| Articles | [List](./REFERENCE.md#articles-list), [Get](./REFERENCE.md#articles-get) |
| Article Attachments | [List](./REFERENCE.md#article-attachments-list), [Get](./REFERENCE.md#article-attachments-get), [Download](./REFERENCE.md#article-attachments-download) |


For detailed documentation on available actions and parameters, see this connector's [full reference documentation](./REFERENCE.md).

For the service's official API docs, see the [Zendesk-Support API reference](https://developer.zendesk.com/api-reference/ticketing/introduction/).

## Version information

- **Package version:** 0.18.29
- **Connector version:** 0.1.4
- **Generated with Connector SDK commit SHA:** d023e05f2b7a1ddabf81fab7640c64de1e0aa6a1