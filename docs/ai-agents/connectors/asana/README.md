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

This connector supports multiple authentication methods:

### OAuth 2

```python
from airbyte_agent_asana import AsanaConnector
from airbyte_agent_asana.models import AsanaOauth2AuthConfig

connector = AsanaConnector(
  auth_config=AsanaOauth2AuthConfig(
    access_token="...",
    refresh_token="...",
    client_id="...",
    client_secret="..."
  )
)
result = await connector.tasks.list()
```

### Personal Access Token

```python
from airbyte_agent_asana import AsanaConnector
from airbyte_agent_asana.models import AsanaPersonalAccessTokenAuthConfig

connector = AsanaConnector(
  auth_config=AsanaPersonalAccessTokenAuthConfig(
    token="..."
  )
)
result = await connector.tasks.list()
```


## Full documentation

This connector supports the following entities and actions.

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


For detailed documentation on available actions and parameters, see this connector's [full reference documentation](./REFERENCE.md).

For the service's official API docs, see the [Asana API reference](https://developers.asana.com/reference/rest-api-reference).

## Version information

- **Package version:** 0.19.31
- **Connector version:** 0.1.6
- **Generated with Connector SDK commit SHA:** d023e05f2b7a1ddabf81fab7640c64de1e0aa6a1