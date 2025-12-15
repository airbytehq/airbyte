# Airbyte Jira AI Connector

Connector for Jira API

## Installation

```bash
uv pip install airbyte-ai-jira
```

## Usage

```python
from airbyte_ai_jira import JiraConnector, JiraAuthConfig

connector = JiraConnector(
  auth_config=JiraAuthConfig(
    username="...",
    password="..."
  )
)
result = connector.issues.search()
```

## Documentation

| Entity | Actions |
|--------|---------|
| Issues | [Search](./REFERENCE.md#issues-search), [Get](./REFERENCE.md#issues-get) |
| Projects | [Search](./REFERENCE.md#projects-search), [Get](./REFERENCE.md#projects-get) |
| Users | [Get](./REFERENCE.md#users-get), [List](./REFERENCE.md#users-list), [Search](./REFERENCE.md#users-search) |
| Issue Fields | [List](./REFERENCE.md#issue-fields-list), [Search](./REFERENCE.md#issue-fields-search) |
| Issue Comments | [List](./REFERENCE.md#issue-comments-list), [Get](./REFERENCE.md#issue-comments-get) |
| Issue Worklogs | [List](./REFERENCE.md#issue-worklogs-list), [Get](./REFERENCE.md#issue-worklogs-get) |


For detailed documentation on available actions and parameters, see [REFERENCE.md](./REFERENCE.md).

For the service's official API docs, see [Jira API Reference](https://developer.atlassian.com/cloud/jira/platform/rest/v3/intro/).

## Version Information

**Package Version:** 0.1.6

**Connector Version:** 1.0.2

**Generated with connector-sdk:** 0bfa6500a4fcf1cba2cffcc4d7ec640a76bbc568