# Google-Search-Console

The Google-Search-Console agent connector is a Python package that equips AI agents to interact with Google-Search-Console through strongly typed, well-documented tools. It's ready to use directly in your Python app, in an agent framework, or exposed through an MCP.

Connector for the Google Search Console API. Provides access to website search performance data including clicks, impressions, CTR, and average position. Supports listing verified sites, sitemaps, and querying search analytics data broken down by date, country, device, page, and query dimensions.


## Example prompts

The Google-Search-Console connector is optimized to handle prompts like these.

- List all my verified sites in Search Console
- Show me the sitemaps for my website
- Get search analytics by date for the last 7 days
- Show search performance broken down by country
- What devices are people using to find my site?
- Which pages get the most clicks?
- What queries bring the most traffic to my site?
- Which country has the highest CTR for my site?
- What are my top 10 search queries by impressions?
- Compare mobile vs desktop click-through rates
- Which pages have the worst average position?
- Show me search performance trends over the last month

## Unsupported prompts

The Google-Search-Console connector isn't currently able to handle prompts like these.

- Submit a new sitemap
- Add a new site to Search Console
- Remove a site from Search Console
- Inspect a URL's index status
- Request indexing for a page

## Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Sites | [List](./REFERENCE.md#sites-list), [Get](./REFERENCE.md#sites-get), [Context Store Search](./REFERENCE.md#sites-context-store-search) |
| Sitemaps | [List](./REFERENCE.md#sitemaps-list), [Get](./REFERENCE.md#sitemaps-get), [Context Store Search](./REFERENCE.md#sitemaps-context-store-search) |
| Search Analytics By Date | [List](./REFERENCE.md#search-analytics-by-date-list), [Context Store Search](./REFERENCE.md#search-analytics-by-date-context-store-search) |
| Search Analytics By Country | [List](./REFERENCE.md#search-analytics-by-country-list), [Context Store Search](./REFERENCE.md#search-analytics-by-country-context-store-search) |
| Search Analytics By Device | [List](./REFERENCE.md#search-analytics-by-device-list), [Context Store Search](./REFERENCE.md#search-analytics-by-device-context-store-search) |
| Search Analytics By Page | [List](./REFERENCE.md#search-analytics-by-page-list), [Context Store Search](./REFERENCE.md#search-analytics-by-page-context-store-search) |
| Search Analytics By Query | [List](./REFERENCE.md#search-analytics-by-query-list), [Context Store Search](./REFERENCE.md#search-analytics-by-query-context-store-search) |
| Search Analytics All Fields | [List](./REFERENCE.md#search-analytics-all-fields-list), [Context Store Search](./REFERENCE.md#search-analytics-all-fields-context-store-search) |


## Google-Search-Console API docs

See the official [Google-Search-Console API reference](https://developers.google.com/webmaster-tools/v1/api_reference_index).

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

The `connect()` factory returns a fully typed `GoogleSearchConsoleConnector` and reads `AIRBYTE_CLIENT_ID` / `AIRBYTE_CLIENT_SECRET` from the environment:


**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.google_search_console import GoogleSearchConsoleConnector

connector = connect("google-search-console", workspace_name="<your_workspace_name>")

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@GoogleSearchConsoleConnector.tool_utils
async def google_search_console_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.google_search_console import GoogleSearchConsoleConnector

connector = connect("google-search-console", workspace_name="<your_workspace_name>")

@tool
@GoogleSearchConsoleConnector.tool_utils
async def google_search_console_execute(entity: str, action: str, params: dict | None = None):
    """Execute Google-Search-Console connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.google_search_console import GoogleSearchConsoleConnector

connector = connect("google-search-console", workspace_name="<your_workspace_name>")

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@GoogleSearchConsoleConnector.tool_utils(framework="openai_agents")
async def google_search_console_execute(entity: str, action: str, params: dict | None = None):
    """Execute Google-Search-Console connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Google-Search-Console Assistant", tools=[google_search_console_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.google_search_console import GoogleSearchConsoleConnector

connector = connect("google-search-console", workspace_name="<your_workspace_name>")

mcp = FastMCP("Google-Search-Console Agent")

@mcp.tool
@GoogleSearchConsoleConnector.tool_utils
async def google_search_console_execute(entity: str, action: str, params: dict | None = None):
    """Execute Google-Search-Console connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

Or pass credentials explicitly (equivalent, useful when you're not loading them from the environment):

**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.google_search_console import GoogleSearchConsoleConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = GoogleSearchConsoleConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@GoogleSearchConsoleConnector.tool_utils
async def google_search_console_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.google_search_console import GoogleSearchConsoleConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = GoogleSearchConsoleConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

@tool
@GoogleSearchConsoleConnector.tool_utils
async def google_search_console_execute(entity: str, action: str, params: dict | None = None):
    """Execute Google-Search-Console connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk.connectors.google_search_console import GoogleSearchConsoleConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = GoogleSearchConsoleConnector(
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
@GoogleSearchConsoleConnector.tool_utils(framework="openai_agents")
async def google_search_console_execute(entity: str, action: str, params: dict | None = None):
    """Execute Google-Search-Console connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Google-Search-Console Assistant", tools=[google_search_console_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.google_search_console import GoogleSearchConsoleConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = GoogleSearchConsoleConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

mcp = FastMCP("Google-Search-Console Agent")

@mcp.tool
@GoogleSearchConsoleConnector.tool_utils
async def google_search_console_execute(entity: str, action: str, params: dict | None = None):
    """Execute Google-Search-Console connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

### Open source

In open source mode, you provide API credentials directly to the connector.

**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.google_search_console import GoogleSearchConsoleConnector
from airbyte_agent_sdk.connectors.google_search_console.models import GoogleSearchConsoleAuthConfig

connector = GoogleSearchConsoleConnector(
    auth_config=GoogleSearchConsoleAuthConfig(
        client_id="<The client ID of your Google Search Console developer application.>",
        client_secret="<The client secret of your Google Search Console developer application.>",
        refresh_token="<The refresh token for obtaining new access tokens.>"
    )
)

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@GoogleSearchConsoleConnector.tool_utils
async def google_search_console_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.google_search_console import GoogleSearchConsoleConnector
from airbyte_agent_sdk.connectors.google_search_console.models import GoogleSearchConsoleAuthConfig

connector = GoogleSearchConsoleConnector(
    auth_config=GoogleSearchConsoleAuthConfig(
        client_id="<The client ID of your Google Search Console developer application.>",
        client_secret="<The client secret of your Google Search Console developer application.>",
        refresh_token="<The refresh token for obtaining new access tokens.>"
    )
)

@tool
@GoogleSearchConsoleConnector.tool_utils
async def google_search_console_execute(entity: str, action: str, params: dict | None = None):
    """Execute Google-Search-Console connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk.connectors.google_search_console import GoogleSearchConsoleConnector
from airbyte_agent_sdk.connectors.google_search_console.models import GoogleSearchConsoleAuthConfig

connector = GoogleSearchConsoleConnector(
    auth_config=GoogleSearchConsoleAuthConfig(
        client_id="<The client ID of your Google Search Console developer application.>",
        client_secret="<The client secret of your Google Search Console developer application.>",
        refresh_token="<The refresh token for obtaining new access tokens.>"
    )
)

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@GoogleSearchConsoleConnector.tool_utils(framework="openai_agents")
async def google_search_console_execute(entity: str, action: str, params: dict | None = None):
    """Execute Google-Search-Console connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Google-Search-Console Assistant", tools=[google_search_console_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.google_search_console import GoogleSearchConsoleConnector
from airbyte_agent_sdk.connectors.google_search_console.models import GoogleSearchConsoleAuthConfig

connector = GoogleSearchConsoleConnector(
    auth_config=GoogleSearchConsoleAuthConfig(
        client_id="<The client ID of your Google Search Console developer application.>",
        client_secret="<The client secret of your Google Search Console developer application.>",
        refresh_token="<The refresh token for obtaining new access tokens.>"
    )
)

mcp = FastMCP("Google-Search-Console Agent")

@mcp.tool
@GoogleSearchConsoleConnector.tool_utils
async def google_search_console_execute(entity: str, action: str, params: dict | None = None):
    """Execute Google-Search-Console connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

## Authentication

For all authentication options, see the connector's [authentication documentation](AUTH.md).

## Version information

**Connector version:** 1.0.3
