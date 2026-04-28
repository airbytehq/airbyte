# Linear

The Linear agent connector is a Python package that equips AI agents to interact with Linear through strongly typed, well-documented tools. It's ready to use directly in your Python app, in an agent framework, or exposed through an MCP.

Linear is a modern issue tracking and project management tool built for software
development teams. This connector provides access to issues, projects, and teams
for sprint planning, backlog management, and development workflow analysis.


## Example questions

The Linear connector is optimized to handle prompts like these.

- Show me the open issues assigned to my team this week
- List out all projects I'm currently involved in
- List all users in my Linear workspace
- Who is assigned to the most recently updated issue?
- Create a new issue titled 'Fix login bug'
- Update the priority of a recent issue to urgent
- Change the title of a recent issue to 'Updated feature request'
- Add a comment to a recent issue saying 'This is ready for review'
- Update my most recent comment to say 'Revised feedback after testing'
- Create a high priority issue about API performance
- Assign a recent issue to a teammate
- Unassign the current assignee from a recent issue
- Reassign a recent issue from one teammate to another
- Create a new issue in the 'Backend Improvements' project
- Add a recent issue to a specific project
- Move an issue to a different project
- Create a new project called 'Q3 Platform Migration'
- Update the description of the 'Backend Improvements' project
- Change the target date of a project to next month
- Mark a project as started
- Set a project lead for the 'API Redesign' project
- Analyze the workload distribution across my development team
- What are the top priority issues in our current sprint?
- Identify the most active projects in our organization right now
- Summarize the recent issues for \{team_member\} in the last two weeks
- Compare the issue complexity across different teams
- Which projects have the most unresolved issues?
- Give me an overview of my team's current project backlog

## Unsupported questions

The Linear connector isn't currently able to handle prompts like these.

- Delete an outdated project from our workspace
- Schedule a sprint planning meeting
- Delete this issue
- Remove a comment from an issue

## Installation

```bash
uv pip install airbyte-agent-sdk
```

## Usage

Connectors can run in open source or hosted mode.

### Open source

In open source mode, you provide API credentials directly to the connector.

```python
from airbyte_agent_sdk.connectors.linear import LinearConnector
from airbyte_agent_sdk.connectors.linear.models import LinearAuthConfig

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
If your Airbyte client can access multiple organizations, also set `organization_id`.

This example assumes you've already authenticated your connector with Airbyte. See [Authentication](AUTH.md) to learn more about authenticating. If you need a step-by-step guide, see the [hosted execution tutorial](https://docs.airbyte.com/ai-agents/quickstarts/tutorial-hosted).

The `connect()` factory returns a fully typed `LinearConnector` and reads `AIRBYTE_CLIENT_ID` / `AIRBYTE_CLIENT_SECRET` from the environment:

```python
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.linear import LinearConnector

connector = connect("linear", workspace_name="<your_workspace_name>")

@agent.tool_plain # assumes you're using Pydantic AI
@LinearConnector.tool_utils
async def linear_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

Or pass credentials explicitly (equivalent, useful when you're not loading them from the environment):

```python
from airbyte_agent_sdk.connectors.linear import LinearConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = LinearConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

@agent.tool_plain # assumes you're using Pydantic AI
@LinearConnector.tool_utils
async def linear_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

## Full documentation

### Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Issues | [List](./REFERENCE.md#issues-list), [Get](./REFERENCE.md#issues-get), [Create](./REFERENCE.md#issues-create), [Update](./REFERENCE.md#issues-update), [Context Store Search](./REFERENCE.md#issues-context-store-search) |
| Projects | [List](./REFERENCE.md#projects-list), [Get](./REFERENCE.md#projects-get), [Create](./REFERENCE.md#projects-create), [Update](./REFERENCE.md#projects-update), [Context Store Search](./REFERENCE.md#projects-context-store-search) |
| Teams | [List](./REFERENCE.md#teams-list), [Get](./REFERENCE.md#teams-get), [Context Store Search](./REFERENCE.md#teams-context-store-search) |
| Workflow States | [List](./REFERENCE.md#workflow-states-list), [Context Store Search](./REFERENCE.md#workflow-states-context-store-search) |
| Users | [List](./REFERENCE.md#users-list), [Get](./REFERENCE.md#users-get), [Context Store Search](./REFERENCE.md#users-context-store-search) |
| Comments | [List](./REFERENCE.md#comments-list), [Get](./REFERENCE.md#comments-get), [Create](./REFERENCE.md#comments-create), [Update](./REFERENCE.md#comments-update), [Context Store Search](./REFERENCE.md#comments-context-store-search) |


### Authentication

For all authentication options, see the connector's [authentication documentation](AUTH.md).

### Linear API docs

See the official [Linear API reference](https://linear.app/developers/graphql).

## Version information

- **Package version:** 0.1.19
- **Connector version:** 0.1.19
- **Generated with Connector SDK commit SHA:** unknown