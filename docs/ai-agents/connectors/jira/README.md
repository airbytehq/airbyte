# Jira agent connector

Connector for Jira API

## Example questions

The Jira connector is optimized to handle prompts like these.

- Show me all open issues in the \{project_key\} project
- What issues are assigned to \{team_member\} this week?
- Find all high priority bugs in our current sprint
- Get the details of issue \{issue_key\}
- List all issues created in the last 7 days
- Show me overdue issues across all projects
- List all projects in my Jira instance
- Get details of the \{project_key\} project
- What projects have the most issues?
- Who are all the users in my Jira instance?
- Search for users named \{user_name\}
- Get details of user \{team_member\}
- Show me all comments on issue \{issue_key\}
- How much time has been logged on issue \{issue_key\}?
- List all worklogs for \{issue_key\} this month

## Unsupported questions

The Jira connector isn't currently able to handle prompts like these.

- Create a new issue in \{project_key\}
- Update the status of \{issue_key\}
- Add a comment to \{issue_key\}
- Log time on \{issue_key\}
- Delete issue \{issue_key\}
- Assign \{issue_key\} to \{team_member\}

## Installation

```bash
uv pip install airbyte-agent-jira
```

## Usage

Connectors can run in open source or hosted mode.

### Open source

In open source mode, you provide API credentials directly to the connector.

```python
from airbyte_agent_jira import JiraConnector
from airbyte_agent_jira.models import JiraAuthConfig

connector = JiraConnector(
    auth_config=JiraAuthConfig(
        username="<Your Atlassian account email address>",
        password="<Your Jira API token from https://id.atlassian.com/manage-profile/security/api-tokens>"
    )
)

@agent.tool_plain # assumes you're using Pydantic AI
@JiraConnector.describe
async def jira_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

### Hosted

In hosted mode, API credentials are stored securely in Airbyte Cloud. You provide your Airbyte credentials instead. 

This example assumes you've already authenticated your connector with Airbyte. See [Authentication](AUTH.md) to learn more about authenticating. If you need a step-by-step guide, see the [hosted execution tutorial](https://docs.airbyte.com/ai-agents/quickstarts/tutorial-hosted).

```python
from airbyte_agent_jira import JiraConnector

connector = JiraConnector(
    external_user_id="<your-scoped-token>",
    airbyte_client_id="<your-client-id>",
    airbyte_client_secret="<your-client-secret>"
)

@agent.tool_plain # assumes you're using Pydantic AI
@JiraConnector.describe
async def jira_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

## Full documentation

This connector supports the following entities and actions.

| Entity | Actions |
|--------|---------|
| Issues | [Api_search](./REFERENCE.md#issues-api_search), [Get](./REFERENCE.md#issues-get) |
| Projects | [Api_search](./REFERENCE.md#projects-api_search), [Get](./REFERENCE.md#projects-get) |
| Users | [Get](./REFERENCE.md#users-get), [List](./REFERENCE.md#users-list), [Api_search](./REFERENCE.md#users-api_search) |
| Issue Fields | [List](./REFERENCE.md#issue-fields-list), [Api_search](./REFERENCE.md#issue-fields-api_search) |
| Issue Comments | [List](./REFERENCE.md#issue-comments-list), [Get](./REFERENCE.md#issue-comments-get) |
| Issue Worklogs | [List](./REFERENCE.md#issue-worklogs-list), [Get](./REFERENCE.md#issue-worklogs-get) |


For all authentication options, see the connector's [authentication documentation](AUTH.md).

For detailed documentation on available actions and parameters, see this connector's [full reference documentation](./REFERENCE.md).

For the service's official API docs, see the [Jira API reference](https://developer.atlassian.com/cloud/jira/platform/rest/v3/intro/).

## Version information

- **Package version:** 0.1.47
- **Connector version:** 1.0.6
- **Generated with Connector SDK commit SHA:** 49e6dfe93fc406c8d2ed525372608fa2766ebece