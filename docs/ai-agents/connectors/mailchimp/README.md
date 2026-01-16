# Mailchimp agent connector

Mailchimp is an email marketing platform that enables businesses to create, send, and analyze
email campaigns, manage subscriber lists, and automate marketing workflows. This connector
provides read access to campaigns, lists, reports, email activity, automations, and more
for marketing analytics and audience management.


## Example questions

The Mailchimp connector is optimized to handle prompts like these.

- Show me all my email campaigns from the last month
- List all subscribers in my main mailing list
- What are the open rates for my recent campaigns?
- Show me the performance report for campaign \{campaign_id\}
- List all automation workflows in my account
- Who unsubscribed from list \{list_id\} this week?
- Show me all segments for my primary audience
- What tags are applied to my subscribers?
- List all interest categories for list \{list_id\}
- Show me email activity for campaign \{campaign_id\}
- How many subscribers do I have in each list?
- What are my top performing campaigns by click rate?

## Unsupported questions

The Mailchimp connector isn't currently able to handle prompts like these.

- Create a new email campaign
- Add a subscriber to my list
- Delete a campaign
- Update subscriber information
- Send a campaign now
- Create a new automation workflow

## Installation

```bash
uv pip install airbyte-agent-mailchimp
```

## Usage

```python
from airbyte_agent_mailchimp import MailchimpConnector, MailchimpAuthConfig

connector = MailchimpConnector(
  auth_config=MailchimpAuthConfig(
    api_key="...",
    data_center="..."
  )
)
result = await connector.campaigns.list()
```


## Full documentation

This connector supports the following entities and actions.

| Entity | Actions |
|--------|---------|
| Campaigns | [List](./REFERENCE.md#campaigns-list), [Get](./REFERENCE.md#campaigns-get) |
| Lists | [List](./REFERENCE.md#lists-list), [Get](./REFERENCE.md#lists-get) |
| List Members | [List](./REFERENCE.md#list-members-list), [Get](./REFERENCE.md#list-members-get) |
| Reports | [List](./REFERENCE.md#reports-list), [Get](./REFERENCE.md#reports-get) |
| Email Activity | [List](./REFERENCE.md#email-activity-list) |
| Automations | [List](./REFERENCE.md#automations-list) |
| Tags | [List](./REFERENCE.md#tags-list) |
| Interest Categories | [List](./REFERENCE.md#interest-categories-list), [Get](./REFERENCE.md#interest-categories-get) |
| Interests | [List](./REFERENCE.md#interests-list), [Get](./REFERENCE.md#interests-get) |
| Segments | [List](./REFERENCE.md#segments-list), [Get](./REFERENCE.md#segments-get) |
| Segment Members | [List](./REFERENCE.md#segment-members-list) |
| Unsubscribes | [List](./REFERENCE.md#unsubscribes-list) |


For detailed documentation on available actions and parameters, see this connector's [full reference documentation](./REFERENCE.md).

For the service's official API docs, see the [Mailchimp API reference](https://mailchimp.com/developer/marketing/api/).

## Version information

- **Package version:** 0.1.4
- **Connector version:** 1.0.1
- **Generated with Connector SDK commit SHA:** ca5acdda8030d8292c059c82f498a95b2227c106