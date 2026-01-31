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

Connectors can run in open source or hosted mode.

### Open source

In open source mode, you provide API credentials directly to the connector.

```python
from airbyte_agent_mailchimp import MailchimpConnector
from airbyte_agent_mailchimp.models import MailchimpAuthConfig

connector = MailchimpConnector(
    auth_config=MailchimpAuthConfig(
        api_key="<Your Mailchimp API key. You can find this in your Mailchimp account under Account > Extras > API keys.>"
    )
)

@agent.tool_plain # assumes you're using Pydantic AI
@MailchimpConnector.tool_utils
async def mailchimp_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

### Hosted

In hosted mode, API credentials are stored securely in Airbyte Cloud. You provide your Airbyte credentials instead. 

This example assumes you've already authenticated your connector with Airbyte. See [Authentication](AUTH.md) to learn more about authenticating. If you need a step-by-step guide, see the [hosted execution tutorial](https://docs.airbyte.com/ai-agents/quickstarts/tutorial-hosted).

```python
from airbyte_agent_mailchimp import MailchimpConnector

connector = MailchimpConnector(
    external_user_id="<your_external_user_id>",
    airbyte_client_id="<your-client-id>",
    airbyte_client_secret="<your-client-secret>"
)

@agent.tool_plain # assumes you're using Pydantic AI
@MailchimpConnector.tool_utils
async def mailchimp_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

## Full documentation

### Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

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


### Authentication and configuration

For all authentication and configuration options, see the connector's [authentication documentation](AUTH.md).

### Mailchimp API docs

See the official [Mailchimp API reference](https://mailchimp.com/developer/marketing/api/).

## Version information

- **Package version:** 0.1.32
- **Connector version:** 1.0.5
- **Generated with Connector SDK commit SHA:** b184da3e22ef8521d2eeebf3c96a0fe8da2424f5
- **Changelog:** [View changelog](https://github.com/airbytehq/airbyte-agent-connectors/blob/main/connectors/mailchimp/CHANGELOG.md)