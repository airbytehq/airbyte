# Woocommerce full reference

This is the full reference documentation for the Woocommerce agent connector.

## Supported entities and actions

The Woocommerce connector supports the following entities and actions.

| Entity | Actions |
|--------|---------|
| Customers | [List](#customers-list), [Get](#customers-get), [Search](#customers-search) |
| Orders | [List](#orders-list), [Get](#orders-get), [Search](#orders-search) |
| Products | [List](#products-list), [Get](#products-get), [Search](#products-search) |
| Coupons | [List](#coupons-list), [Get](#coupons-get), [Search](#coupons-search) |
| Product Categories | [List](#product-categories-list), [Get](#product-categories-get), [Search](#product-categories-search) |
| Product Tags | [List](#product-tags-list), [Get](#product-tags-get), [Search](#product-tags-search) |
| Product Reviews | [List](#product-reviews-list), [Get](#product-reviews-get), [Search](#product-reviews-search) |
| Product Attributes | [List](#product-attributes-list), [Get](#product-attributes-get), [Search](#product-attributes-search) |
| Product Variations | [List](#product-variations-list), [Get](#product-variations-get), [Search](#product-variations-search) |
| Order Notes | [List](#order-notes-list), [Get](#order-notes-get), [Search](#order-notes-search) |
| Refunds | [List](#refunds-list), [Get](#refunds-get), [Search](#refunds-search) |
| Payment Gateways | [List](#payment-gateways-list), [Get](#payment-gateways-get), [Search](#payment-gateways-search) |
| Shipping Methods | [List](#shipping-methods-list), [Get](#shipping-methods-get), [Search](#shipping-methods-search) |
| Shipping Zones | [List](#shipping-zones-list), [Get](#shipping-zones-get), [Search](#shipping-zones-search) |
| Tax Rates | [List](#tax-rates-list), [Get](#tax-rates-get), [Search](#tax-rates-search) |
| Tax Classes | [List](#tax-classes-list), [Search](#tax-classes-search) |

## Customers

### Customers List

List customers

#### Python SDK

```python
await woocommerce.customers.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "customers",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page` | `integer` | No | Current page of the collection |
| `per_page` | `integer` | No | Maximum number of items to return per page |
| `search` | `string` | No | Limit results to those matching a string |
| `orderby` | `"id" \| "include" \| "name" \| "registered_date"` | No | Sort collection by attribute |
| `order` | `"asc" \| "desc"` | No | Order sort attribute ascending or descending |
| `email` | `string` | No | Limit result set to resources with a specific email |
| `role` | `"all" \| "administrator" \| "editor" \| "author" \| "contributor" \| "subscriber" \| "customer" \| "shop_manager"` | No | Limit result set to resources with a specific role |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| integer` |  |
| `date_created` | `null \| string` |  |
| `date_created_gmt` | `null \| string` |  |
| `date_modified` | `null \| string` |  |
| `date_modified_gmt` | `null \| string` |  |
| `email` | `null \| string` |  |
| `first_name` | `null \| string` |  |
| `last_name` | `null \| string` |  |
| `role` | `null \| string` |  |
| `username` | `null \| string` |  |
| `billing` | `null \| object` |  |
| `shipping` | `null \| object` |  |
| `is_paying_customer` | `null \| boolean` |  |
| `avatar_url` | `null \| string` |  |
| `meta_data` | `null \| array` |  |


</details>

### Customers Get

Retrieve a customer

#### Python SDK

```python
await woocommerce.customers.get(
    id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "customers",
    "action": "get",
    "params": {
        "id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `integer` | Yes | Unique identifier for the customer |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| integer` |  |
| `date_created` | `null \| string` |  |
| `date_created_gmt` | `null \| string` |  |
| `date_modified` | `null \| string` |  |
| `date_modified_gmt` | `null \| string` |  |
| `email` | `null \| string` |  |
| `first_name` | `null \| string` |  |
| `last_name` | `null \| string` |  |
| `role` | `null \| string` |  |
| `username` | `null \| string` |  |
| `billing` | `null \| object` |  |
| `shipping` | `null \| object` |  |
| `is_paying_customer` | `null \| boolean` |  |
| `avatar_url` | `null \| string` |  |
| `meta_data` | `null \| array` |  |


</details>

### Customers Search

Search and filter customers records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await woocommerce.customers.search(
    query={"filter": {"eq": {"avatar_url": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "customers",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"avatar_url": "<str>"}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, like, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `avatar_url` | `string` | Avatar URL |
| `billing` | `object` | List of billing address data |
| `date_created` | `string` | The date the customer was created, in the site's timezone |
| `date_created_gmt` | `string` | The date the customer was created, as GMT |
| `date_modified` | `string` | The date the customer was last modified, in the site's timezone |
| `date_modified_gmt` | `string` | The date the customer was last modified, as GMT |
| `email` | `string` | The email address for the customer |
| `first_name` | `string` | Customer first name |
| `id` | `integer` | Unique identifier for the resource |
| `is_paying_customer` | `boolean` | Is the customer a paying customer |
| `last_name` | `string` | Customer last name |
| `meta_data` | `array` | Meta data |
| `role` | `string` | Customer role |
| `shipping` | `object` | List of shipping address data |
| `username` | `string` | Customer login name |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].avatar_url` | `string` | Avatar URL |
| `data[].billing` | `object` | List of billing address data |
| `data[].date_created` | `string` | The date the customer was created, in the site's timezone |
| `data[].date_created_gmt` | `string` | The date the customer was created, as GMT |
| `data[].date_modified` | `string` | The date the customer was last modified, in the site's timezone |
| `data[].date_modified_gmt` | `string` | The date the customer was last modified, as GMT |
| `data[].email` | `string` | The email address for the customer |
| `data[].first_name` | `string` | Customer first name |
| `data[].id` | `integer` | Unique identifier for the resource |
| `data[].is_paying_customer` | `boolean` | Is the customer a paying customer |
| `data[].last_name` | `string` | Customer last name |
| `data[].meta_data` | `array` | Meta data |
| `data[].role` | `string` | Customer role |
| `data[].shipping` | `object` | List of shipping address data |
| `data[].username` | `string` | Customer login name |

</details>

## Orders

### Orders List

List orders

#### Python SDK

```python
await woocommerce.orders.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "orders",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page` | `integer` | No | Current page of the collection |
| `per_page` | `integer` | No | Maximum number of items to return per page |
| `search` | `string` | No | Limit results to those matching a string |
| `after` | `string` | No | Limit response to resources published after a given ISO8601 date |
| `before` | `string` | No | Limit response to resources published before a given ISO8601 date |
| `modified_after` | `string` | No | Limit response to resources modified after a given ISO8601 date |
| `modified_before` | `string` | No | Limit response to resources modified before a given ISO8601 date |
| `status` | `"any" \| "pending" \| "processing" \| "on-hold" \| "completed" \| "cancelled" \| "refunded" \| "failed" \| "trash"` | No | Limit result set to orders with a specific status |
| `customer` | `integer` | No | Limit result set to orders assigned to a specific customer ID |
| `product` | `integer` | No | Limit result set to orders that include a specific product ID |
| `orderby` | `"date" \| "id" \| "include" \| "title" \| "slug" \| "modified"` | No | Sort collection by attribute |
| `order` | `"asc" \| "desc"` | No | Order sort attribute ascending or descending |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| integer` |  |
| `parent_id` | `null \| integer` |  |
| `number` | `null \| string` |  |
| `order_key` | `null \| string` |  |
| `created_via` | `null \| string` |  |
| `version` | `null \| string` |  |
| `status` | `null \| string` |  |
| `currency` | `null \| string` |  |
| `currency_symbol` | `null \| string` |  |
| `date_created` | `null \| string` |  |
| `date_created_gmt` | `null \| string` |  |
| `date_modified` | `null \| string` |  |
| `date_modified_gmt` | `null \| string` |  |
| `discount_total` | `null \| string` |  |
| `discount_tax` | `null \| string` |  |
| `shipping_total` | `null \| string` |  |
| `shipping_tax` | `null \| string` |  |
| `cart_tax` | `null \| string` |  |
| `total` | `null \| string` |  |
| `total_tax` | `null \| string` |  |
| `prices_include_tax` | `null \| boolean` |  |
| `customer_id` | `null \| integer` |  |
| `customer_ip_address` | `null \| string` |  |
| `customer_user_agent` | `null \| string` |  |
| `customer_note` | `null \| string` |  |
| `billing` | `null \| object` |  |
| `shipping` | `null \| object` |  |
| `payment_method` | `null \| string` |  |
| `payment_method_title` | `null \| string` |  |
| `transaction_id` | `null \| string` |  |
| `date_paid` | `null \| string` |  |
| `date_paid_gmt` | `null \| string` |  |
| `date_completed` | `null \| string` |  |
| `date_completed_gmt` | `null \| string` |  |
| `cart_hash` | `null \| string` |  |
| `meta_data` | `null \| array` |  |
| `line_items` | `null \| array` |  |
| `tax_lines` | `null \| array` |  |
| `shipping_lines` | `null \| array` |  |
| `fee_lines` | `null \| array` |  |
| `coupon_lines` | `null \| array` |  |
| `refunds` | `null \| array` |  |
| `payment_url` | `null \| string` |  |
| `is_editable` | `null \| boolean` |  |
| `needs_payment` | `null \| boolean` |  |
| `needs_processing` | `null \| boolean` |  |


</details>

### Orders Get

Retrieve an order

#### Python SDK

```python
await woocommerce.orders.get(
    id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "orders",
    "action": "get",
    "params": {
        "id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `integer` | Yes | Unique identifier for the order |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| integer` |  |
| `parent_id` | `null \| integer` |  |
| `number` | `null \| string` |  |
| `order_key` | `null \| string` |  |
| `created_via` | `null \| string` |  |
| `version` | `null \| string` |  |
| `status` | `null \| string` |  |
| `currency` | `null \| string` |  |
| `currency_symbol` | `null \| string` |  |
| `date_created` | `null \| string` |  |
| `date_created_gmt` | `null \| string` |  |
| `date_modified` | `null \| string` |  |
| `date_modified_gmt` | `null \| string` |  |
| `discount_total` | `null \| string` |  |
| `discount_tax` | `null \| string` |  |
| `shipping_total` | `null \| string` |  |
| `shipping_tax` | `null \| string` |  |
| `cart_tax` | `null \| string` |  |
| `total` | `null \| string` |  |
| `total_tax` | `null \| string` |  |
| `prices_include_tax` | `null \| boolean` |  |
| `customer_id` | `null \| integer` |  |
| `customer_ip_address` | `null \| string` |  |
| `customer_user_agent` | `null \| string` |  |
| `customer_note` | `null \| string` |  |
| `billing` | `null \| object` |  |
| `shipping` | `null \| object` |  |
| `payment_method` | `null \| string` |  |
| `payment_method_title` | `null \| string` |  |
| `transaction_id` | `null \| string` |  |
| `date_paid` | `null \| string` |  |
| `date_paid_gmt` | `null \| string` |  |
| `date_completed` | `null \| string` |  |
| `date_completed_gmt` | `null \| string` |  |
| `cart_hash` | `null \| string` |  |
| `meta_data` | `null \| array` |  |
| `line_items` | `null \| array` |  |
| `tax_lines` | `null \| array` |  |
| `shipping_lines` | `null \| array` |  |
| `fee_lines` | `null \| array` |  |
| `coupon_lines` | `null \| array` |  |
| `refunds` | `null \| array` |  |
| `payment_url` | `null \| string` |  |
| `is_editable` | `null \| boolean` |  |
| `needs_payment` | `null \| boolean` |  |
| `needs_processing` | `null \| boolean` |  |


</details>

### Orders Search

Search and filter orders records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await woocommerce.orders.search(
    query={"filter": {"eq": {"billing": {}}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "orders",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"billing": {}}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, like, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `billing` | `object` | Billing address |
| `cart_hash` | `string` | MD5 hash of cart items to ensure orders are not modified |
| `cart_tax` | `string` | Sum of line item taxes only |
| `coupon_lines` | `array` | Coupons line data |
| `created_via` | `string` | Shows where the order was created |
| `currency` | `string` | Currency the order was created with, in ISO format |
| `customer_id` | `integer` | User ID who owns the order (0 for guests) |
| `customer_ip_address` | `string` | Customer's IP address |
| `customer_note` | `string` | Note left by the customer during checkout |
| `customer_user_agent` | `string` | User agent of the customer |
| `date_completed` | `string` | The date the order was completed, in the site's timezone |
| `date_completed_gmt` | `string` | The date the order was completed, as GMT |
| `date_created` | `string` | The date the order was created, in the site's timezone |
| `date_created_gmt` | `string` | The date the order was created, as GMT |
| `date_modified` | `string` | The date the order was last modified, in the site's timezone |
| `date_modified_gmt` | `string` | The date the order was last modified, as GMT |
| `date_paid` | `string` | The date the order was paid, in the site's timezone |
| `date_paid_gmt` | `string` | The date the order was paid, as GMT |
| `discount_tax` | `string` | Total discount tax amount for the order |
| `discount_total` | `string` | Total discount amount for the order |
| `fee_lines` | `array` | Fee lines data |
| `id` | `integer` | Unique identifier for the resource |
| `line_items` | `array` | Line items data |
| `meta_data` | `array` | Meta data |
| `number` | `string` | Order number |
| `order_key` | `string` | Order key |
| `parent_id` | `integer` | Parent order ID |
| `payment_method` | `string` | Payment method ID |
| `payment_method_title` | `string` | Payment method title |
| `prices_include_tax` | `boolean` | True if the prices included tax during checkout |
| `refunds` | `array` | List of refunds |
| `shipping` | `object` | Shipping address |
| `shipping_lines` | `array` | Shipping lines data |
| `shipping_tax` | `string` | Total shipping tax amount for the order |
| `shipping_total` | `string` | Total shipping amount for the order |
| `status` | `string` | Order status |
| `tax_lines` | `array` | Tax lines data |
| `total` | `string` | Grand total |
| `total_tax` | `string` | Sum of all taxes |
| `transaction_id` | `string` | Unique transaction ID |
| `version` | `string` | Version of WooCommerce which last updated the order |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].billing` | `object` | Billing address |
| `data[].cart_hash` | `string` | MD5 hash of cart items to ensure orders are not modified |
| `data[].cart_tax` | `string` | Sum of line item taxes only |
| `data[].coupon_lines` | `array` | Coupons line data |
| `data[].created_via` | `string` | Shows where the order was created |
| `data[].currency` | `string` | Currency the order was created with, in ISO format |
| `data[].customer_id` | `integer` | User ID who owns the order (0 for guests) |
| `data[].customer_ip_address` | `string` | Customer's IP address |
| `data[].customer_note` | `string` | Note left by the customer during checkout |
| `data[].customer_user_agent` | `string` | User agent of the customer |
| `data[].date_completed` | `string` | The date the order was completed, in the site's timezone |
| `data[].date_completed_gmt` | `string` | The date the order was completed, as GMT |
| `data[].date_created` | `string` | The date the order was created, in the site's timezone |
| `data[].date_created_gmt` | `string` | The date the order was created, as GMT |
| `data[].date_modified` | `string` | The date the order was last modified, in the site's timezone |
| `data[].date_modified_gmt` | `string` | The date the order was last modified, as GMT |
| `data[].date_paid` | `string` | The date the order was paid, in the site's timezone |
| `data[].date_paid_gmt` | `string` | The date the order was paid, as GMT |
| `data[].discount_tax` | `string` | Total discount tax amount for the order |
| `data[].discount_total` | `string` | Total discount amount for the order |
| `data[].fee_lines` | `array` | Fee lines data |
| `data[].id` | `integer` | Unique identifier for the resource |
| `data[].line_items` | `array` | Line items data |
| `data[].meta_data` | `array` | Meta data |
| `data[].number` | `string` | Order number |
| `data[].order_key` | `string` | Order key |
| `data[].parent_id` | `integer` | Parent order ID |
| `data[].payment_method` | `string` | Payment method ID |
| `data[].payment_method_title` | `string` | Payment method title |
| `data[].prices_include_tax` | `boolean` | True if the prices included tax during checkout |
| `data[].refunds` | `array` | List of refunds |
| `data[].shipping` | `object` | Shipping address |
| `data[].shipping_lines` | `array` | Shipping lines data |
| `data[].shipping_tax` | `string` | Total shipping tax amount for the order |
| `data[].shipping_total` | `string` | Total shipping amount for the order |
| `data[].status` | `string` | Order status |
| `data[].tax_lines` | `array` | Tax lines data |
| `data[].total` | `string` | Grand total |
| `data[].total_tax` | `string` | Sum of all taxes |
| `data[].transaction_id` | `string` | Unique transaction ID |
| `data[].version` | `string` | Version of WooCommerce which last updated the order |

</details>

## Products

### Products List

List products

#### Python SDK

```python
await woocommerce.products.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "products",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page` | `integer` | No | Current page of the collection |
| `per_page` | `integer` | No | Maximum number of items to return per page |
| `search` | `string` | No | Limit results to those matching a string |
| `after` | `string` | No | Limit response to resources published after a given ISO8601 date |
| `before` | `string` | No | Limit response to resources published before a given ISO8601 date |
| `modified_after` | `string` | No | Limit response to resources modified after a given ISO8601 date |
| `modified_before` | `string` | No | Limit response to resources modified before a given ISO8601 date |
| `status` | `"any" \| "draft" \| "pending" \| "private" \| "publish"` | No | Limit result set to products with a specific status |
| `type` | `"simple" \| "grouped" \| "external" \| "variable"` | No | Limit result set to products with a specific type |
| `sku` | `string` | No | Limit result set to products with a specific SKU |
| `featured` | `boolean` | No | Limit result set to featured products |
| `category` | `string` | No | Limit result set to products assigned a specific category ID |
| `tag` | `string` | No | Limit result set to products assigned a specific tag ID |
| `on_sale` | `boolean` | No | Limit result set to products on sale |
| `min_price` | `string` | No | Limit result set to products based on a minimum price |
| `max_price` | `string` | No | Limit result set to products based on a maximum price |
| `stock_status` | `"instock" \| "outofstock" \| "onbackorder"` | No | Limit result set to products with specified stock status |
| `orderby` | `"date" \| "id" \| "include" \| "title" \| "slug" \| "price" \| "popularity" \| "rating" \| "menu_order" \| "modified"` | No | Sort collection by attribute |
| `order` | `"asc" \| "desc"` | No | Order sort attribute ascending or descending |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| integer` |  |
| `name` | `null \| string` |  |
| `slug` | `null \| string` |  |
| `permalink` | `null \| string` |  |
| `date_created` | `null \| string` |  |
| `date_created_gmt` | `null \| string` |  |
| `date_modified` | `null \| string` |  |
| `date_modified_gmt` | `null \| string` |  |
| `type` | `null \| string` |  |
| `status` | `null \| string` |  |
| `featured` | `null \| boolean` |  |
| `catalog_visibility` | `null \| string` |  |
| `description` | `null \| string` |  |
| `short_description` | `null \| string` |  |
| `sku` | `null \| string` |  |
| `price` | `null \| string` |  |
| `regular_price` | `null \| string` |  |
| `sale_price` | `null \| string` |  |
| `date_on_sale_from` | `null \| string` |  |
| `date_on_sale_from_gmt` | `null \| string` |  |
| `date_on_sale_to` | `null \| string` |  |
| `date_on_sale_to_gmt` | `null \| string` |  |
| `price_html` | `null \| string` |  |
| `on_sale` | `null \| boolean` |  |
| `purchasable` | `null \| boolean` |  |
| `total_sales` | `null \| integer` |  |
| `virtual` | `null \| boolean` |  |
| `downloadable` | `null \| boolean` |  |
| `downloads` | `null \| array` |  |
| `download_limit` | `null \| integer` |  |
| `download_expiry` | `null \| integer` |  |
| `external_url` | `null \| string` |  |
| `button_text` | `null \| string` |  |
| `tax_status` | `null \| string` |  |
| `tax_class` | `null \| string` |  |
| `manage_stock` | `null \| boolean` |  |
| `stock_quantity` | `null \| integer` |  |
| `stock_status` | `null \| string` |  |
| `backorders` | `null \| string` |  |
| `backorders_allowed` | `null \| boolean` |  |
| `backordered` | `null \| boolean` |  |
| `sold_individually` | `null \| boolean` |  |
| `weight` | `null \| string` |  |
| `dimensions` | `null \| object` |  |
| `shipping_required` | `null \| boolean` |  |
| `shipping_taxable` | `null \| boolean` |  |
| `shipping_class` | `null \| string` |  |
| `shipping_class_id` | `null \| integer` |  |
| `reviews_allowed` | `null \| boolean` |  |
| `average_rating` | `null \| string` |  |
| `rating_count` | `null \| integer` |  |
| `related_ids` | `null \| array` |  |
| `upsell_ids` | `null \| array` |  |
| `cross_sell_ids` | `null \| array` |  |
| `parent_id` | `null \| integer` |  |
| `purchase_note` | `null \| string` |  |
| `categories` | `null \| array` |  |
| `tags` | `null \| array` |  |
| `images` | `null \| array` |  |
| `attributes` | `null \| array` |  |
| `default_attributes` | `null \| array` |  |
| `variations` | `null \| array` |  |
| `grouped_products` | `null \| array` |  |
| `menu_order` | `null \| integer` |  |
| `meta_data` | `null \| array` |  |
| `low_stock_amount` | `null \| integer` |  |
| `brands` | `null \| array` |  |
| `has_options` | `null \| boolean` |  |
| `post_password` | `null \| string` |  |
| `global_unique_id` | `null \| string` |  |


</details>

### Products Get

Retrieve a product

#### Python SDK

```python
await woocommerce.products.get(
    id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "products",
    "action": "get",
    "params": {
        "id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `integer` | Yes | Unique identifier for the product |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| integer` |  |
| `name` | `null \| string` |  |
| `slug` | `null \| string` |  |
| `permalink` | `null \| string` |  |
| `date_created` | `null \| string` |  |
| `date_created_gmt` | `null \| string` |  |
| `date_modified` | `null \| string` |  |
| `date_modified_gmt` | `null \| string` |  |
| `type` | `null \| string` |  |
| `status` | `null \| string` |  |
| `featured` | `null \| boolean` |  |
| `catalog_visibility` | `null \| string` |  |
| `description` | `null \| string` |  |
| `short_description` | `null \| string` |  |
| `sku` | `null \| string` |  |
| `price` | `null \| string` |  |
| `regular_price` | `null \| string` |  |
| `sale_price` | `null \| string` |  |
| `date_on_sale_from` | `null \| string` |  |
| `date_on_sale_from_gmt` | `null \| string` |  |
| `date_on_sale_to` | `null \| string` |  |
| `date_on_sale_to_gmt` | `null \| string` |  |
| `price_html` | `null \| string` |  |
| `on_sale` | `null \| boolean` |  |
| `purchasable` | `null \| boolean` |  |
| `total_sales` | `null \| integer` |  |
| `virtual` | `null \| boolean` |  |
| `downloadable` | `null \| boolean` |  |
| `downloads` | `null \| array` |  |
| `download_limit` | `null \| integer` |  |
| `download_expiry` | `null \| integer` |  |
| `external_url` | `null \| string` |  |
| `button_text` | `null \| string` |  |
| `tax_status` | `null \| string` |  |
| `tax_class` | `null \| string` |  |
| `manage_stock` | `null \| boolean` |  |
| `stock_quantity` | `null \| integer` |  |
| `stock_status` | `null \| string` |  |
| `backorders` | `null \| string` |  |
| `backorders_allowed` | `null \| boolean` |  |
| `backordered` | `null \| boolean` |  |
| `sold_individually` | `null \| boolean` |  |
| `weight` | `null \| string` |  |
| `dimensions` | `null \| object` |  |
| `shipping_required` | `null \| boolean` |  |
| `shipping_taxable` | `null \| boolean` |  |
| `shipping_class` | `null \| string` |  |
| `shipping_class_id` | `null \| integer` |  |
| `reviews_allowed` | `null \| boolean` |  |
| `average_rating` | `null \| string` |  |
| `rating_count` | `null \| integer` |  |
| `related_ids` | `null \| array` |  |
| `upsell_ids` | `null \| array` |  |
| `cross_sell_ids` | `null \| array` |  |
| `parent_id` | `null \| integer` |  |
| `purchase_note` | `null \| string` |  |
| `categories` | `null \| array` |  |
| `tags` | `null \| array` |  |
| `images` | `null \| array` |  |
| `attributes` | `null \| array` |  |
| `default_attributes` | `null \| array` |  |
| `variations` | `null \| array` |  |
| `grouped_products` | `null \| array` |  |
| `menu_order` | `null \| integer` |  |
| `meta_data` | `null \| array` |  |
| `low_stock_amount` | `null \| integer` |  |
| `brands` | `null \| array` |  |
| `has_options` | `null \| boolean` |  |
| `post_password` | `null \| string` |  |
| `global_unique_id` | `null \| string` |  |


</details>

### Products Search

Search and filter products records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await woocommerce.products.search(
    query={"filter": {"eq": {"attributes": []}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "products",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"attributes": []}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, like, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `attributes` | `array` | List of attributes |
| `average_rating` | `string` | Reviews average rating |
| `backordered` | `boolean` | Shows if the product is on backordered |
| `backorders` | `string` | If managing stock, this controls if backorders are allowed |
| `backorders_allowed` | `boolean` | Shows if backorders are allowed |
| `button_text` | `string` | Product external button text |
| `catalog_visibility` | `string` | Catalog visibility |
| `categories` | `array` | List of categories |
| `cross_sell_ids` | `array` | List of cross-sell products IDs |
| `date_created` | `string` | The date the product was created |
| `date_created_gmt` | `string` | The date the product was created, as GMT |
| `date_modified` | `string` | The date the product was last modified |
| `date_modified_gmt` | `string` | The date the product was last modified, as GMT |
| `date_on_sale_from` | `string` | Start date of sale price |
| `date_on_sale_from_gmt` | `string` | Start date of sale price, as GMT |
| `date_on_sale_to` | `string` | End date of sale price |
| `date_on_sale_to_gmt` | `string` | End date of sale price, as GMT |
| `default_attributes` | `array` | Defaults variation attributes |
| `description` | `string` | Product description |
| `dimensions` | `object` | Product dimensions |
| `download_expiry` | `integer` | Number of days until access to downloadable files expires |
| `download_limit` | `integer` | Number of times downloadable files can be downloaded |
| `downloadable` | `boolean` | If the product is downloadable |
| `downloads` | `array` | List of downloadable files |
| `external_url` | `string` | Product external URL |
| `grouped_products` | `array` | List of grouped products ID |
| `id` | `integer` | Unique identifier for the resource |
| `images` | `array` | List of images |
| `manage_stock` | `boolean` | Stock management at product level |
| `menu_order` | `integer` | Menu order |
| `meta_data` | `array` | Meta data |
| `name` | `string` | Product name |
| `on_sale` | `boolean` | Shows if the product is on sale |
| `parent_id` | `integer` | Product parent ID |
| `permalink` | `string` | Product URL |
| `price` | `string` | Current product price |
| `price_html` | `string` | Price formatted in HTML |
| `purchasable` | `boolean` | Shows if the product can be bought |
| `purchase_note` | `string` | Note to send customer after purchase |
| `rating_count` | `integer` | Amount of reviews |
| `regular_price` | `string` | Product regular price |
| `related_ids` | `array` | List of related products IDs |
| `reviews_allowed` | `boolean` | Allow reviews |
| `sale_price` | `string` | Product sale price |
| `shipping_class` | `string` | Shipping class slug |
| `shipping_class_id` | `integer` | Shipping class ID |
| `shipping_required` | `boolean` | Shows if the product needs to be shipped |
| `shipping_taxable` | `boolean` | Shows if product shipping is taxable |
| `short_description` | `string` | Product short description |
| `sku` | `string` | Unique identifier (SKU) |
| `slug` | `string` | Product slug |
| `sold_individually` | `boolean` | Allow one item per order |
| `status` | `string` | Product status |
| `stock_quantity` | `integer` | Stock quantity |
| `stock_status` | `string` | Controls the stock status |
| `tags` | `array` | List of tags |
| `tax_class` | `string` | Tax class |
| `tax_status` | `string` | Tax status |
| `total_sales` | `integer` | Amount of sales |
| `type` | `string` | Product type |
| `upsell_ids` | `array` | List of up-sell products IDs |
| `variations` | `array` | List of variations IDs |
| `virtual` | `boolean` | If the product is virtual |
| `weight` | `string` | Product weight |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].attributes` | `array` | List of attributes |
| `data[].average_rating` | `string` | Reviews average rating |
| `data[].backordered` | `boolean` | Shows if the product is on backordered |
| `data[].backorders` | `string` | If managing stock, this controls if backorders are allowed |
| `data[].backorders_allowed` | `boolean` | Shows if backorders are allowed |
| `data[].button_text` | `string` | Product external button text |
| `data[].catalog_visibility` | `string` | Catalog visibility |
| `data[].categories` | `array` | List of categories |
| `data[].cross_sell_ids` | `array` | List of cross-sell products IDs |
| `data[].date_created` | `string` | The date the product was created |
| `data[].date_created_gmt` | `string` | The date the product was created, as GMT |
| `data[].date_modified` | `string` | The date the product was last modified |
| `data[].date_modified_gmt` | `string` | The date the product was last modified, as GMT |
| `data[].date_on_sale_from` | `string` | Start date of sale price |
| `data[].date_on_sale_from_gmt` | `string` | Start date of sale price, as GMT |
| `data[].date_on_sale_to` | `string` | End date of sale price |
| `data[].date_on_sale_to_gmt` | `string` | End date of sale price, as GMT |
| `data[].default_attributes` | `array` | Defaults variation attributes |
| `data[].description` | `string` | Product description |
| `data[].dimensions` | `object` | Product dimensions |
| `data[].download_expiry` | `integer` | Number of days until access to downloadable files expires |
| `data[].download_limit` | `integer` | Number of times downloadable files can be downloaded |
| `data[].downloadable` | `boolean` | If the product is downloadable |
| `data[].downloads` | `array` | List of downloadable files |
| `data[].external_url` | `string` | Product external URL |
| `data[].grouped_products` | `array` | List of grouped products ID |
| `data[].id` | `integer` | Unique identifier for the resource |
| `data[].images` | `array` | List of images |
| `data[].manage_stock` | `boolean` | Stock management at product level |
| `data[].menu_order` | `integer` | Menu order |
| `data[].meta_data` | `array` | Meta data |
| `data[].name` | `string` | Product name |
| `data[].on_sale` | `boolean` | Shows if the product is on sale |
| `data[].parent_id` | `integer` | Product parent ID |
| `data[].permalink` | `string` | Product URL |
| `data[].price` | `string` | Current product price |
| `data[].price_html` | `string` | Price formatted in HTML |
| `data[].purchasable` | `boolean` | Shows if the product can be bought |
| `data[].purchase_note` | `string` | Note to send customer after purchase |
| `data[].rating_count` | `integer` | Amount of reviews |
| `data[].regular_price` | `string` | Product regular price |
| `data[].related_ids` | `array` | List of related products IDs |
| `data[].reviews_allowed` | `boolean` | Allow reviews |
| `data[].sale_price` | `string` | Product sale price |
| `data[].shipping_class` | `string` | Shipping class slug |
| `data[].shipping_class_id` | `integer` | Shipping class ID |
| `data[].shipping_required` | `boolean` | Shows if the product needs to be shipped |
| `data[].shipping_taxable` | `boolean` | Shows if product shipping is taxable |
| `data[].short_description` | `string` | Product short description |
| `data[].sku` | `string` | Unique identifier (SKU) |
| `data[].slug` | `string` | Product slug |
| `data[].sold_individually` | `boolean` | Allow one item per order |
| `data[].status` | `string` | Product status |
| `data[].stock_quantity` | `integer` | Stock quantity |
| `data[].stock_status` | `string` | Controls the stock status |
| `data[].tags` | `array` | List of tags |
| `data[].tax_class` | `string` | Tax class |
| `data[].tax_status` | `string` | Tax status |
| `data[].total_sales` | `integer` | Amount of sales |
| `data[].type` | `string` | Product type |
| `data[].upsell_ids` | `array` | List of up-sell products IDs |
| `data[].variations` | `array` | List of variations IDs |
| `data[].virtual` | `boolean` | If the product is virtual |
| `data[].weight` | `string` | Product weight |

</details>

## Coupons

### Coupons List

List coupons

#### Python SDK

```python
await woocommerce.coupons.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "coupons",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page` | `integer` | No | Current page of the collection |
| `per_page` | `integer` | No | Maximum number of items to return per page |
| `search` | `string` | No | Limit results to those matching a string |
| `after` | `string` | No | Limit response to resources published after a given ISO8601 date |
| `before` | `string` | No | Limit response to resources published before a given ISO8601 date |
| `modified_after` | `string` | No | Limit response to resources modified after a given ISO8601 date |
| `modified_before` | `string` | No | Limit response to resources modified before a given ISO8601 date |
| `code` | `string` | No | Limit result set to resources with a specific code |
| `orderby` | `"date" \| "id" \| "include" \| "title" \| "slug" \| "modified"` | No | Sort collection by attribute |
| `order` | `"asc" \| "desc"` | No | Order sort attribute ascending or descending |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| integer` |  |
| `code` | `null \| string` |  |
| `amount` | `null \| string` |  |
| `date_created` | `null \| string` |  |
| `date_created_gmt` | `null \| string` |  |
| `date_modified` | `null \| string` |  |
| `date_modified_gmt` | `null \| string` |  |
| `discount_type` | `null \| string` |  |
| `description` | `null \| string` |  |
| `date_expires` | `null \| string` |  |
| `date_expires_gmt` | `null \| string` |  |
| `usage_count` | `null \| integer` |  |
| `individual_use` | `null \| boolean` |  |
| `product_ids` | `null \| array` |  |
| `excluded_product_ids` | `null \| array` |  |
| `usage_limit` | `null \| integer` |  |
| `usage_limit_per_user` | `null \| integer` |  |
| `limit_usage_to_x_items` | `null \| integer` |  |
| `free_shipping` | `null \| boolean` |  |
| `product_categories` | `null \| array` |  |
| `excluded_product_categories` | `null \| array` |  |
| `exclude_sale_items` | `null \| boolean` |  |
| `minimum_amount` | `null \| string` |  |
| `maximum_amount` | `null \| string` |  |
| `email_restrictions` | `null \| array` |  |
| `used_by` | `null \| array` |  |
| `meta_data` | `null \| array` |  |
| `status` | `null \| string` |  |


</details>

### Coupons Get

Retrieve a coupon

#### Python SDK

```python
await woocommerce.coupons.get(
    id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "coupons",
    "action": "get",
    "params": {
        "id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `integer` | Yes | Unique identifier for the coupon |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| integer` |  |
| `code` | `null \| string` |  |
| `amount` | `null \| string` |  |
| `date_created` | `null \| string` |  |
| `date_created_gmt` | `null \| string` |  |
| `date_modified` | `null \| string` |  |
| `date_modified_gmt` | `null \| string` |  |
| `discount_type` | `null \| string` |  |
| `description` | `null \| string` |  |
| `date_expires` | `null \| string` |  |
| `date_expires_gmt` | `null \| string` |  |
| `usage_count` | `null \| integer` |  |
| `individual_use` | `null \| boolean` |  |
| `product_ids` | `null \| array` |  |
| `excluded_product_ids` | `null \| array` |  |
| `usage_limit` | `null \| integer` |  |
| `usage_limit_per_user` | `null \| integer` |  |
| `limit_usage_to_x_items` | `null \| integer` |  |
| `free_shipping` | `null \| boolean` |  |
| `product_categories` | `null \| array` |  |
| `excluded_product_categories` | `null \| array` |  |
| `exclude_sale_items` | `null \| boolean` |  |
| `minimum_amount` | `null \| string` |  |
| `maximum_amount` | `null \| string` |  |
| `email_restrictions` | `null \| array` |  |
| `used_by` | `null \| array` |  |
| `meta_data` | `null \| array` |  |
| `status` | `null \| string` |  |


</details>

### Coupons Search

Search and filter coupons records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await woocommerce.coupons.search(
    query={"filter": {"eq": {"amount": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "coupons",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"amount": "<str>"}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, like, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `amount` | `string` | The amount of discount |
| `code` | `string` | Coupon code |
| `date_created` | `string` | The date the coupon was created |
| `date_created_gmt` | `string` | The date the coupon was created, as GMT |
| `date_expires` | `string` | The date the coupon expires |
| `date_expires_gmt` | `string` | The date the coupon expires, as GMT |
| `date_modified` | `string` | The date the coupon was last modified |
| `date_modified_gmt` | `string` | The date the coupon was last modified, as GMT |
| `description` | `string` | Coupon description |
| `discount_type` | `string` | Determines the type of discount |
| `email_restrictions` | `array` | List of email addresses that can use this coupon |
| `exclude_sale_items` | `boolean` | If true, not applied to sale items |
| `excluded_product_categories` | `array` | Excluded category IDs |
| `excluded_product_ids` | `array` | Excluded product IDs |
| `free_shipping` | `boolean` | Enables free shipping |
| `id` | `integer` | Unique identifier |
| `individual_use` | `boolean` | Can only be used individually |
| `limit_usage_to_x_items` | `integer` | Max cart items coupon applies to |
| `maximum_amount` | `string` | Maximum order amount |
| `meta_data` | `array` | Meta data |
| `minimum_amount` | `string` | Minimum order amount |
| `product_categories` | `array` | Applicable category IDs |
| `product_ids` | `array` | Applicable product IDs |
| `usage_count` | `integer` | Times used |
| `usage_limit` | `integer` | Total usage limit |
| `usage_limit_per_user` | `integer` | Per-customer usage limit |
| `used_by` | `array` | Users who have used the coupon |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].amount` | `string` | The amount of discount |
| `data[].code` | `string` | Coupon code |
| `data[].date_created` | `string` | The date the coupon was created |
| `data[].date_created_gmt` | `string` | The date the coupon was created, as GMT |
| `data[].date_expires` | `string` | The date the coupon expires |
| `data[].date_expires_gmt` | `string` | The date the coupon expires, as GMT |
| `data[].date_modified` | `string` | The date the coupon was last modified |
| `data[].date_modified_gmt` | `string` | The date the coupon was last modified, as GMT |
| `data[].description` | `string` | Coupon description |
| `data[].discount_type` | `string` | Determines the type of discount |
| `data[].email_restrictions` | `array` | List of email addresses that can use this coupon |
| `data[].exclude_sale_items` | `boolean` | If true, not applied to sale items |
| `data[].excluded_product_categories` | `array` | Excluded category IDs |
| `data[].excluded_product_ids` | `array` | Excluded product IDs |
| `data[].free_shipping` | `boolean` | Enables free shipping |
| `data[].id` | `integer` | Unique identifier |
| `data[].individual_use` | `boolean` | Can only be used individually |
| `data[].limit_usage_to_x_items` | `integer` | Max cart items coupon applies to |
| `data[].maximum_amount` | `string` | Maximum order amount |
| `data[].meta_data` | `array` | Meta data |
| `data[].minimum_amount` | `string` | Minimum order amount |
| `data[].product_categories` | `array` | Applicable category IDs |
| `data[].product_ids` | `array` | Applicable product IDs |
| `data[].usage_count` | `integer` | Times used |
| `data[].usage_limit` | `integer` | Total usage limit |
| `data[].usage_limit_per_user` | `integer` | Per-customer usage limit |
| `data[].used_by` | `array` | Users who have used the coupon |

</details>

## Product Categories

### Product Categories List

List product categories

#### Python SDK

```python
await woocommerce.product_categories.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "product_categories",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page` | `integer` | No | Current page of the collection |
| `per_page` | `integer` | No | Maximum number of items to return per page |
| `search` | `string` | No | Limit results to those matching a string |
| `orderby` | `"id" \| "include" \| "name" \| "slug" \| "term_group" \| "description" \| "count"` | No | Sort collection by attribute |
| `order` | `"asc" \| "desc"` | No | Order sort attribute ascending or descending |
| `hide_empty` | `boolean` | No | Whether to hide categories not assigned to any products |
| `parent` | `integer` | No | Limit result set to categories assigned a specific parent |
| `product` | `integer` | No | Limit result set to categories assigned to a specific product |
| `slug` | `string` | No | Limit result set to categories with a specific slug |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| integer` |  |
| `name` | `null \| string` |  |
| `slug` | `null \| string` |  |
| `parent` | `null \| integer` |  |
| `description` | `null \| string` |  |
| `display` | `null \| string` |  |
| `image` | `null \| object` |  |
| `menu_order` | `null \| integer` |  |
| `count` | `null \| integer` |  |


</details>

### Product Categories Get

Retrieve a product category

#### Python SDK

```python
await woocommerce.product_categories.get(
    id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "product_categories",
    "action": "get",
    "params": {
        "id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `integer` | Yes | Unique identifier for the category |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| integer` |  |
| `name` | `null \| string` |  |
| `slug` | `null \| string` |  |
| `parent` | `null \| integer` |  |
| `description` | `null \| string` |  |
| `display` | `null \| string` |  |
| `image` | `null \| object` |  |
| `menu_order` | `null \| integer` |  |
| `count` | `null \| integer` |  |


</details>

### Product Categories Search

Search and filter product categories records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await woocommerce.product_categories.search(
    query={"filter": {"eq": {"count": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "product_categories",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"count": 0}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, like, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `count` | `integer` | Number of published products for the resource |
| `description` | `string` | HTML description of the resource |
| `display` | `string` | Category archive display type |
| `id` | `integer` | Unique identifier for the resource |
| `image` | `array` | Image data |
| `menu_order` | `integer` | Menu order |
| `name` | `string` | Category name |
| `parent` | `integer` | The ID for the parent of the resource |
| `slug` | `string` | An alphanumeric identifier |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].count` | `integer` | Number of published products for the resource |
| `data[].description` | `string` | HTML description of the resource |
| `data[].display` | `string` | Category archive display type |
| `data[].id` | `integer` | Unique identifier for the resource |
| `data[].image` | `array` | Image data |
| `data[].menu_order` | `integer` | Menu order |
| `data[].name` | `string` | Category name |
| `data[].parent` | `integer` | The ID for the parent of the resource |
| `data[].slug` | `string` | An alphanumeric identifier |

</details>

## Product Tags

### Product Tags List

List product tags

#### Python SDK

```python
await woocommerce.product_tags.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "product_tags",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page` | `integer` | No | Current page of the collection |
| `per_page` | `integer` | No | Maximum number of items to return per page |
| `search` | `string` | No | Limit results to those matching a string |
| `orderby` | `"id" \| "include" \| "name" \| "slug" \| "term_group" \| "description" \| "count"` | No | Sort collection by attribute |
| `order` | `"asc" \| "desc"` | No | Order sort attribute ascending or descending |
| `hide_empty` | `boolean` | No | Whether to hide tags not assigned to any products |
| `product` | `integer` | No | Limit result set to tags assigned to a specific product |
| `slug` | `string` | No | Limit result set to tags with a specific slug |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| integer` |  |
| `name` | `null \| string` |  |
| `slug` | `null \| string` |  |
| `description` | `null \| string` |  |
| `count` | `null \| integer` |  |


</details>

### Product Tags Get

Retrieve a product tag

#### Python SDK

```python
await woocommerce.product_tags.get(
    id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "product_tags",
    "action": "get",
    "params": {
        "id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `integer` | Yes | Unique identifier for the tag |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| integer` |  |
| `name` | `null \| string` |  |
| `slug` | `null \| string` |  |
| `description` | `null \| string` |  |
| `count` | `null \| integer` |  |


</details>

### Product Tags Search

Search and filter product tags records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await woocommerce.product_tags.search(
    query={"filter": {"eq": {"count": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "product_tags",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"count": 0}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, like, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `count` | `integer` | Number of published products |
| `description` | `string` | HTML description |
| `id` | `integer` | Unique identifier |
| `name` | `string` | Tag name |
| `slug` | `string` | Alphanumeric identifier |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].count` | `integer` | Number of published products |
| `data[].description` | `string` | HTML description |
| `data[].id` | `integer` | Unique identifier |
| `data[].name` | `string` | Tag name |
| `data[].slug` | `string` | Alphanumeric identifier |

</details>

## Product Reviews

### Product Reviews List

List product reviews

#### Python SDK

```python
await woocommerce.product_reviews.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "product_reviews",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page` | `integer` | No | Current page of the collection |
| `per_page` | `integer` | No | Maximum number of items to return per page |
| `search` | `string` | No | Limit results to those matching a string |
| `after` | `string` | No | Limit response to reviews published after a given ISO8601 date |
| `before` | `string` | No | Limit response to reviews published before a given ISO8601 date |
| `product` | `array<integer>` | No | Limit result set to reviews assigned to specific product IDs |
| `status` | `"all" \| "hold" \| "approved" \| "spam" \| "trash"` | No | Limit result set to reviews assigned a specific status |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| integer` |  |
| `date_created` | `null \| string` |  |
| `date_created_gmt` | `null \| string` |  |
| `product_id` | `null \| integer` |  |
| `product_name` | `null \| string` |  |
| `product_permalink` | `null \| string` |  |
| `status` | `null \| string` |  |
| `reviewer` | `null \| string` |  |
| `reviewer_email` | `null \| string` |  |
| `review` | `null \| string` |  |
| `rating` | `null \| integer` |  |
| `verified` | `null \| boolean` |  |
| `reviewer_avatar_urls` | `null \| object` |  |


</details>

### Product Reviews Get

Retrieve a product review

#### Python SDK

```python
await woocommerce.product_reviews.get(
    id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "product_reviews",
    "action": "get",
    "params": {
        "id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `integer` | Yes | Unique identifier for the review |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| integer` |  |
| `date_created` | `null \| string` |  |
| `date_created_gmt` | `null \| string` |  |
| `product_id` | `null \| integer` |  |
| `product_name` | `null \| string` |  |
| `product_permalink` | `null \| string` |  |
| `status` | `null \| string` |  |
| `reviewer` | `null \| string` |  |
| `reviewer_email` | `null \| string` |  |
| `review` | `null \| string` |  |
| `rating` | `null \| integer` |  |
| `verified` | `null \| boolean` |  |
| `reviewer_avatar_urls` | `null \| object` |  |


</details>

### Product Reviews Search

Search and filter product reviews records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await woocommerce.product_reviews.search(
    query={"filter": {"eq": {"date_created": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "product_reviews",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"date_created": "<str>"}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, like, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `date_created` | `string` | The date the review was created |
| `date_created_gmt` | `string` | The date the review was created, as GMT |
| `id` | `integer` | Unique identifier |
| `product_id` | `integer` | Product the review belongs to |
| `rating` | `integer` | Review rating (0 to 5) |
| `review` | `string` | The content of the review |
| `reviewer` | `string` | Reviewer name |
| `reviewer_email` | `string` | Reviewer email |
| `status` | `string` | Status of the review |
| `verified` | `boolean` | Shows if the reviewer bought the product |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].date_created` | `string` | The date the review was created |
| `data[].date_created_gmt` | `string` | The date the review was created, as GMT |
| `data[].id` | `integer` | Unique identifier |
| `data[].product_id` | `integer` | Product the review belongs to |
| `data[].rating` | `integer` | Review rating (0 to 5) |
| `data[].review` | `string` | The content of the review |
| `data[].reviewer` | `string` | Reviewer name |
| `data[].reviewer_email` | `string` | Reviewer email |
| `data[].status` | `string` | Status of the review |
| `data[].verified` | `boolean` | Shows if the reviewer bought the product |

</details>

## Product Attributes

### Product Attributes List

List product attributes

#### Python SDK

```python
await woocommerce.product_attributes.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "product_attributes",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page` | `integer` | No | Current page of the collection |
| `per_page` | `integer` | No | Maximum number of items to return per page |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| integer` |  |
| `name` | `null \| string` |  |
| `slug` | `null \| string` |  |
| `type` | `null \| string` |  |
| `order_by` | `null \| string` |  |
| `has_archives` | `null \| boolean` |  |


</details>

### Product Attributes Get

Retrieve a product attribute

#### Python SDK

```python
await woocommerce.product_attributes.get(
    id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "product_attributes",
    "action": "get",
    "params": {
        "id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `integer` | Yes | Unique identifier for the attribute |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| integer` |  |
| `name` | `null \| string` |  |
| `slug` | `null \| string` |  |
| `type` | `null \| string` |  |
| `order_by` | `null \| string` |  |
| `has_archives` | `null \| boolean` |  |


</details>

### Product Attributes Search

Search and filter product attributes records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await woocommerce.product_attributes.search(
    query={"filter": {"eq": {"has_archives": True}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "product_attributes",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"has_archives": True}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, like, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `has_archives` | `boolean` | Enable/Disable attribute archives |
| `id` | `integer` | Unique identifier |
| `name` | `string` | Attribute name |
| `order_by` | `string` | Default sort order |
| `slug` | `string` | Alphanumeric identifier |
| `type` | `string` | Type of attribute |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].has_archives` | `boolean` | Enable/Disable attribute archives |
| `data[].id` | `integer` | Unique identifier |
| `data[].name` | `string` | Attribute name |
| `data[].order_by` | `string` | Default sort order |
| `data[].slug` | `string` | Alphanumeric identifier |
| `data[].type` | `string` | Type of attribute |

</details>

## Product Variations

### Product Variations List

List product variations

#### Python SDK

```python
await woocommerce.product_variations.list(
    product_id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "product_variations",
    "action": "list",
    "params": {
        "product_id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `product_id` | `integer` | Yes | Unique identifier for the parent product |
| `page` | `integer` | No | Current page of the collection |
| `per_page` | `integer` | No | Maximum number of items to return per page |
| `search` | `string` | No | Limit results to those matching a string |
| `sku` | `string` | No | Limit result set to variations with a specific SKU |
| `status` | `"any" \| "draft" \| "pending" \| "private" \| "publish"` | No | Limit result set to variations with a specific status |
| `stock_status` | `"instock" \| "outofstock" \| "onbackorder"` | No | Limit result set to variations with specified stock status |
| `on_sale` | `boolean` | No | Limit result set to variations on sale |
| `min_price` | `string` | No | Limit result set to variations based on a minimum price |
| `max_price` | `string` | No | Limit result set to variations based on a maximum price |
| `orderby` | `"date" \| "id" \| "include" \| "title" \| "slug" \| "menu_order" \| "modified"` | No | Sort collection by attribute |
| `order` | `"asc" \| "desc"` | No | Order sort attribute ascending or descending |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| integer` |  |
| `date_created` | `null \| string` |  |
| `date_created_gmt` | `null \| string` |  |
| `date_modified` | `null \| string` |  |
| `date_modified_gmt` | `null \| string` |  |
| `description` | `null \| string` |  |
| `permalink` | `null \| string` |  |
| `sku` | `null \| string` |  |
| `price` | `null \| string` |  |
| `regular_price` | `null \| string` |  |
| `sale_price` | `null \| string` |  |
| `date_on_sale_from` | `null \| string` |  |
| `date_on_sale_from_gmt` | `null \| string` |  |
| `date_on_sale_to` | `null \| string` |  |
| `date_on_sale_to_gmt` | `null \| string` |  |
| `on_sale` | `null \| boolean` |  |
| `status` | `null \| string` |  |
| `purchasable` | `null \| boolean` |  |
| `virtual` | `null \| boolean` |  |
| `downloadable` | `null \| boolean` |  |
| `downloads` | `null \| array` |  |
| `download_limit` | `null \| integer` |  |
| `download_expiry` | `null \| integer` |  |
| `tax_status` | `null \| string` |  |
| `tax_class` | `null \| string` |  |
| `manage_stock` | `null \| boolean` |  |
| `stock_quantity` | `null \| integer` |  |
| `stock_status` | `null \| string` |  |
| `backorders` | `null \| string` |  |
| `backorders_allowed` | `null \| boolean` |  |
| `backordered` | `null \| boolean` |  |
| `weight` | `null \| string` |  |
| `dimensions` | `null \| object` |  |
| `shipping_class` | `null \| string` |  |
| `shipping_class_id` | `null \| integer` |  |
| `image` | `null \| object` |  |
| `attributes` | `null \| array` |  |
| `menu_order` | `null \| integer` |  |
| `meta_data` | `null \| array` |  |
| `type` | `null \| string` |  |
| `global_unique_id` | `null \| string` |  |
| `low_stock_amount` | `null \| integer` |  |
| `name` | `null \| string` |  |
| `parent_id` | `null \| integer` |  |


</details>

### Product Variations Get

Retrieve a product variation

#### Python SDK

```python
await woocommerce.product_variations.get(
    product_id=0,
    id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "product_variations",
    "action": "get",
    "params": {
        "product_id": 0,
        "id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `product_id` | `integer` | Yes | Unique identifier for the parent product |
| `id` | `integer` | Yes | Unique identifier for the variation |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| integer` |  |
| `date_created` | `null \| string` |  |
| `date_created_gmt` | `null \| string` |  |
| `date_modified` | `null \| string` |  |
| `date_modified_gmt` | `null \| string` |  |
| `description` | `null \| string` |  |
| `permalink` | `null \| string` |  |
| `sku` | `null \| string` |  |
| `price` | `null \| string` |  |
| `regular_price` | `null \| string` |  |
| `sale_price` | `null \| string` |  |
| `date_on_sale_from` | `null \| string` |  |
| `date_on_sale_from_gmt` | `null \| string` |  |
| `date_on_sale_to` | `null \| string` |  |
| `date_on_sale_to_gmt` | `null \| string` |  |
| `on_sale` | `null \| boolean` |  |
| `status` | `null \| string` |  |
| `purchasable` | `null \| boolean` |  |
| `virtual` | `null \| boolean` |  |
| `downloadable` | `null \| boolean` |  |
| `downloads` | `null \| array` |  |
| `download_limit` | `null \| integer` |  |
| `download_expiry` | `null \| integer` |  |
| `tax_status` | `null \| string` |  |
| `tax_class` | `null \| string` |  |
| `manage_stock` | `null \| boolean` |  |
| `stock_quantity` | `null \| integer` |  |
| `stock_status` | `null \| string` |  |
| `backorders` | `null \| string` |  |
| `backorders_allowed` | `null \| boolean` |  |
| `backordered` | `null \| boolean` |  |
| `weight` | `null \| string` |  |
| `dimensions` | `null \| object` |  |
| `shipping_class` | `null \| string` |  |
| `shipping_class_id` | `null \| integer` |  |
| `image` | `null \| object` |  |
| `attributes` | `null \| array` |  |
| `menu_order` | `null \| integer` |  |
| `meta_data` | `null \| array` |  |
| `type` | `null \| string` |  |
| `global_unique_id` | `null \| string` |  |
| `low_stock_amount` | `null \| integer` |  |
| `name` | `null \| string` |  |
| `parent_id` | `null \| integer` |  |


</details>

### Product Variations Search

Search and filter product variations records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await woocommerce.product_variations.search(
    query={"filter": {"eq": {"attributes": []}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "product_variations",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"attributes": []}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, like, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `attributes` | `array` | List of attributes |
| `backordered` | `boolean` | On backordered |
| `backorders` | `string` | Backorders allowed setting |
| `backorders_allowed` | `boolean` | Shows if backorders are allowed |
| `date_created` | `string` | The date the variation was created |
| `date_created_gmt` | `string` | The date the variation was created, as GMT |
| `date_modified` | `string` | The date the variation was last modified |
| `date_modified_gmt` | `string` | The date the variation was last modified, as GMT |
| `date_on_sale_from` | `string` | Start date of sale price |
| `date_on_sale_from_gmt` | `string` | Start date of sale price, as GMT |
| `date_on_sale_to` | `string` | End date of sale price |
| `date_on_sale_to_gmt` | `string` | End date of sale price, as GMT |
| `description` | `string` | Variation description |
| `dimensions` | `object` | Variation dimensions |
| `download_expiry` | `integer` | Days until access expires |
| `download_limit` | `integer` | Download limit |
| `downloadable` | `boolean` | If downloadable |
| `downloads` | `array` | Downloadable files |
| `id` | `integer` | Unique identifier |
| `image` | `array` | Variation image data |
| `manage_stock` | `string` | Stock management at variation level |
| `menu_order` | `integer` | Menu order |
| `meta_data` | `array` | Meta data |
| `on_sale` | `boolean` | Shows if on sale |
| `permalink` | `string` | Variation URL |
| `price` | `string` | Current variation price |
| `purchasable` | `boolean` | Can be bought |
| `regular_price` | `string` | Variation regular price |
| `sale_price` | `string` | Variation sale price |
| `shipping_class` | `string` | Shipping class slug |
| `shipping_class_id` | `integer` | Shipping class ID |
| `sku` | `string` | Unique identifier (SKU) |
| `status` | `string` | Variation status |
| `stock_quantity` | `integer` | Stock quantity |
| `stock_status` | `string` | Controls the stock status |
| `tax_class` | `string` | Tax class |
| `tax_status` | `string` | Tax status |
| `virtual` | `boolean` | If virtual |
| `weight` | `string` | Variation weight |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].attributes` | `array` | List of attributes |
| `data[].backordered` | `boolean` | On backordered |
| `data[].backorders` | `string` | Backorders allowed setting |
| `data[].backorders_allowed` | `boolean` | Shows if backorders are allowed |
| `data[].date_created` | `string` | The date the variation was created |
| `data[].date_created_gmt` | `string` | The date the variation was created, as GMT |
| `data[].date_modified` | `string` | The date the variation was last modified |
| `data[].date_modified_gmt` | `string` | The date the variation was last modified, as GMT |
| `data[].date_on_sale_from` | `string` | Start date of sale price |
| `data[].date_on_sale_from_gmt` | `string` | Start date of sale price, as GMT |
| `data[].date_on_sale_to` | `string` | End date of sale price |
| `data[].date_on_sale_to_gmt` | `string` | End date of sale price, as GMT |
| `data[].description` | `string` | Variation description |
| `data[].dimensions` | `object` | Variation dimensions |
| `data[].download_expiry` | `integer` | Days until access expires |
| `data[].download_limit` | `integer` | Download limit |
| `data[].downloadable` | `boolean` | If downloadable |
| `data[].downloads` | `array` | Downloadable files |
| `data[].id` | `integer` | Unique identifier |
| `data[].image` | `array` | Variation image data |
| `data[].manage_stock` | `string` | Stock management at variation level |
| `data[].menu_order` | `integer` | Menu order |
| `data[].meta_data` | `array` | Meta data |
| `data[].on_sale` | `boolean` | Shows if on sale |
| `data[].permalink` | `string` | Variation URL |
| `data[].price` | `string` | Current variation price |
| `data[].purchasable` | `boolean` | Can be bought |
| `data[].regular_price` | `string` | Variation regular price |
| `data[].sale_price` | `string` | Variation sale price |
| `data[].shipping_class` | `string` | Shipping class slug |
| `data[].shipping_class_id` | `integer` | Shipping class ID |
| `data[].sku` | `string` | Unique identifier (SKU) |
| `data[].status` | `string` | Variation status |
| `data[].stock_quantity` | `integer` | Stock quantity |
| `data[].stock_status` | `string` | Controls the stock status |
| `data[].tax_class` | `string` | Tax class |
| `data[].tax_status` | `string` | Tax status |
| `data[].virtual` | `boolean` | If virtual |
| `data[].weight` | `string` | Variation weight |

</details>

## Order Notes

### Order Notes List

List order notes

#### Python SDK

```python
await woocommerce.order_notes.list(
    order_id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "order_notes",
    "action": "list",
    "params": {
        "order_id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `order_id` | `integer` | Yes | Unique identifier for the order |
| `type` | `"any" \| "customer" \| "internal"` | No | Limit result set to a specific note type |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| integer` |  |
| `author` | `null \| string` |  |
| `date_created` | `null \| string` |  |
| `date_created_gmt` | `null \| string` |  |
| `note` | `null \| string` |  |
| `customer_note` | `null \| boolean` |  |


</details>

### Order Notes Get

Retrieve an order note

#### Python SDK

```python
await woocommerce.order_notes.get(
    order_id=0,
    id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "order_notes",
    "action": "get",
    "params": {
        "order_id": 0,
        "id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `order_id` | `integer` | Yes | Unique identifier for the order |
| `id` | `integer` | Yes | Unique identifier for the note |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| integer` |  |
| `author` | `null \| string` |  |
| `date_created` | `null \| string` |  |
| `date_created_gmt` | `null \| string` |  |
| `note` | `null \| string` |  |
| `customer_note` | `null \| boolean` |  |


</details>

### Order Notes Search

Search and filter order notes records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await woocommerce.order_notes.search(
    query={"filter": {"eq": {"author": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "order_notes",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"author": "<str>"}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, like, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `author` | `string` | Order note author |
| `date_created` | `string` | The date the order note was created |
| `date_created_gmt` | `string` | The date the order note was created, as GMT |
| `id` | `integer` | Unique identifier |
| `note` | `string` | Order note content |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].author` | `string` | Order note author |
| `data[].date_created` | `string` | The date the order note was created |
| `data[].date_created_gmt` | `string` | The date the order note was created, as GMT |
| `data[].id` | `integer` | Unique identifier |
| `data[].note` | `string` | Order note content |

</details>

## Refunds

### Refunds List

List order refunds

#### Python SDK

```python
await woocommerce.refunds.list(
    order_id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "refunds",
    "action": "list",
    "params": {
        "order_id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `order_id` | `integer` | Yes | Unique identifier for the order |
| `page` | `integer` | No | Current page of the collection |
| `per_page` | `integer` | No | Maximum number of items to return per page |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| integer` |  |
| `date_created` | `null \| string` |  |
| `date_created_gmt` | `null \| string` |  |
| `amount` | `null \| string` |  |
| `reason` | `null \| string` |  |
| `refunded_by` | `null \| integer` |  |
| `refunded_payment` | `null \| boolean` |  |
| `meta_data` | `null \| array` |  |
| `line_items` | `null \| array` |  |
| `shipping_lines` | `null \| array` |  |
| `tax_lines` | `null \| array` |  |
| `fee_lines` | `null \| array` |  |


</details>

### Refunds Get

Retrieve a refund

#### Python SDK

```python
await woocommerce.refunds.get(
    order_id=0,
    id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "refunds",
    "action": "get",
    "params": {
        "order_id": 0,
        "id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `order_id` | `integer` | Yes | Unique identifier for the order |
| `id` | `integer` | Yes | Unique identifier for the refund |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| integer` |  |
| `date_created` | `null \| string` |  |
| `date_created_gmt` | `null \| string` |  |
| `amount` | `null \| string` |  |
| `reason` | `null \| string` |  |
| `refunded_by` | `null \| integer` |  |
| `refunded_payment` | `null \| boolean` |  |
| `meta_data` | `null \| array` |  |
| `line_items` | `null \| array` |  |
| `shipping_lines` | `null \| array` |  |
| `tax_lines` | `null \| array` |  |
| `fee_lines` | `null \| array` |  |


</details>

### Refunds Search

Search and filter refunds records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await woocommerce.refunds.search(
    query={"filter": {"eq": {"amount": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "refunds",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"amount": "<str>"}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, like, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `amount` | `string` | Refund amount |
| `date_created` | `string` | The date the refund was created |
| `date_created_gmt` | `string` | The date the refund was created, as GMT |
| `id` | `integer` | Unique identifier |
| `line_items` | `array` | Line items data |
| `meta_data` | `array` | Meta data |
| `reason` | `string` | Reason for refund |
| `refunded_by` | `integer` | User ID of user who created the refund |
| `refunded_payment` | `boolean` | If the payment was refunded via the API |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].amount` | `string` | Refund amount |
| `data[].date_created` | `string` | The date the refund was created |
| `data[].date_created_gmt` | `string` | The date the refund was created, as GMT |
| `data[].id` | `integer` | Unique identifier |
| `data[].line_items` | `array` | Line items data |
| `data[].meta_data` | `array` | Meta data |
| `data[].reason` | `string` | Reason for refund |
| `data[].refunded_by` | `integer` | User ID of user who created the refund |
| `data[].refunded_payment` | `boolean` | If the payment was refunded via the API |

</details>

## Payment Gateways

### Payment Gateways List

List payment gateways

#### Python SDK

```python
await woocommerce.payment_gateways.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "payment_gateways",
    "action": "list"
}'
```



<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| string` |  |
| `title` | `null \| string` |  |
| `description` | `null \| string` |  |
| `order` | `null \| integer` |  |
| `enabled` | `null \| boolean` |  |
| `method_title` | `null \| string` |  |
| `method_description` | `null \| string` |  |
| `method_supports` | `null \| array` |  |
| `settings` | `null \| object` |  |
| `needs_setup` | `null \| boolean` |  |
| `post_install_scripts` | `null \| array` |  |
| `settings_url` | `null \| string` |  |
| `connection_url` | `null \| string` |  |
| `setup_help_text` | `null \| string` |  |
| `required_settings_keys` | `null \| array` |  |


</details>

### Payment Gateways Get

Retrieve a payment gateway

#### Python SDK

```python
await woocommerce.payment_gateways.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "payment_gateways",
    "action": "get",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | Unique identifier for the payment gateway |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| string` |  |
| `title` | `null \| string` |  |
| `description` | `null \| string` |  |
| `order` | `null \| integer` |  |
| `enabled` | `null \| boolean` |  |
| `method_title` | `null \| string` |  |
| `method_description` | `null \| string` |  |
| `method_supports` | `null \| array` |  |
| `settings` | `null \| object` |  |
| `needs_setup` | `null \| boolean` |  |
| `post_install_scripts` | `null \| array` |  |
| `settings_url` | `null \| string` |  |
| `connection_url` | `null \| string` |  |
| `setup_help_text` | `null \| string` |  |
| `required_settings_keys` | `null \| array` |  |


</details>

### Payment Gateways Search

Search and filter payment gateways records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await woocommerce.payment_gateways.search(
    query={"filter": {"eq": {"description": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "payment_gateways",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"description": "<str>"}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, like, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `description` | `string` | Payment gateway description on checkout |
| `enabled` | `boolean` | Payment gateway enabled status |
| `id` | `string` | Payment gateway ID |
| `method_description` | `string` | Payment gateway method description |
| `method_supports` | `array` | Supported features |
| `method_title` | `string` | Payment gateway method title |
| `order` | `string | integer` | Payment gateway sort order |
| `settings` | `object` | Payment gateway settings |
| `title` | `string` | Payment gateway title on checkout |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].description` | `string` | Payment gateway description on checkout |
| `data[].enabled` | `boolean` | Payment gateway enabled status |
| `data[].id` | `string` | Payment gateway ID |
| `data[].method_description` | `string` | Payment gateway method description |
| `data[].method_supports` | `array` | Supported features |
| `data[].method_title` | `string` | Payment gateway method title |
| `data[].order` | `string | integer` | Payment gateway sort order |
| `data[].settings` | `object` | Payment gateway settings |
| `data[].title` | `string` | Payment gateway title on checkout |

</details>

## Shipping Methods

### Shipping Methods List

List shipping methods

#### Python SDK

```python
await woocommerce.shipping_methods.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "shipping_methods",
    "action": "list"
}'
```



<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| string` |  |
| `title` | `null \| string` |  |
| `description` | `null \| string` |  |


</details>

### Shipping Methods Get

Retrieve a shipping method

#### Python SDK

```python
await woocommerce.shipping_methods.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "shipping_methods",
    "action": "get",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | Unique identifier for the shipping method |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| string` |  |
| `title` | `null \| string` |  |
| `description` | `null \| string` |  |


</details>

### Shipping Methods Search

Search and filter shipping methods records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await woocommerce.shipping_methods.search(
    query={"filter": {"eq": {"description": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "shipping_methods",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"description": "<str>"}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, like, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `description` | `string` | Shipping method description |
| `id` | `string` | Method ID |
| `title` | `string` | Shipping method title |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].description` | `string` | Shipping method description |
| `data[].id` | `string` | Method ID |
| `data[].title` | `string` | Shipping method title |

</details>

## Shipping Zones

### Shipping Zones List

List shipping zones

#### Python SDK

```python
await woocommerce.shipping_zones.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "shipping_zones",
    "action": "list"
}'
```



<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| integer` |  |
| `name` | `null \| string` |  |
| `order` | `null \| integer` |  |


</details>

### Shipping Zones Get

Retrieve a shipping zone

#### Python SDK

```python
await woocommerce.shipping_zones.get(
    id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "shipping_zones",
    "action": "get",
    "params": {
        "id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `integer` | Yes | Unique identifier for the shipping zone |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| integer` |  |
| `name` | `null \| string` |  |
| `order` | `null \| integer` |  |


</details>

### Shipping Zones Search

Search and filter shipping zones records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await woocommerce.shipping_zones.search(
    query={"filter": {"eq": {"id": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "shipping_zones",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"id": 0}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, like, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` | Unique identifier |
| `name` | `string` | Shipping zone name |
| `order` | `integer` | Shipping zone order |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].id` | `integer` | Unique identifier |
| `data[].name` | `string` | Shipping zone name |
| `data[].order` | `integer` | Shipping zone order |

</details>

## Tax Rates

### Tax Rates List

List tax rates

#### Python SDK

```python
await woocommerce.tax_rates.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "tax_rates",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page` | `integer` | No | Current page of the collection |
| `per_page` | `integer` | No | Maximum number of items to return per page |
| `class` | `string` | No | Sort by tax class |
| `orderby` | `"id" \| "order" \| "priority"` | No | Sort collection by attribute |
| `order` | `"asc" \| "desc"` | No | Order sort attribute ascending or descending |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| integer` |  |
| `country` | `null \| string` |  |
| `state` | `null \| string` |  |
| `postcode` | `null \| string` |  |
| `city` | `null \| string` |  |
| `postcodes` | `null \| array` |  |
| `cities` | `null \| array` |  |
| `rate` | `null \| string` |  |
| `name` | `null \| string` |  |
| `priority` | `null \| integer` |  |
| `compound` | `null \| boolean` |  |
| `shipping` | `null \| boolean` |  |
| `order` | `null \| integer` |  |
| `class` | `null \| string` |  |


</details>

### Tax Rates Get

Retrieve a tax rate

#### Python SDK

```python
await woocommerce.tax_rates.get(
    id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "tax_rates",
    "action": "get",
    "params": {
        "id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `integer` | Yes | Unique identifier for the tax rate |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| integer` |  |
| `country` | `null \| string` |  |
| `state` | `null \| string` |  |
| `postcode` | `null \| string` |  |
| `city` | `null \| string` |  |
| `postcodes` | `null \| array` |  |
| `cities` | `null \| array` |  |
| `rate` | `null \| string` |  |
| `name` | `null \| string` |  |
| `priority` | `null \| integer` |  |
| `compound` | `null \| boolean` |  |
| `shipping` | `null \| boolean` |  |
| `order` | `null \| integer` |  |
| `class` | `null \| string` |  |


</details>

### Tax Rates Search

Search and filter tax rates records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await woocommerce.tax_rates.search(
    query={"filter": {"eq": {"cities": []}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "tax_rates",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"cities": []}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, like, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `cities` | `array` | City names |
| `city` | `string` | City name |
| `class` | `string` | Tax class |
| `compound` | `boolean` | Whether this is a compound rate |
| `country` | `string` | Country ISO 3166 code |
| `id` | `integer` | Unique identifier |
| `name` | `string` | Tax rate name |
| `order` | `integer` | Order in queries |
| `postcode` | `string` | Postcode/ZIP |
| `postcodes` | `array` | Postcodes/ZIPs |
| `priority` | `integer` | Tax priority |
| `rate` | `string` | Tax rate |
| `shipping` | `boolean` | Applied to shipping |
| `state` | `string` | State code |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].cities` | `array` | City names |
| `data[].city` | `string` | City name |
| `data[].class` | `string` | Tax class |
| `data[].compound` | `boolean` | Whether this is a compound rate |
| `data[].country` | `string` | Country ISO 3166 code |
| `data[].id` | `integer` | Unique identifier |
| `data[].name` | `string` | Tax rate name |
| `data[].order` | `integer` | Order in queries |
| `data[].postcode` | `string` | Postcode/ZIP |
| `data[].postcodes` | `array` | Postcodes/ZIPs |
| `data[].priority` | `integer` | Tax priority |
| `data[].rate` | `string` | Tax rate |
| `data[].shipping` | `boolean` | Applied to shipping |
| `data[].state` | `string` | State code |

</details>

## Tax Classes

### Tax Classes List

List tax classes

#### Python SDK

```python
await woocommerce.tax_classes.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "tax_classes",
    "action": "list"
}'
```



<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `slug` | `null \| string` |  |
| `name` | `null \| string` |  |


</details>

### Tax Classes Search

Search and filter tax classes records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await woocommerce.tax_classes.search(
    query={"filter": {"eq": {"name": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "tax_classes",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"name": "<str>"}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, like, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `name` | `string` | Tax class name |
| `slug` | `string` | Unique identifier |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].name` | `string` | Tax class name |
| `data[].slug` | `string` | Unique identifier |

</details>

