# Gitlab

The Gitlab agent connector is a Python package that equips AI agents to interact with Gitlab through strongly typed, well-documented tools. It's ready to use directly in your Python app, in an agent framework, or exposed through an MCP.

Connector for the GitLab REST API (v4). Provides access to projects, issues, merge requests, commits, pipelines, groups, branches, releases, tags, members, milestones, and users. Supports both Personal Access Token and OAuth2 authentication.


## Example questions

The Gitlab connector is optimized to handle prompts like these.

- List all projects I have access to
- Get the details of a specific project
- List all open issues in a project
- Show merge requests for a project
- List all groups I belong to
- Show recent commits in a project
- List pipelines for a project
- Show all branches in a project
- Find issues updated in the last week
- What are the most active projects?
- Show merge requests that are still open
- List projects with the most commits

## Unsupported questions

The Gitlab connector isn't currently able to handle prompts like these.

- Create a new project
- Delete an issue
- Merge a merge request
- Trigger a pipeline

## Installation

```bash
uv pip install airbyte-agent-gitlab
```

## Usage

Connectors can run in open source or hosted mode.

### Open source

In open source mode, you provide API credentials directly to the connector.

```python
from airbyte_agent_gitlab import GitlabConnector
from airbyte_agent_gitlab.models import GitlabPersonalAccessTokenAuthConfig

connector = GitlabConnector(
    auth_config=GitlabPersonalAccessTokenAuthConfig(
        access_token="<Log into your GitLab account and generate a personal access token.>"
    )
)

@agent.tool_plain # assumes you're using Pydantic AI
@GitlabConnector.tool_utils
async def gitlab_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

### Hosted

In hosted mode, API credentials are stored securely in Airbyte Cloud. You provide your Airbyte credentials instead. 
If your Airbyte client can access multiple organizations, also set `organization_id`.

This example assumes you've already authenticated your connector with Airbyte. See [Authentication](AUTH.md) to learn more about authenticating. If you need a step-by-step guide, see the [hosted execution tutorial](https://docs.airbyte.com/ai-agents/quickstarts/tutorial-hosted).

```python
from airbyte_agent_gitlab import GitlabConnector, AirbyteAuthConfig

connector = GitlabConnector(
    auth_config=AirbyteAuthConfig(
        customer_name="<your_customer_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

@agent.tool_plain # assumes you're using Pydantic AI
@GitlabConnector.tool_utils
async def gitlab_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

## Full documentation

### Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Projects | [List](./REFERENCE.md#projects-list), [Get](./REFERENCE.md#projects-get), [Search](./REFERENCE.md#projects-search) |
| Issues | [List](./REFERENCE.md#issues-list), [Get](./REFERENCE.md#issues-get), [Search](./REFERENCE.md#issues-search) |
| Merge Requests | [List](./REFERENCE.md#merge-requests-list), [Get](./REFERENCE.md#merge-requests-get), [Search](./REFERENCE.md#merge-requests-search) |
| Users | [List](./REFERENCE.md#users-list), [Get](./REFERENCE.md#users-get), [Search](./REFERENCE.md#users-search) |
| Commits | [List](./REFERENCE.md#commits-list), [Get](./REFERENCE.md#commits-get), [Search](./REFERENCE.md#commits-search) |
| Groups | [List](./REFERENCE.md#groups-list), [Get](./REFERENCE.md#groups-get), [Search](./REFERENCE.md#groups-search) |
| Branches | [List](./REFERENCE.md#branches-list), [Get](./REFERENCE.md#branches-get), [Search](./REFERENCE.md#branches-search) |
| Pipelines | [List](./REFERENCE.md#pipelines-list), [Get](./REFERENCE.md#pipelines-get), [Search](./REFERENCE.md#pipelines-search) |
| Group Members | [List](./REFERENCE.md#group-members-list), [Get](./REFERENCE.md#group-members-get), [Search](./REFERENCE.md#group-members-search) |
| Project Members | [List](./REFERENCE.md#project-members-list), [Get](./REFERENCE.md#project-members-get), [Search](./REFERENCE.md#project-members-search) |
| Releases | [List](./REFERENCE.md#releases-list), [Get](./REFERENCE.md#releases-get), [Search](./REFERENCE.md#releases-search) |
| Tags | [List](./REFERENCE.md#tags-list), [Get](./REFERENCE.md#tags-get), [Search](./REFERENCE.md#tags-search) |
| Group Milestones | [List](./REFERENCE.md#group-milestones-list), [Get](./REFERENCE.md#group-milestones-get), [Search](./REFERENCE.md#group-milestones-search) |
| Project Milestones | [List](./REFERENCE.md#project-milestones-list), [Get](./REFERENCE.md#project-milestones-get), [Search](./REFERENCE.md#project-milestones-search) |


### Authentication

For all authentication options, see the connector's [authentication documentation](AUTH.md).

### Gitlab API docs

See the official [Gitlab API reference](https://docs.gitlab.com/ee/api/rest/).

## Version information

- **Package version:** 0.1.9
- **Connector version:** 1.0.2
- **Generated with Connector SDK commit SHA:** 09ed4945e89bf743be8a0f0d596ae77c99526607
- **Changelog:** [View changelog](https://github.com/airbytehq/airbyte-agent-connectors/blob/main/connectors/gitlab/CHANGELOG.md)