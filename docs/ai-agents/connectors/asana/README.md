# Asana agent connector

Asana is a work management platform that helps teams organize, track, and manage
projects and tasks. This connector provides access to tasks, projects, workspaces,
teams, and users for project tracking, workload analysis, and productivity insights.


## Example questions

The Asana connector is optimized to handle prompts like these.

- What tasks are assigned to me this week?
- List all projects in my workspace
- Summarize my team's workload and task completion rates
- Show me the tasks for the \{project_name\} project
- Who are the team members in my \{team_name\} team?
- Find all tasks related to \{client_name\} across my workspaces
- Analyze the most active projects in my workspace last month
- Compare task completion rates between my different teams
- Identify overdue tasks across all my projects
- Show me details of my current workspace and its users

## Unsupported questions

The Asana connector isn't currently able to handle prompts like these.

- Create a new task for [TeamMember]
- Update the priority of this task
- Delete the project [ProjectName]
- Schedule a new team meeting
- Add a new team member to [Workspace]
- Move this task to another project

## Installation

```bash
uv pip install airbyte-agent-asana
```

## Usage

Connectors can run in open source or hosted mode.

### Open source

In open source mode, you provide API credentials directly to the connector.

```python
from airbyte_agent_asana import AsanaConnector
from airbyte_agent_asana.models import AsanaPersonalAccessTokenAuthConfig

connector = AsanaConnector(
    auth_config=AsanaPersonalAccessTokenAuthConfig(
        token="<Your Asana Personal Access Token. Generate one at https://app.asana.com/0/my-apps>"
    )
)

@agent.tool_plain # assumes you're using Pydantic AI
@AsanaConnector.tool_utils
async def asana_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

### Hosted

In hosted mode, API credentials are stored securely in Airbyte Cloud. You provide your Airbyte credentials instead. 

This example assumes you've already authenticated your connector with Airbyte. See [Authentication](AUTH.md) to learn more about authenticating. If you need a step-by-step guide, see the [hosted execution tutorial](https://docs.airbyte.com/ai-agents/quickstarts/tutorial-hosted).

```python
from airbyte_agent_asana import AsanaConnector

connector = AsanaConnector(
    external_user_id="<your_external_user_id>",
    airbyte_client_id="<your-client-id>",
    airbyte_client_secret="<your-client-secret>"
)

@agent.tool_plain # assumes you're using Pydantic AI
@AsanaConnector.tool_utils
async def asana_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

## Full documentation

### Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Tasks | [List](./REFERENCE.md#tasks-list), [Get](./REFERENCE.md#tasks-get) |
| Project Tasks | [List](./REFERENCE.md#project-tasks-list) |
| Workspace Task Search | [List](./REFERENCE.md#workspace-task-search-list) |
| Projects | [List](./REFERENCE.md#projects-list), [Get](./REFERENCE.md#projects-get) |
| Task Projects | [List](./REFERENCE.md#task-projects-list) |
| Team Projects | [List](./REFERENCE.md#team-projects-list) |
| Workspace Projects | [List](./REFERENCE.md#workspace-projects-list) |
| Workspaces | [List](./REFERENCE.md#workspaces-list), [Get](./REFERENCE.md#workspaces-get) |
| Users | [List](./REFERENCE.md#users-list), [Get](./REFERENCE.md#users-get) |
| Workspace Users | [List](./REFERENCE.md#workspace-users-list) |
| Team Users | [List](./REFERENCE.md#team-users-list) |
| Teams | [Get](./REFERENCE.md#teams-get) |
| Workspace Teams | [List](./REFERENCE.md#workspace-teams-list) |
| User Teams | [List](./REFERENCE.md#user-teams-list) |
| Attachments | [List](./REFERENCE.md#attachments-list), [Get](./REFERENCE.md#attachments-get), [Download](./REFERENCE.md#attachments-download) |
| Workspace Tags | [List](./REFERENCE.md#workspace-tags-list) |
| Tags | [Get](./REFERENCE.md#tags-get) |
| Project Sections | [List](./REFERENCE.md#project-sections-list) |
| Sections | [Get](./REFERENCE.md#sections-get) |
| Task Subtasks | [List](./REFERENCE.md#task-subtasks-list) |
| Task Dependencies | [List](./REFERENCE.md#task-dependencies-list) |
| Task Dependents | [List](./REFERENCE.md#task-dependents-list) |


### Authentication and configuration

For all authentication and configuration options, see the connector's [authentication documentation](AUTH.md).

### Asana API docs

See the official [Asana API reference](https://developers.asana.com/reference/rest-api-reference).

## Version information

- **Package version:** 0.19.76
- **Connector version:** 0.1.10
- **Generated with Connector SDK commit SHA:** b184da3e22ef8521d2eeebf3c96a0fe8da2424f5
- **Changelog:** [View changelog](https://github.com/airbytehq/airbyte-agent-connectors/blob/main/connectors/asana/CHANGELOG.md)