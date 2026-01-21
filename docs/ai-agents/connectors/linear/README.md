# Linear agent connector

Linear is a modern issue tracking and project management tool built for software
development teams. This connector provides access to issues, projects, and teams
for sprint planning, backlog management, and development workflow analysis.


## Example questions

The Linear connector is optimized to handle prompts like these.

- Show me the open issues assigned to my team this week
- List out all projects I'm currently involved in
- Analyze the workload distribution across my development team
- What are the top priority issues in our current sprint?
- Identify the most active projects in our organization right now
- Summarize the recent issues for \{team_member\} in the last two weeks
- Compare the issue complexity across different teams
- Which projects have the most unresolved issues?
- Give me an overview of my team's current project backlog
- Create a new issue titled 'Fix login bug' for the Engineering team
- Update issue ABC-123 to set priority to urgent
- Change the title of issue XYZ-456 to 'Updated feature request'
- Add a comment to issue DEF-789 saying 'This is ready for review'
- Update my comment on issue to say 'Revised feedback after testing'
- Create a high priority issue for the backend team about the API performance

## Unsupported questions

The Linear connector isn't currently able to handle prompts like these.

- Delete an outdated project from our workspace
- Schedule a sprint planning meeting
- Delete this issue
- Remove a comment from an issue

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
| Issues | [List](./REFERENCE.md#issues-list), [Get](./REFERENCE.md#issues-get), [Create](./REFERENCE.md#issues-create), [Update](./REFERENCE.md#issues-update) |
| Projects | [List](./REFERENCE.md#projects-list), [Get](./REFERENCE.md#projects-get) |
| Teams | [List](./REFERENCE.md#teams-list), [Get](./REFERENCE.md#teams-get) |
| Comments | [List](./REFERENCE.md#comments-list), [Get](./REFERENCE.md#comments-get), [Create](./REFERENCE.md#comments-create), [Update](./REFERENCE.md#comments-update) |


For detailed documentation on available actions and parameters, see this connector's [full reference documentation](./REFERENCE.md).

For the service's official API docs, see the [Linear API reference](https://linear.app/developers/graphql).

## Version information

- **Package version:** 0.19.50
- **Connector version:** 0.1.4
- **Generated with Connector SDK commit SHA:** c7dab97573a377c99c730f5f0f2c02733d2b3161