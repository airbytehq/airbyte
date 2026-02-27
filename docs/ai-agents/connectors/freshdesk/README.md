# Freshdesk

The Freshdesk agent connector is a Python package that equips AI agents to interact with Freshdesk through strongly typed, well-documented tools. It's ready to use directly in your Python app, in an agent framework, or exposed through an MCP.

Connector for the Freshdesk customer support platform API (v2). Provides read access to helpdesk data including tickets, contacts, agents, groups, companies, roles, satisfaction ratings, surveys, time entries, and ticket fields. Freshdesk is a cloud-based customer support solution that enables companies to manage customer conversations across email, phone, chat, and social media.


## Example questions

The Freshdesk connector is optimized to handle prompts like these.

- List all open tickets in Freshdesk
- Show me all agents in the support team
- List all groups configured in Freshdesk
- Get the details of ticket #26
- Show me all companies in Freshdesk
- List all roles defined in the helpdesk
- Show me the ticket fields and their options
- List time entries for tickets
- What are the high priority tickets from last week?
- Which tickets have breached their SLA due date?
- Show me tickets assigned to agent \{agent_name\}
- Find all tickets from company \{company_name\}
- How many tickets were created this month by status?
- What are the satisfaction ratings for resolved tickets?

## Unsupported questions

The Freshdesk connector isn't currently able to handle prompts like these.

- Create a new ticket in Freshdesk
- Update the status of ticket #\{ticket_id\}
- Delete a contact from Freshdesk
- Assign a ticket to a different agent

## Installation

```bash
uv pip install airbyte-agent-freshdesk
```

## Usage

Connectors can run in open source or hosted mode.

### Open source

In open source mode, you provide API credentials directly to the connector.

```python
from airbyte_agent_freshdesk import FreshdeskConnector
from airbyte_agent_freshdesk.models import FreshdeskAuthConfig

connector = FreshdeskConnector(
    auth_config=FreshdeskAuthConfig(
        api_key="<Your Freshdesk API key (found in Profile Settings)>"
    )
)

@agent.tool_plain # assumes you're using Pydantic AI
@FreshdeskConnector.tool_utils
async def freshdesk_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

### Hosted

In hosted mode, API credentials are stored securely in Airbyte Cloud. You provide your Airbyte credentials instead. 
If your Airbyte client can access multiple organizations, also set `organization_id`.

This example assumes you've already authenticated your connector with Airbyte. See [Authentication](AUTH.md) to learn more about authenticating. If you need a step-by-step guide, see the [hosted execution tutorial](https://docs.airbyte.com/ai-agents/quickstarts/tutorial-hosted).

```python
from airbyte_agent_freshdesk import FreshdeskConnector, AirbyteAuthConfig

connector = FreshdeskConnector(
    auth_config=AirbyteAuthConfig(
        customer_name="<your_customer_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

@agent.tool_plain # assumes you're using Pydantic AI
@FreshdeskConnector.tool_utils
async def freshdesk_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

## Full documentation

### Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Tickets | [List](./REFERENCE.md#tickets-list), [Get](./REFERENCE.md#tickets-get), [Search](./REFERENCE.md#tickets-search) |
| Contacts | [List](./REFERENCE.md#contacts-list), [Get](./REFERENCE.md#contacts-get) |
| Agents | [List](./REFERENCE.md#agents-list), [Get](./REFERENCE.md#agents-get), [Search](./REFERENCE.md#agents-search) |
| Groups | [List](./REFERENCE.md#groups-list), [Get](./REFERENCE.md#groups-get), [Search](./REFERENCE.md#groups-search) |
| Companies | [List](./REFERENCE.md#companies-list), [Get](./REFERENCE.md#companies-get) |
| Roles | [List](./REFERENCE.md#roles-list), [Get](./REFERENCE.md#roles-get) |
| Satisfaction Ratings | [List](./REFERENCE.md#satisfaction-ratings-list) |
| Surveys | [List](./REFERENCE.md#surveys-list) |
| Time Entries | [List](./REFERENCE.md#time-entries-list) |
| Ticket Fields | [List](./REFERENCE.md#ticket-fields-list) |


### Authentication

For all authentication options, see the connector's [authentication documentation](AUTH.md).

### Freshdesk API docs

See the official [Freshdesk API reference](https://developers.freshdesk.com/api/).

## Version information

- **Package version:** 0.1.6
- **Connector version:** 1.0.1
- **Generated with Connector SDK commit SHA:** 39690c8e4097a393e4f6a8df586af5002bc93095
- **Changelog:** [View changelog](https://github.com/airbytehq/airbyte-agent-connectors/blob/main/connectors/freshdesk/CHANGELOG.md)