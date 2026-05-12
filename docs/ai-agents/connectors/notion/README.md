# Notion

The Notion agent connector is a Python package that equips AI agents to interact with Notion through strongly typed, well-documented tools. It's ready to use directly in your Python app, in an agent framework, or exposed through an MCP.

Notion is an all-in-one workspace for notes, docs, wikis, projects, and collaboration.
This connector provides read access to Notion workspaces including users, pages, data sources,
blocks, and comments through the Notion REST API (version 2025-09-03). It enables querying
workspace structure, page content, data source schemas, and collaboration data for productivity
analysis and content management insights.


## Example prompts

The Notion connector is optimized to handle prompts like these.

- List all users in my Notion workspace
- Show me all pages in my Notion workspace
- What data sources exist in my Notion workspace?
- Get the details of a specific page by ID
- List child blocks of a specific page
- Show me comments on a specific page
- What is the schema of a specific data source?
- Who are the bot users in my workspace?
- Find pages created in the last week
- List data sources that have been recently edited
- Show me all archived pages

## Unsupported prompts

The Notion connector isn't currently able to handle prompts like these.

- Create a new page in Notion
- Update a data source property
- Delete a block
- Add a comment to a page

## Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Users | [List](./REFERENCE.md#users-list), [Get](./REFERENCE.md#users-get), [Context Store Search](./REFERENCE.md#users-context-store-search) |
| Pages | [List](./REFERENCE.md#pages-list), [Get](./REFERENCE.md#pages-get), [Context Store Search](./REFERENCE.md#pages-context-store-search) |
| Data Sources | [List](./REFERENCE.md#data-sources-list), [Get](./REFERENCE.md#data-sources-get), [Context Store Search](./REFERENCE.md#data-sources-context-store-search) |
| Blocks | [List](./REFERENCE.md#blocks-list), [Get](./REFERENCE.md#blocks-get), [Context Store Search](./REFERENCE.md#blocks-context-store-search) |
| Comments | [List](./REFERENCE.md#comments-list), [Context Store Search](./REFERENCE.md#comments-context-store-search) |


## Notion API docs

See the official [Notion API reference](https://developers.notion.com/reference/intro).

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

The `connect()` factory returns a fully typed `NotionConnector` and reads `AIRBYTE_CLIENT_ID` / `AIRBYTE_CLIENT_SECRET` from the environment:


**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.notion import NotionConnector

connector = connect("notion", workspace_name="<your_workspace_name>")

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@NotionConnector.tool_utils
async def notion_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.notion import NotionConnector

connector = connect("notion", workspace_name="<your_workspace_name>")

@tool
@NotionConnector.tool_utils
async def notion_execute(entity: str, action: str, params: dict | None = None):
    """Execute Notion connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.notion import NotionConnector

connector = connect("notion", workspace_name="<your_workspace_name>")

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@NotionConnector.tool_utils(framework="openai_agents")
async def notion_execute(entity: str, action: str, params: dict | None = None):
    """Execute Notion connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Notion Assistant", tools=[notion_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.notion import NotionConnector

connector = connect("notion", workspace_name="<your_workspace_name>")

mcp = FastMCP("Notion Agent")

@mcp.tool
@NotionConnector.tool_utils
async def notion_execute(entity: str, action: str, params: dict | None = None):
    """Execute Notion connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

Or pass credentials explicitly (equivalent, useful when you're not loading them from the environment):

**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.notion import NotionConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = NotionConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@NotionConnector.tool_utils
async def notion_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.notion import NotionConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = NotionConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

@tool
@NotionConnector.tool_utils
async def notion_execute(entity: str, action: str, params: dict | None = None):
    """Execute Notion connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk.connectors.notion import NotionConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = NotionConnector(
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
@NotionConnector.tool_utils(framework="openai_agents")
async def notion_execute(entity: str, action: str, params: dict | None = None):
    """Execute Notion connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Notion Assistant", tools=[notion_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.notion import NotionConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = NotionConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

mcp = FastMCP("Notion Agent")

@mcp.tool
@NotionConnector.tool_utils
async def notion_execute(entity: str, action: str, params: dict | None = None):
    """Execute Notion connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

### Open source

In open source mode, you provide API credentials directly to the connector.

**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.notion import NotionConnector
from airbyte_agent_sdk.connectors.notion.models import NotionAccessTokenAuthConfig

connector = NotionConnector(
    auth_config=NotionAccessTokenAuthConfig(
        token="<Notion internal integration token (starts with ntn_ or secret_)>"
    )
)

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@NotionConnector.tool_utils
async def notion_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.notion import NotionConnector
from airbyte_agent_sdk.connectors.notion.models import NotionAccessTokenAuthConfig

connector = NotionConnector(
    auth_config=NotionAccessTokenAuthConfig(
        token="<Notion internal integration token (starts with ntn_ or secret_)>"
    )
)

@tool
@NotionConnector.tool_utils
async def notion_execute(entity: str, action: str, params: dict | None = None):
    """Execute Notion connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk.connectors.notion import NotionConnector
from airbyte_agent_sdk.connectors.notion.models import NotionAccessTokenAuthConfig

connector = NotionConnector(
    auth_config=NotionAccessTokenAuthConfig(
        token="<Notion internal integration token (starts with ntn_ or secret_)>"
    )
)

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@NotionConnector.tool_utils(framework="openai_agents")
async def notion_execute(entity: str, action: str, params: dict | None = None):
    """Execute Notion connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Notion Assistant", tools=[notion_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.notion import NotionConnector
from airbyte_agent_sdk.connectors.notion.models import NotionAccessTokenAuthConfig

connector = NotionConnector(
    auth_config=NotionAccessTokenAuthConfig(
        token="<Notion internal integration token (starts with ntn_ or secret_)>"
    )
)

mcp = FastMCP("Notion Agent")

@mcp.tool
@NotionConnector.tool_utils
async def notion_execute(entity: str, action: str, params: dict | None = None):
    """Execute Notion connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

## Authentication

For all authentication options, see the connector's [authentication documentation](AUTH.md).

## Version information

**Connector version:** 0.1.12
