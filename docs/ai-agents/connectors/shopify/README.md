# Shopify agent connector

Shopify is an e-commerce platform that enables businesses to create online stores,
manage products, process orders, and handle customer relationships. This connector
provides access to Shopify Admin REST API for reading store data including customers,
orders, products, inventory, and more.


## Example questions

The Shopify connector is optimized to handle prompts like these.

- List all customers in my Shopify store
- Show me orders from the last 30 days
- Get details for customer \{customer_id\}
- What products do I have in my store?
- Show me abandoned checkouts from this week
- List all locations for my store
- Get inventory levels for location \{location_id\}
- Show me all draft orders
- What price rules are currently active?
- List all custom collections in my store
- Get details for order \{order_id\}
- Show me product variants for product \{product_id\}

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
uv pip install airbyte-agent-shopify
```

## Usage

```python
from airbyte_agent_shopify import ShopifyConnector, ShopifyAuthConfig

connector = ShopifyConnector(
  auth_config=ShopifyAuthConfig(
    api_key="...",
    shop="..."
  )
)
result = await connector.customers.list()
```


## Full documentation

This connector supports the following entities and actions.

| Entity | Actions |
|--------|---------|
| Customers | [List](./REFERENCE.md#customers-list), [Get](./REFERENCE.md#customers-get) |
| Orders | [List](./REFERENCE.md#orders-list), [Get](./REFERENCE.md#orders-get) |
| Products | [List](./REFERENCE.md#products-list), [Get](./REFERENCE.md#products-get) |
| Product Variants | [List](./REFERENCE.md#product-variants-list), [Get](./REFERENCE.md#product-variants-get) |
| Product Images | [List](./REFERENCE.md#product-images-list), [Get](./REFERENCE.md#product-images-get) |
| Abandoned Checkouts | [List](./REFERENCE.md#abandoned-checkouts-list) |
| Locations | [List](./REFERENCE.md#locations-list), [Get](./REFERENCE.md#locations-get) |
| Inventory Levels | [List](./REFERENCE.md#inventory-levels-list) |
| Inventory Items | [List](./REFERENCE.md#inventory-items-list), [Get](./REFERENCE.md#inventory-items-get) |
| Shop | [Get](./REFERENCE.md#shop-get) |
| Price Rules | [List](./REFERENCE.md#price-rules-list), [Get](./REFERENCE.md#price-rules-get) |
| Discount Codes | [List](./REFERENCE.md#discount-codes-list), [Get](./REFERENCE.md#discount-codes-get) |
| Custom Collections | [List](./REFERENCE.md#custom-collections-list), [Get](./REFERENCE.md#custom-collections-get) |
| Smart Collections | [List](./REFERENCE.md#smart-collections-list), [Get](./REFERENCE.md#smart-collections-get) |
| Collects | [List](./REFERENCE.md#collects-list), [Get](./REFERENCE.md#collects-get) |
| Draft Orders | [List](./REFERENCE.md#draft-orders-list), [Get](./REFERENCE.md#draft-orders-get) |
| Fulfillments | [List](./REFERENCE.md#fulfillments-list), [Get](./REFERENCE.md#fulfillments-get) |
| Order Refunds | [List](./REFERENCE.md#order-refunds-list), [Get](./REFERENCE.md#order-refunds-get) |
| Transactions | [List](./REFERENCE.md#transactions-list), [Get](./REFERENCE.md#transactions-get) |
| Tender Transactions | [List](./REFERENCE.md#tender-transactions-list) |
| Countries | [List](./REFERENCE.md#countries-list), [Get](./REFERENCE.md#countries-get) |
| Metafield Shops | [List](./REFERENCE.md#metafield-shops-list), [Get](./REFERENCE.md#metafield-shops-get) |
| Metafield Customers | [List](./REFERENCE.md#metafield-customers-list) |
| Metafield Products | [List](./REFERENCE.md#metafield-products-list) |
| Metafield Orders | [List](./REFERENCE.md#metafield-orders-list) |
| Metafield Draft Orders | [List](./REFERENCE.md#metafield-draft-orders-list) |
| Metafield Locations | [List](./REFERENCE.md#metafield-locations-list) |
| Metafield Product Variants | [List](./REFERENCE.md#metafield-product-variants-list) |
| Metafield Smart Collections | [List](./REFERENCE.md#metafield-smart-collections-list) |
| Metafield Product Images | [List](./REFERENCE.md#metafield-product-images-list) |
| Customer Address | [List](./REFERENCE.md#customer-address-list), [Get](./REFERENCE.md#customer-address-get) |
| Fulfillment Orders | [List](./REFERENCE.md#fulfillment-orders-list), [Get](./REFERENCE.md#fulfillment-orders-get) |


For detailed documentation on available actions and parameters, see this connector's [full reference documentation](./REFERENCE.md).

For the service's official API docs, see the [Shopify API reference](https://shopify.dev/docs/api/admin-rest).

## Version information

- **Package version:** 0.1.2
- **Connector version:** 0.1.1
- **Generated with Connector SDK commit SHA:** c7dab97573a377c99c730f5f0f2c02733d2b3161