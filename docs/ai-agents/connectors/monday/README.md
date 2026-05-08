# Monday

The Monday agent connector is a Python package that equips AI agents to interact with Monday through strongly typed, well-documented tools. It's ready to use directly in your Python app, in an agent framework, or exposed through an MCP.

Connector for the Monday.com platform API. Monday.com is a work operating system that enables teams to build workflows for project management, CRM, software development, and more. This connector provides read access to boards, items, users, teams, tags, updates, workspaces, and activity logs via the Monday.com GraphQL API (v2).


## Example prompts

The Monday connector is optimized to handle prompts like these.

- List all users in the Monday.com account
- Show me all boards
- Get the details of board 18395979459
- List all teams
- Show me all tags
- List recent updates
- Which boards were updated in the last week?
- Find all items assigned to a specific group
- What are the most active boards by update count?
- Show me all users who are admins
- List items with their column values from a specific board

## Unsupported prompts

The Monday connector isn't currently able to handle prompts like these.

- Create a new board
- Delete an item
- Update a column value
- Add a new user to the account
- Create a webhook subscription

## Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Users | [List](./REFERENCE.md#users-list), [Get](./REFERENCE.md#users-get), [Context Store Search](./REFERENCE.md#users-context-store-search) |
| Boards | [List](./REFERENCE.md#boards-list), [Get](./REFERENCE.md#boards-get), [Context Store Search](./REFERENCE.md#boards-context-store-search) |
| Items | [List](./REFERENCE.md#items-list), [Get](./REFERENCE.md#items-get), [Context Store Search](./REFERENCE.md#items-context-store-search) |
| Teams | [List](./REFERENCE.md#teams-list), [Get](./REFERENCE.md#teams-get), [Context Store Search](./REFERENCE.md#teams-context-store-search) |
| Tags | [List](./REFERENCE.md#tags-list), [Context Store Search](./REFERENCE.md#tags-context-store-search) |
| Updates | [List](./REFERENCE.md#updates-list), [Get](./REFERENCE.md#updates-get), [Context Store Search](./REFERENCE.md#updates-context-store-search) |
| Workspaces | [List](./REFERENCE.md#workspaces-list), [Get](./REFERENCE.md#workspaces-get), [Context Store Search](./REFERENCE.md#workspaces-context-store-search) |
| Activity Logs | [List](./REFERENCE.md#activity-logs-list), [Context Store Search](./REFERENCE.md#activity-logs-context-store-search) |


## Monday API docs

See the official [Monday API reference](https://developer.monday.com/api-reference/docs).

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

The `connect()` factory returns a fully typed `MondayConnector` and reads `AIRBYTE_CLIENT_ID` / `AIRBYTE_CLIENT_SECRET` from the environment:


**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.monday import MondayConnector

connector = connect("monday", workspace_name="<your_workspace_name>")

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@MondayConnector.tool_utils
async def monday_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.monday import MondayConnector

connector = connect("monday", workspace_name="<your_workspace_name>")

@tool
@MondayConnector.tool_utils
async def monday_execute(entity: str, action: str, params: dict | None = None):
    """Execute Monday connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.monday import MondayConnector

connector = connect("monday", workspace_name="<your_workspace_name>")

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@MondayConnector.tool_utils(framework="openai_agents")
async def monday_execute(entity: str, action: str, params: dict | None = None):
    """Execute Monday connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Monday Assistant", tools=[monday_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.monday import MondayConnector

connector = connect("monday", workspace_name="<your_workspace_name>")

mcp = FastMCP("Monday Agent")

@mcp.tool
@MondayConnector.tool_utils
async def monday_execute(entity: str, action: str, params: dict | None = None):
    """Execute Monday connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

Or pass credentials explicitly (equivalent, useful when you're not loading them from the environment):

**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.monday import MondayConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = MondayConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@MondayConnector.tool_utils
async def monday_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.monday import MondayConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = MondayConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

@tool
@MondayConnector.tool_utils
async def monday_execute(entity: str, action: str, params: dict | None = None):
    """Execute Monday connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk.connectors.monday import MondayConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = MondayConnector(
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
@MondayConnector.tool_utils(framework="openai_agents")
async def monday_execute(entity: str, action: str, params: dict | None = None):
    """Execute Monday connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Monday Assistant", tools=[monday_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.monday import MondayConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = MondayConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

mcp = FastMCP("Monday Agent")

@mcp.tool
@MondayConnector.tool_utils
async def monday_execute(entity: str, action: str, params: dict | None = None):
    """Execute Monday connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

### Open source

In open source mode, you provide API credentials directly to the connector.

**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.monday import MondayConnector
from airbyte_agent_sdk.connectors.monday.models import MondayApiTokenAuthenticationAuthConfig

connector = MondayConnector(
    auth_config=MondayApiTokenAuthenticationAuthConfig(
        api_key="<Your Monday.com personal API token>"
    )
)

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@MondayConnector.tool_utils
async def monday_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.monday import MondayConnector
from airbyte_agent_sdk.connectors.monday.models import MondayApiTokenAuthenticationAuthConfig

connector = MondayConnector(
    auth_config=MondayApiTokenAuthenticationAuthConfig(
        api_key="<Your Monday.com personal API token>"
    )
)

@tool
@MondayConnector.tool_utils
async def monday_execute(entity: str, action: str, params: dict | None = None):
    """Execute Monday connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk.connectors.monday import MondayConnector
from airbyte_agent_sdk.connectors.monday.models import MondayApiTokenAuthenticationAuthConfig

connector = MondayConnector(
    auth_config=MondayApiTokenAuthenticationAuthConfig(
        api_key="<Your Monday.com personal API token>"
    )
)

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@MondayConnector.tool_utils(framework="openai_agents")
async def monday_execute(entity: str, action: str, params: dict | None = None):
    """Execute Monday connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Monday Assistant", tools=[monday_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.monday import MondayConnector
from airbyte_agent_sdk.connectors.monday.models import MondayApiTokenAuthenticationAuthConfig

connector = MondayConnector(
    auth_config=MondayApiTokenAuthenticationAuthConfig(
        api_key="<Your Monday.com personal API token>"
    )
)

mcp = FastMCP("Monday Agent")

@mcp.tool
@MondayConnector.tool_utils
async def monday_execute(entity: str, action: str, params: dict | None = None):
    """Execute Monday connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

## Authentication

For all authentication options, see the connector's [authentication documentation](AUTH.md).

## Version information

**Connector version:** 1.0.4
