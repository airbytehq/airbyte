# Clickup-Api

The Clickup-Api agent connector is a Python package that equips AI agents to interact with Clickup-Api through strongly typed, well-documented tools. It's ready to use directly in your Python app, in an agent framework, or exposed through an MCP.

ClickUp is a productivity platform that provides project management, task tracking, docs, goals,
and time tracking for teams. This connector provides access to workspaces, spaces, folders, lists,
tasks (including workspace-wide search), comments, goals, views, time tracking, members, and docs.


## Example questions

The Clickup-Api connector is optimized to handle prompts like these.

- List all workspaces I have access to
- Show me the spaces in my workspace
- List the folders in a space
- Show me the lists in a folder
- Get the tasks in a list
- Get details for a specific task
- Search for tasks containing 'bug' across my workspace
- Find all urgent priority tasks in my workspace
- Show me tasks assigned to a specific user
- List comments on a task
- Get threaded replies on a comment
- Create a comment on a task
- Update a comment to mark it resolved
- List all goals in my workspace
- Get details for a specific goal
- Show me all workspace-level views
- Get tasks matching a saved view
- List time entries for my workspace this week
- Get details for a specific time entry
- Show me the members assigned to a task
- List all docs in my workspace
- Get details for a specific doc
- What tasks are overdue in my workspace?
- Which tasks were updated in the last 24 hours?
- Show me all high-priority tasks across all projects
- How much time has been tracked this week?
- What are the most commented tasks?

## Unsupported questions

The Clickup-Api connector isn't currently able to handle prompts like these.

- Delete a task
- Delete a comment
- Delete a goal

## Installation

```bash
uv pip install airbyte-agent-clickup-api
```

## Usage

Connectors can run in open source or hosted mode.

### Open source

In open source mode, you provide API credentials directly to the connector.

```python
from airbyte_agent_clickup_api import ClickupApiConnector
from airbyte_agent_clickup_api.models import ClickupApiAuthConfig

connector = ClickupApiConnector(
    auth_config=ClickupApiAuthConfig(
        api_key="<Your ClickUp personal API token>"
    )
)

@agent.tool_plain # assumes you're using Pydantic AI
@ClickupApiConnector.tool_utils
async def clickup_api_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

### Hosted

In hosted mode, API credentials are stored securely in Airbyte Cloud. You provide your Airbyte credentials instead. 
If your Airbyte client can access multiple organizations, also set `organization_id`.

This example assumes you've already authenticated your connector with Airbyte. See [Authentication](AUTH.md) to learn more about authenticating. If you need a step-by-step guide, see the [hosted execution tutorial](https://docs.airbyte.com/ai-agents/quickstarts/tutorial-hosted).

```python
from airbyte_agent_clickup_api import ClickupApiConnector, AirbyteAuthConfig

connector = ClickupApiConnector(
    auth_config=AirbyteAuthConfig(
        customer_name="<your_customer_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

@agent.tool_plain # assumes you're using Pydantic AI
@ClickupApiConnector.tool_utils
async def clickup_api_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

## Full documentation

### Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| User | [Get](./REFERENCE.md#user-get) |
| Teams | [List](./REFERENCE.md#teams-list) |
| Spaces | [List](./REFERENCE.md#spaces-list), [Get](./REFERENCE.md#spaces-get) |
| Folders | [List](./REFERENCE.md#folders-list), [Get](./REFERENCE.md#folders-get) |
| Lists | [List](./REFERENCE.md#lists-list), [Get](./REFERENCE.md#lists-get) |
| Tasks | [List](./REFERENCE.md#tasks-list), [Get](./REFERENCE.md#tasks-get), [API Search](./REFERENCE.md#tasks-api_search) |
| Comments | [List](./REFERENCE.md#comments-list), [Create](./REFERENCE.md#comments-create), [Get](./REFERENCE.md#comments-get), [Update](./REFERENCE.md#comments-update) |
| Goals | [List](./REFERENCE.md#goals-list), [Get](./REFERENCE.md#goals-get) |
| Views | [List](./REFERENCE.md#views-list), [Get](./REFERENCE.md#views-get) |
| View Tasks | [List](./REFERENCE.md#view-tasks-list) |
| Time Tracking | [List](./REFERENCE.md#time-tracking-list), [Get](./REFERENCE.md#time-tracking-get) |
| Members | [List](./REFERENCE.md#members-list) |
| Docs | [List](./REFERENCE.md#docs-list), [Get](./REFERENCE.md#docs-get) |


### Authentication

For all authentication options, see the connector's [authentication documentation](AUTH.md).

### Clickup-Api API docs

See the official [Clickup-Api API reference](https://developer.clickup.com/reference).

## Version information

- **Package version:** 0.1.9
- **Connector version:** 0.1.3
- **Generated with Connector SDK commit SHA:** 09ed4945e89bf743be8a0f0d596ae77c99526607
- **Changelog:** [View changelog](https://github.com/airbytehq/airbyte-agent-connectors/blob/main/connectors/clickup-api/CHANGELOG.md)