# Shopify

The Shopify agent connector is a Python package that equips AI agents to interact with Shopify through strongly typed, well-documented tools. It's ready to use directly in your Python app, in an agent framework, or exposed through an MCP.

Shopify is an e-commerce platform that enables businesses to create online stores,
manage products, process orders, and handle customer relationships. This connector
provides access to Shopify Admin REST API for reading store data including customers,
orders, products, inventory, and more.


## Example questions

The Shopify connector is optimized to handle prompts like these.

- List all customers in my Shopify store
- Show me details for a recent customer
- What products do I have in my store?
- List all locations for my store
- Show me inventory levels for a recent location
- Show me all draft orders
- List all custom collections in my store
- Show me details for a recent order
- Show me product variants for a recent product
- Show me orders from the last 30 days
- Show me abandoned checkouts from this week
- What price rules are currently active?

## Unsupported questions

The Shopify connector isn't currently able to handle prompts like these.

- Create a new customer in Shopify
- Update product pricing
- Delete an order
- Process a refund
- Send shipping notification to customer
- Create a new discount code

## Installation

```bash
uv pip install airbyte-agent-sdk
```

## Usage

Connectors can run in open source or hosted mode.

### Open source

In open source mode, you provide API credentials directly to the connector.

**Pydantic AI**

```python title="Pydantic AI"
from airbyte_agent_sdk.connectors.shopify import ShopifyConnector
from airbyte_agent_sdk.connectors.shopify.models import ShopifyAuthConfig

connector = ShopifyConnector(
    auth_config=ShopifyAuthConfig(
        api_key="<Your Shopify Admin API access token>"
    )
)

@agent.tool_plain
@ShopifyConnector.tool_utils
async def shopify_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
import json

from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.shopify import ShopifyConnector
from airbyte_agent_sdk.connectors.shopify.models import ShopifyAuthConfig

connector = ShopifyConnector(
    auth_config=ShopifyAuthConfig(
        api_key="<Your Shopify Admin API access token>"
    )
)

@tool
@ShopifyConnector.tool_utils
async def shopify_execute(entity: str, action: str, params: dict | None = None) -> str:
    """Execute Shopify connector operations."""
    result = await connector.execute(entity, action, params or {})
    return json.dumps(result, default=str)
```

**FastMCP**

```python title="FastMCP"
import json

from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.shopify import ShopifyConnector
from airbyte_agent_sdk.connectors.shopify.models import ShopifyAuthConfig

connector = ShopifyConnector(
    auth_config=ShopifyAuthConfig(
        api_key="<Your Shopify Admin API access token>"
    )
)

mcp = FastMCP("Shopify Agent")

@mcp.tool()
@ShopifyConnector.tool_utils
async def shopify_execute(entity: str, action: str, params: dict | None = None) -> str:
    """Execute Shopify connector operations."""
    result = await connector.execute(entity, action, params or {})
    return json.dumps(result, default=str)
```

### Hosted

In hosted mode, API credentials are stored securely in Airbyte Cloud. You provide your Airbyte credentials instead. 
If your Airbyte client can access multiple organizations, also set `organization_id`.

This example assumes you've already authenticated your connector with Airbyte. See [Authentication](AUTH.md) to learn more about authenticating. If you need a step-by-step guide, see the [hosted execution tutorial](https://docs.airbyte.com/ai-agents/quickstarts/tutorial-hosted).

The `connect()` factory returns a fully typed `ShopifyConnector` and reads `AIRBYTE_CLIENT_ID` / `AIRBYTE_CLIENT_SECRET` from the environment:


**Pydantic AI**

```python title="Pydantic AI"
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.shopify import ShopifyConnector

connector = connect("shopify", workspace_name="<your_workspace_name>")

@agent.tool_plain
@ShopifyConnector.tool_utils
async def shopify_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
import json

from langchain_core.tools import tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.shopify import ShopifyConnector

connector = connect("shopify", workspace_name="<your_workspace_name>")

@tool
@ShopifyConnector.tool_utils
async def shopify_execute(entity: str, action: str, params: dict | None = None) -> str:
    """Execute Shopify connector operations."""
    result = await connector.execute(entity, action, params or {})
    return json.dumps(result, default=str)
```

**FastMCP**

```python title="FastMCP"
import json

from fastmcp import FastMCP
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.shopify import ShopifyConnector

connector = connect("shopify", workspace_name="<your_workspace_name>")

mcp = FastMCP("Shopify Agent")

@mcp.tool()
@ShopifyConnector.tool_utils
async def shopify_execute(entity: str, action: str, params: dict | None = None) -> str:
    """Execute Shopify connector operations."""
    result = await connector.execute(entity, action, params or {})
    return json.dumps(result, default=str)
```

Or pass credentials explicitly (equivalent, useful when you're not loading them from the environment):

**Pydantic AI**

```python title="Pydantic AI"
from airbyte_agent_sdk.connectors.shopify import ShopifyConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = ShopifyConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

@agent.tool_plain
@ShopifyConnector.tool_utils
async def shopify_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
import json

from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.shopify import ShopifyConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = ShopifyConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

@tool
@ShopifyConnector.tool_utils
async def shopify_execute(entity: str, action: str, params: dict | None = None) -> str:
    """Execute Shopify connector operations."""
    result = await connector.execute(entity, action, params or {})
    return json.dumps(result, default=str)
```

**FastMCP**

```python title="FastMCP"
import json

from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.shopify import ShopifyConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = ShopifyConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

mcp = FastMCP("Shopify Agent")

@mcp.tool()
@ShopifyConnector.tool_utils
async def shopify_execute(entity: str, action: str, params: dict | None = None) -> str:
    """Execute Shopify connector operations."""
    result = await connector.execute(entity, action, params or {})
    return json.dumps(result, default=str)
```

## Full documentation

### Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Customers | [List](./REFERENCE.md#customers-list), [Get](./REFERENCE.md#customers-get), [Context Store Search](./REFERENCE.md#customers-context-store-search) |
| Orders | [List](./REFERENCE.md#orders-list), [Get](./REFERENCE.md#orders-get) |
| Products | [List](./REFERENCE.md#products-list), [Get](./REFERENCE.md#products-get) |
| Product Variants | [List](./REFERENCE.md#product-variants-list), [Get](./REFERENCE.md#product-variants-get), [Context Store Search](./REFERENCE.md#product-variants-context-store-search) |
| Product Images | [List](./REFERENCE.md#product-images-list), [Get](./REFERENCE.md#product-images-get), [Context Store Search](./REFERENCE.md#product-images-context-store-search) |
| Abandoned Checkouts | [List](./REFERENCE.md#abandoned-checkouts-list), [Context Store Search](./REFERENCE.md#abandoned-checkouts-context-store-search) |
| Locations | [List](./REFERENCE.md#locations-list), [Get](./REFERENCE.md#locations-get), [Context Store Search](./REFERENCE.md#locations-context-store-search) |
| Inventory Levels | [List](./REFERENCE.md#inventory-levels-list), [Context Store Search](./REFERENCE.md#inventory-levels-context-store-search) |
| Inventory Items | [List](./REFERENCE.md#inventory-items-list), [Get](./REFERENCE.md#inventory-items-get), [Context Store Search](./REFERENCE.md#inventory-items-context-store-search) |
| Shop | [Get](./REFERENCE.md#shop-get), [Context Store Search](./REFERENCE.md#shop-context-store-search) |
| Price Rules | [List](./REFERENCE.md#price-rules-list), [Get](./REFERENCE.md#price-rules-get), [Context Store Search](./REFERENCE.md#price-rules-context-store-search) |
| Discount Codes | [List](./REFERENCE.md#discount-codes-list), [Get](./REFERENCE.md#discount-codes-get), [Context Store Search](./REFERENCE.md#discount-codes-context-store-search) |
| Custom Collections | [List](./REFERENCE.md#custom-collections-list), [Get](./REFERENCE.md#custom-collections-get), [Context Store Search](./REFERENCE.md#custom-collections-context-store-search) |
| Smart Collections | [List](./REFERENCE.md#smart-collections-list), [Get](./REFERENCE.md#smart-collections-get), [Context Store Search](./REFERENCE.md#smart-collections-context-store-search) |
| Collects | [List](./REFERENCE.md#collects-list), [Get](./REFERENCE.md#collects-get), [Context Store Search](./REFERENCE.md#collects-context-store-search) |
| Draft Orders | [List](./REFERENCE.md#draft-orders-list), [Get](./REFERENCE.md#draft-orders-get), [Context Store Search](./REFERENCE.md#draft-orders-context-store-search) |
| Fulfillments | [List](./REFERENCE.md#fulfillments-list), [Get](./REFERENCE.md#fulfillments-get), [Context Store Search](./REFERENCE.md#fulfillments-context-store-search) |
| Order Refunds | [List](./REFERENCE.md#order-refunds-list), [Get](./REFERENCE.md#order-refunds-get), [Context Store Search](./REFERENCE.md#order-refunds-context-store-search) |
| Transactions | [List](./REFERENCE.md#transactions-list), [Get](./REFERENCE.md#transactions-get) |
| Tender Transactions | [List](./REFERENCE.md#tender-transactions-list), [Context Store Search](./REFERENCE.md#tender-transactions-context-store-search) |
| Countries | [List](./REFERENCE.md#countries-list), [Get](./REFERENCE.md#countries-get), [Context Store Search](./REFERENCE.md#countries-context-store-search) |
| Metafield Shops | [List](./REFERENCE.md#metafield-shops-list), [Get](./REFERENCE.md#metafield-shops-get), [Context Store Search](./REFERENCE.md#metafield-shops-context-store-search) |
| Metafield Customers | [List](./REFERENCE.md#metafield-customers-list), [Context Store Search](./REFERENCE.md#metafield-customers-context-store-search) |
| Metafield Products | [List](./REFERENCE.md#metafield-products-list), [Context Store Search](./REFERENCE.md#metafield-products-context-store-search) |
| Metafield Orders | [List](./REFERENCE.md#metafield-orders-list), [Context Store Search](./REFERENCE.md#metafield-orders-context-store-search) |
| Metafield Draft Orders | [List](./REFERENCE.md#metafield-draft-orders-list), [Context Store Search](./REFERENCE.md#metafield-draft-orders-context-store-search) |
| Metafield Locations | [List](./REFERENCE.md#metafield-locations-list), [Context Store Search](./REFERENCE.md#metafield-locations-context-store-search) |
| Metafield Product Variants | [List](./REFERENCE.md#metafield-product-variants-list), [Context Store Search](./REFERENCE.md#metafield-product-variants-context-store-search) |
| Metafield Smart Collections | [List](./REFERENCE.md#metafield-smart-collections-list), [Context Store Search](./REFERENCE.md#metafield-smart-collections-context-store-search) |
| Metafield Product Images | [List](./REFERENCE.md#metafield-product-images-list), [Context Store Search](./REFERENCE.md#metafield-product-images-context-store-search) |
| Customer Address | [List](./REFERENCE.md#customer-address-list), [Get](./REFERENCE.md#customer-address-get) |
| Fulfillment Orders | [List](./REFERENCE.md#fulfillment-orders-list), [Get](./REFERENCE.md#fulfillment-orders-get), [Context Store Search](./REFERENCE.md#fulfillment-orders-context-store-search) |


### Authentication

For all authentication options, see the connector's [authentication documentation](AUTH.md).

### Shopify API docs

See the official [Shopify API reference](https://shopify.dev/docs/api/admin-rest).

## Version information

- **Package version:** 0.1.12
- **Connector version:** 0.1.12
- **Generated with Connector SDK commit SHA:** unknown