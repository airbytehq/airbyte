# Clickup-Api

The Clickup-Api agent connector is a Python package that equips AI agents to interact with Clickup-Api through strongly typed, well-documented tools. It's ready to use directly in your Python app, in an agent framework, or exposed through an MCP.

ClickUp is a productivity platform that provides project management, task tracking, docs, goals,
and time tracking for teams. This connector provides access to workspaces, spaces, folders, lists,
tasks (including workspace-wide search), comments, goals, views, time tracking, members, and docs.


## Example prompts

The Clickup-Api connector is optimized to handle prompts like these.

- List all workspaces I have access to
- Show me the spaces in my workspace
- List the folders in a space
- Show me the lists in a folder
- Get the tasks in a list
- Get details for a specific task
- Search for tasks containing 'bug' across my workspace
- Find all urgent priority tasks in my workspace
- Show me tasks assigned to a specific user
- List comments on a task
- Get threaded replies on a comment
- Create a comment on a task
- Update a comment to mark it resolved
- List all goals in my workspace
- Get details for a specific goal
- Show me all workspace-level views
- Get tasks matching a saved view
- List time entries for my workspace this week
- Get details for a specific time entry
- Show me the members assigned to a task
- List all docs in my workspace
- Get details for a specific doc
- What tasks are overdue in my workspace?
- Which tasks were updated in the last 24 hours?
- Show me all high-priority tasks across all projects
- How much time has been tracked this week?
- What are the most commented tasks?

## Unsupported prompts

The Clickup-Api connector isn't currently able to handle prompts like these.

- Delete a task
- Delete a comment
- Delete a goal

## Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| User | [Get](./REFERENCE.md#user-get), [Context Store Search](./REFERENCE.md#user-context-store-search) |
| Teams | [List](./REFERENCE.md#teams-list), [Context Store Search](./REFERENCE.md#teams-context-store-search) |
| Spaces | [List](./REFERENCE.md#spaces-list), [Get](./REFERENCE.md#spaces-get), [Context Store Search](./REFERENCE.md#spaces-context-store-search) |
| Folders | [List](./REFERENCE.md#folders-list), [Get](./REFERENCE.md#folders-get), [Context Store Search](./REFERENCE.md#folders-context-store-search) |
| Lists | [List](./REFERENCE.md#lists-list), [Get](./REFERENCE.md#lists-get), [Context Store Search](./REFERENCE.md#lists-context-store-search) |
| Tasks | [List](./REFERENCE.md#tasks-list), [Get](./REFERENCE.md#tasks-get), [API Search](./REFERENCE.md#tasks-api_search), [Context Store Search](./REFERENCE.md#tasks-context-store-search) |
| Comments | [List](./REFERENCE.md#comments-list), [Create](./REFERENCE.md#comments-create), [Get](./REFERENCE.md#comments-get), [Update](./REFERENCE.md#comments-update), [Context Store Search](./REFERENCE.md#comments-context-store-search) |
| Goals | [List](./REFERENCE.md#goals-list), [Get](./REFERENCE.md#goals-get), [Context Store Search](./REFERENCE.md#goals-context-store-search) |
| Views | [List](./REFERENCE.md#views-list), [Get](./REFERENCE.md#views-get) |
| View Tasks | [List](./REFERENCE.md#view-tasks-list) |
| Time Tracking | [List](./REFERENCE.md#time-tracking-list), [Get](./REFERENCE.md#time-tracking-get), [Context Store Search](./REFERENCE.md#time-tracking-context-store-search) |
| Members | [List](./REFERENCE.md#members-list) |
| Docs | [List](./REFERENCE.md#docs-list), [Get](./REFERENCE.md#docs-get) |


## Clickup-Api API docs

See the official [Clickup-Api API reference](https://developer.clickup.com/reference).

## Interfaces

Use the Clickup-Api connector through the Airbyte Agent CLI, the Python SDK, or the API.

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
  "name": "clickup-api"
}'
```

Describe the connector to see its supported entities and actions:

```bash
airbyte-agent connectors describe --json '{
  "workspace": "<your_workspace_name>",
  "name": "clickup-api"
}'
```

Execute an action:

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "clickup-api",
  "entity": "user",
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

The `connect()` factory returns a fully typed `ClickupApiConnector` and reads `AIRBYTE_CLIENT_ID` / `AIRBYTE_CLIENT_SECRET` from the environment:


The recommended pattern is `build_connector_tools`, which gives the agent three tools bound to this connector: `inspect_connector`, `read_skill_docs`, and `execute`. The agent can inspect the connector, read only the skill-doc section it needs, and then execute:

```text
inspect_connector() -> read_skill_docs() -> read_skill_docs(section="...") -> execute(entity, action, params)
```

**Pydantic AI**

```python title="Pydantic AI"
from airbyte_agent_sdk import build_connector_tools
from pydantic_ai import Agent
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.clickup_api import ClickupApiConnector

connector = connect("clickup-api", workspace_name="<your_workspace_name>")

tools = build_connector_tools(connector, framework="pydantic_ai")
agent = Agent("openai:gpt-4o", tools=tools.as_list())
```

**LangChain**

```python title="LangChain"
from airbyte_agent_sdk import build_connector_tools
from langchain_core.tools import StructuredTool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.clickup_api import ClickupApiConnector

connector = connect("clickup-api", workspace_name="<your_workspace_name>")

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
from airbyte_agent_sdk.connectors.clickup_api import ClickupApiConnector

connector = connect("clickup-api", workspace_name="<your_workspace_name>")

tools = build_connector_tools(connector, framework="openai_agents")
openai_tools = [function_tool(tool, strict_mode=False) for tool in tools.as_list()]

agent = Agent(name="Clickup-Api Assistant", tools=openai_tools)
```

**FastMCP**

```python title="FastMCP"
from airbyte_agent_sdk import build_connector_tools
from fastmcp import FastMCP
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.clickup_api import ClickupApiConnector

connector = connect("clickup-api", workspace_name="<your_workspace_name>")

mcp = FastMCP("Clickup-Api Agent")

for tool in build_connector_tools(connector, framework="mcp").as_list():
    mcp.tool(tool)
```

###### Legacy alternatives

These examples are kept for existing integrations. For new agents, use `build_connector_tools` above. The legacy `ClickupApiConnector.tool_utils` pattern loads the connector's full generated catalog into one broad `execute` tool description instead of letting the agent read skill docs on demand.

**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.clickup_api import ClickupApiConnector

connector = connect("clickup-api", workspace_name="<your_workspace_name>")

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@ClickupApiConnector.tool_utils
async def clickup_api_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.clickup_api import ClickupApiConnector

connector = connect("clickup-api", workspace_name="<your_workspace_name>")

@tool
@ClickupApiConnector.tool_utils
async def clickup_api_execute(entity: str, action: str, params: dict | None = None):
    """Execute Clickup-Api connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.clickup_api import ClickupApiConnector

connector = connect("clickup-api", workspace_name="<your_workspace_name>")

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@ClickupApiConnector.tool_utils(framework="openai_agents")
async def clickup_api_execute(entity: str, action: str, params: dict | None = None):
    """Execute Clickup-Api connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Clickup-Api Assistant", tools=[clickup_api_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.clickup_api import ClickupApiConnector

connector = connect("clickup-api", workspace_name="<your_workspace_name>")

mcp = FastMCP("Clickup-Api Agent")

@mcp.tool
@ClickupApiConnector.tool_utils
async def clickup_api_execute(entity: str, action: str, params: dict | None = None):
    """Execute Clickup-Api connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```


Or pass credentials explicitly (equivalent, useful when you're not loading them from the environment):


**Pydantic AI**

```python title="Pydantic AI"
from airbyte_agent_sdk import build_connector_tools
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.clickup_api import ClickupApiConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = ClickupApiConnector(
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
from airbyte_agent_sdk.connectors.clickup_api import ClickupApiConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = ClickupApiConnector(
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
from airbyte_agent_sdk.connectors.clickup_api import ClickupApiConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = ClickupApiConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

tools = build_connector_tools(connector, framework="openai_agents")
openai_tools = [function_tool(tool, strict_mode=False) for tool in tools.as_list()]

agent = Agent(name="Clickup-Api Assistant", tools=openai_tools)
```

**FastMCP**

```python title="FastMCP"
from airbyte_agent_sdk import build_connector_tools
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.clickup_api import ClickupApiConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = ClickupApiConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

mcp = FastMCP("Clickup-Api Agent")

for tool in build_connector_tools(connector, framework="mcp").as_list():
    mcp.tool(tool)
```


##### Open source

In open source mode, you provide API credentials directly to the connector.

The recommended pattern is `build_connector_tools`, which gives the agent three tools bound to this connector: `inspect_connector`, `read_skill_docs`, and `execute`. The agent can inspect the connector, read only the skill-doc section it needs, and then execute:

```text
inspect_connector() -> read_skill_docs() -> read_skill_docs(section="...") -> execute(entity, action, params)
```

**Pydantic AI**

```python title="Pydantic AI"
from airbyte_agent_sdk import build_connector_tools
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.clickup_api import ClickupApiConnector
from airbyte_agent_sdk.connectors.clickup_api.models import ClickupApiAuthConfig

connector = ClickupApiConnector(
    auth_config=ClickupApiAuthConfig(
        api_key="<Your ClickUp personal API token>"
    )
)

tools = build_connector_tools(connector, framework="pydantic_ai")
agent = Agent("openai:gpt-4o", tools=tools.as_list())
```

**LangChain**

```python title="LangChain"
from airbyte_agent_sdk import build_connector_tools
from langchain_core.tools import StructuredTool
from airbyte_agent_sdk.connectors.clickup_api import ClickupApiConnector
from airbyte_agent_sdk.connectors.clickup_api.models import ClickupApiAuthConfig

connector = ClickupApiConnector(
    auth_config=ClickupApiAuthConfig(
        api_key="<Your ClickUp personal API token>"
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
from airbyte_agent_sdk.connectors.clickup_api import ClickupApiConnector
from airbyte_agent_sdk.connectors.clickup_api.models import ClickupApiAuthConfig

connector = ClickupApiConnector(
    auth_config=ClickupApiAuthConfig(
        api_key="<Your ClickUp personal API token>"
    )
)

tools = build_connector_tools(connector, framework="openai_agents")
openai_tools = [function_tool(tool, strict_mode=False) for tool in tools.as_list()]

agent = Agent(name="Clickup-Api Assistant", tools=openai_tools)
```

**FastMCP**

```python title="FastMCP"
from airbyte_agent_sdk import build_connector_tools
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.clickup_api import ClickupApiConnector
from airbyte_agent_sdk.connectors.clickup_api.models import ClickupApiAuthConfig

connector = ClickupApiConnector(
    auth_config=ClickupApiAuthConfig(
        api_key="<Your ClickUp personal API token>"
    )
)

mcp = FastMCP("Clickup-Api Agent")

for tool in build_connector_tools(connector, framework="mcp").as_list():
    mcp.tool(tool)
```

###### Legacy alternatives

These examples are kept for existing integrations. For new agents, use `build_connector_tools` above. The legacy `ClickupApiConnector.tool_utils` pattern loads the connector's full generated catalog into one broad `execute` tool description instead of letting the agent read skill docs on demand.

**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.clickup_api import ClickupApiConnector
from airbyte_agent_sdk.connectors.clickup_api.models import ClickupApiAuthConfig

connector = ClickupApiConnector(
    auth_config=ClickupApiAuthConfig(
        api_key="<Your ClickUp personal API token>"
    )
)

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@ClickupApiConnector.tool_utils
async def clickup_api_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.clickup_api import ClickupApiConnector
from airbyte_agent_sdk.connectors.clickup_api.models import ClickupApiAuthConfig

connector = ClickupApiConnector(
    auth_config=ClickupApiAuthConfig(
        api_key="<Your ClickUp personal API token>"
    )
)

@tool
@ClickupApiConnector.tool_utils
async def clickup_api_execute(entity: str, action: str, params: dict | None = None):
    """Execute Clickup-Api connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk.connectors.clickup_api import ClickupApiConnector
from airbyte_agent_sdk.connectors.clickup_api.models import ClickupApiAuthConfig

connector = ClickupApiConnector(
    auth_config=ClickupApiAuthConfig(
        api_key="<Your ClickUp personal API token>"
    )
)

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@ClickupApiConnector.tool_utils(framework="openai_agents")
async def clickup_api_execute(entity: str, action: str, params: dict | None = None):
    """Execute Clickup-Api connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Clickup-Api Assistant", tools=[clickup_api_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.clickup_api import ClickupApiConnector
from airbyte_agent_sdk.connectors.clickup_api.models import ClickupApiAuthConfig

connector = ClickupApiConnector(
    auth_config=ClickupApiAuthConfig(
        api_key="<Your ClickUp personal API token>"
    )
)

mcp = FastMCP("Clickup-Api Agent")

@mcp.tool
@ClickupApiConnector.tool_utils
async def clickup_api_execute(entity: str, action: str, params: dict | None = None):
    """Execute Clickup-Api connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```


## Authentication

For all authentication options, see the connector's [authentication documentation](AUTH.md).

## IP allow list

If your organization restricts access to specific IPs, add the [Airbyte Agents IP addresses](https://docs.airbyte.com/ai-agents/admin/ip-allowlist) to your allow list.

## Version information

**Connector version:** 0.1.5