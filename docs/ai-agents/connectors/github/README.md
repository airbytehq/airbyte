# Github agent connector

GitHub is a platform for version control and collaborative software development
using Git. This connector provides access to repositories, branches, commits, issues,
pull requests, reviews, comments, releases, organizations, teams, and users for
development workflow analysis and project management insights.


## Example questions

The Github connector is optimized to handle prompts like these.

- Show me all open issues in my repositories this month
- List the top 5 repositories I've starred recently
- Analyze the commit trends in my main project over the last quarter
- Find all pull requests created by \{team_member\} in the past two weeks
- Search for repositories related to machine learning in my organizations
- Compare the number of contributors across my different team projects
- Identify the most active branches in my main repository
- Get details about the most recent releases in my organization
- List all milestones for our current development sprint
- Show me insights about pull request review patterns in our team

## Unsupported questions

The Github connector isn't currently able to handle prompts like these.

- Create a new issue in the project repository
- Update the status of this pull request
- Delete an old branch from the repository
- Schedule a team review for this code
- Assign a new label to this issue

## Installation

```bash
uv pip install airbyte-agent-github
```

## Usage

This connector supports multiple authentication methods:

### OAuth 2

```python
from airbyte_agent_github import GithubConnector
from airbyte_agent_github.models import GithubOauth2AuthConfig

connector = GithubConnector(
  auth_config=GithubOauth2AuthConfig(
    access_token="..."
  )
)
result = await connector.repositories.get()
```

### Personal Access Token

```python
from airbyte_agent_github import GithubConnector
from airbyte_agent_github.models import GithubPersonalAccessTokenAuthConfig

connector = GithubConnector(
  auth_config=GithubPersonalAccessTokenAuthConfig(
    token="..."
  )
)
result = await connector.repositories.get()
```


## Full documentation

This connector supports the following entities and actions.

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
| Projects | [List](./REFERENCE.md#projects-list), [Get](./REFERENCE.md#projects-get) |
| Project Items | [List](./REFERENCE.md#project-items-list) |


For detailed documentation on available actions and parameters, see this connector's [full reference documentation](./REFERENCE.md).

For the service's official API docs, see the [Github API reference](https://docs.github.com/en/rest).

## Version information

- **Package version:** 0.18.33
- **Connector version:** 0.1.7
- **Generated with Connector SDK commit SHA:** d023e05f2b7a1ddabf81fab7640c64de1e0aa6a1