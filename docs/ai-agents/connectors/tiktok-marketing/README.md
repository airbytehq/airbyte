# Tiktok-Marketing

The Tiktok-Marketing agent connector is a Python package that equips AI agents to interact with Tiktok-Marketing through strongly typed, well-documented tools. It's ready to use directly in your Python app, in an agent framework, or exposed through an MCP.

Connector for the TikTok Marketing API (Business API v1.3). Provides access to advertiser accounts, campaigns, ad groups, ads, audiences, creative assets (images and videos), Spark Ads, product catalogs, and daily performance reports at the advertiser, campaign, ad group, and ad levels. Requires an Access Token from the TikTok for Business platform. All list operations require an advertiser_id parameter to scope results to a specific advertiser account.

## Example prompts

The Tiktok-Marketing connector is optimized to handle prompts like these.

- List all my TikTok advertisers
- Show me all campaigns for my advertiser account
- List all ad groups
- Show me all ads
- List my custom audiences
- Show me all creative asset images
- List creative asset videos
- Show me daily ad performance reports
- Get campaign performance metrics for the last 30 days
- Show me advertiser spend reports
- Show me hourly ad performance reports
- Get lifetime ad performance metrics
- List all Spark Ad posts
- Show me my product catalogs
- Which campaigns have the highest budget?
- Find all paused ad groups
- What ads were created last month?
- Show campaigns with lifetime budget mode
- Which ads had the most impressions yesterday?
- What is my total ad spend this month?
- Which campaigns have the highest click-through rate?
- Which Spark Ads are currently authorized?
- Find catalogs with the most products

## Unsupported prompts

The Tiktok-Marketing connector isn't currently able to handle prompts like these.

- Create a new campaign
- Update ad group targeting
- Delete an ad

## Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Advertisers | [List](./REFERENCE.md#advertisers-list), [Context Store Search](./REFERENCE.md#advertisers-context-store-search) |
| Campaigns | [List](./REFERENCE.md#campaigns-list), [Context Store Search](./REFERENCE.md#campaigns-context-store-search) |
| Ad Groups | [List](./REFERENCE.md#ad-groups-list), [Context Store Search](./REFERENCE.md#ad-groups-context-store-search) |
| Ads | [List](./REFERENCE.md#ads-list), [Context Store Search](./REFERENCE.md#ads-context-store-search) |
| Audiences | [List](./REFERENCE.md#audiences-list), [Context Store Search](./REFERENCE.md#audiences-context-store-search) |
| Creative Assets Images | [List](./REFERENCE.md#creative-assets-images-list), [Context Store Search](./REFERENCE.md#creative-assets-images-context-store-search) |
| Creative Assets Videos | [List](./REFERENCE.md#creative-assets-videos-list), [Context Store Search](./REFERENCE.md#creative-assets-videos-context-store-search) |
| Spark Ads | [List](./REFERENCE.md#spark-ads-list), [Context Store Search](./REFERENCE.md#spark-ads-context-store-search) |
| Catalogs | [List](./REFERENCE.md#catalogs-list) |
| Advertisers Reports Daily | [List](./REFERENCE.md#advertisers-reports-daily-list), [Context Store Search](./REFERENCE.md#advertisers-reports-daily-context-store-search) |
| Campaigns Reports Daily | [List](./REFERENCE.md#campaigns-reports-daily-list), [Context Store Search](./REFERENCE.md#campaigns-reports-daily-context-store-search) |
| Ad Groups Reports Daily | [List](./REFERENCE.md#ad-groups-reports-daily-list), [Context Store Search](./REFERENCE.md#ad-groups-reports-daily-context-store-search) |
| Ads Reports Daily | [List](./REFERENCE.md#ads-reports-daily-list), [Context Store Search](./REFERENCE.md#ads-reports-daily-context-store-search) |
| Ads Reports Hourly | [List](./REFERENCE.md#ads-reports-hourly-list), [Context Store Search](./REFERENCE.md#ads-reports-hourly-context-store-search) |
| Ads Reports Lifetime | [List](./REFERENCE.md#ads-reports-lifetime-list), [Context Store Search](./REFERENCE.md#ads-reports-lifetime-context-store-search) |


## Tiktok-Marketing API docs

See the official [Tiktok-Marketing API reference](https://business-api.tiktok.com/portal/docs?id=1740302848670722).

## Interfaces

Use the Tiktok-Marketing connector through the Airbyte Agent CLI, the Python SDK, or the API.

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
  "name": "tiktok-marketing"
}'
```

Describe the connector to see its supported entities and actions:

```bash
airbyte-agent connectors describe --json '{
  "workspace": "<your_workspace_name>",
  "name": "tiktok-marketing"
}'
```

Execute an action:

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "tiktok-marketing",
  "entity": "advertisers",
  "action": "list"
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

The `connect()` factory returns a fully typed `TiktokMarketingConnector` and reads `AIRBYTE_CLIENT_ID` / `AIRBYTE_CLIENT_SECRET` from the environment:


The recommended pattern is `build_connector_tools`, which gives the agent three tools bound to this connector: `inspect_connector`, `read_skill_docs`, and `execute`. The agent can inspect the connector, read only the skill-doc section it needs, and then execute:

```text
inspect_connector() -> read_skill_docs() -> read_skill_docs(section="...") -> execute(entity, action, params)
```

**Pydantic AI**

```python title="Pydantic AI"
from airbyte_agent_sdk import build_connector_tools
from pydantic_ai import Agent
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.tiktok_marketing import TiktokMarketingConnector

connector = connect("tiktok-marketing", workspace_name="<your_workspace_name>")

tools = build_connector_tools(connector, framework="pydantic_ai")
agent = Agent("openai:gpt-4o", tools=tools.as_list())
```

**LangChain**

```python title="LangChain"
from airbyte_agent_sdk import build_connector_tools
from langchain_core.tools import StructuredTool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.tiktok_marketing import TiktokMarketingConnector

connector = connect("tiktok-marketing", workspace_name="<your_workspace_name>")

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
from airbyte_agent_sdk.connectors.tiktok_marketing import TiktokMarketingConnector

connector = connect("tiktok-marketing", workspace_name="<your_workspace_name>")

tools = build_connector_tools(connector, framework="openai_agents")
openai_tools = [function_tool(tool, strict_mode=False) for tool in tools.as_list()]

agent = Agent(name="Tiktok-Marketing Assistant", tools=openai_tools)
```

**FastMCP**

```python title="FastMCP"
from airbyte_agent_sdk import build_connector_tools
from fastmcp import FastMCP
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.tiktok_marketing import TiktokMarketingConnector

connector = connect("tiktok-marketing", workspace_name="<your_workspace_name>")

mcp = FastMCP("Tiktok-Marketing Agent")

for tool in build_connector_tools(connector, framework="mcp").as_list():
    mcp.tool(tool)
```

###### Legacy alternatives

These examples are kept for existing integrations. For new agents, use `build_connector_tools` above. The legacy `TiktokMarketingConnector.tool_utils` pattern loads the connector's full generated catalog into one broad `execute` tool description instead of letting the agent read skill docs on demand.

**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.tiktok_marketing import TiktokMarketingConnector

connector = connect("tiktok-marketing", workspace_name="<your_workspace_name>")

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@TiktokMarketingConnector.tool_utils
async def tiktok_marketing_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.tiktok_marketing import TiktokMarketingConnector

connector = connect("tiktok-marketing", workspace_name="<your_workspace_name>")

@tool
@TiktokMarketingConnector.tool_utils
async def tiktok_marketing_execute(entity: str, action: str, params: dict | None = None):
    """Execute Tiktok-Marketing connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.tiktok_marketing import TiktokMarketingConnector

connector = connect("tiktok-marketing", workspace_name="<your_workspace_name>")

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@TiktokMarketingConnector.tool_utils(framework="openai_agents")
async def tiktok_marketing_execute(entity: str, action: str, params: dict | None = None):
    """Execute Tiktok-Marketing connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Tiktok-Marketing Assistant", tools=[tiktok_marketing_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.tiktok_marketing import TiktokMarketingConnector

connector = connect("tiktok-marketing", workspace_name="<your_workspace_name>")

mcp = FastMCP("Tiktok-Marketing Agent")

@mcp.tool
@TiktokMarketingConnector.tool_utils
async def tiktok_marketing_execute(entity: str, action: str, params: dict | None = None):
    """Execute Tiktok-Marketing connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```


Or pass credentials explicitly (equivalent, useful when you're not loading them from the environment):


**Pydantic AI**

```python title="Pydantic AI"
from airbyte_agent_sdk import build_connector_tools
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.tiktok_marketing import TiktokMarketingConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = TiktokMarketingConnector(
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
from airbyte_agent_sdk.connectors.tiktok_marketing import TiktokMarketingConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = TiktokMarketingConnector(
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
from airbyte_agent_sdk.connectors.tiktok_marketing import TiktokMarketingConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = TiktokMarketingConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

tools = build_connector_tools(connector, framework="openai_agents")
openai_tools = [function_tool(tool, strict_mode=False) for tool in tools.as_list()]

agent = Agent(name="Tiktok-Marketing Assistant", tools=openai_tools)
```

**FastMCP**

```python title="FastMCP"
from airbyte_agent_sdk import build_connector_tools
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.tiktok_marketing import TiktokMarketingConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = TiktokMarketingConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

mcp = FastMCP("Tiktok-Marketing Agent")

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
from airbyte_agent_sdk.connectors.tiktok_marketing import TiktokMarketingConnector
from airbyte_agent_sdk.connectors.tiktok_marketing.models import TiktokMarketingAuthConfig

connector = TiktokMarketingConnector(
    auth_config=TiktokMarketingAuthConfig(
        access_token="<Your TikTok Marketing API access token>"
    )
)

tools = build_connector_tools(connector, framework="pydantic_ai")
agent = Agent("openai:gpt-4o", tools=tools.as_list())
```

**LangChain**

```python title="LangChain"
from airbyte_agent_sdk import build_connector_tools
from langchain_core.tools import StructuredTool
from airbyte_agent_sdk.connectors.tiktok_marketing import TiktokMarketingConnector
from airbyte_agent_sdk.connectors.tiktok_marketing.models import TiktokMarketingAuthConfig

connector = TiktokMarketingConnector(
    auth_config=TiktokMarketingAuthConfig(
        access_token="<Your TikTok Marketing API access token>"
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
from airbyte_agent_sdk.connectors.tiktok_marketing import TiktokMarketingConnector
from airbyte_agent_sdk.connectors.tiktok_marketing.models import TiktokMarketingAuthConfig

connector = TiktokMarketingConnector(
    auth_config=TiktokMarketingAuthConfig(
        access_token="<Your TikTok Marketing API access token>"
    )
)

tools = build_connector_tools(connector, framework="openai_agents")
openai_tools = [function_tool(tool, strict_mode=False) for tool in tools.as_list()]

agent = Agent(name="Tiktok-Marketing Assistant", tools=openai_tools)
```

**FastMCP**

```python title="FastMCP"
from airbyte_agent_sdk import build_connector_tools
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.tiktok_marketing import TiktokMarketingConnector
from airbyte_agent_sdk.connectors.tiktok_marketing.models import TiktokMarketingAuthConfig

connector = TiktokMarketingConnector(
    auth_config=TiktokMarketingAuthConfig(
        access_token="<Your TikTok Marketing API access token>"
    )
)

mcp = FastMCP("Tiktok-Marketing Agent")

for tool in build_connector_tools(connector, framework="mcp").as_list():
    mcp.tool(tool)
```

###### Legacy alternatives

These examples are kept for existing integrations. For new agents, use `build_connector_tools` above. The legacy `TiktokMarketingConnector.tool_utils` pattern loads the connector's full generated catalog into one broad `execute` tool description instead of letting the agent read skill docs on demand.

**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.tiktok_marketing import TiktokMarketingConnector
from airbyte_agent_sdk.connectors.tiktok_marketing.models import TiktokMarketingAuthConfig

connector = TiktokMarketingConnector(
    auth_config=TiktokMarketingAuthConfig(
        access_token="<Your TikTok Marketing API access token>"
    )
)

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@TiktokMarketingConnector.tool_utils
async def tiktok_marketing_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.tiktok_marketing import TiktokMarketingConnector
from airbyte_agent_sdk.connectors.tiktok_marketing.models import TiktokMarketingAuthConfig

connector = TiktokMarketingConnector(
    auth_config=TiktokMarketingAuthConfig(
        access_token="<Your TikTok Marketing API access token>"
    )
)

@tool
@TiktokMarketingConnector.tool_utils
async def tiktok_marketing_execute(entity: str, action: str, params: dict | None = None):
    """Execute Tiktok-Marketing connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk.connectors.tiktok_marketing import TiktokMarketingConnector
from airbyte_agent_sdk.connectors.tiktok_marketing.models import TiktokMarketingAuthConfig

connector = TiktokMarketingConnector(
    auth_config=TiktokMarketingAuthConfig(
        access_token="<Your TikTok Marketing API access token>"
    )
)

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@TiktokMarketingConnector.tool_utils(framework="openai_agents")
async def tiktok_marketing_execute(entity: str, action: str, params: dict | None = None):
    """Execute Tiktok-Marketing connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Tiktok-Marketing Assistant", tools=[tiktok_marketing_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.tiktok_marketing import TiktokMarketingConnector
from airbyte_agent_sdk.connectors.tiktok_marketing.models import TiktokMarketingAuthConfig

connector = TiktokMarketingConnector(
    auth_config=TiktokMarketingAuthConfig(
        access_token="<Your TikTok Marketing API access token>"
    )
)

mcp = FastMCP("Tiktok-Marketing Agent")

@mcp.tool
@TiktokMarketingConnector.tool_utils
async def tiktok_marketing_execute(entity: str, action: str, params: dict | None = None):
    """Execute Tiktok-Marketing connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```


## Authentication

For all authentication options, see the connector's [authentication documentation](AUTH.md).

## IP allow list

If your organization restricts access to specific IPs, add the [Airbyte Agents IP addresses](https://docs.airbyte.com/ai-agents/admin/ip-allowlist) to your allow list.

## Version information

**Connector version:** 1.1.6