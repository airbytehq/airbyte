# Sendgrid

The Sendgrid agent connector is a Python package that equips AI agents to interact with Sendgrid through strongly typed, well-documented tools. It's ready to use directly in your Python app, in an agent framework, or exposed through an MCP.

Connector for the Twilio SendGrid v3 API. Provides read access to marketing campaigns, contacts, lists, segments, single sends, transactional templates, and suppression management (bounces, blocks, spam reports, invalid emails, global suppressions, suppression groups, and suppression group members).


## Example questions

The Sendgrid connector is optimized to handle prompts like these.

- List all marketing contacts
- Get the details of a specific contact
- Show me all marketing lists
- List all transactional templates
- Show all single sends
- List all bounced emails
- Show all blocked email addresses
- List all spam reports
- Show all suppression groups
- How many contacts are in each marketing list?
- Which single sends were scheduled in the last month?
- What are the most common bounce reasons?
- Show me contacts created in the last 7 days

## Unsupported questions

The Sendgrid connector isn't currently able to handle prompts like these.

- Send an email
- Create a new contact
- Delete a bounce record
- Update a marketing list

## Installation

```bash
uv pip install airbyte-agent-sendgrid
```

## Usage

Connectors can run in open source or hosted mode.

### Open source

In open source mode, you provide API credentials directly to the connector.

```python
from airbyte_agent_sendgrid import SendgridConnector
from airbyte_agent_sendgrid.models import SendgridAuthConfig

connector = SendgridConnector(
    auth_config=SendgridAuthConfig(
        api_key="<Your SendGrid API key (generated at https://app.sendgrid.com/settings/api_keys)>"
    )
)

@agent.tool_plain # assumes you're using Pydantic AI
@SendgridConnector.tool_utils
async def sendgrid_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

### Hosted

In hosted mode, API credentials are stored securely in Airbyte Cloud. You provide your Airbyte credentials instead. 
If your Airbyte client can access multiple organizations, also set `organization_id`.

This example assumes you've already authenticated your connector with Airbyte. See [Authentication](AUTH.md) to learn more about authenticating. If you need a step-by-step guide, see the [hosted execution tutorial](https://docs.airbyte.com/ai-agents/quickstarts/tutorial-hosted).

```python
from airbyte_agent_sendgrid import SendgridConnector, AirbyteAuthConfig

connector = SendgridConnector(
    auth_config=AirbyteAuthConfig(
        customer_name="<your_customer_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

@agent.tool_plain # assumes you're using Pydantic AI
@SendgridConnector.tool_utils
async def sendgrid_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

## Full documentation

### Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Contacts | [List](./REFERENCE.md#contacts-list), [Get](./REFERENCE.md#contacts-get), [Search](./REFERENCE.md#contacts-search) |
| Lists | [List](./REFERENCE.md#lists-list), [Get](./REFERENCE.md#lists-get), [Search](./REFERENCE.md#lists-search) |
| Segments | [List](./REFERENCE.md#segments-list), [Get](./REFERENCE.md#segments-get), [Search](./REFERENCE.md#segments-search) |
| Campaigns | [List](./REFERENCE.md#campaigns-list), [Search](./REFERENCE.md#campaigns-search) |
| Singlesends | [List](./REFERENCE.md#singlesends-list), [Get](./REFERENCE.md#singlesends-get), [Search](./REFERENCE.md#singlesends-search) |
| Templates | [List](./REFERENCE.md#templates-list), [Get](./REFERENCE.md#templates-get), [Search](./REFERENCE.md#templates-search) |
| Singlesend Stats | [List](./REFERENCE.md#singlesend-stats-list), [Search](./REFERENCE.md#singlesend-stats-search) |
| Bounces | [List](./REFERENCE.md#bounces-list), [Search](./REFERENCE.md#bounces-search) |
| Blocks | [List](./REFERENCE.md#blocks-list), [Search](./REFERENCE.md#blocks-search) |
| Spam Reports | [List](./REFERENCE.md#spam-reports-list) |
| Invalid Emails | [List](./REFERENCE.md#invalid-emails-list), [Search](./REFERENCE.md#invalid-emails-search) |
| Global Suppressions | [List](./REFERENCE.md#global-suppressions-list), [Search](./REFERENCE.md#global-suppressions-search) |
| Suppression Groups | [List](./REFERENCE.md#suppression-groups-list), [Get](./REFERENCE.md#suppression-groups-get), [Search](./REFERENCE.md#suppression-groups-search) |
| Suppression Group Members | [List](./REFERENCE.md#suppression-group-members-list), [Search](./REFERENCE.md#suppression-group-members-search) |


### Authentication

For all authentication options, see the connector's [authentication documentation](AUTH.md).

### Sendgrid API docs

See the official [Sendgrid API reference](https://docs.sendgrid.com/api-reference).

## Version information

- **Package version:** 0.1.2
- **Connector version:** 1.0.1
- **Generated with Connector SDK commit SHA:** 39690c8e4097a393e4f6a8df586af5002bc93095
- **Changelog:** [View changelog](https://github.com/airbytehq/airbyte-agent-connectors/blob/main/connectors/sendgrid/CHANGELOG.md)