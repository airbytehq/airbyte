# Snapchat-Marketing

The Snapchat-Marketing agent connector is a Python package that equips AI agents to interact with Snapchat-Marketing through strongly typed, well-documented tools. It's ready to use directly in your Python app, in an agent framework, or exposed through an MCP.

Connector for the Snapchat Marketing API (Ads API). Provides access to Snapchat advertising entities including organizations, ad accounts, campaigns, ad squads, ads, creatives, media, and audience segments. Supports OAuth2 authentication with automatic token refresh.


## Example prompts

The Snapchat-Marketing connector is optimized to handle prompts like these.

- List all organizations I belong to
- Show me all ad accounts for my organization
- List all campaigns in my ad account
- Show me the ad squads for my ad account
- List all ads in my ad account
- Show me the creatives for my ad account
- List all media files in my ad account
- Show me the audience segments in my ad account
- Which campaigns are currently active?
- What ad squads have the highest daily budget?
- Show me ads that are pending review
- Find campaigns created in the last month

## Unsupported prompts

The Snapchat-Marketing connector isn't currently able to handle prompts like these.

- Create a new campaign
- Update an ad's status
- Delete a creative
- Show me ad performance statistics

## Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Organizations | [List](./REFERENCE.md#organizations-list), [Get](./REFERENCE.md#organizations-get), [Context Store Search](./REFERENCE.md#organizations-context-store-search) |
| Adaccounts | [List](./REFERENCE.md#adaccounts-list), [Get](./REFERENCE.md#adaccounts-get), [Context Store Search](./REFERENCE.md#adaccounts-context-store-search) |
| Campaigns | [List](./REFERENCE.md#campaigns-list), [Get](./REFERENCE.md#campaigns-get), [Context Store Search](./REFERENCE.md#campaigns-context-store-search) |
| Adsquads | [List](./REFERENCE.md#adsquads-list), [Get](./REFERENCE.md#adsquads-get), [Context Store Search](./REFERENCE.md#adsquads-context-store-search) |
| Ads | [List](./REFERENCE.md#ads-list), [Get](./REFERENCE.md#ads-get), [Context Store Search](./REFERENCE.md#ads-context-store-search) |
| Creatives | [List](./REFERENCE.md#creatives-list), [Get](./REFERENCE.md#creatives-get), [Context Store Search](./REFERENCE.md#creatives-context-store-search) |
| Media | [List](./REFERENCE.md#media-list), [Get](./REFERENCE.md#media-get), [Context Store Search](./REFERENCE.md#media-context-store-search) |
| Segments | [List](./REFERENCE.md#segments-list), [Get](./REFERENCE.md#segments-get), [Context Store Search](./REFERENCE.md#segments-context-store-search) |


## Snapchat-Marketing API docs

See the official [Snapchat-Marketing API reference](https://developers.snap.com/api/marketing-api/Ads-API/introduction).

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

The `connect()` factory returns a fully typed `SnapchatMarketingConnector` and reads `AIRBYTE_CLIENT_ID` / `AIRBYTE_CLIENT_SECRET` from the environment:


**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.snapchat_marketing import SnapchatMarketingConnector

connector = connect("snapchat-marketing", workspace_name="<your_workspace_name>")

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@SnapchatMarketingConnector.tool_utils
async def snapchat_marketing_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.snapchat_marketing import SnapchatMarketingConnector

connector = connect("snapchat-marketing", workspace_name="<your_workspace_name>")

@tool
@SnapchatMarketingConnector.tool_utils
async def snapchat_marketing_execute(entity: str, action: str, params: dict | None = None):
    """Execute Snapchat-Marketing connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.snapchat_marketing import SnapchatMarketingConnector

connector = connect("snapchat-marketing", workspace_name="<your_workspace_name>")

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@SnapchatMarketingConnector.tool_utils(framework="openai_agents")
async def snapchat_marketing_execute(entity: str, action: str, params: dict | None = None):
    """Execute Snapchat-Marketing connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Snapchat-Marketing Assistant", tools=[snapchat_marketing_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.snapchat_marketing import SnapchatMarketingConnector

connector = connect("snapchat-marketing", workspace_name="<your_workspace_name>")

mcp = FastMCP("Snapchat-Marketing Agent")

@mcp.tool
@SnapchatMarketingConnector.tool_utils
async def snapchat_marketing_execute(entity: str, action: str, params: dict | None = None):
    """Execute Snapchat-Marketing connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

Or pass credentials explicitly (equivalent, useful when you're not loading them from the environment):

**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.snapchat_marketing import SnapchatMarketingConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = SnapchatMarketingConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@SnapchatMarketingConnector.tool_utils
async def snapchat_marketing_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.snapchat_marketing import SnapchatMarketingConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = SnapchatMarketingConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

@tool
@SnapchatMarketingConnector.tool_utils
async def snapchat_marketing_execute(entity: str, action: str, params: dict | None = None):
    """Execute Snapchat-Marketing connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk.connectors.snapchat_marketing import SnapchatMarketingConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = SnapchatMarketingConnector(
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
@SnapchatMarketingConnector.tool_utils(framework="openai_agents")
async def snapchat_marketing_execute(entity: str, action: str, params: dict | None = None):
    """Execute Snapchat-Marketing connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Snapchat-Marketing Assistant", tools=[snapchat_marketing_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.snapchat_marketing import SnapchatMarketingConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = SnapchatMarketingConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

mcp = FastMCP("Snapchat-Marketing Agent")

@mcp.tool
@SnapchatMarketingConnector.tool_utils
async def snapchat_marketing_execute(entity: str, action: str, params: dict | None = None):
    """Execute Snapchat-Marketing connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

### Open source

In open source mode, you provide API credentials directly to the connector.

**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.snapchat_marketing import SnapchatMarketingConnector
from airbyte_agent_sdk.connectors.snapchat_marketing.models import SnapchatMarketingAuthConfig

connector = SnapchatMarketingConnector(
    auth_config=SnapchatMarketingAuthConfig(
        client_id="<The Client ID of your Snapchat developer application>",
        client_secret="<The Client Secret of your Snapchat developer application>",
        refresh_token="<Refresh Token to renew the expired Access Token>"
    )
)

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@SnapchatMarketingConnector.tool_utils
async def snapchat_marketing_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.snapchat_marketing import SnapchatMarketingConnector
from airbyte_agent_sdk.connectors.snapchat_marketing.models import SnapchatMarketingAuthConfig

connector = SnapchatMarketingConnector(
    auth_config=SnapchatMarketingAuthConfig(
        client_id="<The Client ID of your Snapchat developer application>",
        client_secret="<The Client Secret of your Snapchat developer application>",
        refresh_token="<Refresh Token to renew the expired Access Token>"
    )
)

@tool
@SnapchatMarketingConnector.tool_utils
async def snapchat_marketing_execute(entity: str, action: str, params: dict | None = None):
    """Execute Snapchat-Marketing connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk.connectors.snapchat_marketing import SnapchatMarketingConnector
from airbyte_agent_sdk.connectors.snapchat_marketing.models import SnapchatMarketingAuthConfig

connector = SnapchatMarketingConnector(
    auth_config=SnapchatMarketingAuthConfig(
        client_id="<The Client ID of your Snapchat developer application>",
        client_secret="<The Client Secret of your Snapchat developer application>",
        refresh_token="<Refresh Token to renew the expired Access Token>"
    )
)

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@SnapchatMarketingConnector.tool_utils(framework="openai_agents")
async def snapchat_marketing_execute(entity: str, action: str, params: dict | None = None):
    """Execute Snapchat-Marketing connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Snapchat-Marketing Assistant", tools=[snapchat_marketing_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.snapchat_marketing import SnapchatMarketingConnector
from airbyte_agent_sdk.connectors.snapchat_marketing.models import SnapchatMarketingAuthConfig

connector = SnapchatMarketingConnector(
    auth_config=SnapchatMarketingAuthConfig(
        client_id="<The Client ID of your Snapchat developer application>",
        client_secret="<The Client Secret of your Snapchat developer application>",
        refresh_token="<Refresh Token to renew the expired Access Token>"
    )
)

mcp = FastMCP("Snapchat-Marketing Agent")

@mcp.tool
@SnapchatMarketingConnector.tool_utils
async def snapchat_marketing_execute(entity: str, action: str, params: dict | None = None):
    """Execute Snapchat-Marketing connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

## Authentication

For all authentication options, see the connector's [authentication documentation](AUTH.md).

## Version information

**Connector version:** 1.0.5
