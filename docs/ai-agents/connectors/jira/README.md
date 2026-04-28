# Jira

The Jira agent connector is a Python package that equips AI agents to interact with Jira through strongly typed, well-documented tools. It's ready to use directly in your Python app, in an agent framework, or exposed through an MCP.

Connector for Jira API

## Example questions

The Jira connector is optimized to handle prompts like these.

- Show me all open issues in my Jira instance
- List recent issues created in the last 7 days
- List all projects in my Jira instance
- Show me details for the most recently updated issue
- List all users in my Jira instance
- Show me comments on the most recent issue
- Show me worklogs from the last 7 days
- Assign a recent issue to a teammate
- Unassign a recent issue
- Create a new task called 'Sample task' in a project
- Create a bug with high priority
- Update the summary of a recent issue to 'Updated summary'
- Change the priority of a recent issue to high
- Add a comment to a recent issue saying 'Please investigate'
- Update my most recent comment
- Delete a test issue
- Remove my most recent comment
- Transition \{issue_key\} to In Progress
- Move \{issue_key\} to Done
- What transitions are available for \{issue_key\}?
- Log 2 hours of work on \{issue_key\}
- Log 30 minutes on \{issue_key\} with a comment about what I did
- Link \{issue_key_1\} as blocking \{issue_key_2\}
- Create a 'relates to' link between \{issue_key_1\} and \{issue_key_2\}
- What issues are assigned to \{team_member\} this week?
- Find all high priority bugs in our current sprint
- Show me overdue issues across all projects
- What projects have the most issues?
- Search for users named \{user_name\}

## Unsupported questions

The Jira connector isn't currently able to handle prompts like these.

- Attach a file to \{issue_key\}
- Add a watcher to \{issue_key\}

## Installation

```bash
uv pip install airbyte-agent-sdk
```

## Usage

Connectors can run in open source or hosted mode.

### Open source

In open source mode, you provide API credentials directly to the connector.

```python
from airbyte_agent_sdk.connectors.jira import JiraConnector
from airbyte_agent_sdk.connectors.jira.models import JiraAuthConfig

connector = JiraConnector(
    auth_config=JiraAuthConfig(
        username="<Your Atlassian account email address>",
        password="<Your Jira API token from https://id.atlassian.com/manage-profile/security/api-tokens>"
    )
)

@agent.tool_plain # assumes you're using Pydantic AI
@JiraConnector.tool_utils
async def jira_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

### Hosted

In hosted mode, API credentials are stored securely in Airbyte Cloud. You provide your Airbyte credentials instead. 
If your Airbyte client can access multiple organizations, also set `organization_id`.

This example assumes you've already authenticated your connector with Airbyte. See [Authentication](AUTH.md) to learn more about authenticating. If you need a step-by-step guide, see the [hosted execution tutorial](https://docs.airbyte.com/ai-agents/quickstarts/tutorial-hosted).

The `connect()` factory returns a fully typed `JiraConnector` and reads `AIRBYTE_CLIENT_ID` / `AIRBYTE_CLIENT_SECRET` from the environment:

```python
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.jira import JiraConnector

connector = connect("jira", workspace_name="<your_workspace_name>")

@agent.tool_plain # assumes you're using Pydantic AI
@JiraConnector.tool_utils
async def jira_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

Or pass credentials explicitly (equivalent, useful when you're not loading them from the environment):

```python
from airbyte_agent_sdk.connectors.jira import JiraConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = JiraConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

@agent.tool_plain # assumes you're using Pydantic AI
@JiraConnector.tool_utils
async def jira_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

## Full documentation

### Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Issues | [API Search](./REFERENCE.md#issues-api_search), [Create](./REFERENCE.md#issues-create), [Get](./REFERENCE.md#issues-get), [Update](./REFERENCE.md#issues-update), [Delete](./REFERENCE.md#issues-delete), [Context Store Search](./REFERENCE.md#issues-context-store-search) |
| Projects | [API Search](./REFERENCE.md#projects-api_search), [Get](./REFERENCE.md#projects-get), [Context Store Search](./REFERENCE.md#projects-context-store-search) |
| Users | [Get](./REFERENCE.md#users-get), [List](./REFERENCE.md#users-list), [API Search](./REFERENCE.md#users-api_search), [Context Store Search](./REFERENCE.md#users-context-store-search) |
| Issue Fields | [List](./REFERENCE.md#issue-fields-list), [API Search](./REFERENCE.md#issue-fields-api_search), [Context Store Search](./REFERENCE.md#issue-fields-context-store-search) |
| Issue Comments | [List](./REFERENCE.md#issue-comments-list), [Create](./REFERENCE.md#issue-comments-create), [Get](./REFERENCE.md#issue-comments-get), [Update](./REFERENCE.md#issue-comments-update), [Delete](./REFERENCE.md#issue-comments-delete), [Context Store Search](./REFERENCE.md#issue-comments-context-store-search) |
| Issue Worklogs | [Get](./REFERENCE.md#issue-worklogs-get), [List](./REFERENCE.md#issue-worklogs-list), [Create](./REFERENCE.md#issue-worklogs-create), [Context Store Search](./REFERENCE.md#issue-worklogs-context-store-search) |
| Issues Assignee | [Update](./REFERENCE.md#issues-assignee-update) |
| Issue Transitions | [List](./REFERENCE.md#issue-transitions-list), [Create](./REFERENCE.md#issue-transitions-create) |
| Issue Links | [Create](./REFERENCE.md#issue-links-create) |


### Authentication

For all authentication options, see the connector's [authentication documentation](AUTH.md).

### Jira API docs

See the official [Jira API reference](https://developer.atlassian.com/cloud/jira/platform/rest/v3/intro/).

## Version information

- **Package version:** 1.1.9
- **Connector version:** 1.1.9
- **Generated with Connector SDK commit SHA:** unknown