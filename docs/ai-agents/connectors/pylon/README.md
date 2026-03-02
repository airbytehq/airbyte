# Pylon

The Pylon agent connector is a Python package that equips AI agents to interact with Pylon through strongly typed, well-documented tools. It's ready to use directly in your Python app, in an agent framework, or exposed through an MCP.

Pylon is a customer support platform that helps B2B companies manage customer interactions
across Slack, email, chat widgets, and other channels. This connector provides access to
issues, accounts, contacts, teams, tags, users, custom fields, ticket forms, and user roles
for customer support analytics and account intelligence insights.


## Example questions

The Pylon connector is optimized to handle prompts like these.

- List all open issues in Pylon
- Show me all accounts in Pylon
- List all contacts in Pylon
- What teams are configured in my Pylon workspace?
- Show me all tags used in Pylon
- List all users in my Pylon account
- Show me the custom fields configured for issues
- List all ticket forms in Pylon
- What user roles are available in Pylon?
- Show me details for a specific issue
- Get details for a specific account
- Show me details for a specific contact
- What are the most common issue sources this month?
- Show me issues assigned to a specific team
- Which accounts have the most open issues?
- Analyze issue resolution times over the last 30 days
- List contacts associated with a specific account

## Unsupported questions

The Pylon connector isn't currently able to handle prompts like these.

- Delete an issue
- Delete an account
- Send a message to a customer
- Schedule a meeting with a contact

## Installation

```bash
uv pip install airbyte-agent-pylon
```

## Usage

Connectors can run in open source or hosted mode.

### Open source

In open source mode, you provide API credentials directly to the connector.

```python
from airbyte_agent_pylon import PylonConnector
from airbyte_agent_pylon.models import PylonAuthConfig

connector = PylonConnector(
    auth_config=PylonAuthConfig(
        api_token="<Your Pylon API token. Only admin users can create API tokens.>"
    )
)

@agent.tool_plain # assumes you're using Pydantic AI
@PylonConnector.tool_utils
async def pylon_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

### Hosted

In hosted mode, API credentials are stored securely in Airbyte Cloud. You provide your Airbyte credentials instead. 
If your Airbyte client can access multiple organizations, also set `organization_id`.

This example assumes you've already authenticated your connector with Airbyte. See [Authentication](AUTH.md) to learn more about authenticating. If you need a step-by-step guide, see the [hosted execution tutorial](https://docs.airbyte.com/ai-agents/quickstarts/tutorial-hosted).

```python
from airbyte_agent_pylon import PylonConnector, AirbyteAuthConfig

connector = PylonConnector(
    auth_config=AirbyteAuthConfig(
        customer_name="<your_customer_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

@agent.tool_plain # assumes you're using Pydantic AI
@PylonConnector.tool_utils
async def pylon_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

## Full documentation

### Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Issues | [List](./REFERENCE.md#issues-list), [Create](./REFERENCE.md#issues-create), [Get](./REFERENCE.md#issues-get), [Update](./REFERENCE.md#issues-update) |
| Messages | [List](./REFERENCE.md#messages-list) |
| Issue Notes | [Create](./REFERENCE.md#issue-notes-create) |
| Issue Threads | [Create](./REFERENCE.md#issue-threads-create) |
| Accounts | [List](./REFERENCE.md#accounts-list), [Create](./REFERENCE.md#accounts-create), [Get](./REFERENCE.md#accounts-get), [Update](./REFERENCE.md#accounts-update) |
| Contacts | [List](./REFERENCE.md#contacts-list), [Create](./REFERENCE.md#contacts-create), [Get](./REFERENCE.md#contacts-get), [Update](./REFERENCE.md#contacts-update) |
| Teams | [List](./REFERENCE.md#teams-list), [Create](./REFERENCE.md#teams-create), [Get](./REFERENCE.md#teams-get), [Update](./REFERENCE.md#teams-update) |
| Tags | [List](./REFERENCE.md#tags-list), [Create](./REFERENCE.md#tags-create), [Get](./REFERENCE.md#tags-get), [Update](./REFERENCE.md#tags-update) |
| Users | [List](./REFERENCE.md#users-list), [Get](./REFERENCE.md#users-get) |
| Custom Fields | [List](./REFERENCE.md#custom-fields-list), [Get](./REFERENCE.md#custom-fields-get) |
| Ticket Forms | [List](./REFERENCE.md#ticket-forms-list) |
| User Roles | [List](./REFERENCE.md#user-roles-list) |
| Tasks | [Create](./REFERENCE.md#tasks-create), [Update](./REFERENCE.md#tasks-update) |
| Projects | [Create](./REFERENCE.md#projects-create), [Update](./REFERENCE.md#projects-update) |
| Milestones | [Create](./REFERENCE.md#milestones-create), [Update](./REFERENCE.md#milestones-update) |
| Articles | [Create](./REFERENCE.md#articles-create), [Update](./REFERENCE.md#articles-update) |
| Collections | [Create](./REFERENCE.md#collections-create) |
| Me | [Get](./REFERENCE.md#me-get) |


### Authentication

For all authentication options, see the connector's [authentication documentation](AUTH.md).

### Pylon API docs

See the official [Pylon API reference](https://docs.usepylon.com/pylon-docs/developer/api/api-reference).

## Version information

- **Package version:** 0.1.7
- **Connector version:** 0.1.3
- **Generated with Connector SDK commit SHA:** a735c402798904c84a7f4df7969653341d95b11d
- **Changelog:** [View changelog](https://github.com/airbytehq/airbyte-agent-connectors/blob/main/connectors/pylon/CHANGELOG.md)