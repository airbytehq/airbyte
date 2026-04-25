# Asana

The Asana agent connector is a Python package that equips AI agents to interact with Asana through strongly typed, well-documented tools. It's ready to use directly in your Python app, in an agent framework, or exposed through an MCP.

Asana is a work management platform that helps teams organize, track, and manage
projects and tasks. This connector provides access to tasks, projects, workspaces,
teams, and users for project tracking, workload analysis, and productivity insights.


## Example questions

The Asana connector is optimized to handle prompts like these.

- What tasks are assigned to me this week?
- List all projects in my workspace
- Show me the tasks for a recent project
- Who are the team members in one of my teams?
- Show me details of my current workspace and its users
- Create a new task called 'Review Q3 report' in my project
- Mark the task 'Submit proposal' as completed
- Update the due date of task X to next Friday
- Create a new project called 'Product Launch' in my workspace
- Add a comment on the task saying 'Looks good, approved!'
- Assign the task to me and set the due date to tomorrow
- Delete the project 'Old Campaign'
- Schedule a new team meeting as a task for next Tuesday
- Add a new team member to my workspace by email
- Delete the task 'Outdated draft'
- Summarize my team's workload and task completion rates
- Find all tasks related to \{client_name\} across my workspaces
- Analyze the most active projects in my workspace last month
- Compare task completion rates between my different teams
- Identify overdue tasks across all my projects
- Create a new section called 'In Review' in my project
- Move a task to the 'Done' section
- List all tasks in the 'To do' section
- Rename the 'Backlog' section to 'Icebox'
- Delete the empty 'Old Section' from the project
- Create a tag called 'Urgent' in my workspace
- Tag this task with 'Bug'
- Remove the 'Low Priority' tag from this task
- List all tasks tagged 'Release v2'
- Rename the tag 'WIP' to 'In Progress'
- Delete the tag 'Deprecated'

## Unsupported questions

The Asana connector isn't currently able to handle prompts like these.

- Move this task to another project

## Installation

```bash
uv pip install airbyte-agent-sdk
```

## Usage

Connectors can run in open source or hosted mode.

### Open source

In open source mode, you provide API credentials directly to the connector.

```python
from airbyte_agent_sdk.connectors.asana import AsanaConnector
from airbyte_agent_sdk.connectors.asana.models import AsanaPersonalAccessTokenAuthConfig

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
If your Airbyte client can access multiple organizations, also set `organization_id`.

This example assumes you've already authenticated your connector with Airbyte. See [Authentication](AUTH.md) to learn more about authenticating. If you need a step-by-step guide, see the [hosted execution tutorial](https://docs.airbyte.com/ai-agents/quickstarts/tutorial-hosted).

```python
from airbyte_agent_sdk.connectors.asana import AsanaConnector, AirbyteAuthConfig

connector = AsanaConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
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
| Tasks | [List](./REFERENCE.md#tasks-list), [Create](./REFERENCE.md#tasks-create), [Get](./REFERENCE.md#tasks-get), [Update](./REFERENCE.md#tasks-update), [Delete](./REFERENCE.md#tasks-delete), [Context Store Search](./REFERENCE.md#tasks-context-store-search) |
| Project Tasks | [List](./REFERENCE.md#project-tasks-list) |
| Workspace Task Search | [List](./REFERENCE.md#workspace-task-search-list) |
| Projects | [List](./REFERENCE.md#projects-list), [Create](./REFERENCE.md#projects-create), [Get](./REFERENCE.md#projects-get), [Update](./REFERENCE.md#projects-update), [Delete](./REFERENCE.md#projects-delete), [Context Store Search](./REFERENCE.md#projects-context-store-search) |
| Task Projects | [List](./REFERENCE.md#task-projects-list) |
| Team Projects | [List](./REFERENCE.md#team-projects-list) |
| Workspace Projects | [List](./REFERENCE.md#workspace-projects-list) |
| Workspaces | [List](./REFERENCE.md#workspaces-list), [Get](./REFERENCE.md#workspaces-get), [Context Store Search](./REFERENCE.md#workspaces-context-store-search) |
| Users | [List](./REFERENCE.md#users-list), [Get](./REFERENCE.md#users-get), [Context Store Search](./REFERENCE.md#users-context-store-search) |
| Workspace Users | [List](./REFERENCE.md#workspace-users-list) |
| Team Users | [List](./REFERENCE.md#team-users-list) |
| Teams | [Get](./REFERENCE.md#teams-get), [Context Store Search](./REFERENCE.md#teams-context-store-search) |
| Workspace Teams | [List](./REFERENCE.md#workspace-teams-list) |
| User Teams | [List](./REFERENCE.md#user-teams-list) |
| Attachments | [List](./REFERENCE.md#attachments-list), [Get](./REFERENCE.md#attachments-get), [Download](./REFERENCE.md#attachments-download), [Context Store Search](./REFERENCE.md#attachments-context-store-search) |
| Workspace Tags | [List](./REFERENCE.md#workspace-tags-list), [Create](./REFERENCE.md#workspace-tags-create) |
| Tags | [Get](./REFERENCE.md#tags-get), [Update](./REFERENCE.md#tags-update), [Delete](./REFERENCE.md#tags-delete), [Context Store Search](./REFERENCE.md#tags-context-store-search) |
| Tag Tasks | [List](./REFERENCE.md#tag-tasks-list) |
| Project Sections | [List](./REFERENCE.md#project-sections-list), [Create](./REFERENCE.md#project-sections-create) |
| Sections | [Get](./REFERENCE.md#sections-get), [Update](./REFERENCE.md#sections-update), [Delete](./REFERENCE.md#sections-delete), [Context Store Search](./REFERENCE.md#sections-context-store-search) |
| Section Tasks | [List](./REFERENCE.md#section-tasks-list), [Create](./REFERENCE.md#section-tasks-create) |
| Task Subtasks | [List](./REFERENCE.md#task-subtasks-list) |
| Task Dependencies | [List](./REFERENCE.md#task-dependencies-list) |
| Task Dependents | [List](./REFERENCE.md#task-dependents-list) |
| Task Stories | [Create](./REFERENCE.md#task-stories-create) |
| Task Tags | [Create](./REFERENCE.md#task-tags-create), [Delete](./REFERENCE.md#task-tags-delete) |
| Workspace Memberships | [Create](./REFERENCE.md#workspace-memberships-create) |


### Authentication

For all authentication options, see the connector's [authentication documentation](AUTH.md).

### Asana API docs

See the official [Asana API reference](https://developers.asana.com/reference/rest-api-reference).

## Version information

- **Package version:** 0.1.20
- **Connector version:** 0.1.20
- **Generated with Connector SDK commit SHA:** unknown