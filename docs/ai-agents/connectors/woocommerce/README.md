# Woocommerce

The Woocommerce agent connector is a Python package that equips AI agents to interact with Woocommerce through strongly typed, well-documented tools. It's ready to use directly in your Python app, in an agent framework, or exposed through an MCP.

Connector for the WooCommerce REST API (v3). Provides read access to a WooCommerce store's
customers, orders, products, coupons, product categories, tags, reviews, attributes,
variations, order notes, refunds, payment gateways, shipping methods, shipping zones,
tax rates, and tax classes. Requires a WooCommerce store URL and REST API consumer
key / consumer secret for authentication.


## Example questions

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

## Unsupported questions

The Woocommerce connector isn't currently able to handle prompts like these.

- Create a new product
- Update an order status
- Delete a customer
- Apply a coupon to an order
- Process a refund

## Installation

```bash
uv pip install airbyte-agent-sdk
```

## Usage

Connectors can run in open source or hosted mode.

### Open source

In open source mode, you provide API credentials directly to the connector.

```python
from airbyte_agent_sdk.connectors.woocommerce import WoocommerceConnector
from airbyte_agent_sdk.connectors.woocommerce.models import WoocommerceAuthConfig

connector = WoocommerceConnector(
    auth_config=WoocommerceAuthConfig(
        api_key="<WooCommerce REST API consumer key (starts with ck_)>",
        api_secret="<WooCommerce REST API consumer secret (starts with cs_)>"
    )
)

@agent.tool_plain # assumes you're using Pydantic AI
@WoocommerceConnector.tool_utils
async def woocommerce_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

### Hosted

In hosted mode, API credentials are stored securely in Airbyte Cloud. You provide your Airbyte credentials instead. 
If your Airbyte client can access multiple organizations, also set `organization_id`.

This example assumes you've already authenticated your connector with Airbyte. See [Authentication](AUTH.md) to learn more about authenticating. If you need a step-by-step guide, see the [hosted execution tutorial](https://docs.airbyte.com/ai-agents/quickstarts/tutorial-hosted).

The `connect()` factory returns a fully typed `WoocommerceConnector` and reads `AIRBYTE_CLIENT_ID` / `AIRBYTE_CLIENT_SECRET` from the environment:

```python
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.woocommerce import WoocommerceConnector

connector = connect("woocommerce", workspace_name="<your_workspace_name>")

@agent.tool_plain # assumes you're using Pydantic AI
@WoocommerceConnector.tool_utils
async def woocommerce_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

Or pass credentials explicitly (equivalent, useful when you're not loading them from the environment):

```python
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

@agent.tool_plain # assumes you're using Pydantic AI
@WoocommerceConnector.tool_utils
async def woocommerce_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

## Full documentation

### Entities and actions

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


### Authentication

For all authentication options, see the connector's [authentication documentation](AUTH.md).

### Woocommerce API docs

See the official [Woocommerce API reference](https://woocommerce.github.io/woocommerce-rest-api-docs/).

## Version information

- **Package version:** 1.0.4
- **Connector version:** 1.0.4
- **Generated with Connector SDK commit SHA:** unknown