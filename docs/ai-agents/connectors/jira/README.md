# Jira agent connector

Connector for Jira API

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

- **Package version:** 0.1.11
- **Connector version:** 1.0.2
- **Generated with Connector SDK commit SHA:** f7c55d3e3cdc7568cab2da9d736285eec58f044b