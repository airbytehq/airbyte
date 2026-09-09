# Amazon-Seller-Partner

The Amazon-Seller-Partner agent connector is a Python package that equips AI agents to interact with Amazon-Seller-Partner through strongly typed, well-documented tools. It's ready to use directly in your Python app, in an agent framework, or exposed through an MCP.

Connector for the Amazon Selling Partner API (SP-API). Provides access to seller orders and order items, financial events and event groups, catalog item search and details, and report metadata. Supports OAuth 2.0 authentication via Login with Amazon (LWA) with automatic token refresh.


## Example prompts

The Amazon-Seller-Partner connector is optimized to handle prompts like these.

- List all orders from the last 7 days
- Show me shipped orders from January 2024
- Show me order items for order 111-2222222-3333333
- List financial event groups from the last 90 days
- Show refund events from last month
- Search the catalog for wireless headphones
- Look up product details for ASIN B08N5WRWNW
- List completed reports from this week
- What are my top-selling products by order volume this month?
- Show orders with status Shipped from the last 30 days
- Find all refund financial events from last quarter
- Which orders have the highest total value this week?
- How many orders were canceled in the last 60 days?
- What service fees were charged last month?

## Unsupported prompts

The Amazon-Seller-Partner connector isn't currently able to handle prompts like these.

- Create a new order
- Cancel an order
- Submit a new report request
- Update product listings
- Change the marketplace region

## Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Orders | [List](./REFERENCE.md#orders-list), [Get](./REFERENCE.md#orders-get), [Context Store Search](./REFERENCE.md#orders-context-store-search) |
| Order Items | [List](./REFERENCE.md#order-items-list), [Context Store Search](./REFERENCE.md#order-items-context-store-search) |
| List Financial Event Groups | [List](./REFERENCE.md#list-financial-event-groups-list), [Context Store Search](./REFERENCE.md#list-financial-event-groups-context-store-search) |
| List Financial Events | [List](./REFERENCE.md#list-financial-events-list), [Context Store Search](./REFERENCE.md#list-financial-events-context-store-search) |
| Catalog Items | [List](./REFERENCE.md#catalog-items-list), [Get](./REFERENCE.md#catalog-items-get) |
| Reports | [List](./REFERENCE.md#reports-list), [Get](./REFERENCE.md#reports-get) |


## Amazon-Seller-Partner API docs

See the official [Amazon-Seller-Partner API reference](https://developer-docs.amazon.com/sp-api/).

## Interfaces

Use the Amazon-Seller-Partner connector through the Airbyte Agent CLI, the Python SDK, or the API.

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
  "name": "amazon-seller-partner"
}'
```

Describe the connector to see its supported entities and actions:

```bash
airbyte-agent connectors describe --json '{
  "workspace": "<your_workspace_name>",
  "name": "amazon-seller-partner"
}'
```

Execute an action:

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "amazon-seller-partner",
  "entity": "orders",
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

The `connect()` factory returns a fully typed `AmazonSellerPartnerConnector` and reads `AIRBYTE_CLIENT_ID` / `AIRBYTE_CLIENT_SECRET` from the environment:


The recommended pattern is `build_connector_tools`, which gives the agent three tools bound to this connector: `inspect_connector`, `read_skill_docs`, and `execute`. The agent can inspect the connector, read only the skill-doc section it needs, and then execute:

```text
inspect_connector() -> read_skill_docs() -> read_skill_docs(section="...") -> execute(entity, action, params)
```

**Pydantic AI**

```python title="Pydantic AI"
from airbyte_agent_sdk import build_connector_tools
from pydantic_ai import Agent
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.amazon_seller_partner import AmazonSellerPartnerConnector

connector = connect("amazon-seller-partner", workspace_name="<your_workspace_name>")

tools = build_connector_tools(connector, framework="pydantic_ai")
agent = Agent("openai:gpt-4o", tools=tools.as_list())
```

**LangChain**

```python title="LangChain"
from airbyte_agent_sdk import build_connector_tools
from langchain_core.tools import StructuredTool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.amazon_seller_partner import AmazonSellerPartnerConnector

connector = connect("amazon-seller-partner", workspace_name="<your_workspace_name>")

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
from airbyte_agent_sdk.connectors.amazon_seller_partner import AmazonSellerPartnerConnector

connector = connect("amazon-seller-partner", workspace_name="<your_workspace_name>")

tools = build_connector_tools(connector, framework="openai_agents")
openai_tools = [function_tool(tool, strict_mode=False) for tool in tools.as_list()]

agent = Agent(name="Amazon-Seller-Partner Assistant", tools=openai_tools)
```

**FastMCP**

```python title="FastMCP"
from airbyte_agent_sdk import build_connector_tools
from fastmcp import FastMCP
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.amazon_seller_partner import AmazonSellerPartnerConnector

connector = connect("amazon-seller-partner", workspace_name="<your_workspace_name>")

mcp = FastMCP("Amazon-Seller-Partner Agent")

for tool in build_connector_tools(connector, framework="mcp").as_list():
    mcp.tool(tool)
```

###### Legacy alternatives

These examples are kept for existing integrations. For new agents, use `build_connector_tools` above. The legacy `AmazonSellerPartnerConnector.tool_utils` pattern loads the connector's full generated catalog into one broad `execute` tool description instead of letting the agent read skill docs on demand.

**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.amazon_seller_partner import AmazonSellerPartnerConnector

connector = connect("amazon-seller-partner", workspace_name="<your_workspace_name>")

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@AmazonSellerPartnerConnector.tool_utils
async def amazon_seller_partner_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.amazon_seller_partner import AmazonSellerPartnerConnector

connector = connect("amazon-seller-partner", workspace_name="<your_workspace_name>")

@tool
@AmazonSellerPartnerConnector.tool_utils
async def amazon_seller_partner_execute(entity: str, action: str, params: dict | None = None):
    """Execute Amazon-Seller-Partner connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.amazon_seller_partner import AmazonSellerPartnerConnector

connector = connect("amazon-seller-partner", workspace_name="<your_workspace_name>")

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@AmazonSellerPartnerConnector.tool_utils(framework="openai_agents")
async def amazon_seller_partner_execute(entity: str, action: str, params: dict | None = None):
    """Execute Amazon-Seller-Partner connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Amazon-Seller-Partner Assistant", tools=[amazon_seller_partner_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.amazon_seller_partner import AmazonSellerPartnerConnector

connector = connect("amazon-seller-partner", workspace_name="<your_workspace_name>")

mcp = FastMCP("Amazon-Seller-Partner Agent")

@mcp.tool
@AmazonSellerPartnerConnector.tool_utils
async def amazon_seller_partner_execute(entity: str, action: str, params: dict | None = None):
    """Execute Amazon-Seller-Partner connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```


Or pass credentials explicitly (equivalent, useful when you're not loading them from the environment):


**Pydantic AI**

```python title="Pydantic AI"
from airbyte_agent_sdk import build_connector_tools
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.amazon_seller_partner import AmazonSellerPartnerConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = AmazonSellerPartnerConnector(
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
from airbyte_agent_sdk.connectors.amazon_seller_partner import AmazonSellerPartnerConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = AmazonSellerPartnerConnector(
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
from airbyte_agent_sdk.connectors.amazon_seller_partner import AmazonSellerPartnerConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = AmazonSellerPartnerConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

tools = build_connector_tools(connector, framework="openai_agents")
openai_tools = [function_tool(tool, strict_mode=False) for tool in tools.as_list()]

agent = Agent(name="Amazon-Seller-Partner Assistant", tools=openai_tools)
```

**FastMCP**

```python title="FastMCP"
from airbyte_agent_sdk import build_connector_tools
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.amazon_seller_partner import AmazonSellerPartnerConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = AmazonSellerPartnerConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

mcp = FastMCP("Amazon-Seller-Partner Agent")

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
from airbyte_agent_sdk.connectors.amazon_seller_partner import AmazonSellerPartnerConnector
from airbyte_agent_sdk.connectors.amazon_seller_partner.models import AmazonSellerPartnerAuthConfig

connector = AmazonSellerPartnerConnector(
    auth_config=AmazonSellerPartnerAuthConfig(
        lwa_app_id="<Your Login with Amazon Client ID.>",
        lwa_client_secret="<Your Login with Amazon Client Secret.>",
        refresh_token="<The Refresh Token obtained via the OAuth authorization flow.>",
        access_token="<Access token (optional if refresh_token is provided).>"
    )
)

tools = build_connector_tools(connector, framework="pydantic_ai")
agent = Agent("openai:gpt-4o", tools=tools.as_list())
```

**LangChain**

```python title="LangChain"
from airbyte_agent_sdk import build_connector_tools
from langchain_core.tools import StructuredTool
from airbyte_agent_sdk.connectors.amazon_seller_partner import AmazonSellerPartnerConnector
from airbyte_agent_sdk.connectors.amazon_seller_partner.models import AmazonSellerPartnerAuthConfig

connector = AmazonSellerPartnerConnector(
    auth_config=AmazonSellerPartnerAuthConfig(
        lwa_app_id="<Your Login with Amazon Client ID.>",
        lwa_client_secret="<Your Login with Amazon Client Secret.>",
        refresh_token="<The Refresh Token obtained via the OAuth authorization flow.>",
        access_token="<Access token (optional if refresh_token is provided).>"
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
from airbyte_agent_sdk.connectors.amazon_seller_partner import AmazonSellerPartnerConnector
from airbyte_agent_sdk.connectors.amazon_seller_partner.models import AmazonSellerPartnerAuthConfig

connector = AmazonSellerPartnerConnector(
    auth_config=AmazonSellerPartnerAuthConfig(
        lwa_app_id="<Your Login with Amazon Client ID.>",
        lwa_client_secret="<Your Login with Amazon Client Secret.>",
        refresh_token="<The Refresh Token obtained via the OAuth authorization flow.>",
        access_token="<Access token (optional if refresh_token is provided).>"
    )
)

tools = build_connector_tools(connector, framework="openai_agents")
openai_tools = [function_tool(tool, strict_mode=False) for tool in tools.as_list()]

agent = Agent(name="Amazon-Seller-Partner Assistant", tools=openai_tools)
```

**FastMCP**

```python title="FastMCP"
from airbyte_agent_sdk import build_connector_tools
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.amazon_seller_partner import AmazonSellerPartnerConnector
from airbyte_agent_sdk.connectors.amazon_seller_partner.models import AmazonSellerPartnerAuthConfig

connector = AmazonSellerPartnerConnector(
    auth_config=AmazonSellerPartnerAuthConfig(
        lwa_app_id="<Your Login with Amazon Client ID.>",
        lwa_client_secret="<Your Login with Amazon Client Secret.>",
        refresh_token="<The Refresh Token obtained via the OAuth authorization flow.>",
        access_token="<Access token (optional if refresh_token is provided).>"
    )
)

mcp = FastMCP("Amazon-Seller-Partner Agent")

for tool in build_connector_tools(connector, framework="mcp").as_list():
    mcp.tool(tool)
```

###### Legacy alternatives

These examples are kept for existing integrations. For new agents, use `build_connector_tools` above. The legacy `AmazonSellerPartnerConnector.tool_utils` pattern loads the connector's full generated catalog into one broad `execute` tool description instead of letting the agent read skill docs on demand.

**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.amazon_seller_partner import AmazonSellerPartnerConnector
from airbyte_agent_sdk.connectors.amazon_seller_partner.models import AmazonSellerPartnerAuthConfig

connector = AmazonSellerPartnerConnector(
    auth_config=AmazonSellerPartnerAuthConfig(
        lwa_app_id="<Your Login with Amazon Client ID.>",
        lwa_client_secret="<Your Login with Amazon Client Secret.>",
        refresh_token="<The Refresh Token obtained via the OAuth authorization flow.>",
        access_token="<Access token (optional if refresh_token is provided).>"
    )
)

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@AmazonSellerPartnerConnector.tool_utils
async def amazon_seller_partner_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.amazon_seller_partner import AmazonSellerPartnerConnector
from airbyte_agent_sdk.connectors.amazon_seller_partner.models import AmazonSellerPartnerAuthConfig

connector = AmazonSellerPartnerConnector(
    auth_config=AmazonSellerPartnerAuthConfig(
        lwa_app_id="<Your Login with Amazon Client ID.>",
        lwa_client_secret="<Your Login with Amazon Client Secret.>",
        refresh_token="<The Refresh Token obtained via the OAuth authorization flow.>",
        access_token="<Access token (optional if refresh_token is provided).>"
    )
)

@tool
@AmazonSellerPartnerConnector.tool_utils
async def amazon_seller_partner_execute(entity: str, action: str, params: dict | None = None):
    """Execute Amazon-Seller-Partner connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk.connectors.amazon_seller_partner import AmazonSellerPartnerConnector
from airbyte_agent_sdk.connectors.amazon_seller_partner.models import AmazonSellerPartnerAuthConfig

connector = AmazonSellerPartnerConnector(
    auth_config=AmazonSellerPartnerAuthConfig(
        lwa_app_id="<Your Login with Amazon Client ID.>",
        lwa_client_secret="<Your Login with Amazon Client Secret.>",
        refresh_token="<The Refresh Token obtained via the OAuth authorization flow.>",
        access_token="<Access token (optional if refresh_token is provided).>"
    )
)

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@AmazonSellerPartnerConnector.tool_utils(framework="openai_agents")
async def amazon_seller_partner_execute(entity: str, action: str, params: dict | None = None):
    """Execute Amazon-Seller-Partner connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Amazon-Seller-Partner Assistant", tools=[amazon_seller_partner_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.amazon_seller_partner import AmazonSellerPartnerConnector
from airbyte_agent_sdk.connectors.amazon_seller_partner.models import AmazonSellerPartnerAuthConfig

connector = AmazonSellerPartnerConnector(
    auth_config=AmazonSellerPartnerAuthConfig(
        lwa_app_id="<Your Login with Amazon Client ID.>",
        lwa_client_secret="<Your Login with Amazon Client Secret.>",
        refresh_token="<The Refresh Token obtained via the OAuth authorization flow.>",
        access_token="<Access token (optional if refresh_token is provided).>"
    )
)

mcp = FastMCP("Amazon-Seller-Partner Agent")

@mcp.tool
@AmazonSellerPartnerConnector.tool_utils
async def amazon_seller_partner_execute(entity: str, action: str, params: dict | None = None):
    """Execute Amazon-Seller-Partner connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```


## Authentication

For all authentication options, see the connector's [authentication documentation](AUTH.md).

## IP allow list

If your organization restricts access to specific IPs, add the [Airbyte Agents IP addresses](https://docs.airbyte.com/ai-agents/admin/ip-allowlist) to your allow list.

## Version information

**Connector version:** 1.0.5