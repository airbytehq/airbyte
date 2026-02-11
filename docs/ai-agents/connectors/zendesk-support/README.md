# Zendesk-Support

The Zendesk-Support agent connector is a Python package that equips AI agents to interact with Zendesk-Support through strongly typed, well-documented tools. It's ready to use directly in your Python app, in an agent framework, or exposed through an MCP.

Zendesk Support is a customer service platform that helps businesses manage support
tickets, customer interactions, and help center content. This connector provides
access to tickets, users, organizations, groups, comments, attachments, automations,
triggers, macros, views, satisfaction ratings, SLA policies, and help center articles
for customer support analytics and service performance insights.


## Example questions

The Zendesk-Support connector is optimized to handle prompts like these.

- Show me the tickets assigned to me last week
- List all unresolved tickets
- Show me the details of recent tickets
- What are the top 5 support issues our organization has faced this month?
- Analyze the satisfaction ratings for our support team in the last 30 days
- Compare ticket resolution times across different support groups
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

Connectors can run in open source or hosted mode.

### Open source

In open source mode, you provide API credentials directly to the connector.

```python
from airbyte_agent_zendesk_support import ZendeskSupportConnector
from airbyte_agent_zendesk_support.models import ZendeskSupportApiTokenAuthConfig

connector = ZendeskSupportConnector(
    auth_config=ZendeskSupportApiTokenAuthConfig(
        email="<Your Zendesk account email address>",
        api_token="<Your Zendesk API token from Admin Center>"
    )
)

@agent.tool_plain # assumes you're using Pydantic AI
@ZendeskSupportConnector.tool_utils
async def zendesk_support_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

### Hosted

In hosted mode, API credentials are stored securely in Airbyte Cloud. You provide your Airbyte credentials instead. 

This example assumes you've already authenticated your connector with Airbyte. See [Authentication](AUTH.md) to learn more about authenticating. If you need a step-by-step guide, see the [hosted execution tutorial](https://docs.airbyte.com/ai-agents/quickstarts/tutorial-hosted).

```python
from airbyte_agent_zendesk_support import ZendeskSupportConnector, AirbyteAuthConfig

connector = ZendeskSupportConnector(
    auth_config=AirbyteAuthConfig(
        external_user_id="<your_external_user_id>",
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

@agent.tool_plain # assumes you're using Pydantic AI
@ZendeskSupportConnector.tool_utils
async def zendesk_support_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

## Full documentation

### Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Tickets | [List](./REFERENCE.md#tickets-list), [Get](./REFERENCE.md#tickets-get), [Search](./REFERENCE.md#tickets-search) |
| Users | [List](./REFERENCE.md#users-list), [Get](./REFERENCE.md#users-get), [Search](./REFERENCE.md#users-search) |
| Organizations | [List](./REFERENCE.md#organizations-list), [Get](./REFERENCE.md#organizations-get), [Search](./REFERENCE.md#organizations-search) |
| Groups | [List](./REFERENCE.md#groups-list), [Get](./REFERENCE.md#groups-get), [Search](./REFERENCE.md#groups-search) |
| Ticket Comments | [List](./REFERENCE.md#ticket-comments-list), [Search](./REFERENCE.md#ticket-comments-search) |
| Attachments | [Get](./REFERENCE.md#attachments-get), [Download](./REFERENCE.md#attachments-download) |
| Ticket Audits | [List](./REFERENCE.md#ticket-audits-list), [List](./REFERENCE.md#ticket-audits-list), [Search](./REFERENCE.md#ticket-audits-search) |
| Ticket Metrics | [List](./REFERENCE.md#ticket-metrics-list), [Search](./REFERENCE.md#ticket-metrics-search) |
| Ticket Fields | [List](./REFERENCE.md#ticket-fields-list), [Get](./REFERENCE.md#ticket-fields-get), [Search](./REFERENCE.md#ticket-fields-search) |
| Brands | [List](./REFERENCE.md#brands-list), [Get](./REFERENCE.md#brands-get), [Search](./REFERENCE.md#brands-search) |
| Views | [List](./REFERENCE.md#views-list), [Get](./REFERENCE.md#views-get) |
| Macros | [List](./REFERENCE.md#macros-list), [Get](./REFERENCE.md#macros-get) |
| Triggers | [List](./REFERENCE.md#triggers-list), [Get](./REFERENCE.md#triggers-get) |
| Automations | [List](./REFERENCE.md#automations-list), [Get](./REFERENCE.md#automations-get) |
| Tags | [List](./REFERENCE.md#tags-list), [Search](./REFERENCE.md#tags-search) |
| Satisfaction Ratings | [List](./REFERENCE.md#satisfaction-ratings-list), [Get](./REFERENCE.md#satisfaction-ratings-get), [Search](./REFERENCE.md#satisfaction-ratings-search) |
| Group Memberships | [List](./REFERENCE.md#group-memberships-list) |
| Organization Memberships | [List](./REFERENCE.md#organization-memberships-list) |
| Sla Policies | [List](./REFERENCE.md#sla-policies-list), [Get](./REFERENCE.md#sla-policies-get) |
| Ticket Forms | [List](./REFERENCE.md#ticket-forms-list), [Get](./REFERENCE.md#ticket-forms-get), [Search](./REFERENCE.md#ticket-forms-search) |
| Articles | [List](./REFERENCE.md#articles-list), [Get](./REFERENCE.md#articles-get) |
| Article Attachments | [List](./REFERENCE.md#article-attachments-list), [Get](./REFERENCE.md#article-attachments-get), [Download](./REFERENCE.md#article-attachments-download) |


### Authentication

For all authentication options, see the connector's [authentication documentation](AUTH.md).

### Zendesk-Support API docs

See the official [Zendesk-Support API reference](https://developer.zendesk.com/api-reference/ticketing/introduction/).

## Version information

- **Package version:** 0.18.104
- **Connector version:** 0.1.13
- **Generated with Connector SDK commit SHA:** 8c602f77c94fa829be7c1e10d063c5234b17dbef
- **Changelog:** [View changelog](https://github.com/airbytehq/airbyte-agent-connectors/blob/main/connectors/zendesk-support/CHANGELOG.md)