# Google-Analytics-Data-Api

The Google-Analytics-Data-Api agent connector is a Python package that equips AI agents to interact with Google-Analytics-Data-Api through strongly typed, well-documented tools. It's ready to use directly in your Python app, in an agent framework, or exposed through an MCP.

Google Analytics 4 (GA4) Data API connector for accessing website and app analytics data.
This connector provides access to pre-configured analytics reports including website overview,
active users, traffic sources, page performance, device breakdowns, and geographic locations.
Reports are retrieved via the GA4 Data API v1beta using configurable date ranges and
property IDs. Requires OAuth2 authentication with Google Analytics read-only scope.


## Example prompts

The Google-Analytics-Data-Api connector is optimized to handle prompts like these.

- Show me the website overview report
- List daily active users
- Show weekly active user trends
- Get the four-weekly active users report
- List traffic sources
- Show me page performance metrics
- Get device breakdown data
- List user locations
- What are the top traffic sources by sessions?
- Which pages have the highest bounce rate?
- What devices do most users browse from?
- Which countries send the most traffic?
- How has daily active users changed over the last month?

## Unsupported prompts

The Google-Analytics-Data-Api connector isn't currently able to handle prompts like these.

- Create a new GA4 property
- Delete analytics data
- Modify tracking configurations
- Run a custom report with arbitrary dimensions
- Access real-time analytics data

## Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Website Overview | [List](./REFERENCE.md#website-overview-list), [Context Store Search](./REFERENCE.md#website-overview-context-store-search) |
| Daily Active Users | [List](./REFERENCE.md#daily-active-users-list), [Context Store Search](./REFERENCE.md#daily-active-users-context-store-search) |
| Weekly Active Users | [List](./REFERENCE.md#weekly-active-users-list), [Context Store Search](./REFERENCE.md#weekly-active-users-context-store-search) |
| Four Weekly Active Users | [List](./REFERENCE.md#four-weekly-active-users-list), [Context Store Search](./REFERENCE.md#four-weekly-active-users-context-store-search) |
| Traffic Sources | [List](./REFERENCE.md#traffic-sources-list), [Context Store Search](./REFERENCE.md#traffic-sources-context-store-search) |
| Pages | [List](./REFERENCE.md#pages-list), [Context Store Search](./REFERENCE.md#pages-context-store-search) |
| Devices | [List](./REFERENCE.md#devices-list), [Context Store Search](./REFERENCE.md#devices-context-store-search) |
| Locations | [List](./REFERENCE.md#locations-list), [Context Store Search](./REFERENCE.md#locations-context-store-search) |


## Google-Analytics-Data-Api API docs

See the official [Google-Analytics-Data-Api API reference](https://developers.google.com/analytics/devguides/reporting/data/v1/rest).

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

The `connect()` factory returns a fully typed `GoogleAnalyticsDataApiConnector` and reads `AIRBYTE_CLIENT_ID` / `AIRBYTE_CLIENT_SECRET` from the environment:


**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.google_analytics_data_api import GoogleAnalyticsDataApiConnector

connector = connect("google-analytics-data-api", workspace_name="<your_workspace_name>")

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@GoogleAnalyticsDataApiConnector.tool_utils
async def google_analytics_data_api_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.google_analytics_data_api import GoogleAnalyticsDataApiConnector

connector = connect("google-analytics-data-api", workspace_name="<your_workspace_name>")

@tool
@GoogleAnalyticsDataApiConnector.tool_utils
async def google_analytics_data_api_execute(entity: str, action: str, params: dict | None = None):
    """Execute Google-Analytics-Data-Api connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.google_analytics_data_api import GoogleAnalyticsDataApiConnector

connector = connect("google-analytics-data-api", workspace_name="<your_workspace_name>")

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@GoogleAnalyticsDataApiConnector.tool_utils(framework="openai_agents")
async def google_analytics_data_api_execute(entity: str, action: str, params: dict | None = None):
    """Execute Google-Analytics-Data-Api connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Google-Analytics-Data-Api Assistant", tools=[google_analytics_data_api_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.google_analytics_data_api import GoogleAnalyticsDataApiConnector

connector = connect("google-analytics-data-api", workspace_name="<your_workspace_name>")

mcp = FastMCP("Google-Analytics-Data-Api Agent")

@mcp.tool
@GoogleAnalyticsDataApiConnector.tool_utils
async def google_analytics_data_api_execute(entity: str, action: str, params: dict | None = None):
    """Execute Google-Analytics-Data-Api connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

Or pass credentials explicitly (equivalent, useful when you're not loading them from the environment):

**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.google_analytics_data_api import GoogleAnalyticsDataApiConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = GoogleAnalyticsDataApiConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@GoogleAnalyticsDataApiConnector.tool_utils
async def google_analytics_data_api_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.google_analytics_data_api import GoogleAnalyticsDataApiConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = GoogleAnalyticsDataApiConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

@tool
@GoogleAnalyticsDataApiConnector.tool_utils
async def google_analytics_data_api_execute(entity: str, action: str, params: dict | None = None):
    """Execute Google-Analytics-Data-Api connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk.connectors.google_analytics_data_api import GoogleAnalyticsDataApiConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = GoogleAnalyticsDataApiConnector(
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
@GoogleAnalyticsDataApiConnector.tool_utils(framework="openai_agents")
async def google_analytics_data_api_execute(entity: str, action: str, params: dict | None = None):
    """Execute Google-Analytics-Data-Api connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Google-Analytics-Data-Api Assistant", tools=[google_analytics_data_api_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.google_analytics_data_api import GoogleAnalyticsDataApiConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = GoogleAnalyticsDataApiConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

mcp = FastMCP("Google-Analytics-Data-Api Agent")

@mcp.tool
@GoogleAnalyticsDataApiConnector.tool_utils
async def google_analytics_data_api_execute(entity: str, action: str, params: dict | None = None):
    """Execute Google-Analytics-Data-Api connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

### Open source

In open source mode, you provide API credentials directly to the connector.

**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.google_analytics_data_api import GoogleAnalyticsDataApiConnector
from airbyte_agent_sdk.connectors.google_analytics_data_api.models import GoogleAnalyticsDataApiAuthConfig

connector = GoogleAnalyticsDataApiConnector(
    auth_config=GoogleAnalyticsDataApiAuthConfig(
        client_id="<OAuth 2.0 Client ID from Google Cloud Console>",
        client_secret="<OAuth 2.0 Client Secret from Google Cloud Console>",
        refresh_token="<OAuth 2.0 Refresh Token for obtaining new access tokens>"
    )
)

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@GoogleAnalyticsDataApiConnector.tool_utils
async def google_analytics_data_api_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.google_analytics_data_api import GoogleAnalyticsDataApiConnector
from airbyte_agent_sdk.connectors.google_analytics_data_api.models import GoogleAnalyticsDataApiAuthConfig

connector = GoogleAnalyticsDataApiConnector(
    auth_config=GoogleAnalyticsDataApiAuthConfig(
        client_id="<OAuth 2.0 Client ID from Google Cloud Console>",
        client_secret="<OAuth 2.0 Client Secret from Google Cloud Console>",
        refresh_token="<OAuth 2.0 Refresh Token for obtaining new access tokens>"
    )
)

@tool
@GoogleAnalyticsDataApiConnector.tool_utils
async def google_analytics_data_api_execute(entity: str, action: str, params: dict | None = None):
    """Execute Google-Analytics-Data-Api connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk.connectors.google_analytics_data_api import GoogleAnalyticsDataApiConnector
from airbyte_agent_sdk.connectors.google_analytics_data_api.models import GoogleAnalyticsDataApiAuthConfig

connector = GoogleAnalyticsDataApiConnector(
    auth_config=GoogleAnalyticsDataApiAuthConfig(
        client_id="<OAuth 2.0 Client ID from Google Cloud Console>",
        client_secret="<OAuth 2.0 Client Secret from Google Cloud Console>",
        refresh_token="<OAuth 2.0 Refresh Token for obtaining new access tokens>"
    )
)

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@GoogleAnalyticsDataApiConnector.tool_utils(framework="openai_agents")
async def google_analytics_data_api_execute(entity: str, action: str, params: dict | None = None):
    """Execute Google-Analytics-Data-Api connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Google-Analytics-Data-Api Assistant", tools=[google_analytics_data_api_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.google_analytics_data_api import GoogleAnalyticsDataApiConnector
from airbyte_agent_sdk.connectors.google_analytics_data_api.models import GoogleAnalyticsDataApiAuthConfig

connector = GoogleAnalyticsDataApiConnector(
    auth_config=GoogleAnalyticsDataApiAuthConfig(
        client_id="<OAuth 2.0 Client ID from Google Cloud Console>",
        client_secret="<OAuth 2.0 Client Secret from Google Cloud Console>",
        refresh_token="<OAuth 2.0 Refresh Token for obtaining new access tokens>"
    )
)

mcp = FastMCP("Google-Analytics-Data-Api Agent")

@mcp.tool
@GoogleAnalyticsDataApiConnector.tool_utils
async def google_analytics_data_api_execute(entity: str, action: str, params: dict | None = None):
    """Execute Google-Analytics-Data-Api connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

## Authentication

For all authentication options, see the connector's [authentication documentation](AUTH.md).

## Version information

**Connector version:** 1.0.5
