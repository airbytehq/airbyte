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

Connectors can run in open source or hosted mode.

### Open source

In open source mode, you provide API credentials directly to the connector.

```python
from airbyte_agent_github import GithubConnector
from airbyte_agent_github.models import GithubPersonalAccessTokenAuthConfig

connector = GithubConnector(
    auth_config=GithubPersonalAccessTokenAuthConfig(
        token="<GitHub personal access token (fine-grained or classic)>"
    )
)

@agent.tool_plain # assumes you're using Pydantic AI
@GithubConnector.tool_utils
async def github_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

### Hosted

In hosted mode, API credentials are stored securely in Airbyte Cloud. You provide your Airbyte credentials instead. 

This example assumes you've already authenticated your connector with Airbyte. See [Authentication](AUTH.md) to learn more about authenticating. If you need a step-by-step guide, see the [hosted execution tutorial](https://docs.airbyte.com/ai-agents/quickstarts/tutorial-hosted).

```python
from airbyte_agent_github import GithubConnector

connector = GithubConnector(
    external_user_id="<your_external_user_id>",
    airbyte_client_id="<your-client-id>",
    airbyte_client_secret="<your-client-secret>"
)

@agent.tool_plain # assumes you're using Pydantic AI
@GithubConnector.tool_utils
async def github_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

## Full documentation

### Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Repositories | [Get](./REFERENCE.md#repositories-get), [List](./REFERENCE.md#repositories-list), [API Search](./REFERENCE.md#repositories-api_search) |
| Org Repositories | [List](./REFERENCE.md#org-repositories-list) |
| Branches | [List](./REFERENCE.md#branches-list), [Get](./REFERENCE.md#branches-get) |
| Commits | [List](./REFERENCE.md#commits-list), [Get](./REFERENCE.md#commits-get) |
| Releases | [List](./REFERENCE.md#releases-list), [Get](./REFERENCE.md#releases-get) |
| Issues | [List](./REFERENCE.md#issues-list), [Get](./REFERENCE.md#issues-get), [API Search](./REFERENCE.md#issues-api_search) |
| Pull Requests | [List](./REFERENCE.md#pull-requests-list), [Get](./REFERENCE.md#pull-requests-get), [API Search](./REFERENCE.md#pull-requests-api_search) |
| Reviews | [List](./REFERENCE.md#reviews-list) |
| Comments | [List](./REFERENCE.md#comments-list), [Get](./REFERENCE.md#comments-get) |
| Pr Comments | [List](./REFERENCE.md#pr-comments-list), [Get](./REFERENCE.md#pr-comments-get) |
| Labels | [List](./REFERENCE.md#labels-list), [Get](./REFERENCE.md#labels-get) |
| Milestones | [List](./REFERENCE.md#milestones-list), [Get](./REFERENCE.md#milestones-get) |
| Organizations | [Get](./REFERENCE.md#organizations-get), [List](./REFERENCE.md#organizations-list) |
| Users | [Get](./REFERENCE.md#users-get), [List](./REFERENCE.md#users-list), [API Search](./REFERENCE.md#users-api_search) |
| Teams | [List](./REFERENCE.md#teams-list), [Get](./REFERENCE.md#teams-get) |
| Tags | [List](./REFERENCE.md#tags-list), [Get](./REFERENCE.md#tags-get) |
| Stargazers | [List](./REFERENCE.md#stargazers-list) |
| Viewer | [Get](./REFERENCE.md#viewer-get) |
| Viewer Repositories | [List](./REFERENCE.md#viewer-repositories-list) |
| Projects | [List](./REFERENCE.md#projects-list), [Get](./REFERENCE.md#projects-get) |
| Project Items | [List](./REFERENCE.md#project-items-list) |


### Authentication and configuration

For all authentication and configuration options, see the connector's [authentication documentation](AUTH.md).

### Github API docs

See the official [Github API reference](https://docs.github.com/en/rest).

## Version information

- **Package version:** 0.18.76
- **Connector version:** 0.1.9
- **Generated with Connector SDK commit SHA:** b184da3e22ef8521d2eeebf3c96a0fe8da2424f5
- **Changelog:** [View changelog](https://github.com/airbytehq/airbyte-agent-connectors/blob/main/connectors/github/CHANGELOG.md)