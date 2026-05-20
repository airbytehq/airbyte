# Linkedin-Ads

The Linkedin-Ads agent connector is a Python package that equips AI agents to interact with Linkedin-Ads through strongly typed, well-documented tools. It's ready to use directly in your Python app, in an agent framework, or exposed through an MCP.

Connector for the LinkedIn Ads Marketing API. Provides access to ad accounts, campaigns, campaign groups, creatives, conversions, and ad analytics data. Supports OAuth 2.0 and direct access token authentication. Use this connector to retrieve advertising performance metrics, manage campaign structures, and monitor creative assets across your LinkedIn advertising accounts.


## Example prompts

The Linkedin-Ads connector is optimized to handle prompts like these.

- List all my LinkedIn ad accounts
- Show me all campaigns in my ad account
- List all campaign groups
- Show me the creatives for my campaigns
- List all conversions configured for my ad accounts
- Show me account users for my LinkedIn ads accounts
- Which campaigns have the highest click-through rate?
- What is the total ad spend across all campaigns this month?
- Show me campaigns with status ACTIVE
- Which creatives have the most impressions?
- Compare campaign performance by cost type

## Unsupported prompts

The Linkedin-Ads connector isn't currently able to handle prompts like these.

- Create a new campaign
- Update campaign budgets
- Delete an ad creative
- Pause a campaign

## Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Accounts | [List](./REFERENCE.md#accounts-list), [Get](./REFERENCE.md#accounts-get), [Context Store Search](./REFERENCE.md#accounts-context-store-search) |
| Account Users | [List](./REFERENCE.md#account-users-list), [Context Store Search](./REFERENCE.md#account-users-context-store-search) |
| Campaigns | [List](./REFERENCE.md#campaigns-list), [Get](./REFERENCE.md#campaigns-get), [Context Store Search](./REFERENCE.md#campaigns-context-store-search) |
| Campaign Groups | [List](./REFERENCE.md#campaign-groups-list), [Get](./REFERENCE.md#campaign-groups-get), [Context Store Search](./REFERENCE.md#campaign-groups-context-store-search) |
| Creatives | [List](./REFERENCE.md#creatives-list), [Get](./REFERENCE.md#creatives-get), [Context Store Search](./REFERENCE.md#creatives-context-store-search) |
| Conversions | [List](./REFERENCE.md#conversions-list), [Get](./REFERENCE.md#conversions-get), [Context Store Search](./REFERENCE.md#conversions-context-store-search) |
| Ad Campaign Analytics | [List](./REFERENCE.md#ad-campaign-analytics-list), [Context Store Search](./REFERENCE.md#ad-campaign-analytics-context-store-search) |
| Ad Creative Analytics | [List](./REFERENCE.md#ad-creative-analytics-list), [Context Store Search](./REFERENCE.md#ad-creative-analytics-context-store-search) |


## Linkedin-Ads API docs

See the official [Linkedin-Ads API reference](https://learn.microsoft.com/en-us/linkedin/marketing/).

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

The `connect()` factory returns a fully typed `LinkedinAdsConnector` and reads `AIRBYTE_CLIENT_ID` / `AIRBYTE_CLIENT_SECRET` from the environment:


**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.linkedin_ads import LinkedinAdsConnector

connector = connect("linkedin-ads", workspace_name="<your_workspace_name>")

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@LinkedinAdsConnector.tool_utils
async def linkedin_ads_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.linkedin_ads import LinkedinAdsConnector

connector = connect("linkedin-ads", workspace_name="<your_workspace_name>")

@tool
@LinkedinAdsConnector.tool_utils
async def linkedin_ads_execute(entity: str, action: str, params: dict | None = None):
    """Execute Linkedin-Ads connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.linkedin_ads import LinkedinAdsConnector

connector = connect("linkedin-ads", workspace_name="<your_workspace_name>")

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@LinkedinAdsConnector.tool_utils(framework="openai_agents")
async def linkedin_ads_execute(entity: str, action: str, params: dict | None = None):
    """Execute Linkedin-Ads connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Linkedin-Ads Assistant", tools=[linkedin_ads_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.linkedin_ads import LinkedinAdsConnector

connector = connect("linkedin-ads", workspace_name="<your_workspace_name>")

mcp = FastMCP("Linkedin-Ads Agent")

@mcp.tool
@LinkedinAdsConnector.tool_utils
async def linkedin_ads_execute(entity: str, action: str, params: dict | None = None):
    """Execute Linkedin-Ads connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

Or pass credentials explicitly (equivalent, useful when you're not loading them from the environment):

**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.linkedin_ads import LinkedinAdsConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = LinkedinAdsConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@LinkedinAdsConnector.tool_utils
async def linkedin_ads_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.linkedin_ads import LinkedinAdsConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = LinkedinAdsConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

@tool
@LinkedinAdsConnector.tool_utils
async def linkedin_ads_execute(entity: str, action: str, params: dict | None = None):
    """Execute Linkedin-Ads connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk.connectors.linkedin_ads import LinkedinAdsConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = LinkedinAdsConnector(
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
@LinkedinAdsConnector.tool_utils(framework="openai_agents")
async def linkedin_ads_execute(entity: str, action: str, params: dict | None = None):
    """Execute Linkedin-Ads connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Linkedin-Ads Assistant", tools=[linkedin_ads_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.linkedin_ads import LinkedinAdsConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = LinkedinAdsConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

mcp = FastMCP("Linkedin-Ads Agent")

@mcp.tool
@LinkedinAdsConnector.tool_utils
async def linkedin_ads_execute(entity: str, action: str, params: dict | None = None):
    """Execute Linkedin-Ads connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

### Open source

In open source mode, you provide API credentials directly to the connector.

**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.linkedin_ads import LinkedinAdsConnector
from airbyte_agent_sdk.connectors.linkedin_ads.models import LinkedinAdsAuthConfig

connector = LinkedinAdsConnector(
    auth_config=LinkedinAdsAuthConfig(
        refresh_token="<OAuth 2.0 refresh token for automatic renewal>",
        client_id="<OAuth 2.0 application client ID>",
        client_secret="<OAuth 2.0 application client secret>"
    )
)

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@LinkedinAdsConnector.tool_utils
async def linkedin_ads_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.linkedin_ads import LinkedinAdsConnector
from airbyte_agent_sdk.connectors.linkedin_ads.models import LinkedinAdsAuthConfig

connector = LinkedinAdsConnector(
    auth_config=LinkedinAdsAuthConfig(
        refresh_token="<OAuth 2.0 refresh token for automatic renewal>",
        client_id="<OAuth 2.0 application client ID>",
        client_secret="<OAuth 2.0 application client secret>"
    )
)

@tool
@LinkedinAdsConnector.tool_utils
async def linkedin_ads_execute(entity: str, action: str, params: dict | None = None):
    """Execute Linkedin-Ads connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk.connectors.linkedin_ads import LinkedinAdsConnector
from airbyte_agent_sdk.connectors.linkedin_ads.models import LinkedinAdsAuthConfig

connector = LinkedinAdsConnector(
    auth_config=LinkedinAdsAuthConfig(
        refresh_token="<OAuth 2.0 refresh token for automatic renewal>",
        client_id="<OAuth 2.0 application client ID>",
        client_secret="<OAuth 2.0 application client secret>"
    )
)

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@LinkedinAdsConnector.tool_utils(framework="openai_agents")
async def linkedin_ads_execute(entity: str, action: str, params: dict | None = None):
    """Execute Linkedin-Ads connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Linkedin-Ads Assistant", tools=[linkedin_ads_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.linkedin_ads import LinkedinAdsConnector
from airbyte_agent_sdk.connectors.linkedin_ads.models import LinkedinAdsAuthConfig

connector = LinkedinAdsConnector(
    auth_config=LinkedinAdsAuthConfig(
        refresh_token="<OAuth 2.0 refresh token for automatic renewal>",
        client_id="<OAuth 2.0 application client ID>",
        client_secret="<OAuth 2.0 application client secret>"
    )
)

mcp = FastMCP("Linkedin-Ads Agent")

@mcp.tool
@LinkedinAdsConnector.tool_utils
async def linkedin_ads_execute(entity: str, action: str, params: dict | None = None):
    """Execute Linkedin-Ads connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

## Authentication

For all authentication options, see the connector's [authentication documentation](AUTH.md).

## Version information

**Connector version:** 1.0.5
