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

```python
from airbyte_agent_jira import JiraConnector, JiraAuthConfig

connector = JiraConnector(
  auth_config=JiraAuthConfig(
    username="...",
    password="..."
  )
)
result = await connector.issues.search()
```


## Full documentation

This connector supports the following entities and actions.

| Entity | Actions |
|--------|---------|
| Issues | [Search](./REFERENCE.md#issues-search), [Get](./REFERENCE.md#issues-get) |
| Projects | [Search](./REFERENCE.md#projects-search), [Get](./REFERENCE.md#projects-get) |
| Users | [Get](./REFERENCE.md#users-get), [List](./REFERENCE.md#users-list), [Search](./REFERENCE.md#users-search) |
| Issue Fields | [List](./REFERENCE.md#issue-fields-list), [Search](./REFERENCE.md#issue-fields-search) |
| Issue Comments | [List](./REFERENCE.md#issue-comments-list), [Get](./REFERENCE.md#issue-comments-get) |
| Issue Worklogs | [List](./REFERENCE.md#issue-worklogs-list), [Get](./REFERENCE.md#issue-worklogs-get) |


For detailed documentation on available actions and parameters, see this connector's [full reference documentation](./REFERENCE.md).

For the service's official API docs, see the [Jira API reference](https://developer.atlassian.com/cloud/jira/platform/rest/v3/intro/).

## Version information

- **Package version:** 0.1.19
- **Connector version:** 1.0.3
- **Generated with Connector SDK commit SHA:** d023e05f2b7a1ddabf81fab7640c64de1e0aa6a1