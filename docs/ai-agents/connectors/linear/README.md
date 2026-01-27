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
- List all users in my Linear workspace
- Assign John to issue ABC-123
- Unassign the current assignee from issue XYZ-456
- Who is assigned to issue DEF-789?
- Reassign issue ABC-123 from John to Jane

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

Connectors can run in open source or hosted mode.

### Open source

In open source mode, you provide API credentials directly to the connector.

```python
from airbyte_agent_linear import LinearConnector
from airbyte_agent_linear.models import LinearAuthConfig

connector = LinearConnector(
    auth_config=LinearAuthConfig(
        api_key="<Your Linear API key from Settings > API > Personal API keys>"
    )
)

@agent.tool_plain # assumes you're using Pydantic AI
@LinearConnector.tool_utils
async def linear_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

### Hosted

In hosted mode, API credentials are stored securely in Airbyte Cloud. You provide your Airbyte credentials instead. 

This example assumes you've already authenticated your connector with Airbyte. See [Authentication](AUTH.md) to learn more about authenticating. If you need a step-by-step guide, see the [hosted execution tutorial](https://docs.airbyte.com/ai-agents/quickstarts/tutorial-hosted).

```python
from airbyte_agent_linear import LinearConnector

connector = LinearConnector(
    external_user_id="<your-scoped-token>",
    airbyte_client_id="<your-client-id>",
    airbyte_client_secret="<your-client-secret>"
)

@agent.tool_plain # assumes you're using Pydantic AI
@LinearConnector.tool_utils
async def linear_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```


## Full documentation

This connector supports the following entities and actions.

| Entity | Actions |
|--------|---------|
| Issues | [List](./REFERENCE.md#issues-list), [Get](./REFERENCE.md#issues-get), [Create](./REFERENCE.md#issues-create), [Update](./REFERENCE.md#issues-update) |
| Projects | [List](./REFERENCE.md#projects-list), [Get](./REFERENCE.md#projects-get) |
| Teams | [List](./REFERENCE.md#teams-list), [Get](./REFERENCE.md#teams-get) |
| Users | [List](./REFERENCE.md#users-list), [Get](./REFERENCE.md#users-get) |
| Comments | [List](./REFERENCE.md#comments-list), [Get](./REFERENCE.md#comments-get), [Create](./REFERENCE.md#comments-create), [Update](./REFERENCE.md#comments-update) |


For all authentication options, see the connector's [authentication documentation](AUTH.md).

For detailed documentation on available actions and parameters, see this connector's [full reference documentation](./REFERENCE.md).

For the service's official API docs, see the [Linear API reference](https://linear.app/developers/graphql).

## Version information

- **Package version:** 0.19.59
- **Connector version:** 0.1.6
- **Generated with Connector SDK commit SHA:** 609c1d86c76b36ff699b57123a5a8c2050d958c3