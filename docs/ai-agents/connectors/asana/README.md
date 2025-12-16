# Airbyte Asana AI Connector

Asana is a work management platform that helps teams organize, track, and manage
projects and tasks. This connector provides access to tasks, projects, workspaces,
teams, and users for project tracking, workload analysis, and productivity insights.


## Example Questions

- What tasks are assigned to me this week?
- List all projects in my workspace
- Summarize my team's workload and task completion rates
- Show me the tasks for the [ProjectName] project
- Who are the team members in my [TeamName] team?
- Find all tasks related to [ClientName] across my workspaces
- Analyze the most active projects in my workspace last month
- Compare task completion rates between my different teams
- Identify overdue tasks across all my projects
- Show me details of my current workspace and its users

## Unsupported Questions

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

```python
from airbyte_agent_asana import AsanaConnector, AsanaAuthConfig

connector = AsanaConnector(
  auth_config=AsanaAuthConfig(
    access_token="...",
    refresh_token="...",
    client_id="...",
    client_secret="..."
  )
)
result = connector.tasks.list()
```

## Documentation

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


For detailed documentation on available actions and parameters, see [REFERENCE.md](./REFERENCE.md).

For the service's official API docs, see [Asana API Reference](https://developers.asana.com/reference/rest-api-reference).

## Version Information

**Package Version:** 0.19.19

**Connector Version:** 0.1.4

**Generated with connector-sdk:** c4c39c2797ecd929407c9417c728d425f77b37ed