# Woocommerce

The Woocommerce agent connector is a Python package that equips AI agents to interact with Woocommerce through strongly typed, well-documented tools. It's ready to use directly in your Python app, in an agent framework, or exposed through an MCP.

Connector for the WooCommerce REST API (v3). Provides read access to a WooCommerce store's
customers, orders, products, coupons, product categories, tags, reviews, attributes,
variations, order notes, refunds, payment gateways, shipping methods, shipping zones,
tax rates, and tax classes. Requires a WooCommerce store URL and REST API consumer
key / consumer secret for authentication.


## Example prompts

The Woocommerce connector is optimized to handle prompts like these.

- List all customers in WooCommerce
- Show me all orders
- List all products
- Show me all coupons
- List all product categories
- Show me the product reviews
- List all shipping zones
- Show me the tax rates
- List all payment gateways
- Find orders placed this month
- What are the top-selling products?
- Show me customers who have made purchases
- Find all coupons expiring this year
- What orders are still processing?

## Unsupported prompts

The Woocommerce connector isn't currently able to handle prompts like these.

- Create a new product
- Update an order status
- Delete a customer
- Apply a coupon to an order
- Process a refund

## Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Customers | [List](./REFERENCE.md#customers-list), [Get](./REFERENCE.md#customers-get), [Context Store Search](./REFERENCE.md#customers-context-store-search) |
| Orders | [List](./REFERENCE.md#orders-list), [Get](./REFERENCE.md#orders-get), [Context Store Search](./REFERENCE.md#orders-context-store-search) |
| Products | [List](./REFERENCE.md#products-list), [Get](./REFERENCE.md#products-get), [Context Store Search](./REFERENCE.md#products-context-store-search) |
| Coupons | [List](./REFERENCE.md#coupons-list), [Get](./REFERENCE.md#coupons-get), [Context Store Search](./REFERENCE.md#coupons-context-store-search) |
| Product Categories | [List](./REFERENCE.md#product-categories-list), [Get](./REFERENCE.md#product-categories-get), [Context Store Search](./REFERENCE.md#product-categories-context-store-search) |
| Product Tags | [List](./REFERENCE.md#product-tags-list), [Get](./REFERENCE.md#product-tags-get), [Context Store Search](./REFERENCE.md#product-tags-context-store-search) |
| Product Reviews | [List](./REFERENCE.md#product-reviews-list), [Get](./REFERENCE.md#product-reviews-get), [Context Store Search](./REFERENCE.md#product-reviews-context-store-search) |
| Product Attributes | [List](./REFERENCE.md#product-attributes-list), [Get](./REFERENCE.md#product-attributes-get), [Context Store Search](./REFERENCE.md#product-attributes-context-store-search) |
| Product Variations | [List](./REFERENCE.md#product-variations-list), [Get](./REFERENCE.md#product-variations-get), [Context Store Search](./REFERENCE.md#product-variations-context-store-search) |
| Order Notes | [List](./REFERENCE.md#order-notes-list), [Get](./REFERENCE.md#order-notes-get), [Context Store Search](./REFERENCE.md#order-notes-context-store-search) |
| Refunds | [List](./REFERENCE.md#refunds-list), [Get](./REFERENCE.md#refunds-get), [Context Store Search](./REFERENCE.md#refunds-context-store-search) |
| Payment Gateways | [List](./REFERENCE.md#payment-gateways-list), [Get](./REFERENCE.md#payment-gateways-get), [Context Store Search](./REFERENCE.md#payment-gateways-context-store-search) |
| Shipping Methods | [List](./REFERENCE.md#shipping-methods-list), [Get](./REFERENCE.md#shipping-methods-get), [Context Store Search](./REFERENCE.md#shipping-methods-context-store-search) |
| Shipping Zones | [List](./REFERENCE.md#shipping-zones-list), [Get](./REFERENCE.md#shipping-zones-get), [Context Store Search](./REFERENCE.md#shipping-zones-context-store-search) |
| Tax Rates | [List](./REFERENCE.md#tax-rates-list), [Get](./REFERENCE.md#tax-rates-get), [Context Store Search](./REFERENCE.md#tax-rates-context-store-search) |
| Tax Classes | [List](./REFERENCE.md#tax-classes-list), [Context Store Search](./REFERENCE.md#tax-classes-context-store-search) |


## Woocommerce API docs

See the official [Woocommerce API reference](https://woocommerce.github.io/woocommerce-rest-api-docs/).

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

The `connect()` factory returns a fully typed `WoocommerceConnector` and reads `AIRBYTE_CLIENT_ID` / `AIRBYTE_CLIENT_SECRET` from the environment:


**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.woocommerce import WoocommerceConnector

connector = connect("woocommerce", workspace_name="<your_workspace_name>")

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@WoocommerceConnector.tool_utils
async def woocommerce_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.woocommerce import WoocommerceConnector

connector = connect("woocommerce", workspace_name="<your_workspace_name>")

@tool
@WoocommerceConnector.tool_utils
async def woocommerce_execute(entity: str, action: str, params: dict | None = None):
    """Execute Woocommerce connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.woocommerce import WoocommerceConnector

connector = connect("woocommerce", workspace_name="<your_workspace_name>")

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@WoocommerceConnector.tool_utils(framework="openai_agents")
async def woocommerce_execute(entity: str, action: str, params: dict | None = None):
    """Execute Woocommerce connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Woocommerce Assistant", tools=[woocommerce_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.woocommerce import WoocommerceConnector

connector = connect("woocommerce", workspace_name="<your_workspace_name>")

mcp = FastMCP("Woocommerce Agent")

@mcp.tool
@WoocommerceConnector.tool_utils
async def woocommerce_execute(entity: str, action: str, params: dict | None = None):
    """Execute Woocommerce connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

Or pass credentials explicitly (equivalent, useful when you're not loading them from the environment):

**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.woocommerce import WoocommerceConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = WoocommerceConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@WoocommerceConnector.tool_utils
async def woocommerce_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.woocommerce import WoocommerceConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = WoocommerceConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

@tool
@WoocommerceConnector.tool_utils
async def woocommerce_execute(entity: str, action: str, params: dict | None = None):
    """Execute Woocommerce connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk.connectors.woocommerce import WoocommerceConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = WoocommerceConnector(
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
@WoocommerceConnector.tool_utils(framework="openai_agents")
async def woocommerce_execute(entity: str, action: str, params: dict | None = None):
    """Execute Woocommerce connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Woocommerce Assistant", tools=[woocommerce_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.woocommerce import WoocommerceConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = WoocommerceConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

mcp = FastMCP("Woocommerce Agent")

@mcp.tool
@WoocommerceConnector.tool_utils
async def woocommerce_execute(entity: str, action: str, params: dict | None = None):
    """Execute Woocommerce connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

### Open source

In open source mode, you provide API credentials directly to the connector.

**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.woocommerce import WoocommerceConnector
from airbyte_agent_sdk.connectors.woocommerce.models import WoocommerceAuthConfig

connector = WoocommerceConnector(
    auth_config=WoocommerceAuthConfig(
        api_key="<WooCommerce REST API consumer key (starts with ck_)>",
        api_secret="<WooCommerce REST API consumer secret (starts with cs_)>"
    )
)

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@WoocommerceConnector.tool_utils
async def woocommerce_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.woocommerce import WoocommerceConnector
from airbyte_agent_sdk.connectors.woocommerce.models import WoocommerceAuthConfig

connector = WoocommerceConnector(
    auth_config=WoocommerceAuthConfig(
        api_key="<WooCommerce REST API consumer key (starts with ck_)>",
        api_secret="<WooCommerce REST API consumer secret (starts with cs_)>"
    )
)

@tool
@WoocommerceConnector.tool_utils
async def woocommerce_execute(entity: str, action: str, params: dict | None = None):
    """Execute Woocommerce connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk.connectors.woocommerce import WoocommerceConnector
from airbyte_agent_sdk.connectors.woocommerce.models import WoocommerceAuthConfig

connector = WoocommerceConnector(
    auth_config=WoocommerceAuthConfig(
        api_key="<WooCommerce REST API consumer key (starts with ck_)>",
        api_secret="<WooCommerce REST API consumer secret (starts with cs_)>"
    )
)

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@WoocommerceConnector.tool_utils(framework="openai_agents")
async def woocommerce_execute(entity: str, action: str, params: dict | None = None):
    """Execute Woocommerce connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Woocommerce Assistant", tools=[woocommerce_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.woocommerce import WoocommerceConnector
from airbyte_agent_sdk.connectors.woocommerce.models import WoocommerceAuthConfig

connector = WoocommerceConnector(
    auth_config=WoocommerceAuthConfig(
        api_key="<WooCommerce REST API consumer key (starts with ck_)>",
        api_secret="<WooCommerce REST API consumer secret (starts with cs_)>"
    )
)

mcp = FastMCP("Woocommerce Agent")

@mcp.tool
@WoocommerceConnector.tool_utils
async def woocommerce_execute(entity: str, action: str, params: dict | None = None):
    """Execute Woocommerce connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

## Authentication

For all authentication options, see the connector's [authentication documentation](AUTH.md).

## Version information

**Connector version:** 1.0.5
