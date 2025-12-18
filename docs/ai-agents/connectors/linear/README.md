# Linear agent connector

Linear is a modern issue tracking and project management tool built for software
development teams. This connector provides access to issues, projects, and teams
for sprint planning, backlog management, and development workflow analysis.


## Example questions

- Show me the open issues assigned to my team this week
- List out all projects I'm currently involved in
- Analyze the workload distribution across my development team
- What are the top priority issues in our current sprint?
- Identify the most active projects in our organization right now
- Summarize the recent issues for [teamMember] in the last two weeks
- Compare the issue complexity across different teams
- Which projects have the most unresolved issues?
- Give me an overview of my team's current project backlog

## Unsupported questions

- Create a new issue for the backend team
- Update the priority of this specific issue
- Assign a team member to this project
- Delete an outdated project from our workspace
- Schedule a sprint planning meeting
- Move an issue to a different project

## Installation

```bash
uv pip install airbyte-agent-linear
```

## Usage

```python
from airbyte_agent_linear import LinearConnector, LinearAuthConfig

connector = LinearConnector(
  auth_config=LinearAuthConfig(
    api_key="..."
  )
)
result = await connector.issues.list()
```

## Full documentation

This connector supports the following entities and actions.

| Entity | Actions |
|--------|---------|
| Issues | [List](./REFERENCE.md#issues-list), [Get](./REFERENCE.md#issues-get) |
| Projects | [List](./REFERENCE.md#projects-list), [Get](./REFERENCE.md#projects-get) |
| Teams | [List](./REFERENCE.md#teams-list), [Get](./REFERENCE.md#teams-get) |


For detailed documentation on available actions and parameters, see this connector's [full reference documentation](./REFERENCE.md).

For the service's official API docs, see the [Linear API reference](https://linear.app/developers/graphql).

## Version information

- **Package version:** 0.19.20
- **Connector version:** 0.1.1
- **Generated with Connector SDK commit SHA:** f7c55d3e3cdc7568cab2da9d736285eec58f044b