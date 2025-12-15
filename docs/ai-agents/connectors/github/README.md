# Airbyte Github AI Connector

GitHub is a platform for version control and collaborative software development
using Git. This connector provides access to repositories, branches, commits, issues,
pull requests, reviews, comments, releases, organizations, teams, and users for
development workflow analysis and project management insights.


## Example Questions

- Show me all open issues in my repositories this month
- List the top 5 repositories I've starred recently
- Analyze the commit trends in my main project over the last quarter
- Find all pull requests created by [teamMember] in the past two weeks
- Search for repositories related to machine learning in my organizations
- Compare the number of contributors across my different team projects
- Identify the most active branches in my main repository
- Get details about the most recent releases in my organization
- List all milestones for our current development sprint
- Show me insights about pull request review patterns in our team

## Unsupported Questions

- Create a new issue in the project repository
- Update the status of this pull request
- Delete an old branch from the repository
- Schedule a team review for this code
- Assign a new label to this issue

## Installation

```bash
uv pip install airbyte-ai-github
```

## Usage

```python
from airbyte_ai_github import GithubConnector, GithubAuthConfig

connector = GithubConnector(
  auth_config=GithubAuthConfig(
    access_token="...",
    refresh_token="...",
    client_id="...",
    client_secret="..."
  )
)
result = connector.repositories.get()
```

## Documentation

| Entity | Actions |
|--------|---------|
| Repositories | [Get](./REFERENCE.md#repositories-get), [List](./REFERENCE.md#repositories-list), [Search](./REFERENCE.md#repositories-search) |
| Org Repositories | [List](./REFERENCE.md#org-repositories-list) |
| Branches | [List](./REFERENCE.md#branches-list), [Get](./REFERENCE.md#branches-get) |
| Commits | [List](./REFERENCE.md#commits-list), [Get](./REFERENCE.md#commits-get) |
| Releases | [List](./REFERENCE.md#releases-list), [Get](./REFERENCE.md#releases-get) |
| Issues | [List](./REFERENCE.md#issues-list), [Get](./REFERENCE.md#issues-get), [Search](./REFERENCE.md#issues-search) |
| Pull Requests | [List](./REFERENCE.md#pull-requests-list), [Get](./REFERENCE.md#pull-requests-get), [Search](./REFERENCE.md#pull-requests-search) |
| Reviews | [List](./REFERENCE.md#reviews-list) |
| Comments | [List](./REFERENCE.md#comments-list), [Get](./REFERENCE.md#comments-get) |
| Pr Comments | [List](./REFERENCE.md#pr-comments-list), [Get](./REFERENCE.md#pr-comments-get) |
| Labels | [List](./REFERENCE.md#labels-list), [Get](./REFERENCE.md#labels-get) |
| Milestones | [List](./REFERENCE.md#milestones-list), [Get](./REFERENCE.md#milestones-get) |
| Organizations | [Get](./REFERENCE.md#organizations-get), [List](./REFERENCE.md#organizations-list) |
| Users | [Get](./REFERENCE.md#users-get), [List](./REFERENCE.md#users-list), [Search](./REFERENCE.md#users-search) |
| Teams | [List](./REFERENCE.md#teams-list), [Get](./REFERENCE.md#teams-get) |
| Tags | [List](./REFERENCE.md#tags-list), [Get](./REFERENCE.md#tags-get) |
| Stargazers | [List](./REFERENCE.md#stargazers-list) |
| Viewer | [Get](./REFERENCE.md#viewer-get) |
| Viewer Repositories | [List](./REFERENCE.md#viewer-repositories-list) |


For detailed documentation on available actions and parameters, see [REFERENCE.md](./REFERENCE.md).

For the service's official API docs, see [Github API Reference](https://docs.github.com/en/rest).

## Version Information

**Package Version:** 0.18.10

**Connector Version:** 0.1.1

**Generated with connector-sdk:** 1ab72bd8e7249872a4cf66327dd1a0bf68905acb