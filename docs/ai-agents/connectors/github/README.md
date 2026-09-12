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
| Repositories | [Get](./REFERENCE.md#repositories-get), [List](./REFERENCE.md#repositories-list), [API Search](./REFERENCE.md#repositories-api_search), [Context Store Search](./REFERENCE.md#repositories-context-store-search), [Context Store SQL Query](./REFERENCE.md#repositories-context-store-sql-query) |
| Org Repositories | [List](./REFERENCE.md#org-repositories-list), [Context Store Search](./REFERENCE.md#org-repositories-context-store-search), [Context Store SQL Query](./REFERENCE.md#org-repositories-context-store-sql-query) |
| Branches | [List](./REFERENCE.md#branches-list), [Get](./REFERENCE.md#branches-get), [Context Store Search](./REFERENCE.md#branches-context-store-search), [Context Store SQL Query](./REFERENCE.md#branches-context-store-sql-query) |
| Commits | [List](./REFERENCE.md#commits-list), [Get](./REFERENCE.md#commits-get), [Context Store Search](./REFERENCE.md#commits-context-store-search), [Context Store SQL Query](./REFERENCE.md#commits-context-store-sql-query) |
| Releases | [List](./REFERENCE.md#releases-list), [Get](./REFERENCE.md#releases-get), [Context Store Search](./REFERENCE.md#releases-context-store-search), [Context Store SQL Query](./REFERENCE.md#releases-context-store-sql-query) |
| Issues | [List](./REFERENCE.md#issues-list), [Get](./REFERENCE.md#issues-get), [API Search](./REFERENCE.md#issues-api_search), [Create](./REFERENCE.md#issues-create), [Update](./REFERENCE.md#issues-update), [Context Store Search](./REFERENCE.md#issues-context-store-search), [Context Store SQL Query](./REFERENCE.md#issues-context-store-sql-query), [Semantic Search](./REFERENCE.md#issues-semantic-search) |
| Comments | [Create](./REFERENCE.md#comments-create), [List](./REFERENCE.md#comments-list), [Get](./REFERENCE.md#comments-get), [Context Store Search](./REFERENCE.md#comments-context-store-search), [Context Store SQL Query](./REFERENCE.md#comments-context-store-sql-query), [Semantic Search](./REFERENCE.md#comments-semantic-search) |
| Pull Requests | [Create](./REFERENCE.md#pull-requests-create), [List](./REFERENCE.md#pull-requests-list), [Get](./REFERENCE.md#pull-requests-get), [API Search](./REFERENCE.md#pull-requests-api_search), [Context Store Search](./REFERENCE.md#pull-requests-context-store-search), [Context Store SQL Query](./REFERENCE.md#pull-requests-context-store-sql-query), [Semantic Search](./REFERENCE.md#pull-requests-semantic-search) |
| Reviews | [List](./REFERENCE.md#reviews-list), [Context Store Search](./REFERENCE.md#reviews-context-store-search), [Context Store SQL Query](./REFERENCE.md#reviews-context-store-sql-query) |
| Pr Comments | [List](./REFERENCE.md#pr-comments-list), [Get](./REFERENCE.md#pr-comments-get), [Context Store Search](./REFERENCE.md#pr-comments-context-store-search), [Context Store SQL Query](./REFERENCE.md#pr-comments-context-store-sql-query) |
| Labels | [List](./REFERENCE.md#labels-list), [Get](./REFERENCE.md#labels-get), [Context Store Search](./REFERENCE.md#labels-context-store-search), [Context Store SQL Query](./REFERENCE.md#labels-context-store-sql-query) |
| Milestones | [List](./REFERENCE.md#milestones-list), [Get](./REFERENCE.md#milestones-get), [Context Store Search](./REFERENCE.md#milestones-context-store-search), [Context Store SQL Query](./REFERENCE.md#milestones-context-store-sql-query) |
| Organizations | [Get](./REFERENCE.md#organizations-get), [List](./REFERENCE.md#organizations-list), [Context Store Search](./REFERENCE.md#organizations-context-store-search), [Context Store SQL Query](./REFERENCE.md#organizations-context-store-sql-query) |
| Users | [Get](./REFERENCE.md#users-get), [List](./REFERENCE.md#users-list), [API Search](./REFERENCE.md#users-api_search), [Context Store Search](./REFERENCE.md#users-context-store-search), [Context Store SQL Query](./REFERENCE.md#users-context-store-sql-query) |
| Teams | [List](./REFERENCE.md#teams-list), [Get](./REFERENCE.md#teams-get), [Context Store Search](./REFERENCE.md#teams-context-store-search), [Context Store SQL Query](./REFERENCE.md#teams-context-store-sql-query) |
| Tags | [List](./REFERENCE.md#tags-list), [Get](./REFERENCE.md#tags-get), [Context Store Search](./REFERENCE.md#tags-context-store-search), [Context Store SQL Query](./REFERENCE.md#tags-context-store-sql-query) |
| Stargazers | [List](./REFERENCE.md#stargazers-list), [Context Store Search](./REFERENCE.md#stargazers-context-store-search), [Context Store SQL Query](./REFERENCE.md#stargazers-context-store-sql-query) |
| Viewer | [Get](./REFERENCE.md#viewer-get), [Context Store Search](./REFERENCE.md#viewer-context-store-search), [Context Store SQL Query](./REFERENCE.md#viewer-context-store-sql-query) |
| Viewer Repositories | [List](./REFERENCE.md#viewer-repositories-list), [Context Store Search](./REFERENCE.md#viewer-repositories-context-store-search), [Context Store SQL Query](./REFERENCE.md#viewer-repositories-context-store-sql-query) |
| Projects | [List](./REFERENCE.md#projects-list), [Get](./REFERENCE.md#projects-get), [Context Store Search](./REFERENCE.md#projects-context-store-search), [Context Store SQL Query](./REFERENCE.md#projects-context-store-sql-query) |
| Project Items | [List](./REFERENCE.md#project-items-list), [Context Store Search](./REFERENCE.md#project-items-context-store-search), [Context Store SQL Query](./REFERENCE.md#project-items-context-store-sql-query) |
| Discussions | [List](./REFERENCE.md#discussions-list), [Get](./REFERENCE.md#discussions-get), [API Search](./REFERENCE.md#discussions-api_search), [Context Store Search](./REFERENCE.md#discussions-context-store-search), [Context Store SQL Query](./REFERENCE.md#discussions-context-store-sql-query) |
| File Content | [Get](./REFERENCE.md#file-content-get), [Context Store Search](./REFERENCE.md#file-content-context-store-search), [Context Store SQL Query](./REFERENCE.md#file-content-context-store-sql-query) |
| Directory Content | [List](./REFERENCE.md#directory-content-list), [Context Store Search](./REFERENCE.md#directory-content-context-store-search), [Context Store SQL Query](./REFERENCE.md#directory-content-context-store-sql-query) |


## Github API docs

See the official [Github API reference](https://docs.github.com/en/rest).

## Interfaces

Use the Github connector through the Airbyte Agent CLI, the Python SDK, or the API.

### CLI

Install the CLI:

```bash
curl -fsSL https://airbyte.ai/install.sh | bash
```

Authenticate with Airbyte:

```bash
airbyte-agent login
```

Create the connector. The CLI opens the hosted setup flow:

```bash
airbyte-agent connectors create --json '{
  "workspace": "<your_workspace_name>",
  "name": "github"
}'
```

Describe the connector to see its supported entities and actions:

```bash
airbyte-agent connectors describe --json '{
  "workspace": "<your_workspace_name>",
  "name": "github"
}'
```

Execute an action:

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "github",
  "entity": "repositories",
  "action": "get"
}'
```

### Python SDK

#### Installation

```bash
uv pip install airbyte-agent-sdk
```

#### Usage

Connectors can run in hosted or open source mode.

##### Hosted

In hosted mode, API credentials are stored securely in Airbyte Agents. You provide your Airbyte credentials instead.
If your Airbyte client can access multiple organizations, also set `organization_id`.

This example assumes you've already authenticated your connector with Airbyte. See [Authentication](AUTH.md) to learn more about authenticating. If you need a step-by-step guide, see the [hosted execution tutorial](https://docs.airbyte.com/ai-agents/get-started/developer-quickstart/).

The `connect()` factory returns a fully typed `GithubConnector` and reads `AIRBYTE_CLIENT_ID` / `AIRBYTE_CLIENT_SECRET` from the environment:


The recommended pattern is `build_connector_tools`, which gives the agent three tools bound to this connector: `inspect_connector`, `read_skill_docs`, and `execute`. The agent can inspect the connector, read only the skill-doc section it needs, and then execute:

```text
inspect_connector() -> read_skill_docs() -> read_skill_docs(section="...") -> execute(entity, action, params)
```

Pass section IDs verbatim as the outline lists them, prefix included (`actions.<entity>.<action>`, not `<entity>.<action>`); anything else returns an error the agent has to recover from.

The builder names its tools `inspect_connector`, `read_skill_docs`, and `execute`, so the tool sets for more than one connector collide when registered on the same agent. Renaming the callables at registration avoids the collision, but the generated `execute` guidance still names `inspect_connector` and `read_skill_docs`, pointing the model at the wrong tools. Use the `agent_tool` pattern below instead: it weaves your own names into that guidance.

**Pydantic AI**

```python title="Pydantic AI"
from airbyte_agent_sdk import build_connector_tools
from pydantic_ai import Agent
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.github import GithubConnector

connector = connect("github", workspace_name="<your_workspace_name>")

tools = build_connector_tools(connector, framework="pydantic_ai")
agent = Agent("openai:gpt-4o", tools=tools.as_list())
```

**LangChain**

```python title="LangChain"
from airbyte_agent_sdk import build_connector_tools
from langchain_core.tools import StructuredTool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.github import GithubConnector

connector = connect("github", workspace_name="<your_workspace_name>")

tools = build_connector_tools(connector, framework="langchain")
langchain_tools = [
    StructuredTool.from_function(
        coroutine=tool,
        name=tool.__name__,
        description=tool.__doc__,
    )
    for tool in tools.as_list()
]
```

**OpenAI Agents**

```python title="OpenAI Agents"
from airbyte_agent_sdk import build_connector_tools
from agents import Agent, function_tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.github import GithubConnector

connector = connect("github", workspace_name="<your_workspace_name>")

tools = build_connector_tools(connector, framework="openai_agents")
openai_tools = [function_tool(tool, strict_mode=False) for tool in tools.as_list()]

agent = Agent(name="Github Assistant", tools=openai_tools)
```

**FastMCP**

```python title="FastMCP"
from airbyte_agent_sdk import build_connector_tools
from fastmcp import FastMCP
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.github import GithubConnector

connector = connect("github", workspace_name="<your_workspace_name>")

mcp = FastMCP("Github Agent")

for tool in build_connector_tools(connector, framework="mcp").as_list():
    mcp.tool(tool)
```

###### Custom tool bodies

When you need custom tool bodies — or a framework without native support — use `GithubConnector.agent_tool`. Register execute, inspect, and docs together so the agent can fetch connector guidance progressively. Pass the framework explicitly when it has a supported failure strategy:

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.github import GithubConnector

connector = connect("github", workspace_name="<your_workspace_name>")

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@GithubConnector.agent_tool(
    framework="pydantic_ai",
    inspect_tool="github_inspect",
    docs_tool="github_read_docs",
)
async def github_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})

@agent.tool_plain
@GithubConnector.agent_tool(framework="pydantic_ai")
async def github_inspect():
    return await connector.inspect_connector()

@agent.tool_plain
@GithubConnector.agent_tool(framework="pydantic_ai")
async def github_read_docs(section: str | None = None):
    return await connector.read_skill_docs(section)
```

Use the same three-function pattern with `framework="langchain"`, `"openai_agents"`, or `"mcp"` and that framework's registration decorator. Each value translates connector failures into the framework's own signal:

| `framework=` | Tool failures surface as |
|--------------|--------------------------|
| `"pydantic_ai"` | `pydantic_ai.ModelRetry` |
| `"langchain"` | `langchain_core.tools.ToolException` (set `handle_tool_error=True` to feed it back to the model) |
| `"openai_agents"` | the failure message returned to the model as the tool result |
| `"mcp"` | `fastmcp.exceptions.ToolError` |
| `"none"` (default) | `airbyte_agent_sdk.AirbyteToolError` |

On a framework the SDK does not support natively — or in a raw LLM dispatch loop — omit `framework=` and handle `AirbyteToolError` yourself:

```python title="No framework"
from airbyte_agent_sdk import AirbyteToolError
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.github import GithubConnector

connector = connect("github", workspace_name="<your_workspace_name>")

@GithubConnector.agent_tool(
    inspect_tool="github_inspect",
    docs_tool="github_read_docs",
)
async def github_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})

@GithubConnector.agent_tool()
async def github_inspect():
    return await connector.inspect_connector()

@GithubConnector.agent_tool()
async def github_read_docs(section: str | None = None):
    return await connector.read_skill_docs(section)

# Advertise all three to the model, using each function's docstring as its description.
handlers = {
    fn.__name__: fn
    for fn in (github_inspect, github_read_docs, github_execute)
}

# `tool_name` and `tool_args` come from the model's tool call in your dispatch loop.
try:
    tool_result = await handlers[tool_name](**tool_args)
except AirbyteToolError as err:
    tool_result = str(err)  # hand the message back to the model as an errored tool result
```

Each function's docstring carries the guidance the model needs, so pass it through as the tool description wherever you register it.

###### Legacy alternatives

These examples are kept for existing integrations. The deprecated `GithubConnector.tool_utils` pattern loads the connector's full generated catalog into one broad `execute` tool description instead of letting the agent read skill docs on demand. For new code, use `build_connector_tools` or `GithubConnector.agent_tool` above.

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
from airbyte_agent_sdk import build_connector_tools
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

tools = build_connector_tools(connector, framework="pydantic_ai")
agent = Agent("openai:gpt-4o", tools=tools.as_list())
```

**LangChain**

```python title="LangChain"
from airbyte_agent_sdk import build_connector_tools
from langchain_core.tools import StructuredTool
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

tools = build_connector_tools(connector, framework="langchain")
langchain_tools = [
    StructuredTool.from_function(
        coroutine=tool,
        name=tool.__name__,
        description=tool.__doc__,
    )
    for tool in tools.as_list()
]
```

**OpenAI Agents**

```python title="OpenAI Agents"
from airbyte_agent_sdk import build_connector_tools
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

tools = build_connector_tools(connector, framework="openai_agents")
openai_tools = [function_tool(tool, strict_mode=False) for tool in tools.as_list()]

agent = Agent(name="Github Assistant", tools=openai_tools)
```

**FastMCP**

```python title="FastMCP"
from airbyte_agent_sdk import build_connector_tools
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

for tool in build_connector_tools(connector, framework="mcp").as_list():
    mcp.tool(tool)
```


##### Open source

In open source mode, you provide API credentials directly to the connector.

The recommended pattern is `build_connector_tools`, which gives the agent three tools bound to this connector: `inspect_connector`, `read_skill_docs`, and `execute`. The agent can inspect the connector, read only the skill-doc section it needs, and then execute:

```text
inspect_connector() -> read_skill_docs() -> read_skill_docs(section="...") -> execute(entity, action, params)
```

Pass section IDs verbatim as the outline lists them, prefix included (`actions.<entity>.<action>`, not `<entity>.<action>`); anything else returns an error the agent has to recover from.

The builder names its tools `inspect_connector`, `read_skill_docs`, and `execute`, so the tool sets for more than one connector collide when registered on the same agent. Renaming the callables at registration avoids the collision, but the generated `execute` guidance still names `inspect_connector` and `read_skill_docs`, pointing the model at the wrong tools. Use the `agent_tool` pattern below instead: it weaves your own names into that guidance.

**Pydantic AI**

```python title="Pydantic AI"
from airbyte_agent_sdk import build_connector_tools
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.github import GithubConnector
from airbyte_agent_sdk.connectors.github.models import GithubPersonalAccessTokenAuthConfig

connector = GithubConnector(
    auth_config=GithubPersonalAccessTokenAuthConfig(
        token="<GitHub personal access token (fine-grained or classic)>"
    )
)

tools = build_connector_tools(connector, framework="pydantic_ai")
agent = Agent("openai:gpt-4o", tools=tools.as_list())
```

**LangChain**

```python title="LangChain"
from airbyte_agent_sdk import build_connector_tools
from langchain_core.tools import StructuredTool
from airbyte_agent_sdk.connectors.github import GithubConnector
from airbyte_agent_sdk.connectors.github.models import GithubPersonalAccessTokenAuthConfig

connector = GithubConnector(
    auth_config=GithubPersonalAccessTokenAuthConfig(
        token="<GitHub personal access token (fine-grained or classic)>"
    )
)

tools = build_connector_tools(connector, framework="langchain")
langchain_tools = [
    StructuredTool.from_function(
        coroutine=tool,
        name=tool.__name__,
        description=tool.__doc__,
    )
    for tool in tools.as_list()
]
```

**OpenAI Agents**

```python title="OpenAI Agents"
from airbyte_agent_sdk import build_connector_tools
from agents import Agent, function_tool
from airbyte_agent_sdk.connectors.github import GithubConnector
from airbyte_agent_sdk.connectors.github.models import GithubPersonalAccessTokenAuthConfig

connector = GithubConnector(
    auth_config=GithubPersonalAccessTokenAuthConfig(
        token="<GitHub personal access token (fine-grained or classic)>"
    )
)

tools = build_connector_tools(connector, framework="openai_agents")
openai_tools = [function_tool(tool, strict_mode=False) for tool in tools.as_list()]

agent = Agent(name="Github Assistant", tools=openai_tools)
```

**FastMCP**

```python title="FastMCP"
from airbyte_agent_sdk import build_connector_tools
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.github import GithubConnector
from airbyte_agent_sdk.connectors.github.models import GithubPersonalAccessTokenAuthConfig

connector = GithubConnector(
    auth_config=GithubPersonalAccessTokenAuthConfig(
        token="<GitHub personal access token (fine-grained or classic)>"
    )
)

mcp = FastMCP("Github Agent")

for tool in build_connector_tools(connector, framework="mcp").as_list():
    mcp.tool(tool)
```

###### Custom tool bodies

When you need custom tool bodies — or a framework without native support — use `GithubConnector.agent_tool`. Register execute, inspect, and docs together so the agent can fetch connector guidance progressively. Pass the framework explicitly when it has a supported failure strategy:

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
@GithubConnector.agent_tool(
    framework="pydantic_ai",
    inspect_tool="github_inspect",
    docs_tool="github_read_docs",
)
async def github_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})

@agent.tool_plain
@GithubConnector.agent_tool(framework="pydantic_ai")
async def github_inspect():
    return await connector.inspect_connector()

@agent.tool_plain
@GithubConnector.agent_tool(framework="pydantic_ai")
async def github_read_docs(section: str | None = None):
    return await connector.read_skill_docs(section)
```

Use the same three-function pattern with `framework="langchain"`, `"openai_agents"`, or `"mcp"` and that framework's registration decorator. Each value translates connector failures into the framework's own signal:

| `framework=` | Tool failures surface as |
|--------------|--------------------------|
| `"pydantic_ai"` | `pydantic_ai.ModelRetry` |
| `"langchain"` | `langchain_core.tools.ToolException` (set `handle_tool_error=True` to feed it back to the model) |
| `"openai_agents"` | the failure message returned to the model as the tool result |
| `"mcp"` | `fastmcp.exceptions.ToolError` |
| `"none"` (default) | `airbyte_agent_sdk.AirbyteToolError` |

On a framework the SDK does not support natively — or in a raw LLM dispatch loop — omit `framework=` and handle `AirbyteToolError` yourself:

```python title="No framework"
from airbyte_agent_sdk import AirbyteToolError
from airbyte_agent_sdk.connectors.github import GithubConnector
from airbyte_agent_sdk.connectors.github.models import GithubPersonalAccessTokenAuthConfig

connector = GithubConnector(
    auth_config=GithubPersonalAccessTokenAuthConfig(
        token="<GitHub personal access token (fine-grained or classic)>"
    )
)

@GithubConnector.agent_tool(
    inspect_tool="github_inspect",
    docs_tool="github_read_docs",
)
async def github_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})

@GithubConnector.agent_tool()
async def github_inspect():
    return await connector.inspect_connector()

@GithubConnector.agent_tool()
async def github_read_docs(section: str | None = None):
    return await connector.read_skill_docs(section)

# Advertise all three to the model, using each function's docstring as its description.
handlers = {
    fn.__name__: fn
    for fn in (github_inspect, github_read_docs, github_execute)
}

# `tool_name` and `tool_args` come from the model's tool call in your dispatch loop.
try:
    tool_result = await handlers[tool_name](**tool_args)
except AirbyteToolError as err:
    tool_result = str(err)  # hand the message back to the model as an errored tool result
```

Each function's docstring carries the guidance the model needs, so pass it through as the tool description wherever you register it.

###### Legacy alternatives

These examples are kept for existing integrations. The deprecated `GithubConnector.tool_utils` pattern loads the connector's full generated catalog into one broad `execute` tool description instead of letting the agent read skill docs on demand. For new code, use `build_connector_tools` or `GithubConnector.agent_tool` above.

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

## IP allow list

If your organization restricts access to specific IPs, add the [Airbyte Agents IP addresses](https://docs.airbyte.com/ai-agents/admin/ip-allowlist) to your allow list.

## Version information

**Connector version:** 0.1.19