# Jira agent connector

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
- What issues are assigned to \{team_member\} this week?
- Find all high priority bugs in our current sprint
- Show me overdue issues across all projects
- What projects have the most issues?
- Search for users named \{user_name\}

## Unsupported questions

The Jira connector isn't currently able to handle prompts like these.

- Log time on \{issue_key\}
- Transition \{issue_key\} to Done

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
@JiraConnector.tool_utils
async def jira_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

### Hosted

In hosted mode, API credentials are stored securely in Airbyte Cloud. You provide your Airbyte credentials instead. 

This example assumes you've already authenticated your connector with Airbyte. See [Authentication](AUTH.md) to learn more about authenticating. If you need a step-by-step guide, see the [hosted execution tutorial](https://docs.airbyte.com/ai-agents/quickstarts/tutorial-hosted).

```python
from airbyte_agent_jira import JiraConnector, AirbyteAuthConfig

connector = JiraConnector(
    auth_config=AirbyteAuthConfig(
        external_user_id="<your_external_user_id>",
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
| Issues | [API Search](./REFERENCE.md#issues-api_search), [Create](./REFERENCE.md#issues-create), [Get](./REFERENCE.md#issues-get), [Update](./REFERENCE.md#issues-update), [Delete](./REFERENCE.md#issues-delete) |
| Projects | [API Search](./REFERENCE.md#projects-api_search), [Get](./REFERENCE.md#projects-get) |
| Users | [Get](./REFERENCE.md#users-get), [List](./REFERENCE.md#users-list), [API Search](./REFERENCE.md#users-api_search) |
| Issue Fields | [List](./REFERENCE.md#issue-fields-list), [API Search](./REFERENCE.md#issue-fields-api_search) |
| Issue Comments | [List](./REFERENCE.md#issue-comments-list), [Create](./REFERENCE.md#issue-comments-create), [Get](./REFERENCE.md#issue-comments-get), [Update](./REFERENCE.md#issue-comments-update), [Delete](./REFERENCE.md#issue-comments-delete) |
| Issue Worklogs | [List](./REFERENCE.md#issue-worklogs-list), [Get](./REFERENCE.md#issue-worklogs-get) |
| Issues Assignee | [Update](./REFERENCE.md#issues-assignee-update) |


### Authentication and configuration

For all authentication and configuration options, see the connector's [authentication documentation](AUTH.md).

### Jira API docs

See the official [Jira API reference](https://developer.atlassian.com/cloud/jira/platform/rest/v3/intro/).

## Version information

- **Package version:** 0.1.83
- **Connector version:** 1.1.5
- **Generated with Connector SDK commit SHA:** cddf6b9fb41e981bb489b71675cc4a9059e55608
- **Changelog:** [View changelog](https://github.com/airbytehq/airbyte-agent-connectors/blob/main/connectors/jira/CHANGELOG.md)