# Monday

The Monday agent connector is a Python package that equips AI agents to interact with Monday through strongly typed, well-documented tools. It's ready to use directly in your Python app, in an agent framework, or exposed through an MCP.

Connector for the Monday.com platform API. Monday.com is a work operating system that enables teams to build workflows for project management, CRM, software development, and more. This connector provides read access to boards, items, users, teams, tags, updates, workspaces, and activity logs via the Monday.com GraphQL API (v2).


## Example questions

The Monday connector is optimized to handle prompts like these.

- List all users in the Monday.com account
- Show me all boards
- Get the details of board 18395979459
- List all teams
- Show me all tags
- List recent updates
- Which boards were updated in the last week?
- Find all items assigned to a specific group
- What are the most active boards by update count?
- Show me all users who are admins
- List items with their column values from a specific board

## Unsupported questions

The Monday connector isn't currently able to handle prompts like these.

- Create a new board
- Delete an item
- Update a column value
- Add a new user to the account
- Create a webhook subscription

## Installation

```bash
uv pip install airbyte-agent-monday
```

## Usage

Connectors can run in open source or hosted mode.

### Open source

In open source mode, you provide API credentials directly to the connector.

```python
from airbyte_agent_monday import MondayConnector
from airbyte_agent_monday.models import MondayApiTokenAuthenticationAuthConfig

connector = MondayConnector(
    auth_config=MondayApiTokenAuthenticationAuthConfig(
        api_key="<Your Monday.com personal API token>"
    )
)

@agent.tool_plain # assumes you're using Pydantic AI
@MondayConnector.tool_utils
async def monday_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

### Hosted

In hosted mode, API credentials are stored securely in Airbyte Cloud. You provide your Airbyte credentials instead. 
If your Airbyte client can access multiple organizations, also set `organization_id`.

This example assumes you've already authenticated your connector with Airbyte. See [Authentication](AUTH.md) to learn more about authenticating. If you need a step-by-step guide, see the [hosted execution tutorial](https://docs.airbyte.com/ai-agents/quickstarts/tutorial-hosted).

```python
from airbyte_agent_monday import MondayConnector, AirbyteAuthConfig

connector = MondayConnector(
    auth_config=AirbyteAuthConfig(
        customer_name="<your_customer_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

@agent.tool_plain # assumes you're using Pydantic AI
@MondayConnector.tool_utils
async def monday_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

## Full documentation

### Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Users | [List](./REFERENCE.md#users-list), [Get](./REFERENCE.md#users-get), [Search](./REFERENCE.md#users-search) |
| Boards | [List](./REFERENCE.md#boards-list), [Get](./REFERENCE.md#boards-get), [Search](./REFERENCE.md#boards-search) |
| Items | [List](./REFERENCE.md#items-list), [Get](./REFERENCE.md#items-get), [Search](./REFERENCE.md#items-search) |
| Teams | [List](./REFERENCE.md#teams-list), [Get](./REFERENCE.md#teams-get), [Search](./REFERENCE.md#teams-search) |
| Tags | [List](./REFERENCE.md#tags-list), [Search](./REFERENCE.md#tags-search) |
| Updates | [List](./REFERENCE.md#updates-list), [Get](./REFERENCE.md#updates-get), [Search](./REFERENCE.md#updates-search) |
| Workspaces | [List](./REFERENCE.md#workspaces-list), [Get](./REFERENCE.md#workspaces-get), [Search](./REFERENCE.md#workspaces-search) |
| Activity Logs | [List](./REFERENCE.md#activity-logs-list), [Search](./REFERENCE.md#activity-logs-search) |


### Authentication

For all authentication options, see the connector's [authentication documentation](AUTH.md).

### Monday API docs

See the official [Monday API reference](https://developer.monday.com/api-reference/docs).

## Version information

- **Package version:** 0.1.3
- **Connector version:** 1.0.0
- **Generated with Connector SDK commit SHA:** a735c402798904c84a7f4df7969653341d95b11d
- **Changelog:** [View changelog](https://github.com/airbytehq/airbyte-agent-connectors/blob/main/connectors/monday/CHANGELOG.md)