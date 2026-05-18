# Pinterest

The Pinterest agent connector is a Python package that equips AI agents to interact with Pinterest through strongly typed, well-documented tools. It's ready to use directly in your Python app, in an agent framework, or exposed through an MCP.

Connector for the Pinterest API v5, enabling access to Pinterest advertising and content management data. Supports reading ad accounts, boards, campaigns, ad groups, ads, board sections, board pins, catalogs, catalog feeds, catalog product groups, audiences, conversion tags, customer lists, and keywords.


## Example prompts

The Pinterest connector is optimized to handle prompts like these.

- List all my Pinterest ad accounts
- List all my Pinterest boards
- Show me all campaigns in my ad account
- List all ads in my ad account
- Show me all ad groups in my ad account
- List all audiences for my ad account
- Show me my catalog feeds
- Which campaigns are currently active?
- What are the top boards by pin count?
- Show me ads that have been rejected
- Find campaigns with the highest daily spend cap

## Unsupported prompts

The Pinterest connector isn't currently able to handle prompts like these.

- Create a new Pinterest board
- Update a campaign budget
- Delete an ad group
- Post a new pin
- Show me campaign analytics or performance metrics

## Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Ad Accounts | [List](./REFERENCE.md#ad-accounts-list), [Get](./REFERENCE.md#ad-accounts-get), [Context Store Search](./REFERENCE.md#ad-accounts-context-store-search) |
| Boards | [List](./REFERENCE.md#boards-list), [Get](./REFERENCE.md#boards-get), [Context Store Search](./REFERENCE.md#boards-context-store-search) |
| Campaigns | [List](./REFERENCE.md#campaigns-list), [Context Store Search](./REFERENCE.md#campaigns-context-store-search) |
| Ad Groups | [List](./REFERENCE.md#ad-groups-list), [Context Store Search](./REFERENCE.md#ad-groups-context-store-search) |
| Ads | [List](./REFERENCE.md#ads-list), [Context Store Search](./REFERENCE.md#ads-context-store-search) |
| Board Sections | [List](./REFERENCE.md#board-sections-list), [Context Store Search](./REFERENCE.md#board-sections-context-store-search) |
| Board Pins | [List](./REFERENCE.md#board-pins-list), [Context Store Search](./REFERENCE.md#board-pins-context-store-search) |
| Catalogs | [List](./REFERENCE.md#catalogs-list), [Context Store Search](./REFERENCE.md#catalogs-context-store-search) |
| Catalogs Feeds | [List](./REFERENCE.md#catalogs-feeds-list), [Context Store Search](./REFERENCE.md#catalogs-feeds-context-store-search) |
| Catalogs Product Groups | [List](./REFERENCE.md#catalogs-product-groups-list), [Context Store Search](./REFERENCE.md#catalogs-product-groups-context-store-search) |
| Audiences | [List](./REFERENCE.md#audiences-list), [Context Store Search](./REFERENCE.md#audiences-context-store-search) |
| Conversion Tags | [List](./REFERENCE.md#conversion-tags-list), [Context Store Search](./REFERENCE.md#conversion-tags-context-store-search) |
| Customer Lists | [List](./REFERENCE.md#customer-lists-list), [Context Store Search](./REFERENCE.md#customer-lists-context-store-search) |
| Keywords | [List](./REFERENCE.md#keywords-list), [Context Store Search](./REFERENCE.md#keywords-context-store-search) |


## Pinterest API docs

See the official [Pinterest API reference](https://developers.pinterest.com/docs/api/v5/).

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

The `connect()` factory returns a fully typed `PinterestConnector` and reads `AIRBYTE_CLIENT_ID` / `AIRBYTE_CLIENT_SECRET` from the environment:


**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.pinterest import PinterestConnector

connector = connect("pinterest", workspace_name="<your_workspace_name>")

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@PinterestConnector.tool_utils
async def pinterest_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.pinterest import PinterestConnector

connector = connect("pinterest", workspace_name="<your_workspace_name>")

@tool
@PinterestConnector.tool_utils
async def pinterest_execute(entity: str, action: str, params: dict | None = None):
    """Execute Pinterest connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.pinterest import PinterestConnector

connector = connect("pinterest", workspace_name="<your_workspace_name>")

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@PinterestConnector.tool_utils(framework="openai_agents")
async def pinterest_execute(entity: str, action: str, params: dict | None = None):
    """Execute Pinterest connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Pinterest Assistant", tools=[pinterest_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.pinterest import PinterestConnector

connector = connect("pinterest", workspace_name="<your_workspace_name>")

mcp = FastMCP("Pinterest Agent")

@mcp.tool
@PinterestConnector.tool_utils
async def pinterest_execute(entity: str, action: str, params: dict | None = None):
    """Execute Pinterest connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

Or pass credentials explicitly (equivalent, useful when you're not loading them from the environment):

**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.pinterest import PinterestConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = PinterestConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@PinterestConnector.tool_utils
async def pinterest_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.pinterest import PinterestConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = PinterestConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

@tool
@PinterestConnector.tool_utils
async def pinterest_execute(entity: str, action: str, params: dict | None = None):
    """Execute Pinterest connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk.connectors.pinterest import PinterestConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = PinterestConnector(
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
@PinterestConnector.tool_utils(framework="openai_agents")
async def pinterest_execute(entity: str, action: str, params: dict | None = None):
    """Execute Pinterest connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Pinterest Assistant", tools=[pinterest_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.pinterest import PinterestConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = PinterestConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

mcp = FastMCP("Pinterest Agent")

@mcp.tool
@PinterestConnector.tool_utils
async def pinterest_execute(entity: str, action: str, params: dict | None = None):
    """Execute Pinterest connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

### Open source

In open source mode, you provide API credentials directly to the connector.

**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.pinterest import PinterestConnector
from airbyte_agent_sdk.connectors.pinterest.models import PinterestAuthConfig

connector = PinterestConnector(
    auth_config=PinterestAuthConfig(
        refresh_token="<Pinterest OAuth2 refresh token.>",
        client_id="<Pinterest OAuth2 client ID.>",
        client_secret="<Pinterest OAuth2 client secret.>"
    )
)

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@PinterestConnector.tool_utils
async def pinterest_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.pinterest import PinterestConnector
from airbyte_agent_sdk.connectors.pinterest.models import PinterestAuthConfig

connector = PinterestConnector(
    auth_config=PinterestAuthConfig(
        refresh_token="<Pinterest OAuth2 refresh token.>",
        client_id="<Pinterest OAuth2 client ID.>",
        client_secret="<Pinterest OAuth2 client secret.>"
    )
)

@tool
@PinterestConnector.tool_utils
async def pinterest_execute(entity: str, action: str, params: dict | None = None):
    """Execute Pinterest connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk.connectors.pinterest import PinterestConnector
from airbyte_agent_sdk.connectors.pinterest.models import PinterestAuthConfig

connector = PinterestConnector(
    auth_config=PinterestAuthConfig(
        refresh_token="<Pinterest OAuth2 refresh token.>",
        client_id="<Pinterest OAuth2 client ID.>",
        client_secret="<Pinterest OAuth2 client secret.>"
    )
)

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@PinterestConnector.tool_utils(framework="openai_agents")
async def pinterest_execute(entity: str, action: str, params: dict | None = None):
    """Execute Pinterest connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Pinterest Assistant", tools=[pinterest_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.pinterest import PinterestConnector
from airbyte_agent_sdk.connectors.pinterest.models import PinterestAuthConfig

connector = PinterestConnector(
    auth_config=PinterestAuthConfig(
        refresh_token="<Pinterest OAuth2 refresh token.>",
        client_id="<Pinterest OAuth2 client ID.>",
        client_secret="<Pinterest OAuth2 client secret.>"
    )
)

mcp = FastMCP("Pinterest Agent")

@mcp.tool
@PinterestConnector.tool_utils
async def pinterest_execute(entity: str, action: str, params: dict | None = None):
    """Execute Pinterest connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

## Authentication

For all authentication options, see the connector's [authentication documentation](AUTH.md).

## Version information

**Connector version:** 0.1.5
