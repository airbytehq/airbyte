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
uv pip install airbyte-agent-sdk
```

## Usage

Connectors can run in open source or hosted mode.

### Open source

In open source mode, you provide API credentials directly to the connector.

```python
from airbyte_agent_sdk.connectors.gitlab import GitlabConnector
from airbyte_agent_sdk.connectors.gitlab.models import GitlabPersonalAccessTokenAuthConfig

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
from airbyte_agent_sdk.connectors.gitlab import GitlabConnector, AirbyteAuthConfig

connector = GitlabConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
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
| Projects | [List](./REFERENCE.md#projects-list), [Get](./REFERENCE.md#projects-get), [Context Store Search](./REFERENCE.md#projects-context-store-search) |
| Issues | [List](./REFERENCE.md#issues-list), [Get](./REFERENCE.md#issues-get), [Context Store Search](./REFERENCE.md#issues-context-store-search) |
| Merge Requests | [List](./REFERENCE.md#merge-requests-list), [Get](./REFERENCE.md#merge-requests-get), [Context Store Search](./REFERENCE.md#merge-requests-context-store-search) |
| Users | [List](./REFERENCE.md#users-list), [Get](./REFERENCE.md#users-get), [Context Store Search](./REFERENCE.md#users-context-store-search) |
| Commits | [List](./REFERENCE.md#commits-list), [Get](./REFERENCE.md#commits-get), [Context Store Search](./REFERENCE.md#commits-context-store-search) |
| Groups | [List](./REFERENCE.md#groups-list), [Get](./REFERENCE.md#groups-get), [Context Store Search](./REFERENCE.md#groups-context-store-search) |
| Branches | [List](./REFERENCE.md#branches-list), [Get](./REFERENCE.md#branches-get), [Context Store Search](./REFERENCE.md#branches-context-store-search) |
| Pipelines | [List](./REFERENCE.md#pipelines-list), [Get](./REFERENCE.md#pipelines-get), [Context Store Search](./REFERENCE.md#pipelines-context-store-search) |
| Group Members | [List](./REFERENCE.md#group-members-list), [Get](./REFERENCE.md#group-members-get), [Context Store Search](./REFERENCE.md#group-members-context-store-search) |
| Project Members | [List](./REFERENCE.md#project-members-list), [Get](./REFERENCE.md#project-members-get), [Context Store Search](./REFERENCE.md#project-members-context-store-search) |
| Releases | [List](./REFERENCE.md#releases-list), [Get](./REFERENCE.md#releases-get), [Context Store Search](./REFERENCE.md#releases-context-store-search) |
| Tags | [List](./REFERENCE.md#tags-list), [Get](./REFERENCE.md#tags-get), [Context Store Search](./REFERENCE.md#tags-context-store-search) |
| Group Milestones | [List](./REFERENCE.md#group-milestones-list), [Get](./REFERENCE.md#group-milestones-get), [Context Store Search](./REFERENCE.md#group-milestones-context-store-search) |
| Project Milestones | [List](./REFERENCE.md#project-milestones-list), [Get](./REFERENCE.md#project-milestones-get), [Context Store Search](./REFERENCE.md#project-milestones-context-store-search) |


### Authentication

For all authentication options, see the connector's [authentication documentation](AUTH.md).

### Gitlab API docs

See the official [Gitlab API reference](https://docs.gitlab.com/ee/api/rest/).

## Version information

- **Package version:** 1.0.4
- **Connector version:** 1.0.4
- **Generated with Connector SDK commit SHA:** unknown