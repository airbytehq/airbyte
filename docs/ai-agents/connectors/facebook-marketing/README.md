# Facebook-Marketing

The Facebook-Marketing agent connector is a Python package that equips AI agents to interact with Facebook-Marketing through strongly typed, well-documented tools. It's ready to use directly in your Python app, in an agent framework, or exposed through an MCP.

Facebook Marketing API connector for managing ad campaigns, ad sets, ads, creatives,
and accessing performance insights, pixel configuration, and event quality data.
This connector provides read access to Facebook Ads Manager data for analytics
and reporting purposes.


## Example prompts

The Facebook-Marketing connector is optimized to handle prompts like these.

- List all active campaigns in my ad account
- What ads are currently running in a recent campaign?
- List all ad creatives in my account
- What is the status of my campaigns?
- List all custom conversion events in my account
- Show me all ad images in my account
- What videos are available in my ad account?
- Create a new campaign called 'Summer Sale 2026' with traffic objective
- Pause my most recent campaign
- Create a new ad set with a $50 daily budget in my latest campaign
- Update the daily budget of my top performing ad set to $100
- Rename my most recent ad set to 'Holiday Promo'
- Create a new ad in my latest ad set
- Pause all ads in my most recent ad set
- List all pixels in my ad account
- Show me the event stats for my pixel
- What events is my Facebook pixel tracking?
- Search the Ad Library for political ads in the US
- Find ads about climate change in the Ad Library
- Show me Ad Library ads from a specific Facebook page
- Show me the ad sets with the highest daily budget
- Show me the performance insights for the last 7 days
- Which campaigns have the most spend this month?
- Show me ads with the highest click-through rate

## Unsupported prompts

The Facebook-Marketing connector isn't currently able to handle prompts like these.

- Delete this ad creative
- Delete this campaign
- Delete this ad set
- Delete this ad

## Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Current User | [Get](./REFERENCE.md#current-user-get) |
| Ad Accounts | [List](./REFERENCE.md#ad-accounts-list), [Get](./REFERENCE.md#ad-accounts-get), [Context Store Search](./REFERENCE.md#ad-accounts-context-store-search) |
| Campaigns | [List](./REFERENCE.md#campaigns-list), [Create](./REFERENCE.md#campaigns-create), [Get](./REFERENCE.md#campaigns-get), [Update](./REFERENCE.md#campaigns-update), [Context Store Search](./REFERENCE.md#campaigns-context-store-search) |
| Ad Sets | [List](./REFERENCE.md#ad-sets-list), [Create](./REFERENCE.md#ad-sets-create), [Get](./REFERENCE.md#ad-sets-get), [Update](./REFERENCE.md#ad-sets-update), [Context Store Search](./REFERENCE.md#ad-sets-context-store-search) |
| Ads | [List](./REFERENCE.md#ads-list), [Create](./REFERENCE.md#ads-create), [Get](./REFERENCE.md#ads-get), [Update](./REFERENCE.md#ads-update), [Context Store Search](./REFERENCE.md#ads-context-store-search) |
| Ad Creatives | [List](./REFERENCE.md#ad-creatives-list), [Context Store Search](./REFERENCE.md#ad-creatives-context-store-search) |
| Ads Insights | [List](./REFERENCE.md#ads-insights-list), [Context Store Search](./REFERENCE.md#ads-insights-context-store-search) |
| Custom Conversions | [List](./REFERENCE.md#custom-conversions-list), [Context Store Search](./REFERENCE.md#custom-conversions-context-store-search) |
| Images | [List](./REFERENCE.md#images-list), [Context Store Search](./REFERENCE.md#images-context-store-search) |
| Videos | [List](./REFERENCE.md#videos-list), [Context Store Search](./REFERENCE.md#videos-context-store-search) |
| Pixels | [List](./REFERENCE.md#pixels-list), [Get](./REFERENCE.md#pixels-get) |
| Pixel Stats | [List](./REFERENCE.md#pixel-stats-list) |
| Ad Library | [List](./REFERENCE.md#ad-library-list) |


## Facebook-Marketing API docs

See the official [Facebook-Marketing API reference](https://developers.facebook.com/docs/marketing-api/).

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

The `connect()` factory returns a fully typed `FacebookMarketingConnector` and reads `AIRBYTE_CLIENT_ID` / `AIRBYTE_CLIENT_SECRET` from the environment:


**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.facebook_marketing import FacebookMarketingConnector

connector = connect("facebook-marketing", workspace_name="<your_workspace_name>")

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@FacebookMarketingConnector.tool_utils
async def facebook_marketing_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.facebook_marketing import FacebookMarketingConnector

connector = connect("facebook-marketing", workspace_name="<your_workspace_name>")

@tool
@FacebookMarketingConnector.tool_utils
async def facebook_marketing_execute(entity: str, action: str, params: dict | None = None):
    """Execute Facebook-Marketing connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.facebook_marketing import FacebookMarketingConnector

connector = connect("facebook-marketing", workspace_name="<your_workspace_name>")

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@FacebookMarketingConnector.tool_utils(framework="openai_agents")
async def facebook_marketing_execute(entity: str, action: str, params: dict | None = None):
    """Execute Facebook-Marketing connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Facebook-Marketing Assistant", tools=[facebook_marketing_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.facebook_marketing import FacebookMarketingConnector

connector = connect("facebook-marketing", workspace_name="<your_workspace_name>")

mcp = FastMCP("Facebook-Marketing Agent")

@mcp.tool
@FacebookMarketingConnector.tool_utils
async def facebook_marketing_execute(entity: str, action: str, params: dict | None = None):
    """Execute Facebook-Marketing connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

Or pass credentials explicitly (equivalent, useful when you're not loading them from the environment):

**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.facebook_marketing import FacebookMarketingConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = FacebookMarketingConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@FacebookMarketingConnector.tool_utils
async def facebook_marketing_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.facebook_marketing import FacebookMarketingConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = FacebookMarketingConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

@tool
@FacebookMarketingConnector.tool_utils
async def facebook_marketing_execute(entity: str, action: str, params: dict | None = None):
    """Execute Facebook-Marketing connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk.connectors.facebook_marketing import FacebookMarketingConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = FacebookMarketingConnector(
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
@FacebookMarketingConnector.tool_utils(framework="openai_agents")
async def facebook_marketing_execute(entity: str, action: str, params: dict | None = None):
    """Execute Facebook-Marketing connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Facebook-Marketing Assistant", tools=[facebook_marketing_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.facebook_marketing import FacebookMarketingConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = FacebookMarketingConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

mcp = FastMCP("Facebook-Marketing Agent")

@mcp.tool
@FacebookMarketingConnector.tool_utils
async def facebook_marketing_execute(entity: str, action: str, params: dict | None = None):
    """Execute Facebook-Marketing connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

### Open source

In open source mode, you provide API credentials directly to the connector.

**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.facebook_marketing import FacebookMarketingConnector
from airbyte_agent_sdk.connectors.facebook_marketing.models import FacebookMarketingServiceAccountKeyAuthenticationAuthConfig

connector = FacebookMarketingConnector(
    auth_config=FacebookMarketingServiceAccountKeyAuthenticationAuthConfig(
        account_key="<Facebook long-lived access token for Service Account authentication>"
    )
)

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@FacebookMarketingConnector.tool_utils
async def facebook_marketing_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.facebook_marketing import FacebookMarketingConnector
from airbyte_agent_sdk.connectors.facebook_marketing.models import FacebookMarketingServiceAccountKeyAuthenticationAuthConfig

connector = FacebookMarketingConnector(
    auth_config=FacebookMarketingServiceAccountKeyAuthenticationAuthConfig(
        account_key="<Facebook long-lived access token for Service Account authentication>"
    )
)

@tool
@FacebookMarketingConnector.tool_utils
async def facebook_marketing_execute(entity: str, action: str, params: dict | None = None):
    """Execute Facebook-Marketing connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk.connectors.facebook_marketing import FacebookMarketingConnector
from airbyte_agent_sdk.connectors.facebook_marketing.models import FacebookMarketingServiceAccountKeyAuthenticationAuthConfig

connector = FacebookMarketingConnector(
    auth_config=FacebookMarketingServiceAccountKeyAuthenticationAuthConfig(
        account_key="<Facebook long-lived access token for Service Account authentication>"
    )
)

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@FacebookMarketingConnector.tool_utils(framework="openai_agents")
async def facebook_marketing_execute(entity: str, action: str, params: dict | None = None):
    """Execute Facebook-Marketing connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Facebook-Marketing Assistant", tools=[facebook_marketing_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.facebook_marketing import FacebookMarketingConnector
from airbyte_agent_sdk.connectors.facebook_marketing.models import FacebookMarketingServiceAccountKeyAuthenticationAuthConfig

connector = FacebookMarketingConnector(
    auth_config=FacebookMarketingServiceAccountKeyAuthenticationAuthConfig(
        account_key="<Facebook long-lived access token for Service Account authentication>"
    )
)

mcp = FastMCP("Facebook-Marketing Agent")

@mcp.tool
@FacebookMarketingConnector.tool_utils
async def facebook_marketing_execute(entity: str, action: str, params: dict | None = None):
    """Execute Facebook-Marketing connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

## Authentication

For all authentication options, see the connector's [authentication documentation](AUTH.md).

## Version information

**Connector version:** 1.0.24
