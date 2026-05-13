# Github

The Github agent connector is a Python package that equips AI agents to interact with Github through strongly typed, well-documented tools. It's ready to use directly in your Python app, in an agent framework, or exposed through an MCP.

GitHub is a platform for version control and collaborative software development
using Git. This connector provides access to repositories, branches, commits, issues,
pull requests, reviews, comments, releases, discussions, organizations, teams, and users for
development workflow analysis and project management insights.


## Example prompts

The Github connector is optimized to handle prompts like these.

- Show me all open issues in my repositories this month
- List the top 5 repositories I've starred recently
- Analyze the commit trends in my main project over the last quarter
- Find all pull requests created in the past two weeks
- Search for repositories related to machine learning in my organizations
- Compare the number of contributors across my different team projects
- Identify the most active branches in my main repository
- Get details about the most recent releases in my organization
- List all milestones for our current development sprint
- Show me insights about pull request review patterns in our team
- List all unanswered discussions in a repository
- Show me recent discussions in the General category
- Create a new issue titled 'Fix login bug' in my repository
- Create an issue with labels 'bug' and 'urgent' in owner/repo
- File a new bug report issue in our project repository
- Create an issue and assign it to a team member
- Open a new feature request issue in the repository
- Close issue #42 in owner/repo as completed
- Reopen issue #15 in our repository
- Add the 'bug' and 'urgent' labels to issue #10
- Assign user @johndoe to issue #25 in owner/repo
- Update the title of issue #30 to 'New title'
- Add a comment to issue #5 saying 'This has been fixed in the latest release'
- Post a comment on pull request #100 with a status update
- Create a pull request from feature-branch to main in owner/repo
- Open a draft PR titled 'Add new feature' from my-branch to main

## Unsupported prompts

The Github connector isn't currently able to handle prompts like these.

- Delete an old branch from the repository
- Schedule a team review for this code
- Merge a pull request
- Delete an issue or comment

## Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Repositories | [Get](./REFERENCE.md#repositories-get), [List](./REFERENCE.md#repositories-list), [API Search](./REFERENCE.md#repositories-api_search), [Context Store Search](./REFERENCE.md#repositories-context-store-search) |
| Org Repositories | [List](./REFERENCE.md#org-repositories-list), [Context Store Search](./REFERENCE.md#org-repositories-context-store-search) |
| Branches | [List](./REFERENCE.md#branches-list), [Get](./REFERENCE.md#branches-get), [Context Store Search](./REFERENCE.md#branches-context-store-search) |
| Commits | [List](./REFERENCE.md#commits-list), [Get](./REFERENCE.md#commits-get), [Context Store Search](./REFERENCE.md#commits-context-store-search) |
| Releases | [List](./REFERENCE.md#releases-list), [Get](./REFERENCE.md#releases-get), [Context Store Search](./REFERENCE.md#releases-context-store-search) |
| Issues | [List](./REFERENCE.md#issues-list), [Get](./REFERENCE.md#issues-get), [API Search](./REFERENCE.md#issues-api_search), [Create](./REFERENCE.md#issues-create), [Update](./REFERENCE.md#issues-update), [Context Store Search](./REFERENCE.md#issues-context-store-search) |
| Comments | [Create](./REFERENCE.md#comments-create), [List](./REFERENCE.md#comments-list), [Get](./REFERENCE.md#comments-get), [Context Store Search](./REFERENCE.md#comments-context-store-search) |
| Pull Requests | [Create](./REFERENCE.md#pull-requests-create), [List](./REFERENCE.md#pull-requests-list), [Get](./REFERENCE.md#pull-requests-get), [API Search](./REFERENCE.md#pull-requests-api_search), [Context Store Search](./REFERENCE.md#pull-requests-context-store-search) |
| Reviews | [List](./REFERENCE.md#reviews-list), [Context Store Search](./REFERENCE.md#reviews-context-store-search) |
| Pr Comments | [List](./REFERENCE.md#pr-comments-list), [Get](./REFERENCE.md#pr-comments-get), [Context Store Search](./REFERENCE.md#pr-comments-context-store-search) |
| Labels | [List](./REFERENCE.md#labels-list), [Get](./REFERENCE.md#labels-get), [Context Store Search](./REFERENCE.md#labels-context-store-search) |
| Milestones | [List](./REFERENCE.md#milestones-list), [Get](./REFERENCE.md#milestones-get), [Context Store Search](./REFERENCE.md#milestones-context-store-search) |
| Organizations | [Get](./REFERENCE.md#organizations-get), [List](./REFERENCE.md#organizations-list), [Context Store Search](./REFERENCE.md#organizations-context-store-search) |
| Users | [Get](./REFERENCE.md#users-get), [List](./REFERENCE.md#users-list), [API Search](./REFERENCE.md#users-api_search), [Context Store Search](./REFERENCE.md#users-context-store-search) |
| Teams | [List](./REFERENCE.md#teams-list), [Get](./REFERENCE.md#teams-get), [Context Store Search](./REFERENCE.md#teams-context-store-search) |
| Tags | [List](./REFERENCE.md#tags-list), [Get](./REFERENCE.md#tags-get), [Context Store Search](./REFERENCE.md#tags-context-store-search) |
| Stargazers | [List](./REFERENCE.md#stargazers-list), [Context Store Search](./REFERENCE.md#stargazers-context-store-search) |
| Viewer | [Get](./REFERENCE.md#viewer-get), [Context Store Search](./REFERENCE.md#viewer-context-store-search) |
| Viewer Repositories | [List](./REFERENCE.md#viewer-repositories-list), [Context Store Search](./REFERENCE.md#viewer-repositories-context-store-search) |
| Projects | [List](./REFERENCE.md#projects-list), [Get](./REFERENCE.md#projects-get), [Context Store Search](./REFERENCE.md#projects-context-store-search) |
| Project Items | [List](./REFERENCE.md#project-items-list), [Context Store Search](./REFERENCE.md#project-items-context-store-search) |
| Discussions | [List](./REFERENCE.md#discussions-list), [Get](./REFERENCE.md#discussions-get), [API Search](./REFERENCE.md#discussions-api_search), [Context Store Search](./REFERENCE.md#discussions-context-store-search) |
| File Content | [Get](./REFERENCE.md#file-content-get), [Context Store Search](./REFERENCE.md#file-content-context-store-search) |
| Directory Content | [List](./REFERENCE.md#directory-content-list), [Context Store Search](./REFERENCE.md#directory-content-context-store-search) |


## Github API docs

See the official [Github API reference](https://docs.github.com/en/rest).

## SDK installation

```bash
uv pip install airbyte-agent-sdk
```

## SDK usage

Connectors can run in hosted or open source mode.

### Hosted

In hosted mode, API credentials are stored securely in Airbyte Agents. You provide your Airbyte credentials instead.
If your Airbyte client can access multiple organizations, also set `organization_id`.

This example assumes you've already authenticated your connector with Airbyte. See [Authentication](AUTH.md) to learn more about authenticating. If you need a step-by-step guide, see the [hosted execution tutorial](https://docs.airbyte.com/ai-agents/get-started/developer-quickstart/).

The `connect()` factory returns a fully typed `GithubConnector` and reads `AIRBYTE_CLIENT_ID` / `AIRBYTE_CLIENT_SECRET` from the environment:


**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.github import GithubConnector

connector = connect("github", workspace_name="<your_workspace_name>")

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@GithubConnector.tool_utils
async def github_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.github import GithubConnector

connector = connect("github", workspace_name="<your_workspace_name>")

@tool
@GithubConnector.tool_utils
async def github_execute(entity: str, action: str, params: dict | None = None):
    """Execute Github connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.github import GithubConnector

connector = connect("github", workspace_name="<your_workspace_name>")

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@GithubConnector.tool_utils(framework="openai_agents")
async def github_execute(entity: str, action: str, params: dict | None = None):
    """Execute Github connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Github Assistant", tools=[github_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.github import GithubConnector

connector = connect("github", workspace_name="<your_workspace_name>")

mcp = FastMCP("Github Agent")

@mcp.tool
@GithubConnector.tool_utils
async def github_execute(entity: str, action: str, params: dict | None = None):
    """Execute Github connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

Or pass credentials explicitly (equivalent, useful when you're not loading them from the environment):

**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.github import GithubConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = GithubConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@GithubConnector.tool_utils
async def github_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.github import GithubConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = GithubConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

@tool
@GithubConnector.tool_utils
async def github_execute(entity: str, action: str, params: dict | None = None):
    """Execute Github connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk.connectors.github import GithubConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = GithubConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@GithubConnector.tool_utils(framework="openai_agents")
async def github_execute(entity: str, action: str, params: dict | None = None):
    """Execute Github connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Github Assistant", tools=[github_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.github import GithubConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = GithubConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

mcp = FastMCP("Github Agent")

@mcp.tool
@GithubConnector.tool_utils
async def github_execute(entity: str, action: str, params: dict | None = None):
    """Execute Github connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

### Open source

In open source mode, you provide API credentials directly to the connector.

**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.github import GithubConnector
from airbyte_agent_sdk.connectors.github.models import GithubPersonalAccessTokenAuthConfig

connector = GithubConnector(
    auth_config=GithubPersonalAccessTokenAuthConfig(
        token="<GitHub personal access token (fine-grained or classic)>"
    )
)

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@GithubConnector.tool_utils
async def github_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.github import GithubConnector
from airbyte_agent_sdk.connectors.github.models import GithubPersonalAccessTokenAuthConfig

connector = GithubConnector(
    auth_config=GithubPersonalAccessTokenAuthConfig(
        token="<GitHub personal access token (fine-grained or classic)>"
    )
)

@tool
@GithubConnector.tool_utils
async def github_execute(entity: str, action: str, params: dict | None = None):
    """Execute Github connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk.connectors.github import GithubConnector
from airbyte_agent_sdk.connectors.github.models import GithubPersonalAccessTokenAuthConfig

connector = GithubConnector(
    auth_config=GithubPersonalAccessTokenAuthConfig(
        token="<GitHub personal access token (fine-grained or classic)>"
    )
)

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@GithubConnector.tool_utils(framework="openai_agents")
async def github_execute(entity: str, action: str, params: dict | None = None):
    """Execute Github connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Github Assistant", tools=[github_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.github import GithubConnector
from airbyte_agent_sdk.connectors.github.models import GithubPersonalAccessTokenAuthConfig

connector = GithubConnector(
    auth_config=GithubPersonalAccessTokenAuthConfig(
        token="<GitHub personal access token (fine-grained or classic)>"
    )
)

mcp = FastMCP("Github Agent")

@mcp.tool
@GithubConnector.tool_utils
async def github_execute(entity: str, action: str, params: dict | None = None):
    """Execute Github connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

## Authentication

For all authentication options, see the connector's [authentication documentation](AUTH.md).

## Version information

**Connector version:** 0.1.19
