# Shopify full reference

This is the full reference documentation for the Shopify agent connector.

## Supported entities and actions

The Shopify connector supports the following entities and actions.

| Entity | Actions |
|--------|---------|
| Customers | [List](#customers-list), [Get](#customers-get), [Context Store Search](#customers-context-store-search) |
| Orders | [List](#orders-list), [Get](#orders-get) |
| Products | [List](#products-list), [Get](#products-get) |
| Product Variants | [List](#product-variants-list), [Get](#product-variants-get), [Context Store Search](#product-variants-context-store-search) |
| Product Images | [List](#product-images-list), [Get](#product-images-get), [Context Store Search](#product-images-context-store-search) |
| Abandoned Checkouts | [List](#abandoned-checkouts-list), [Context Store Search](#abandoned-checkouts-context-store-search) |
| Locations | [List](#locations-list), [Get](#locations-get), [Context Store Search](#locations-context-store-search) |
| Inventory Levels | [List](#inventory-levels-list), [Context Store Search](#inventory-levels-context-store-search) |
| Inventory Items | [List](#inventory-items-list), [Get](#inventory-items-get), [Context Store Search](#inventory-items-context-store-search) |
| Shop | [Get](#shop-get), [Context Store Search](#shop-context-store-search) |
| Price Rules | [List](#price-rules-list), [Get](#price-rules-get), [Context Store Search](#price-rules-context-store-search) |
| Discount Codes | [List](#discount-codes-list), [Get](#discount-codes-get), [Context Store Search](#discount-codes-context-store-search) |
| Custom Collections | [List](#custom-collections-list), [Get](#custom-collections-get), [Context Store Search](#custom-collections-context-store-search) |
| Smart Collections | [List](#smart-collections-list), [Get](#smart-collections-get), [Context Store Search](#smart-collections-context-store-search) |
| Collects | [List](#collects-list), [Get](#collects-get), [Context Store Search](#collects-context-store-search) |
| Draft Orders | [List](#draft-orders-list), [Get](#draft-orders-get), [Context Store Search](#draft-orders-context-store-search) |
| Fulfillments | [List](#fulfillments-list), [Get](#fulfillments-get), [Context Store Search](#fulfillments-context-store-search) |
| Order Refunds | [List](#order-refunds-list), [Get](#order-refunds-get), [Context Store Search](#order-refunds-context-store-search) |
| Transactions | [List](#transactions-list), [Get](#transactions-get) |
| Tender Transactions | [List](#tender-transactions-list), [Context Store Search](#tender-transactions-context-store-search) |
| Countries | [List](#countries-list), [Get](#countries-get), [Context Store Search](#countries-context-store-search) |
| Metafield Shops | [List](#metafield-shops-list), [Get](#metafield-shops-get), [Context Store Search](#metafield-shops-context-store-search) |
| Metafield Customers | [List](#metafield-customers-list), [Context Store Search](#metafield-customers-context-store-search) |
| Metafield Products | [List](#metafield-products-list), [Context Store Search](#metafield-products-context-store-search) |
| Metafield Orders | [List](#metafield-orders-list), [Context Store Search](#metafield-orders-context-store-search) |
| Metafield Draft Orders | [List](#metafield-draft-orders-list), [Context Store Search](#metafield-draft-orders-context-store-search) |
| Metafield Locations | [List](#metafield-locations-list), [Context Store Search](#metafield-locations-context-store-search) |
| Metafield Product Variants | [List](#metafield-product-variants-list), [Context Store Search](#metafield-product-variants-context-store-search) |
| Metafield Smart Collections | [List](#metafield-smart-collections-list), [Context Store Search](#metafield-smart-collections-context-store-search) |
| Metafield Product Images | [List](#metafield-product-images-list), [Context Store Search](#metafield-product-images-context-store-search) |
| Customer Address | [List](#customer-address-list), [Get](#customer-address-get) |
| Fulfillment Orders | [List](#fulfillment-orders-list), [Get](#fulfillment-orders-get), [Context Store Search](#fulfillment-orders-context-store-search) |

## Customers

### Customers List

Returns a list of customers from the store

#### Python SDK

```python
await shopify.customers.list()
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
| `limit` | `integer` | No | Maximum number of results to return (max 250) |
| `since_id` | `integer` | No | Restrict results to after the specified ID |
| `created_at_min` | `string` | No | Show customers created after date (ISO 8601 format) |
| `created_at_max` | `string` | No | Show customers created before date (ISO 8601 format) |
| `updated_at_min` | `string` | No | Show customers last updated after date (ISO 8601 format) |
| `updated_at_max` | `string` | No | Show customers last updated before date (ISO 8601 format) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `email` | `string \| null` |  |
| `accepts_marketing` | `boolean \| null` |  |
| `created_at` | `string \| null` |  |
| `updated_at` | `string \| null` |  |
| `first_name` | `string \| null` |  |
| `last_name` | `string \| null` |  |
| `orders_count` | `integer \| null` |  |
| `state` | `string \| null` |  |
| `total_spent` | `string \| null` |  |
| `last_order_id` | `integer \| null` |  |
| `note` | `string \| null` |  |
| `verified_email` | `boolean \| null` |  |
| `multipass_identifier` | `string \| null` |  |
| `tax_exempt` | `boolean \| null` |  |
| `tags` | `string \| null` |  |
| `last_order_name` | `string \| null` |  |
| `currency` | `string \| null` |  |
| `phone` | `string \| null` |  |
| `addresses` | `array \| null` |  |
| `addresses[].id` | `integer` |  |
| `addresses[].customer_id` | `integer \| null` |  |
| `addresses[].first_name` | `string \| null` |  |
| `addresses[].last_name` | `string \| null` |  |
| `addresses[].company` | `string \| null` |  |
| `addresses[].address1` | `string \| null` |  |
| `addresses[].address2` | `string \| null` |  |
| `addresses[].city` | `string \| null` |  |
| `addresses[].province` | `string \| null` |  |
| `addresses[].country` | `string \| null` |  |
| `addresses[].zip` | `string \| null` |  |
| `addresses[].phone` | `string \| null` |  |
| `addresses[].name` | `string \| null` |  |
| `addresses[].province_code` | `string \| null` |  |
| `addresses[].country_code` | `string \| null` |  |
| `addresses[].country_name` | `string \| null` |  |
| `addresses[].default` | `boolean \| null` |  |
| `accepts_marketing_updated_at` | `string \| null` |  |
| `marketing_opt_in_level` | `string \| null` |  |
| `tax_exemptions` | `array \| null` |  |
| `email_marketing_consent` | `object \| any` |  |
| `sms_marketing_consent` | `object \| any` |  |
| `admin_graphql_api_id` | `string \| null` |  |
| `default_address` | `object \| any` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page_url` | `string` |  |

</details>

### Customers Get

Retrieves a single customer by ID

#### Python SDK

```python
await shopify.customers.get(
    customer_id=0
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
        "customer_id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `customer_id` | `integer` | Yes | The customer ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `email` | `string \| null` |  |
| `accepts_marketing` | `boolean \| null` |  |
| `created_at` | `string \| null` |  |
| `updated_at` | `string \| null` |  |
| `first_name` | `string \| null` |  |
| `last_name` | `string \| null` |  |
| `orders_count` | `integer \| null` |  |
| `state` | `string \| null` |  |
| `total_spent` | `string \| null` |  |
| `last_order_id` | `integer \| null` |  |
| `note` | `string \| null` |  |
| `verified_email` | `boolean \| null` |  |
| `multipass_identifier` | `string \| null` |  |
| `tax_exempt` | `boolean \| null` |  |
| `tags` | `string \| null` |  |
| `last_order_name` | `string \| null` |  |
| `currency` | `string \| null` |  |
| `phone` | `string \| null` |  |
| `addresses` | `array \| null` |  |
| `addresses[].id` | `integer` |  |
| `addresses[].customer_id` | `integer \| null` |  |
| `addresses[].first_name` | `string \| null` |  |
| `addresses[].last_name` | `string \| null` |  |
| `addresses[].company` | `string \| null` |  |
| `addresses[].address1` | `string \| null` |  |
| `addresses[].address2` | `string \| null` |  |
| `addresses[].city` | `string \| null` |  |
| `addresses[].province` | `string \| null` |  |
| `addresses[].country` | `string \| null` |  |
| `addresses[].zip` | `string \| null` |  |
| `addresses[].phone` | `string \| null` |  |
| `addresses[].name` | `string \| null` |  |
| `addresses[].province_code` | `string \| null` |  |
| `addresses[].country_code` | `string \| null` |  |
| `addresses[].country_name` | `string \| null` |  |
| `addresses[].default` | `boolean \| null` |  |
| `accepts_marketing_updated_at` | `string \| null` |  |
| `marketing_opt_in_level` | `string \| null` |  |
| `tax_exemptions` | `array \| null` |  |
| `email_marketing_consent` | `object \| any` |  |
| `sms_marketing_consent` | `object \| any` |  |
| `admin_graphql_api_id` | `string \| null` |  |
| `default_address` | `object \| any` |  |


</details>

### Customers Context Store Search

Search and filter customers records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await shopify.customers.context_store_search(
    query={"filter": {"eq": {"id": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "customers",
    "action": "context_store_search",
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
| `id` | `integer` | Unique identifier for the customer |
| `email` | `string` | Primary email address of the customer |
| `phone` | `string` | Primary phone number of the customer |
| `first_name` | `string` | First name of the customer |
| `last_name` | `string` | Last name of the customer |
| `state` | `string` | Account state (`disabled`, `invited`, `enabled`, `declined`) |
| `orders_count` | `integer` | Number of orders placed by the customer |
| `total_spent` | `string` | Total lifetime amount spent by the customer |
| `currency` | `string` | ISO 4217 currency code for the customer's total spend |
| `created_at` | `string` | ISO 8601 timestamp when the customer record was created |
| `updated_at` | `string` | ISO 8601 timestamp when the customer record was last updated |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].id` | `integer` | Unique identifier for the customer |
| `data[].email` | `string` | Primary email address of the customer |
| `data[].phone` | `string` | Primary phone number of the customer |
| `data[].first_name` | `string` | First name of the customer |
| `data[].last_name` | `string` | Last name of the customer |
| `data[].state` | `string` | Account state (`disabled`, `invited`, `enabled`, `declined`) |
| `data[].orders_count` | `integer` | Number of orders placed by the customer |
| `data[].total_spent` | `string` | Total lifetime amount spent by the customer |
| `data[].currency` | `string` | ISO 4217 currency code for the customer's total spend |
| `data[].created_at` | `string` | ISO 8601 timestamp when the customer record was created |
| `data[].updated_at` | `string` | ISO 8601 timestamp when the customer record was last updated |

</details>

## Orders

### Orders List

Returns a list of orders from the store

#### Python SDK

```python
await shopify.orders.list()
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
| `limit` | `integer` | No | Maximum number of results to return (max 250) |
| `since_id` | `integer` | No | Restrict results to after the specified ID |
| `created_at_min` | `string` | No | Show orders created after date (ISO 8601 format) |
| `created_at_max` | `string` | No | Show orders created before date (ISO 8601 format) |
| `updated_at_min` | `string` | No | Show orders last updated after date (ISO 8601 format) |
| `updated_at_max` | `string` | No | Show orders last updated before date (ISO 8601 format) |
| `status` | `"open" \| "closed" \| "cancelled" \| "any"` | No | Filter orders by status |
| `financial_status` | `"authorized" \| "pending" \| "paid" \| "partially_paid" \| "refunded" \| "voided" \| "partially_refunded" \| "any" \| "unpaid"` | No | Filter orders by financial status |
| `fulfillment_status` | `"shipped" \| "partial" \| "unshipped" \| "any" \| "unfulfilled"` | No | Filter orders by fulfillment status |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `admin_graphql_api_id` | `string \| null` |  |
| `app_id` | `integer \| null` |  |
| `browser_ip` | `string \| null` |  |
| `buyer_accepts_marketing` | `boolean \| null` |  |
| `cancel_reason` | `string \| null` |  |
| `cancelled_at` | `string \| null` |  |
| `cart_token` | `string \| null` |  |
| `checkout_id` | `integer \| null` |  |
| `checkout_token` | `string \| null` |  |
| `client_details` | `object \| null` |  |
| `closed_at` | `string \| null` |  |
| `company` | `object \| null` |  |
| `confirmation_number` | `string \| null` |  |
| `confirmed` | `boolean \| null` |  |
| `contact_email` | `string \| null` |  |
| `created_at` | `string \| null` |  |
| `currency` | `string \| null` |  |
| `current_subtotal_price` | `string \| null` |  |
| `current_subtotal_price_set` | `object \| null` |  |
| `current_total_additional_fees_set` | `object \| null` |  |
| `current_total_discounts` | `string \| null` |  |
| `current_total_discounts_set` | `object \| null` |  |
| `current_total_duties_set` | `object \| null` |  |
| `current_total_price` | `string \| null` |  |
| `current_total_price_set` | `object \| null` |  |
| `current_total_tax` | `string \| null` |  |
| `current_total_tax_set` | `object \| null` |  |
| `customer` | `object \| any` |  |
| `customer_locale` | `string \| null` |  |
| `device_id` | `integer \| null` |  |
| `discount_applications` | `array \| null` |  |
| `discount_codes` | `array \| null` |  |
| `email` | `string \| null` |  |
| `estimated_taxes` | `boolean \| null` |  |
| `financial_status` | `string \| null` |  |
| `fulfillment_status` | `string \| null` |  |
| `fulfillments` | `array \| null` |  |
| `fulfillments[].id` | `integer` |  |
| `fulfillments[].order_id` | `integer \| null` |  |
| `fulfillments[].status` | `string \| null` |  |
| `fulfillments[].created_at` | `string \| null` |  |
| `fulfillments[].service` | `string \| null` |  |
| `fulfillments[].updated_at` | `string \| null` |  |
| `fulfillments[].tracking_company` | `string \| null` |  |
| `fulfillments[].shipment_status` | `string \| null` |  |
| `fulfillments[].location_id` | `integer \| null` |  |
| `fulfillments[].origin_address` | `object \| null` |  |
| `fulfillments[].line_items` | `array \| null` |  |
| `fulfillments[].line_items[].id` | `integer` |  |
| `fulfillments[].line_items[].admin_graphql_api_id` | `string \| null` |  |
| `fulfillments[].line_items[].attributed_staffs` | `array \| null` |  |
| `fulfillments[].line_items[].current_quantity` | `integer \| null` |  |
| `fulfillments[].line_items[].fulfillable_quantity` | `integer \| null` |  |
| `fulfillments[].line_items[].fulfillment_service` | `string \| null` |  |
| `fulfillments[].line_items[].fulfillment_status` | `string \| null` |  |
| `fulfillments[].line_items[].gift_card` | `boolean \| null` |  |
| `fulfillments[].line_items[].grams` | `integer \| null` |  |
| `fulfillments[].line_items[].name` | `string \| null` |  |
| `fulfillments[].line_items[].price` | `string \| null` |  |
| `fulfillments[].line_items[].price_set` | `object \| null` |  |
| `fulfillments[].line_items[].product_exists` | `boolean \| null` |  |
| `fulfillments[].line_items[].product_id` | `integer \| null` |  |
| `fulfillments[].line_items[].properties` | `array \| null` |  |
| `fulfillments[].line_items[].quantity` | `integer \| null` |  |
| `fulfillments[].line_items[].requires_shipping` | `boolean \| null` |  |
| `fulfillments[].line_items[].sku` | `string \| null` |  |
| `fulfillments[].line_items[].taxable` | `boolean \| null` |  |
| `fulfillments[].line_items[].title` | `string \| null` |  |
| `fulfillments[].line_items[].total_discount` | `string \| null` |  |
| `fulfillments[].line_items[].total_discount_set` | `object \| null` |  |
| `fulfillments[].line_items[].variant_id` | `integer \| null` |  |
| `fulfillments[].line_items[].variant_inventory_management` | `string \| null` |  |
| `fulfillments[].line_items[].variant_title` | `string \| null` |  |
| `fulfillments[].line_items[].vendor` | `string \| null` |  |
| `fulfillments[].line_items[].tax_lines` | `array \| null` |  |
| `fulfillments[].line_items[].duties` | `array \| null` |  |
| `fulfillments[].line_items[].discount_allocations` | `array \| null` |  |
| `fulfillments[].tracking_number` | `string \| null` |  |
| `fulfillments[].tracking_numbers` | `array \| null` |  |
| `fulfillments[].tracking_url` | `string \| null` |  |
| `fulfillments[].tracking_urls` | `array \| null` |  |
| `fulfillments[].receipt` | `object \| null` |  |
| `fulfillments[].name` | `string \| null` |  |
| `fulfillments[].admin_graphql_api_id` | `string \| null` |  |
| `gateway` | `string \| null` |  |
| `landing_site` | `string \| null` |  |
| `landing_site_ref` | `string \| null` |  |
| `line_items` | `array \| null` |  |
| `line_items[].id` | `integer` |  |
| `line_items[].admin_graphql_api_id` | `string \| null` |  |
| `line_items[].attributed_staffs` | `array \| null` |  |
| `line_items[].current_quantity` | `integer \| null` |  |
| `line_items[].fulfillable_quantity` | `integer \| null` |  |
| `line_items[].fulfillment_service` | `string \| null` |  |
| `line_items[].fulfillment_status` | `string \| null` |  |
| `line_items[].gift_card` | `boolean \| null` |  |
| `line_items[].grams` | `integer \| null` |  |
| `line_items[].name` | `string \| null` |  |
| `line_items[].price` | `string \| null` |  |
| `line_items[].price_set` | `object \| null` |  |
| `line_items[].product_exists` | `boolean \| null` |  |
| `line_items[].product_id` | `integer \| null` |  |
| `line_items[].properties` | `array \| null` |  |
| `line_items[].quantity` | `integer \| null` |  |
| `line_items[].requires_shipping` | `boolean \| null` |  |
| `line_items[].sku` | `string \| null` |  |
| `line_items[].taxable` | `boolean \| null` |  |
| `line_items[].title` | `string \| null` |  |
| `line_items[].total_discount` | `string \| null` |  |
| `line_items[].total_discount_set` | `object \| null` |  |
| `line_items[].variant_id` | `integer \| null` |  |
| `line_items[].variant_inventory_management` | `string \| null` |  |
| `line_items[].variant_title` | `string \| null` |  |
| `line_items[].vendor` | `string \| null` |  |
| `line_items[].tax_lines` | `array \| null` |  |
| `line_items[].duties` | `array \| null` |  |
| `line_items[].discount_allocations` | `array \| null` |  |
| `location_id` | `integer \| null` |  |
| `merchant_of_record_app_id` | `integer \| null` |  |
| `merchant_business_entity_id` | `string \| null` |  |
| `duties_included` | `boolean \| null` |  |
| `total_cash_rounding_payment_adjustment_set` | `object \| null` |  |
| `total_cash_rounding_refund_adjustment_set` | `object \| null` |  |
| `payment_terms` | `object \| null` |  |
| `name` | `string \| null` |  |
| `note` | `string \| null` |  |
| `note_attributes` | `array \| null` |  |
| `number` | `integer \| null` |  |
| `order_number` | `integer \| null` |  |
| `order_status_url` | `string \| null` |  |
| `original_total_additional_fees_set` | `object \| null` |  |
| `original_total_duties_set` | `object \| null` |  |
| `payment_gateway_names` | `array \| null` |  |
| `phone` | `string \| null` |  |
| `po_number` | `string \| null` |  |
| `presentment_currency` | `string \| null` |  |
| `processed_at` | `string \| null` |  |
| `reference` | `string \| null` |  |
| `referring_site` | `string \| null` |  |
| `refunds` | `array \| null` |  |
| `refunds[].id` | `integer` |  |
| `refunds[].order_id` | `integer \| null` |  |
| `refunds[].created_at` | `string \| null` |  |
| `refunds[].note` | `string \| null` |  |
| `refunds[].user_id` | `integer \| null` |  |
| `refunds[].processed_at` | `string \| null` |  |
| `refunds[].restock` | `boolean \| null` |  |
| `refunds[].duties` | `array \| null` |  |
| `refunds[].total_duties_set` | `object \| null` |  |
| `refunds[].return` | `object \| null` |  |
| `refunds[].refund_line_items` | `array \| null` |  |
| `refunds[].transactions` | `array \| null` |  |
| `refunds[].transactions[].id` | `integer` |  |
| `refunds[].transactions[].order_id` | `integer \| null` |  |
| `refunds[].transactions[].kind` | `string \| null` |  |
| `refunds[].transactions[].gateway` | `string \| null` |  |
| `refunds[].transactions[].status` | `string \| null` |  |
| `refunds[].transactions[].message` | `string \| null` |  |
| `refunds[].transactions[].created_at` | `string \| null` |  |
| `refunds[].transactions[].test` | `boolean \| null` |  |
| `refunds[].transactions[].authorization` | `string \| null` |  |
| `refunds[].transactions[].location_id` | `integer \| null` |  |
| `refunds[].transactions[].user_id` | `integer \| null` |  |
| `refunds[].transactions[].parent_id` | `integer \| null` |  |
| `refunds[].transactions[].processed_at` | `string \| null` |  |
| `refunds[].transactions[].device_id` | `integer \| null` |  |
| `refunds[].transactions[].error_code` | `string \| null` |  |
| `refunds[].transactions[].source_name` | `string \| null` |  |
| `refunds[].transactions[].receipt` | `object \| null` |  |
| `refunds[].transactions[].currency_exchange_adjustment` | `object \| null` |  |
| `refunds[].transactions[].amount` | `string \| null` |  |
| `refunds[].transactions[].currency` | `string \| null` |  |
| `refunds[].transactions[].payment_id` | `string \| null` |  |
| `refunds[].transactions[].total_unsettled_set` | `object \| null` |  |
| `refunds[].transactions[].manual_payment_gateway` | `boolean \| null` |  |
| `refunds[].transactions[].admin_graphql_api_id` | `string \| null` |  |
| `refunds[].order_adjustments` | `array \| null` |  |
| `refunds[].admin_graphql_api_id` | `string \| null` |  |
| `refunds[].refund_shipping_lines` | `array \| null` |  |
| `shipping_address` | `object \| any` |  |
| `shipping_lines` | `array \| null` |  |
| `source_identifier` | `string \| null` |  |
| `source_name` | `string \| null` |  |
| `source_url` | `string \| null` |  |
| `subtotal_price` | `string \| null` |  |
| `subtotal_price_set` | `object \| null` |  |
| `tags` | `string \| null` |  |
| `tax_exempt` | `boolean \| null` |  |
| `tax_lines` | `array \| null` |  |
| `taxes_included` | `boolean \| null` |  |
| `test` | `boolean \| null` |  |
| `token` | `string \| null` |  |
| `total_discounts` | `string \| null` |  |
| `total_discounts_set` | `object \| null` |  |
| `total_line_items_price` | `string \| null` |  |
| `total_line_items_price_set` | `object \| null` |  |
| `total_outstanding` | `string \| null` |  |
| `total_price` | `string \| null` |  |
| `total_price_set` | `object \| null` |  |
| `total_shipping_price_set` | `object \| null` |  |
| `total_tax` | `string \| null` |  |
| `total_tax_set` | `object \| null` |  |
| `total_tip_received` | `string \| null` |  |
| `total_weight` | `integer \| null` |  |
| `updated_at` | `string \| null` |  |
| `user_id` | `integer \| null` |  |
| `billing_address` | `object \| any` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page_url` | `string` |  |

</details>

### Orders Get

Retrieves a single order by ID

#### Python SDK

```python
await shopify.orders.get(
    order_id=0
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
        "order_id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `order_id` | `integer` | Yes | The order ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `admin_graphql_api_id` | `string \| null` |  |
| `app_id` | `integer \| null` |  |
| `browser_ip` | `string \| null` |  |
| `buyer_accepts_marketing` | `boolean \| null` |  |
| `cancel_reason` | `string \| null` |  |
| `cancelled_at` | `string \| null` |  |
| `cart_token` | `string \| null` |  |
| `checkout_id` | `integer \| null` |  |
| `checkout_token` | `string \| null` |  |
| `client_details` | `object \| null` |  |
| `closed_at` | `string \| null` |  |
| `company` | `object \| null` |  |
| `confirmation_number` | `string \| null` |  |
| `confirmed` | `boolean \| null` |  |
| `contact_email` | `string \| null` |  |
| `created_at` | `string \| null` |  |
| `currency` | `string \| null` |  |
| `current_subtotal_price` | `string \| null` |  |
| `current_subtotal_price_set` | `object \| null` |  |
| `current_total_additional_fees_set` | `object \| null` |  |
| `current_total_discounts` | `string \| null` |  |
| `current_total_discounts_set` | `object \| null` |  |
| `current_total_duties_set` | `object \| null` |  |
| `current_total_price` | `string \| null` |  |
| `current_total_price_set` | `object \| null` |  |
| `current_total_tax` | `string \| null` |  |
| `current_total_tax_set` | `object \| null` |  |
| `customer` | `object \| any` |  |
| `customer_locale` | `string \| null` |  |
| `device_id` | `integer \| null` |  |
| `discount_applications` | `array \| null` |  |
| `discount_codes` | `array \| null` |  |
| `email` | `string \| null` |  |
| `estimated_taxes` | `boolean \| null` |  |
| `financial_status` | `string \| null` |  |
| `fulfillment_status` | `string \| null` |  |
| `fulfillments` | `array \| null` |  |
| `fulfillments[].id` | `integer` |  |
| `fulfillments[].order_id` | `integer \| null` |  |
| `fulfillments[].status` | `string \| null` |  |
| `fulfillments[].created_at` | `string \| null` |  |
| `fulfillments[].service` | `string \| null` |  |
| `fulfillments[].updated_at` | `string \| null` |  |
| `fulfillments[].tracking_company` | `string \| null` |  |
| `fulfillments[].shipment_status` | `string \| null` |  |
| `fulfillments[].location_id` | `integer \| null` |  |
| `fulfillments[].origin_address` | `object \| null` |  |
| `fulfillments[].line_items` | `array \| null` |  |
| `fulfillments[].line_items[].id` | `integer` |  |
| `fulfillments[].line_items[].admin_graphql_api_id` | `string \| null` |  |
| `fulfillments[].line_items[].attributed_staffs` | `array \| null` |  |
| `fulfillments[].line_items[].current_quantity` | `integer \| null` |  |
| `fulfillments[].line_items[].fulfillable_quantity` | `integer \| null` |  |
| `fulfillments[].line_items[].fulfillment_service` | `string \| null` |  |
| `fulfillments[].line_items[].fulfillment_status` | `string \| null` |  |
| `fulfillments[].line_items[].gift_card` | `boolean \| null` |  |
| `fulfillments[].line_items[].grams` | `integer \| null` |  |
| `fulfillments[].line_items[].name` | `string \| null` |  |
| `fulfillments[].line_items[].price` | `string \| null` |  |
| `fulfillments[].line_items[].price_set` | `object \| null` |  |
| `fulfillments[].line_items[].product_exists` | `boolean \| null` |  |
| `fulfillments[].line_items[].product_id` | `integer \| null` |  |
| `fulfillments[].line_items[].properties` | `array \| null` |  |
| `fulfillments[].line_items[].quantity` | `integer \| null` |  |
| `fulfillments[].line_items[].requires_shipping` | `boolean \| null` |  |
| `fulfillments[].line_items[].sku` | `string \| null` |  |
| `fulfillments[].line_items[].taxable` | `boolean \| null` |  |
| `fulfillments[].line_items[].title` | `string \| null` |  |
| `fulfillments[].line_items[].total_discount` | `string \| null` |  |
| `fulfillments[].line_items[].total_discount_set` | `object \| null` |  |
| `fulfillments[].line_items[].variant_id` | `integer \| null` |  |
| `fulfillments[].line_items[].variant_inventory_management` | `string \| null` |  |
| `fulfillments[].line_items[].variant_title` | `string \| null` |  |
| `fulfillments[].line_items[].vendor` | `string \| null` |  |
| `fulfillments[].line_items[].tax_lines` | `array \| null` |  |
| `fulfillments[].line_items[].duties` | `array \| null` |  |
| `fulfillments[].line_items[].discount_allocations` | `array \| null` |  |
| `fulfillments[].tracking_number` | `string \| null` |  |
| `fulfillments[].tracking_numbers` | `array \| null` |  |
| `fulfillments[].tracking_url` | `string \| null` |  |
| `fulfillments[].tracking_urls` | `array \| null` |  |
| `fulfillments[].receipt` | `object \| null` |  |
| `fulfillments[].name` | `string \| null` |  |
| `fulfillments[].admin_graphql_api_id` | `string \| null` |  |
| `gateway` | `string \| null` |  |
| `landing_site` | `string \| null` |  |
| `landing_site_ref` | `string \| null` |  |
| `line_items` | `array \| null` |  |
| `line_items[].id` | `integer` |  |
| `line_items[].admin_graphql_api_id` | `string \| null` |  |
| `line_items[].attributed_staffs` | `array \| null` |  |
| `line_items[].current_quantity` | `integer \| null` |  |
| `line_items[].fulfillable_quantity` | `integer \| null` |  |
| `line_items[].fulfillment_service` | `string \| null` |  |
| `line_items[].fulfillment_status` | `string \| null` |  |
| `line_items[].gift_card` | `boolean \| null` |  |
| `line_items[].grams` | `integer \| null` |  |
| `line_items[].name` | `string \| null` |  |
| `line_items[].price` | `string \| null` |  |
| `line_items[].price_set` | `object \| null` |  |
| `line_items[].product_exists` | `boolean \| null` |  |
| `line_items[].product_id` | `integer \| null` |  |
| `line_items[].properties` | `array \| null` |  |
| `line_items[].quantity` | `integer \| null` |  |
| `line_items[].requires_shipping` | `boolean \| null` |  |
| `line_items[].sku` | `string \| null` |  |
| `line_items[].taxable` | `boolean \| null` |  |
| `line_items[].title` | `string \| null` |  |
| `line_items[].total_discount` | `string \| null` |  |
| `line_items[].total_discount_set` | `object \| null` |  |
| `line_items[].variant_id` | `integer \| null` |  |
| `line_items[].variant_inventory_management` | `string \| null` |  |
| `line_items[].variant_title` | `string \| null` |  |
| `line_items[].vendor` | `string \| null` |  |
| `line_items[].tax_lines` | `array \| null` |  |
| `line_items[].duties` | `array \| null` |  |
| `line_items[].discount_allocations` | `array \| null` |  |
| `location_id` | `integer \| null` |  |
| `merchant_of_record_app_id` | `integer \| null` |  |
| `merchant_business_entity_id` | `string \| null` |  |
| `duties_included` | `boolean \| null` |  |
| `total_cash_rounding_payment_adjustment_set` | `object \| null` |  |
| `total_cash_rounding_refund_adjustment_set` | `object \| null` |  |
| `payment_terms` | `object \| null` |  |
| `name` | `string \| null` |  |
| `note` | `string \| null` |  |
| `note_attributes` | `array \| null` |  |
| `number` | `integer \| null` |  |
| `order_number` | `integer \| null` |  |
| `order_status_url` | `string \| null` |  |
| `original_total_additional_fees_set` | `object \| null` |  |
| `original_total_duties_set` | `object \| null` |  |
| `payment_gateway_names` | `array \| null` |  |
| `phone` | `string \| null` |  |
| `po_number` | `string \| null` |  |
| `presentment_currency` | `string \| null` |  |
| `processed_at` | `string \| null` |  |
| `reference` | `string \| null` |  |
| `referring_site` | `string \| null` |  |
| `refunds` | `array \| null` |  |
| `refunds[].id` | `integer` |  |
| `refunds[].order_id` | `integer \| null` |  |
| `refunds[].created_at` | `string \| null` |  |
| `refunds[].note` | `string \| null` |  |
| `refunds[].user_id` | `integer \| null` |  |
| `refunds[].processed_at` | `string \| null` |  |
| `refunds[].restock` | `boolean \| null` |  |
| `refunds[].duties` | `array \| null` |  |
| `refunds[].total_duties_set` | `object \| null` |  |
| `refunds[].return` | `object \| null` |  |
| `refunds[].refund_line_items` | `array \| null` |  |
| `refunds[].transactions` | `array \| null` |  |
| `refunds[].transactions[].id` | `integer` |  |
| `refunds[].transactions[].order_id` | `integer \| null` |  |
| `refunds[].transactions[].kind` | `string \| null` |  |
| `refunds[].transactions[].gateway` | `string \| null` |  |
| `refunds[].transactions[].status` | `string \| null` |  |
| `refunds[].transactions[].message` | `string \| null` |  |
| `refunds[].transactions[].created_at` | `string \| null` |  |
| `refunds[].transactions[].test` | `boolean \| null` |  |
| `refunds[].transactions[].authorization` | `string \| null` |  |
| `refunds[].transactions[].location_id` | `integer \| null` |  |
| `refunds[].transactions[].user_id` | `integer \| null` |  |
| `refunds[].transactions[].parent_id` | `integer \| null` |  |
| `refunds[].transactions[].processed_at` | `string \| null` |  |
| `refunds[].transactions[].device_id` | `integer \| null` |  |
| `refunds[].transactions[].error_code` | `string \| null` |  |
| `refunds[].transactions[].source_name` | `string \| null` |  |
| `refunds[].transactions[].receipt` | `object \| null` |  |
| `refunds[].transactions[].currency_exchange_adjustment` | `object \| null` |  |
| `refunds[].transactions[].amount` | `string \| null` |  |
| `refunds[].transactions[].currency` | `string \| null` |  |
| `refunds[].transactions[].payment_id` | `string \| null` |  |
| `refunds[].transactions[].total_unsettled_set` | `object \| null` |  |
| `refunds[].transactions[].manual_payment_gateway` | `boolean \| null` |  |
| `refunds[].transactions[].admin_graphql_api_id` | `string \| null` |  |
| `refunds[].order_adjustments` | `array \| null` |  |
| `refunds[].admin_graphql_api_id` | `string \| null` |  |
| `refunds[].refund_shipping_lines` | `array \| null` |  |
| `shipping_address` | `object \| any` |  |
| `shipping_lines` | `array \| null` |  |
| `source_identifier` | `string \| null` |  |
| `source_name` | `string \| null` |  |
| `source_url` | `string \| null` |  |
| `subtotal_price` | `string \| null` |  |
| `subtotal_price_set` | `object \| null` |  |
| `tags` | `string \| null` |  |
| `tax_exempt` | `boolean \| null` |  |
| `tax_lines` | `array \| null` |  |
| `taxes_included` | `boolean \| null` |  |
| `test` | `boolean \| null` |  |
| `token` | `string \| null` |  |
| `total_discounts` | `string \| null` |  |
| `total_discounts_set` | `object \| null` |  |
| `total_line_items_price` | `string \| null` |  |
| `total_line_items_price_set` | `object \| null` |  |
| `total_outstanding` | `string \| null` |  |
| `total_price` | `string \| null` |  |
| `total_price_set` | `object \| null` |  |
| `total_shipping_price_set` | `object \| null` |  |
| `total_tax` | `string \| null` |  |
| `total_tax_set` | `object \| null` |  |
| `total_tip_received` | `string \| null` |  |
| `total_weight` | `integer \| null` |  |
| `updated_at` | `string \| null` |  |
| `user_id` | `integer \| null` |  |
| `billing_address` | `object \| any` |  |


</details>

## Products

### Products List

Returns a list of products from the store

#### Python SDK

```python
await shopify.products.list()
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
| `limit` | `integer` | No | Maximum number of results to return (max 250) |
| `since_id` | `integer` | No | Restrict results to after the specified ID |
| `created_at_min` | `string` | No | Show products created after date (ISO 8601 format) |
| `created_at_max` | `string` | No | Show products created before date (ISO 8601 format) |
| `updated_at_min` | `string` | No | Show products last updated after date (ISO 8601 format) |
| `updated_at_max` | `string` | No | Show products last updated before date (ISO 8601 format) |
| `status` | `"active" \| "archived" \| "draft"` | No | Filter products by status |
| `product_type` | `string` | No | Filter by product type |
| `vendor` | `string` | No | Filter by vendor |
| `collection_id` | `integer` | No | Filter by collection ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `title` | `string \| null` |  |
| `body_html` | `string \| null` |  |
| `vendor` | `string \| null` |  |
| `product_type` | `string \| null` |  |
| `created_at` | `string \| null` |  |
| `handle` | `string \| null` |  |
| `updated_at` | `string \| null` |  |
| `published_at` | `string \| null` |  |
| `template_suffix` | `string \| null` |  |
| `published_scope` | `string \| null` |  |
| `tags` | `string \| null` |  |
| `status` | `string \| null` |  |
| `admin_graphql_api_id` | `string \| null` |  |
| `variants` | `array \| null` |  |
| `variants[].id` | `integer` |  |
| `variants[].product_id` | `integer \| null` |  |
| `variants[].title` | `string \| null` |  |
| `variants[].price` | `string \| null` |  |
| `variants[].sku` | `string \| null` |  |
| `variants[].position` | `integer \| null` |  |
| `variants[].inventory_policy` | `string \| null` |  |
| `variants[].compare_at_price` | `string \| null` |  |
| `variants[].fulfillment_service` | `string \| null` |  |
| `variants[].inventory_management` | `string \| null` |  |
| `variants[].option1` | `string \| null` |  |
| `variants[].option2` | `string \| null` |  |
| `variants[].option3` | `string \| null` |  |
| `variants[].created_at` | `string \| null` |  |
| `variants[].updated_at` | `string \| null` |  |
| `variants[].taxable` | `boolean \| null` |  |
| `variants[].barcode` | `string \| null` |  |
| `variants[].grams` | `integer \| null` |  |
| `variants[].image_id` | `integer \| null` |  |
| `variants[].weight` | `number \| null` |  |
| `variants[].weight_unit` | `string \| null` |  |
| `variants[].inventory_item_id` | `integer \| null` |  |
| `variants[].inventory_quantity` | `integer \| null` |  |
| `variants[].old_inventory_quantity` | `integer \| null` |  |
| `variants[].requires_shipping` | `boolean \| null` |  |
| `variants[].admin_graphql_api_id` | `string \| null` |  |
| `options` | `array \| null` |  |
| `images` | `array \| null` |  |
| `images[].id` | `integer` |  |
| `images[].product_id` | `integer \| null` |  |
| `images[].position` | `integer \| null` |  |
| `images[].created_at` | `string \| null` |  |
| `images[].updated_at` | `string \| null` |  |
| `images[].alt` | `string \| null` |  |
| `images[].width` | `integer \| null` |  |
| `images[].height` | `integer \| null` |  |
| `images[].src` | `string \| null` |  |
| `images[].variant_ids` | `array \| null` |  |
| `images[].admin_graphql_api_id` | `string \| null` |  |
| `image` | `object \| any` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page_url` | `string` |  |

</details>

### Products Get

Retrieves a single product by ID

#### Python SDK

```python
await shopify.products.get(
    product_id=0
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
        "product_id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `product_id` | `integer` | Yes | The product ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `title` | `string \| null` |  |
| `body_html` | `string \| null` |  |
| `vendor` | `string \| null` |  |
| `product_type` | `string \| null` |  |
| `created_at` | `string \| null` |  |
| `handle` | `string \| null` |  |
| `updated_at` | `string \| null` |  |
| `published_at` | `string \| null` |  |
| `template_suffix` | `string \| null` |  |
| `published_scope` | `string \| null` |  |
| `tags` | `string \| null` |  |
| `status` | `string \| null` |  |
| `admin_graphql_api_id` | `string \| null` |  |
| `variants` | `array \| null` |  |
| `variants[].id` | `integer` |  |
| `variants[].product_id` | `integer \| null` |  |
| `variants[].title` | `string \| null` |  |
| `variants[].price` | `string \| null` |  |
| `variants[].sku` | `string \| null` |  |
| `variants[].position` | `integer \| null` |  |
| `variants[].inventory_policy` | `string \| null` |  |
| `variants[].compare_at_price` | `string \| null` |  |
| `variants[].fulfillment_service` | `string \| null` |  |
| `variants[].inventory_management` | `string \| null` |  |
| `variants[].option1` | `string \| null` |  |
| `variants[].option2` | `string \| null` |  |
| `variants[].option3` | `string \| null` |  |
| `variants[].created_at` | `string \| null` |  |
| `variants[].updated_at` | `string \| null` |  |
| `variants[].taxable` | `boolean \| null` |  |
| `variants[].barcode` | `string \| null` |  |
| `variants[].grams` | `integer \| null` |  |
| `variants[].image_id` | `integer \| null` |  |
| `variants[].weight` | `number \| null` |  |
| `variants[].weight_unit` | `string \| null` |  |
| `variants[].inventory_item_id` | `integer \| null` |  |
| `variants[].inventory_quantity` | `integer \| null` |  |
| `variants[].old_inventory_quantity` | `integer \| null` |  |
| `variants[].requires_shipping` | `boolean \| null` |  |
| `variants[].admin_graphql_api_id` | `string \| null` |  |
| `options` | `array \| null` |  |
| `images` | `array \| null` |  |
| `images[].id` | `integer` |  |
| `images[].product_id` | `integer \| null` |  |
| `images[].position` | `integer \| null` |  |
| `images[].created_at` | `string \| null` |  |
| `images[].updated_at` | `string \| null` |  |
| `images[].alt` | `string \| null` |  |
| `images[].width` | `integer \| null` |  |
| `images[].height` | `integer \| null` |  |
| `images[].src` | `string \| null` |  |
| `images[].variant_ids` | `array \| null` |  |
| `images[].admin_graphql_api_id` | `string \| null` |  |
| `image` | `object \| any` |  |


</details>

## Product Variants

### Product Variants List

Returns a list of variants for a product

#### Python SDK

```python
await shopify.product_variants.list(
    product_id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "product_variants",
    "action": "list",
    "params": {
        "product_id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `product_id` | `integer` | Yes | The product ID |
| `limit` | `integer` | No | Maximum number of results to return (max 250) |
| `since_id` | `integer` | No | Restrict results to after the specified ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `product_id` | `integer \| null` |  |
| `title` | `string \| null` |  |
| `price` | `string \| null` |  |
| `sku` | `string \| null` |  |
| `position` | `integer \| null` |  |
| `inventory_policy` | `string \| null` |  |
| `compare_at_price` | `string \| null` |  |
| `fulfillment_service` | `string \| null` |  |
| `inventory_management` | `string \| null` |  |
| `option1` | `string \| null` |  |
| `option2` | `string \| null` |  |
| `option3` | `string \| null` |  |
| `created_at` | `string \| null` |  |
| `updated_at` | `string \| null` |  |
| `taxable` | `boolean \| null` |  |
| `barcode` | `string \| null` |  |
| `grams` | `integer \| null` |  |
| `image_id` | `integer \| null` |  |
| `weight` | `number \| null` |  |
| `weight_unit` | `string \| null` |  |
| `inventory_item_id` | `integer \| null` |  |
| `inventory_quantity` | `integer \| null` |  |
| `old_inventory_quantity` | `integer \| null` |  |
| `requires_shipping` | `boolean \| null` |  |
| `admin_graphql_api_id` | `string \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page_url` | `string` |  |

</details>

### Product Variants Get

Retrieves a single product variant by ID

#### Python SDK

```python
await shopify.product_variants.get(
    variant_id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "product_variants",
    "action": "get",
    "params": {
        "variant_id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `variant_id` | `integer` | Yes | The variant ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `product_id` | `integer \| null` |  |
| `title` | `string \| null` |  |
| `price` | `string \| null` |  |
| `sku` | `string \| null` |  |
| `position` | `integer \| null` |  |
| `inventory_policy` | `string \| null` |  |
| `compare_at_price` | `string \| null` |  |
| `fulfillment_service` | `string \| null` |  |
| `inventory_management` | `string \| null` |  |
| `option1` | `string \| null` |  |
| `option2` | `string \| null` |  |
| `option3` | `string \| null` |  |
| `created_at` | `string \| null` |  |
| `updated_at` | `string \| null` |  |
| `taxable` | `boolean \| null` |  |
| `barcode` | `string \| null` |  |
| `grams` | `integer \| null` |  |
| `image_id` | `integer \| null` |  |
| `weight` | `number \| null` |  |
| `weight_unit` | `string \| null` |  |
| `inventory_item_id` | `integer \| null` |  |
| `inventory_quantity` | `integer \| null` |  |
| `old_inventory_quantity` | `integer \| null` |  |
| `requires_shipping` | `boolean \| null` |  |
| `admin_graphql_api_id` | `string \| null` |  |


</details>

### Product Variants Context Store Search

Search and filter product variants records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await shopify.product_variants.context_store_search(
    query={"filter": {"eq": {"id": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "product_variants",
    "action": "context_store_search",
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
| `id` | `integer` | Unique identifier for the product variant |
| `product_id` | `integer` | Identifier of the parent product |
| `title` | `string` | Display title of the variant |
| `sku` | `string` | Stock keeping unit for the variant |
| `price` | `string` | Price of the variant in the shop's currency |
| `compare_at_price` | `string` | Original (compare-at) price of the variant, if set |
| `position` | `integer` | Display position of the variant within the product |
| `inventory_policy` | `string` | Behaviour when out of stock (`deny` or `continue`) |
| `created_at` | `string` | ISO 8601 timestamp when the variant was created |
| `updated_at` | `string` | ISO 8601 timestamp when the variant was last updated |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].id` | `integer` | Unique identifier for the product variant |
| `data[].product_id` | `integer` | Identifier of the parent product |
| `data[].title` | `string` | Display title of the variant |
| `data[].sku` | `string` | Stock keeping unit for the variant |
| `data[].price` | `string` | Price of the variant in the shop's currency |
| `data[].compare_at_price` | `string` | Original (compare-at) price of the variant, if set |
| `data[].position` | `integer` | Display position of the variant within the product |
| `data[].inventory_policy` | `string` | Behaviour when out of stock (`deny` or `continue`) |
| `data[].created_at` | `string` | ISO 8601 timestamp when the variant was created |
| `data[].updated_at` | `string` | ISO 8601 timestamp when the variant was last updated |

</details>

## Product Images

### Product Images List

Returns a list of images for a product

#### Python SDK

```python
await shopify.product_images.list(
    product_id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "product_images",
    "action": "list",
    "params": {
        "product_id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `product_id` | `integer` | Yes | The product ID |
| `since_id` | `integer` | No | Restrict results to after the specified ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `product_id` | `integer \| null` |  |
| `position` | `integer \| null` |  |
| `created_at` | `string \| null` |  |
| `updated_at` | `string \| null` |  |
| `alt` | `string \| null` |  |
| `width` | `integer \| null` |  |
| `height` | `integer \| null` |  |
| `src` | `string \| null` |  |
| `variant_ids` | `array \| null` |  |
| `admin_graphql_api_id` | `string \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page_url` | `string` |  |

</details>

### Product Images Get

Retrieves a single product image by ID

#### Python SDK

```python
await shopify.product_images.get(
    product_id=0,
    image_id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "product_images",
    "action": "get",
    "params": {
        "product_id": 0,
        "image_id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `product_id` | `integer` | Yes | The product ID |
| `image_id` | `integer` | Yes | The image ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `product_id` | `integer \| null` |  |
| `position` | `integer \| null` |  |
| `created_at` | `string \| null` |  |
| `updated_at` | `string \| null` |  |
| `alt` | `string \| null` |  |
| `width` | `integer \| null` |  |
| `height` | `integer \| null` |  |
| `src` | `string \| null` |  |
| `variant_ids` | `array \| null` |  |
| `admin_graphql_api_id` | `string \| null` |  |


</details>

### Product Images Context Store Search

Search and filter product images records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await shopify.product_images.context_store_search(
    query={"filter": {"eq": {"id": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "product_images",
    "action": "context_store_search",
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
| `id` | `integer` | Unique identifier for the product image |
| `product_id` | `integer` | Identifier of the product the image belongs to |
| `position` | `integer` | Display position of the image within the product |
| `alt` | `string` | Alt text for the image |
| `width` | `integer` | Image width in pixels |
| `height` | `integer` | Image height in pixels |
| `src` | `string` | Public URL of the image |
| `created_at` | `string` | ISO 8601 timestamp when the image was created |
| `updated_at` | `string` | ISO 8601 timestamp when the image was last updated |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].id` | `integer` | Unique identifier for the product image |
| `data[].product_id` | `integer` | Identifier of the product the image belongs to |
| `data[].position` | `integer` | Display position of the image within the product |
| `data[].alt` | `string` | Alt text for the image |
| `data[].width` | `integer` | Image width in pixels |
| `data[].height` | `integer` | Image height in pixels |
| `data[].src` | `string` | Public URL of the image |
| `data[].created_at` | `string` | ISO 8601 timestamp when the image was created |
| `data[].updated_at` | `string` | ISO 8601 timestamp when the image was last updated |

</details>

## Abandoned Checkouts

### Abandoned Checkouts List

Returns a list of abandoned checkouts

#### Python SDK

```python
await shopify.abandoned_checkouts.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "abandoned_checkouts",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `limit` | `integer` | No | Maximum number of results to return (max 250) |
| `since_id` | `integer` | No | Restrict results to after the specified ID |
| `created_at_min` | `string` | No | Show checkouts created after date (ISO 8601 format) |
| `created_at_max` | `string` | No | Show checkouts created before date (ISO 8601 format) |
| `updated_at_min` | `string` | No | Show checkouts last updated after date (ISO 8601 format) |
| `updated_at_max` | `string` | No | Show checkouts last updated before date (ISO 8601 format) |
| `status` | `"open" \| "closed" \| "any"` | No | Filter checkouts by status |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `token` | `string \| null` |  |
| `cart_token` | `string \| null` |  |
| `email` | `string \| null` |  |
| `gateway` | `string \| null` |  |
| `buyer_accepts_marketing` | `boolean \| null` |  |
| `created_at` | `string \| null` |  |
| `updated_at` | `string \| null` |  |
| `landing_site` | `string \| null` |  |
| `note` | `string \| null` |  |
| `note_attributes` | `array \| null` |  |
| `referring_site` | `string \| null` |  |
| `shipping_lines` | `array \| null` |  |
| `taxes_included` | `boolean \| null` |  |
| `total_weight` | `integer \| null` |  |
| `currency` | `string \| null` |  |
| `completed_at` | `string \| null` |  |
| `closed_at` | `string \| null` |  |
| `user_id` | `integer \| null` |  |
| `location_id` | `integer \| null` |  |
| `source_identifier` | `string \| null` |  |
| `source_url` | `string \| null` |  |
| `device_id` | `integer \| null` |  |
| `phone` | `string \| null` |  |
| `customer_locale` | `string \| null` |  |
| `line_items` | `array \| null` |  |
| `line_items[].id` | `integer` |  |
| `line_items[].admin_graphql_api_id` | `string \| null` |  |
| `line_items[].attributed_staffs` | `array \| null` |  |
| `line_items[].current_quantity` | `integer \| null` |  |
| `line_items[].fulfillable_quantity` | `integer \| null` |  |
| `line_items[].fulfillment_service` | `string \| null` |  |
| `line_items[].fulfillment_status` | `string \| null` |  |
| `line_items[].gift_card` | `boolean \| null` |  |
| `line_items[].grams` | `integer \| null` |  |
| `line_items[].name` | `string \| null` |  |
| `line_items[].price` | `string \| null` |  |
| `line_items[].price_set` | `object \| null` |  |
| `line_items[].product_exists` | `boolean \| null` |  |
| `line_items[].product_id` | `integer \| null` |  |
| `line_items[].properties` | `array \| null` |  |
| `line_items[].quantity` | `integer \| null` |  |
| `line_items[].requires_shipping` | `boolean \| null` |  |
| `line_items[].sku` | `string \| null` |  |
| `line_items[].taxable` | `boolean \| null` |  |
| `line_items[].title` | `string \| null` |  |
| `line_items[].total_discount` | `string \| null` |  |
| `line_items[].total_discount_set` | `object \| null` |  |
| `line_items[].variant_id` | `integer \| null` |  |
| `line_items[].variant_inventory_management` | `string \| null` |  |
| `line_items[].variant_title` | `string \| null` |  |
| `line_items[].vendor` | `string \| null` |  |
| `line_items[].tax_lines` | `array \| null` |  |
| `line_items[].duties` | `array \| null` |  |
| `line_items[].discount_allocations` | `array \| null` |  |
| `name` | `string \| null` |  |
| `source` | `string \| null` |  |
| `abandoned_checkout_url` | `string \| null` |  |
| `discount_codes` | `array \| null` |  |
| `tax_lines` | `array \| null` |  |
| `source_name` | `string \| null` |  |
| `presentment_currency` | `string \| null` |  |
| `buyer_accepts_sms_marketing` | `boolean \| null` |  |
| `sms_marketing_phone` | `string \| null` |  |
| `total_discounts` | `string \| null` |  |
| `total_line_items_price` | `string \| null` |  |
| `total_price` | `string \| null` |  |
| `total_tax` | `string \| null` |  |
| `subtotal_price` | `string \| null` |  |
| `total_duties` | `string \| null` |  |
| `billing_address` | `object \| any` |  |
| `shipping_address` | `object \| any` |  |
| `customer` | `object \| any` |  |
| `admin_graphql_api_id` | `string \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page_url` | `string` |  |

</details>

### Abandoned Checkouts Context Store Search

Search and filter abandoned checkouts records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await shopify.abandoned_checkouts.context_store_search(
    query={"filter": {"eq": {"id": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "abandoned_checkouts",
    "action": "context_store_search",
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
| `id` | `integer` | Unique identifier for the abandoned checkout |
| `token` | `string` | Unique token identifying the checkout |
| `email` | `string` | Email address provided for the checkout |
| `phone` | `string` | Phone number provided for the checkout |
| `name` | `string` | Shopify-assigned display name for the checkout (e.g. `#C12345`) |
| `currency` | `string` | ISO 4217 currency code for the checkout totals |
| `total_price` | `string` | Total price of the checkout in the shop's currency |
| `created_at` | `string` | ISO 8601 timestamp when the checkout was created |
| `updated_at` | `string` | ISO 8601 timestamp when the checkout was last updated |
| `completed_at` | `string` | ISO 8601 timestamp when the checkout was completed, if applicable |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].id` | `integer` | Unique identifier for the abandoned checkout |
| `data[].token` | `string` | Unique token identifying the checkout |
| `data[].email` | `string` | Email address provided for the checkout |
| `data[].phone` | `string` | Phone number provided for the checkout |
| `data[].name` | `string` | Shopify-assigned display name for the checkout (e.g. `#C12345`) |
| `data[].currency` | `string` | ISO 4217 currency code for the checkout totals |
| `data[].total_price` | `string` | Total price of the checkout in the shop's currency |
| `data[].created_at` | `string` | ISO 8601 timestamp when the checkout was created |
| `data[].updated_at` | `string` | ISO 8601 timestamp when the checkout was last updated |
| `data[].completed_at` | `string` | ISO 8601 timestamp when the checkout was completed, if applicable |

</details>

## Locations

### Locations List

Returns a list of locations for the store

#### Python SDK

```python
await shopify.locations.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "locations",
    "action": "list"
}'
```



<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `name` | `string \| null` |  |
| `address1` | `string \| null` |  |
| `address2` | `string \| null` |  |
| `city` | `string \| null` |  |
| `zip` | `string \| null` |  |
| `province` | `string \| null` |  |
| `country` | `string \| null` |  |
| `phone` | `string \| null` |  |
| `created_at` | `string \| null` |  |
| `updated_at` | `string \| null` |  |
| `country_code` | `string \| null` |  |
| `country_name` | `string \| null` |  |
| `province_code` | `string \| null` |  |
| `legacy` | `boolean \| null` |  |
| `active` | `boolean \| null` |  |
| `admin_graphql_api_id` | `string \| null` |  |
| `localized_country_name` | `string \| null` |  |
| `localized_province_name` | `string \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page_url` | `string` |  |

</details>

### Locations Get

Retrieves a single location by ID

#### Python SDK

```python
await shopify.locations.get(
    location_id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "locations",
    "action": "get",
    "params": {
        "location_id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `location_id` | `integer` | Yes | The location ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `name` | `string \| null` |  |
| `address1` | `string \| null` |  |
| `address2` | `string \| null` |  |
| `city` | `string \| null` |  |
| `zip` | `string \| null` |  |
| `province` | `string \| null` |  |
| `country` | `string \| null` |  |
| `phone` | `string \| null` |  |
| `created_at` | `string \| null` |  |
| `updated_at` | `string \| null` |  |
| `country_code` | `string \| null` |  |
| `country_name` | `string \| null` |  |
| `province_code` | `string \| null` |  |
| `legacy` | `boolean \| null` |  |
| `active` | `boolean \| null` |  |
| `admin_graphql_api_id` | `string \| null` |  |
| `localized_country_name` | `string \| null` |  |
| `localized_province_name` | `string \| null` |  |


</details>

### Locations Context Store Search

Search and filter locations records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await shopify.locations.context_store_search(
    query={"filter": {"eq": {"id": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "locations",
    "action": "context_store_search",
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
| `id` | `integer` | Unique identifier for the location |
| `name` | `string` | Display name of the location |
| `address1` | `string` | Primary street address of the location |
| `city` | `string` | City of the location |
| `province` | `string` | Province, state, or region of the location |
| `country` | `string` | Country name of the location |
| `country_code` | `string` | ISO 3166-1 alpha-2 country code of the location |
| `phone` | `string` | Phone number for the location |
| `active` | `boolean` | Whether the location is currently active |
| `created_at` | `string` | ISO 8601 timestamp when the location was created |
| `updated_at` | `string` | ISO 8601 timestamp when the location was last updated |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].id` | `integer` | Unique identifier for the location |
| `data[].name` | `string` | Display name of the location |
| `data[].address1` | `string` | Primary street address of the location |
| `data[].city` | `string` | City of the location |
| `data[].province` | `string` | Province, state, or region of the location |
| `data[].country` | `string` | Country name of the location |
| `data[].country_code` | `string` | ISO 3166-1 alpha-2 country code of the location |
| `data[].phone` | `string` | Phone number for the location |
| `data[].active` | `boolean` | Whether the location is currently active |
| `data[].created_at` | `string` | ISO 8601 timestamp when the location was created |
| `data[].updated_at` | `string` | ISO 8601 timestamp when the location was last updated |

</details>

## Inventory Levels

### Inventory Levels List

Returns a list of inventory levels for a specific location

#### Python SDK

```python
await shopify.inventory_levels.list(
    location_id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "inventory_levels",
    "action": "list",
    "params": {
        "location_id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `location_id` | `integer` | Yes | The location ID |
| `limit` | `integer` | No | Maximum number of results to return (max 250) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `inventory_item_id` | `integer` |  |
| `location_id` | `integer \| null` |  |
| `available` | `integer \| null` |  |
| `updated_at` | `string \| null` |  |
| `admin_graphql_api_id` | `string \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page_url` | `string` |  |

</details>

### Inventory Levels Context Store Search

Search and filter inventory levels records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await shopify.inventory_levels.context_store_search(
    query={"filter": {"eq": {"inventory_item_id": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "inventory_levels",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"inventory_item_id": 0}}}
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
| `inventory_item_id` | `integer` | Identifier of the inventory item |
| `location_id` | `integer` | Identifier of the location holding the inventory |
| `available` | `integer` | Number of units available at the location |
| `updated_at` | `string` | ISO 8601 timestamp when the inventory level was last updated |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].inventory_item_id` | `integer` | Identifier of the inventory item |
| `data[].location_id` | `integer` | Identifier of the location holding the inventory |
| `data[].available` | `integer` | Number of units available at the location |
| `data[].updated_at` | `string` | ISO 8601 timestamp when the inventory level was last updated |

</details>

## Inventory Items

### Inventory Items List

Returns a list of inventory items

#### Python SDK

```python
await shopify.inventory_items.list(
    ids="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "inventory_items",
    "action": "list",
    "params": {
        "ids": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `ids` | `string` | Yes | Comma-separated list of inventory item IDs |
| `limit` | `integer` | No | Maximum number of results to return (max 250) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `sku` | `string \| null` |  |
| `created_at` | `string \| null` |  |
| `updated_at` | `string \| null` |  |
| `requires_shipping` | `boolean \| null` |  |
| `cost` | `string \| null` |  |
| `country_code_of_origin` | `string \| null` |  |
| `province_code_of_origin` | `string \| null` |  |
| `harmonized_system_code` | `string \| null` |  |
| `tracked` | `boolean \| null` |  |
| `country_harmonized_system_codes` | `array \| null` |  |
| `admin_graphql_api_id` | `string \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page_url` | `string` |  |

</details>

### Inventory Items Get

Retrieves a single inventory item by ID

#### Python SDK

```python
await shopify.inventory_items.get(
    inventory_item_id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "inventory_items",
    "action": "get",
    "params": {
        "inventory_item_id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `inventory_item_id` | `integer` | Yes | The inventory item ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `sku` | `string \| null` |  |
| `created_at` | `string \| null` |  |
| `updated_at` | `string \| null` |  |
| `requires_shipping` | `boolean \| null` |  |
| `cost` | `string \| null` |  |
| `country_code_of_origin` | `string \| null` |  |
| `province_code_of_origin` | `string \| null` |  |
| `harmonized_system_code` | `string \| null` |  |
| `tracked` | `boolean \| null` |  |
| `country_harmonized_system_codes` | `array \| null` |  |
| `admin_graphql_api_id` | `string \| null` |  |


</details>

### Inventory Items Context Store Search

Search and filter inventory items records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await shopify.inventory_items.context_store_search(
    query={"filter": {"eq": {"id": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "inventory_items",
    "action": "context_store_search",
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
| `id` | `integer` | Unique identifier for the inventory item |
| `sku` | `string` | Stock keeping unit associated with the inventory item |
| `tracked` | `boolean` | Whether Shopify is tracking inventory for this item |
| `requires_shipping` | `boolean` | Whether the item requires shipping |
| `country_code_of_origin` | `string` | ISO country code of the item's country of origin |
| `created_at` | `string` | ISO 8601 timestamp when the inventory item was created |
| `updated_at` | `string` | ISO 8601 timestamp when the inventory item was last updated |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].id` | `integer` | Unique identifier for the inventory item |
| `data[].sku` | `string` | Stock keeping unit associated with the inventory item |
| `data[].tracked` | `boolean` | Whether Shopify is tracking inventory for this item |
| `data[].requires_shipping` | `boolean` | Whether the item requires shipping |
| `data[].country_code_of_origin` | `string` | ISO country code of the item's country of origin |
| `data[].created_at` | `string` | ISO 8601 timestamp when the inventory item was created |
| `data[].updated_at` | `string` | ISO 8601 timestamp when the inventory item was last updated |

</details>

## Shop

### Shop Get

Retrieves the shop's configuration

#### Python SDK

```python
await shopify.shop.get()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "shop",
    "action": "get"
}'
```



<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `name` | `string \| null` |  |
| `email` | `string \| null` |  |
| `domain` | `string \| null` |  |
| `province` | `string \| null` |  |
| `country` | `string \| null` |  |
| `address1` | `string \| null` |  |
| `zip` | `string \| null` |  |
| `city` | `string \| null` |  |
| `source` | `string \| null` |  |
| `phone` | `string \| null` |  |
| `latitude` | `number \| null` |  |
| `longitude` | `number \| null` |  |
| `primary_locale` | `string \| null` |  |
| `address2` | `string \| null` |  |
| `created_at` | `string \| null` |  |
| `updated_at` | `string \| null` |  |
| `country_code` | `string \| null` |  |
| `country_name` | `string \| null` |  |
| `currency` | `string \| null` |  |
| `customer_email` | `string \| null` |  |
| `timezone` | `string \| null` |  |
| `iana_timezone` | `string \| null` |  |
| `shop_owner` | `string \| null` |  |
| `money_format` | `string \| null` |  |
| `money_with_currency_format` | `string \| null` |  |
| `weight_unit` | `string \| null` |  |
| `province_code` | `string \| null` |  |
| `taxes_included` | `boolean \| null` |  |
| `auto_configure_tax_inclusivity` | `boolean \| null` |  |
| `tax_shipping` | `boolean \| null` |  |
| `county_taxes` | `boolean \| null` |  |
| `plan_display_name` | `string \| null` |  |
| `plan_name` | `string \| null` |  |
| `has_discounts` | `boolean \| null` |  |
| `has_gift_cards` | `boolean \| null` |  |
| `myshopify_domain` | `string \| null` |  |
| `google_apps_domain` | `string \| null` |  |
| `google_apps_login_enabled` | `boolean \| null` |  |
| `money_in_emails_format` | `string \| null` |  |
| `money_with_currency_in_emails_format` | `string \| null` |  |
| `eligible_for_payments` | `boolean \| null` |  |
| `requires_extra_payments_agreement` | `boolean \| null` |  |
| `password_enabled` | `boolean \| null` |  |
| `has_storefront` | `boolean \| null` |  |
| `finances` | `boolean \| null` |  |
| `primary_location_id` | `integer \| null` |  |
| `checkout_api_supported` | `boolean \| null` |  |
| `multi_location_enabled` | `boolean \| null` |  |
| `setup_required` | `boolean \| null` |  |
| `pre_launch_enabled` | `boolean \| null` |  |
| `enabled_presentment_currencies` | `array \| null` |  |
| `transactional_sms_disabled` | `boolean \| null` |  |
| `marketing_sms_consent_enabled_at_checkout` | `boolean \| null` |  |


</details>

### Shop Context Store Search

Search and filter shop records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await shopify.shop.context_store_search(
    query={"filter": {"eq": {"id": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "shop",
    "action": "context_store_search",
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
| `id` | `integer` | Unique identifier for the shop |
| `name` | `string` | Display name of the shop |
| `email` | `string` | Primary contact email for the shop |
| `domain` | `string` | Custom domain configured for the shop, if any |
| `myshopify_domain` | `string` | Canonical `*.myshopify.com` domain for the shop |
| `country_code` | `string` | ISO 3166-1 alpha-2 country code of the shop |
| `currency` | `string` | ISO 4217 currency code used by the shop |
| `timezone` | `string` | Timezone configured for the shop (e.g. `(GMT-05:00) Eastern Time`) |
| `plan_name` | `string` | Shopify plan identifier (e.g. `shopify_plus`, `basic`) |
| `created_at` | `string` | ISO 8601 timestamp when the shop was created |
| `updated_at` | `string` | ISO 8601 timestamp when the shop was last updated |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].id` | `integer` | Unique identifier for the shop |
| `data[].name` | `string` | Display name of the shop |
| `data[].email` | `string` | Primary contact email for the shop |
| `data[].domain` | `string` | Custom domain configured for the shop, if any |
| `data[].myshopify_domain` | `string` | Canonical `*.myshopify.com` domain for the shop |
| `data[].country_code` | `string` | ISO 3166-1 alpha-2 country code of the shop |
| `data[].currency` | `string` | ISO 4217 currency code used by the shop |
| `data[].timezone` | `string` | Timezone configured for the shop (e.g. `(GMT-05:00) Eastern Time`) |
| `data[].plan_name` | `string` | Shopify plan identifier (e.g. `shopify_plus`, `basic`) |
| `data[].created_at` | `string` | ISO 8601 timestamp when the shop was created |
| `data[].updated_at` | `string` | ISO 8601 timestamp when the shop was last updated |

</details>

## Price Rules

### Price Rules List

Returns a list of price rules

#### Python SDK

```python
await shopify.price_rules.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "price_rules",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `limit` | `integer` | No | Maximum number of results to return (max 250) |
| `since_id` | `integer` | No | Restrict results to after the specified ID |
| `created_at_min` | `string` | No | Show price rules created after date (ISO 8601 format) |
| `created_at_max` | `string` | No | Show price rules created before date (ISO 8601 format) |
| `updated_at_min` | `string` | No | Show price rules last updated after date (ISO 8601 format) |
| `updated_at_max` | `string` | No | Show price rules last updated before date (ISO 8601 format) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `value_type` | `string \| null` |  |
| `value` | `string \| null` |  |
| `customer_selection` | `string \| null` |  |
| `target_type` | `string \| null` |  |
| `target_selection` | `string \| null` |  |
| `allocation_method` | `string \| null` |  |
| `allocation_limit` | `integer \| null` |  |
| `once_per_customer` | `boolean \| null` |  |
| `usage_limit` | `integer \| null` |  |
| `starts_at` | `string \| null` |  |
| `ends_at` | `string \| null` |  |
| `created_at` | `string \| null` |  |
| `updated_at` | `string \| null` |  |
| `entitled_product_ids` | `array \| null` |  |
| `entitled_variant_ids` | `array \| null` |  |
| `entitled_collection_ids` | `array \| null` |  |
| `entitled_country_ids` | `array \| null` |  |
| `prerequisite_product_ids` | `array \| null` |  |
| `prerequisite_variant_ids` | `array \| null` |  |
| `prerequisite_collection_ids` | `array \| null` |  |
| `customer_segment_prerequisite_ids` | `array \| null` |  |
| `prerequisite_customer_ids` | `array \| null` |  |
| `prerequisite_subtotal_range` | `object \| null` |  |
| `prerequisite_quantity_range` | `object \| null` |  |
| `prerequisite_shipping_price_range` | `object \| null` |  |
| `prerequisite_to_entitlement_quantity_ratio` | `object \| null` |  |
| `prerequisite_to_entitlement_purchase` | `object \| null` |  |
| `title` | `string \| null` |  |
| `admin_graphql_api_id` | `string \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page_url` | `string` |  |

</details>

### Price Rules Get

Retrieves a single price rule by ID

#### Python SDK

```python
await shopify.price_rules.get(
    price_rule_id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "price_rules",
    "action": "get",
    "params": {
        "price_rule_id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `price_rule_id` | `integer` | Yes | The price rule ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `value_type` | `string \| null` |  |
| `value` | `string \| null` |  |
| `customer_selection` | `string \| null` |  |
| `target_type` | `string \| null` |  |
| `target_selection` | `string \| null` |  |
| `allocation_method` | `string \| null` |  |
| `allocation_limit` | `integer \| null` |  |
| `once_per_customer` | `boolean \| null` |  |
| `usage_limit` | `integer \| null` |  |
| `starts_at` | `string \| null` |  |
| `ends_at` | `string \| null` |  |
| `created_at` | `string \| null` |  |
| `updated_at` | `string \| null` |  |
| `entitled_product_ids` | `array \| null` |  |
| `entitled_variant_ids` | `array \| null` |  |
| `entitled_collection_ids` | `array \| null` |  |
| `entitled_country_ids` | `array \| null` |  |
| `prerequisite_product_ids` | `array \| null` |  |
| `prerequisite_variant_ids` | `array \| null` |  |
| `prerequisite_collection_ids` | `array \| null` |  |
| `customer_segment_prerequisite_ids` | `array \| null` |  |
| `prerequisite_customer_ids` | `array \| null` |  |
| `prerequisite_subtotal_range` | `object \| null` |  |
| `prerequisite_quantity_range` | `object \| null` |  |
| `prerequisite_shipping_price_range` | `object \| null` |  |
| `prerequisite_to_entitlement_quantity_ratio` | `object \| null` |  |
| `prerequisite_to_entitlement_purchase` | `object \| null` |  |
| `title` | `string \| null` |  |
| `admin_graphql_api_id` | `string \| null` |  |


</details>

### Price Rules Context Store Search

Search and filter price rules records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await shopify.price_rules.context_store_search(
    query={"filter": {"eq": {"id": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "price_rules",
    "action": "context_store_search",
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
| `id` | `integer` | Unique identifier for the price rule |
| `title` | `string` | Administrative title of the price rule |
| `value_type` | `string` | How the discount value is interpreted (`fixed_amount` or `percentage`) |
| `value` | `string` | Discount value applied by the rule |
| `target_type` | `string` | Type of target the rule applies to (`line_item` or `shipping_line`) |
| `target_selection` | `string` | Which target items the rule applies to (`all` or `entitled`) |
| `allocation_method` | `string` | How the discount is allocated (`each` or `across`) |
| `starts_at` | `string` | ISO 8601 timestamp when the rule starts being active |
| `ends_at` | `string` | ISO 8601 timestamp when the rule stops being active, if applicable |
| `created_at` | `string` | ISO 8601 timestamp when the rule was created |
| `updated_at` | `string` | ISO 8601 timestamp when the rule was last updated |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].id` | `integer` | Unique identifier for the price rule |
| `data[].title` | `string` | Administrative title of the price rule |
| `data[].value_type` | `string` | How the discount value is interpreted (`fixed_amount` or `percentage`) |
| `data[].value` | `string` | Discount value applied by the rule |
| `data[].target_type` | `string` | Type of target the rule applies to (`line_item` or `shipping_line`) |
| `data[].target_selection` | `string` | Which target items the rule applies to (`all` or `entitled`) |
| `data[].allocation_method` | `string` | How the discount is allocated (`each` or `across`) |
| `data[].starts_at` | `string` | ISO 8601 timestamp when the rule starts being active |
| `data[].ends_at` | `string` | ISO 8601 timestamp when the rule stops being active, if applicable |
| `data[].created_at` | `string` | ISO 8601 timestamp when the rule was created |
| `data[].updated_at` | `string` | ISO 8601 timestamp when the rule was last updated |

</details>

## Discount Codes

### Discount Codes List

Returns a list of discount codes for a price rule

#### Python SDK

```python
await shopify.discount_codes.list(
    price_rule_id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "discount_codes",
    "action": "list",
    "params": {
        "price_rule_id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `price_rule_id` | `integer` | Yes | The price rule ID |
| `limit` | `integer` | No | Maximum number of results to return (max 250) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `price_rule_id` | `integer \| null` |  |
| `code` | `string \| null` |  |
| `usage_count` | `integer \| null` |  |
| `created_at` | `string \| null` |  |
| `updated_at` | `string \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page_url` | `string` |  |

</details>

### Discount Codes Get

Retrieves a single discount code by ID

#### Python SDK

```python
await shopify.discount_codes.get(
    price_rule_id=0,
    discount_code_id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "discount_codes",
    "action": "get",
    "params": {
        "price_rule_id": 0,
        "discount_code_id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `price_rule_id` | `integer` | Yes | The price rule ID |
| `discount_code_id` | `integer` | Yes | The discount code ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `price_rule_id` | `integer \| null` |  |
| `code` | `string \| null` |  |
| `usage_count` | `integer \| null` |  |
| `created_at` | `string \| null` |  |
| `updated_at` | `string \| null` |  |


</details>

### Discount Codes Context Store Search

Search and filter discount codes records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await shopify.discount_codes.context_store_search(
    query={"filter": {"eq": {"id": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "discount_codes",
    "action": "context_store_search",
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
| `id` | `integer` | Unique identifier for the discount code |
| `price_rule_id` | `integer` | Identifier of the parent price rule |
| `code` | `string` | Discount code string shoppers enter at checkout |
| `usage_count` | `integer` | Number of times the code has been redeemed |
| `created_at` | `string` | ISO 8601 timestamp when the code was created |
| `updated_at` | `string` | ISO 8601 timestamp when the code was last updated |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].id` | `integer` | Unique identifier for the discount code |
| `data[].price_rule_id` | `integer` | Identifier of the parent price rule |
| `data[].code` | `string` | Discount code string shoppers enter at checkout |
| `data[].usage_count` | `integer` | Number of times the code has been redeemed |
| `data[].created_at` | `string` | ISO 8601 timestamp when the code was created |
| `data[].updated_at` | `string` | ISO 8601 timestamp when the code was last updated |

</details>

## Custom Collections

### Custom Collections List

Returns a list of custom collections

#### Python SDK

```python
await shopify.custom_collections.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "custom_collections",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `limit` | `integer` | No | Maximum number of results to return (max 250) |
| `since_id` | `integer` | No | Restrict results to after the specified ID |
| `title` | `string` | No | Filter by collection title |
| `product_id` | `integer` | No | Filter by product ID |
| `updated_at_min` | `string` | No | Show collections last updated after date (ISO 8601 format) |
| `updated_at_max` | `string` | No | Show collections last updated before date (ISO 8601 format) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `handle` | `string \| null` |  |
| `title` | `string \| null` |  |
| `updated_at` | `string \| null` |  |
| `body_html` | `string \| null` |  |
| `published_at` | `string \| null` |  |
| `sort_order` | `string \| null` |  |
| `template_suffix` | `string \| null` |  |
| `published_scope` | `string \| null` |  |
| `admin_graphql_api_id` | `string \| null` |  |
| `image` | `object \| null` |  |
| `products_count` | `integer \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page_url` | `string` |  |

</details>

### Custom Collections Get

Retrieves a single custom collection by ID

#### Python SDK

```python
await shopify.custom_collections.get(
    collection_id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "custom_collections",
    "action": "get",
    "params": {
        "collection_id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `collection_id` | `integer` | Yes | The collection ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `handle` | `string \| null` |  |
| `title` | `string \| null` |  |
| `updated_at` | `string \| null` |  |
| `body_html` | `string \| null` |  |
| `published_at` | `string \| null` |  |
| `sort_order` | `string \| null` |  |
| `template_suffix` | `string \| null` |  |
| `published_scope` | `string \| null` |  |
| `admin_graphql_api_id` | `string \| null` |  |
| `image` | `object \| null` |  |
| `products_count` | `integer \| null` |  |


</details>

### Custom Collections Context Store Search

Search and filter custom collections records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await shopify.custom_collections.context_store_search(
    query={"filter": {"eq": {"id": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "custom_collections",
    "action": "context_store_search",
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
| `id` | `integer` | Unique identifier for the custom collection |
| `handle` | `string` | URL-friendly handle for the custom collection |
| `title` | `string` | Display title of the custom collection |
| `sort_order` | `string` | How products are sorted within the collection (e.g. `best-selling`) |
| `published_scope` | `string` | Publishing scope (`web` or `global`) |
| `published_at` | `string` | ISO 8601 timestamp when the collection was published |
| `updated_at` | `string` | ISO 8601 timestamp when the collection was last updated |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].id` | `integer` | Unique identifier for the custom collection |
| `data[].handle` | `string` | URL-friendly handle for the custom collection |
| `data[].title` | `string` | Display title of the custom collection |
| `data[].sort_order` | `string` | How products are sorted within the collection (e.g. `best-selling`) |
| `data[].published_scope` | `string` | Publishing scope (`web` or `global`) |
| `data[].published_at` | `string` | ISO 8601 timestamp when the collection was published |
| `data[].updated_at` | `string` | ISO 8601 timestamp when the collection was last updated |

</details>

## Smart Collections

### Smart Collections List

Returns a list of smart collections

#### Python SDK

```python
await shopify.smart_collections.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "smart_collections",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `limit` | `integer` | No | Maximum number of results to return (max 250) |
| `since_id` | `integer` | No | Restrict results to after the specified ID |
| `title` | `string` | No | Filter by collection title |
| `product_id` | `integer` | No | Filter by product ID |
| `updated_at_min` | `string` | No | Show collections last updated after date (ISO 8601 format) |
| `updated_at_max` | `string` | No | Show collections last updated before date (ISO 8601 format) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `handle` | `string \| null` |  |
| `title` | `string \| null` |  |
| `updated_at` | `string \| null` |  |
| `body_html` | `string \| null` |  |
| `published_at` | `string \| null` |  |
| `sort_order` | `string \| null` |  |
| `template_suffix` | `string \| null` |  |
| `disjunctive` | `boolean \| null` |  |
| `rules` | `array \| null` |  |
| `published_scope` | `string \| null` |  |
| `admin_graphql_api_id` | `string \| null` |  |
| `image` | `object \| null` |  |
| `products_count` | `integer \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page_url` | `string` |  |

</details>

### Smart Collections Get

Retrieves a single smart collection by ID

#### Python SDK

```python
await shopify.smart_collections.get(
    collection_id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "smart_collections",
    "action": "get",
    "params": {
        "collection_id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `collection_id` | `integer` | Yes | The collection ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `handle` | `string \| null` |  |
| `title` | `string \| null` |  |
| `updated_at` | `string \| null` |  |
| `body_html` | `string \| null` |  |
| `published_at` | `string \| null` |  |
| `sort_order` | `string \| null` |  |
| `template_suffix` | `string \| null` |  |
| `disjunctive` | `boolean \| null` |  |
| `rules` | `array \| null` |  |
| `published_scope` | `string \| null` |  |
| `admin_graphql_api_id` | `string \| null` |  |
| `image` | `object \| null` |  |
| `products_count` | `integer \| null` |  |


</details>

### Smart Collections Context Store Search

Search and filter smart collections records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await shopify.smart_collections.context_store_search(
    query={"filter": {"eq": {"id": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "smart_collections",
    "action": "context_store_search",
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
| `id` | `integer` | Unique identifier for the smart collection |
| `handle` | `string` | URL-friendly handle for the smart collection |
| `title` | `string` | Display title of the smart collection |
| `sort_order` | `string` | How products are sorted within the collection |
| `published_scope` | `string` | Publishing scope (`web` or `global`) |
| `published_at` | `string` | ISO 8601 timestamp when the collection was published |
| `updated_at` | `string` | ISO 8601 timestamp when the collection was last updated |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].id` | `integer` | Unique identifier for the smart collection |
| `data[].handle` | `string` | URL-friendly handle for the smart collection |
| `data[].title` | `string` | Display title of the smart collection |
| `data[].sort_order` | `string` | How products are sorted within the collection |
| `data[].published_scope` | `string` | Publishing scope (`web` or `global`) |
| `data[].published_at` | `string` | ISO 8601 timestamp when the collection was published |
| `data[].updated_at` | `string` | ISO 8601 timestamp when the collection was last updated |

</details>

## Collects

### Collects List

Returns a list of collects (links between products and collections)

#### Python SDK

```python
await shopify.collects.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "collects",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `limit` | `integer` | No | Maximum number of results to return (max 250) |
| `since_id` | `integer` | No | Restrict results to after the specified ID |
| `collection_id` | `integer` | No | Filter by collection ID |
| `product_id` | `integer` | No | Filter by product ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `collection_id` | `integer \| null` |  |
| `product_id` | `integer \| null` |  |
| `created_at` | `string \| null` |  |
| `updated_at` | `string \| null` |  |
| `position` | `integer \| null` |  |
| `sort_value` | `string \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page_url` | `string` |  |

</details>

### Collects Get

Retrieves a single collect by ID

#### Python SDK

```python
await shopify.collects.get(
    collect_id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "collects",
    "action": "get",
    "params": {
        "collect_id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `collect_id` | `integer` | Yes | The collect ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `collection_id` | `integer \| null` |  |
| `product_id` | `integer \| null` |  |
| `created_at` | `string \| null` |  |
| `updated_at` | `string \| null` |  |
| `position` | `integer \| null` |  |
| `sort_value` | `string \| null` |  |


</details>

### Collects Context Store Search

Search and filter collects records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await shopify.collects.context_store_search(
    query={"filter": {"eq": {"id": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "collects",
    "action": "context_store_search",
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
| `id` | `integer` | Unique identifier for the collect |
| `collection_id` | `integer` | Identifier of the collection the product belongs to |
| `product_id` | `integer` | Identifier of the product in the collection |
| `position` | `integer` | Position of the product within the collection |
| `created_at` | `string` | ISO 8601 timestamp when the collect was created |
| `updated_at` | `string` | ISO 8601 timestamp when the collect was last updated |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].id` | `integer` | Unique identifier for the collect |
| `data[].collection_id` | `integer` | Identifier of the collection the product belongs to |
| `data[].product_id` | `integer` | Identifier of the product in the collection |
| `data[].position` | `integer` | Position of the product within the collection |
| `data[].created_at` | `string` | ISO 8601 timestamp when the collect was created |
| `data[].updated_at` | `string` | ISO 8601 timestamp when the collect was last updated |

</details>

## Draft Orders

### Draft Orders List

Returns a list of draft orders

#### Python SDK

```python
await shopify.draft_orders.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "draft_orders",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `limit` | `integer` | No | Maximum number of results to return (max 250) |
| `since_id` | `integer` | No | Restrict results to after the specified ID |
| `status` | `"open" \| "invoice_sent" \| "completed"` | No | Filter draft orders by status |
| `updated_at_min` | `string` | No | Show draft orders last updated after date (ISO 8601 format) |
| `updated_at_max` | `string` | No | Show draft orders last updated before date (ISO 8601 format) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `note` | `string \| null` |  |
| `email` | `string \| null` |  |
| `taxes_included` | `boolean \| null` |  |
| `currency` | `string \| null` |  |
| `invoice_sent_at` | `string \| null` |  |
| `created_at` | `string \| null` |  |
| `updated_at` | `string \| null` |  |
| `tax_exempt` | `boolean \| null` |  |
| `completed_at` | `string \| null` |  |
| `name` | `string \| null` |  |
| `status` | `string \| null` |  |
| `line_items` | `array \| null` |  |
| `line_items[].id` | `integer` |  |
| `line_items[].admin_graphql_api_id` | `string \| null` |  |
| `line_items[].attributed_staffs` | `array \| null` |  |
| `line_items[].current_quantity` | `integer \| null` |  |
| `line_items[].fulfillable_quantity` | `integer \| null` |  |
| `line_items[].fulfillment_service` | `string \| null` |  |
| `line_items[].fulfillment_status` | `string \| null` |  |
| `line_items[].gift_card` | `boolean \| null` |  |
| `line_items[].grams` | `integer \| null` |  |
| `line_items[].name` | `string \| null` |  |
| `line_items[].price` | `string \| null` |  |
| `line_items[].price_set` | `object \| null` |  |
| `line_items[].product_exists` | `boolean \| null` |  |
| `line_items[].product_id` | `integer \| null` |  |
| `line_items[].properties` | `array \| null` |  |
| `line_items[].quantity` | `integer \| null` |  |
| `line_items[].requires_shipping` | `boolean \| null` |  |
| `line_items[].sku` | `string \| null` |  |
| `line_items[].taxable` | `boolean \| null` |  |
| `line_items[].title` | `string \| null` |  |
| `line_items[].total_discount` | `string \| null` |  |
| `line_items[].total_discount_set` | `object \| null` |  |
| `line_items[].variant_id` | `integer \| null` |  |
| `line_items[].variant_inventory_management` | `string \| null` |  |
| `line_items[].variant_title` | `string \| null` |  |
| `line_items[].vendor` | `string \| null` |  |
| `line_items[].tax_lines` | `array \| null` |  |
| `line_items[].duties` | `array \| null` |  |
| `line_items[].discount_allocations` | `array \| null` |  |
| `shipping_address` | `object \| any` |  |
| `billing_address` | `object \| any` |  |
| `invoice_url` | `string \| null` |  |
| `applied_discount` | `object \| null` |  |
| `order_id` | `integer \| null` |  |
| `shipping_line` | `object \| null` |  |
| `tax_lines` | `array \| null` |  |
| `tags` | `string \| null` |  |
| `note_attributes` | `array \| null` |  |
| `total_price` | `string \| null` |  |
| `subtotal_price` | `string \| null` |  |
| `total_tax` | `string \| null` |  |
| `payment_terms` | `object \| null` |  |
| `admin_graphql_api_id` | `string \| null` |  |
| `customer` | `object \| any` |  |
| `allow_discount_codes_in_checkout?` | `boolean \| null` |  |
| `b2b?` | `boolean \| null` |  |
| `api_client_id` | `integer \| null` |  |
| `created_on_api_version_handle` | `string \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page_url` | `string` |  |

</details>

### Draft Orders Get

Retrieves a single draft order by ID

#### Python SDK

```python
await shopify.draft_orders.get(
    draft_order_id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "draft_orders",
    "action": "get",
    "params": {
        "draft_order_id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `draft_order_id` | `integer` | Yes | The draft order ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `note` | `string \| null` |  |
| `email` | `string \| null` |  |
| `taxes_included` | `boolean \| null` |  |
| `currency` | `string \| null` |  |
| `invoice_sent_at` | `string \| null` |  |
| `created_at` | `string \| null` |  |
| `updated_at` | `string \| null` |  |
| `tax_exempt` | `boolean \| null` |  |
| `completed_at` | `string \| null` |  |
| `name` | `string \| null` |  |
| `status` | `string \| null` |  |
| `line_items` | `array \| null` |  |
| `line_items[].id` | `integer` |  |
| `line_items[].admin_graphql_api_id` | `string \| null` |  |
| `line_items[].attributed_staffs` | `array \| null` |  |
| `line_items[].current_quantity` | `integer \| null` |  |
| `line_items[].fulfillable_quantity` | `integer \| null` |  |
| `line_items[].fulfillment_service` | `string \| null` |  |
| `line_items[].fulfillment_status` | `string \| null` |  |
| `line_items[].gift_card` | `boolean \| null` |  |
| `line_items[].grams` | `integer \| null` |  |
| `line_items[].name` | `string \| null` |  |
| `line_items[].price` | `string \| null` |  |
| `line_items[].price_set` | `object \| null` |  |
| `line_items[].product_exists` | `boolean \| null` |  |
| `line_items[].product_id` | `integer \| null` |  |
| `line_items[].properties` | `array \| null` |  |
| `line_items[].quantity` | `integer \| null` |  |
| `line_items[].requires_shipping` | `boolean \| null` |  |
| `line_items[].sku` | `string \| null` |  |
| `line_items[].taxable` | `boolean \| null` |  |
| `line_items[].title` | `string \| null` |  |
| `line_items[].total_discount` | `string \| null` |  |
| `line_items[].total_discount_set` | `object \| null` |  |
| `line_items[].variant_id` | `integer \| null` |  |
| `line_items[].variant_inventory_management` | `string \| null` |  |
| `line_items[].variant_title` | `string \| null` |  |
| `line_items[].vendor` | `string \| null` |  |
| `line_items[].tax_lines` | `array \| null` |  |
| `line_items[].duties` | `array \| null` |  |
| `line_items[].discount_allocations` | `array \| null` |  |
| `shipping_address` | `object \| any` |  |
| `billing_address` | `object \| any` |  |
| `invoice_url` | `string \| null` |  |
| `applied_discount` | `object \| null` |  |
| `order_id` | `integer \| null` |  |
| `shipping_line` | `object \| null` |  |
| `tax_lines` | `array \| null` |  |
| `tags` | `string \| null` |  |
| `note_attributes` | `array \| null` |  |
| `total_price` | `string \| null` |  |
| `subtotal_price` | `string \| null` |  |
| `total_tax` | `string \| null` |  |
| `payment_terms` | `object \| null` |  |
| `admin_graphql_api_id` | `string \| null` |  |
| `customer` | `object \| any` |  |
| `allow_discount_codes_in_checkout?` | `boolean \| null` |  |
| `b2b?` | `boolean \| null` |  |
| `api_client_id` | `integer \| null` |  |
| `created_on_api_version_handle` | `string \| null` |  |


</details>

### Draft Orders Context Store Search

Search and filter draft orders records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await shopify.draft_orders.context_store_search(
    query={"filter": {"eq": {"id": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "draft_orders",
    "action": "context_store_search",
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
| `id` | `integer` | Unique identifier for the draft order |
| `name` | `string` | Shopify-assigned display name for the draft order (e.g. `#D12345`) |
| `email` | `string` | Email address associated with the draft order |
| `status` | `string` | Status of the draft order (`open`, `invoice_sent`, `completed`) |
| `currency` | `string` | ISO 4217 currency code for the draft order totals |
| `total_price` | `string` | Total price of the draft order |
| `order_id` | `integer` | Identifier of the completed order, if the draft has been completed |
| `created_at` | `string` | ISO 8601 timestamp when the draft order was created |
| `updated_at` | `string` | ISO 8601 timestamp when the draft order was last updated |
| `completed_at` | `string` | ISO 8601 timestamp when the draft order was completed, if applicable |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].id` | `integer` | Unique identifier for the draft order |
| `data[].name` | `string` | Shopify-assigned display name for the draft order (e.g. `#D12345`) |
| `data[].email` | `string` | Email address associated with the draft order |
| `data[].status` | `string` | Status of the draft order (`open`, `invoice_sent`, `completed`) |
| `data[].currency` | `string` | ISO 4217 currency code for the draft order totals |
| `data[].total_price` | `string` | Total price of the draft order |
| `data[].order_id` | `integer` | Identifier of the completed order, if the draft has been completed |
| `data[].created_at` | `string` | ISO 8601 timestamp when the draft order was created |
| `data[].updated_at` | `string` | ISO 8601 timestamp when the draft order was last updated |
| `data[].completed_at` | `string` | ISO 8601 timestamp when the draft order was completed, if applicable |

</details>

## Fulfillments

### Fulfillments List

Returns a list of fulfillments for an order

#### Python SDK

```python
await shopify.fulfillments.list(
    order_id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "fulfillments",
    "action": "list",
    "params": {
        "order_id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `order_id` | `integer` | Yes | The order ID |
| `limit` | `integer` | No | Maximum number of results to return (max 250) |
| `since_id` | `integer` | No | Restrict results to after the specified ID |
| `created_at_min` | `string` | No | Show fulfillments created after date (ISO 8601 format) |
| `created_at_max` | `string` | No | Show fulfillments created before date (ISO 8601 format) |
| `updated_at_min` | `string` | No | Show fulfillments last updated after date (ISO 8601 format) |
| `updated_at_max` | `string` | No | Show fulfillments last updated before date (ISO 8601 format) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `order_id` | `integer \| null` |  |
| `status` | `string \| null` |  |
| `created_at` | `string \| null` |  |
| `service` | `string \| null` |  |
| `updated_at` | `string \| null` |  |
| `tracking_company` | `string \| null` |  |
| `shipment_status` | `string \| null` |  |
| `location_id` | `integer \| null` |  |
| `origin_address` | `object \| null` |  |
| `line_items` | `array \| null` |  |
| `line_items[].id` | `integer` |  |
| `line_items[].admin_graphql_api_id` | `string \| null` |  |
| `line_items[].attributed_staffs` | `array \| null` |  |
| `line_items[].current_quantity` | `integer \| null` |  |
| `line_items[].fulfillable_quantity` | `integer \| null` |  |
| `line_items[].fulfillment_service` | `string \| null` |  |
| `line_items[].fulfillment_status` | `string \| null` |  |
| `line_items[].gift_card` | `boolean \| null` |  |
| `line_items[].grams` | `integer \| null` |  |
| `line_items[].name` | `string \| null` |  |
| `line_items[].price` | `string \| null` |  |
| `line_items[].price_set` | `object \| null` |  |
| `line_items[].product_exists` | `boolean \| null` |  |
| `line_items[].product_id` | `integer \| null` |  |
| `line_items[].properties` | `array \| null` |  |
| `line_items[].quantity` | `integer \| null` |  |
| `line_items[].requires_shipping` | `boolean \| null` |  |
| `line_items[].sku` | `string \| null` |  |
| `line_items[].taxable` | `boolean \| null` |  |
| `line_items[].title` | `string \| null` |  |
| `line_items[].total_discount` | `string \| null` |  |
| `line_items[].total_discount_set` | `object \| null` |  |
| `line_items[].variant_id` | `integer \| null` |  |
| `line_items[].variant_inventory_management` | `string \| null` |  |
| `line_items[].variant_title` | `string \| null` |  |
| `line_items[].vendor` | `string \| null` |  |
| `line_items[].tax_lines` | `array \| null` |  |
| `line_items[].duties` | `array \| null` |  |
| `line_items[].discount_allocations` | `array \| null` |  |
| `tracking_number` | `string \| null` |  |
| `tracking_numbers` | `array \| null` |  |
| `tracking_url` | `string \| null` |  |
| `tracking_urls` | `array \| null` |  |
| `receipt` | `object \| null` |  |
| `name` | `string \| null` |  |
| `admin_graphql_api_id` | `string \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page_url` | `string` |  |

</details>

### Fulfillments Get

Retrieves a single fulfillment by ID

#### Python SDK

```python
await shopify.fulfillments.get(
    order_id=0,
    fulfillment_id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "fulfillments",
    "action": "get",
    "params": {
        "order_id": 0,
        "fulfillment_id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `order_id` | `integer` | Yes | The order ID |
| `fulfillment_id` | `integer` | Yes | The fulfillment ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `order_id` | `integer \| null` |  |
| `status` | `string \| null` |  |
| `created_at` | `string \| null` |  |
| `service` | `string \| null` |  |
| `updated_at` | `string \| null` |  |
| `tracking_company` | `string \| null` |  |
| `shipment_status` | `string \| null` |  |
| `location_id` | `integer \| null` |  |
| `origin_address` | `object \| null` |  |
| `line_items` | `array \| null` |  |
| `line_items[].id` | `integer` |  |
| `line_items[].admin_graphql_api_id` | `string \| null` |  |
| `line_items[].attributed_staffs` | `array \| null` |  |
| `line_items[].current_quantity` | `integer \| null` |  |
| `line_items[].fulfillable_quantity` | `integer \| null` |  |
| `line_items[].fulfillment_service` | `string \| null` |  |
| `line_items[].fulfillment_status` | `string \| null` |  |
| `line_items[].gift_card` | `boolean \| null` |  |
| `line_items[].grams` | `integer \| null` |  |
| `line_items[].name` | `string \| null` |  |
| `line_items[].price` | `string \| null` |  |
| `line_items[].price_set` | `object \| null` |  |
| `line_items[].product_exists` | `boolean \| null` |  |
| `line_items[].product_id` | `integer \| null` |  |
| `line_items[].properties` | `array \| null` |  |
| `line_items[].quantity` | `integer \| null` |  |
| `line_items[].requires_shipping` | `boolean \| null` |  |
| `line_items[].sku` | `string \| null` |  |
| `line_items[].taxable` | `boolean \| null` |  |
| `line_items[].title` | `string \| null` |  |
| `line_items[].total_discount` | `string \| null` |  |
| `line_items[].total_discount_set` | `object \| null` |  |
| `line_items[].variant_id` | `integer \| null` |  |
| `line_items[].variant_inventory_management` | `string \| null` |  |
| `line_items[].variant_title` | `string \| null` |  |
| `line_items[].vendor` | `string \| null` |  |
| `line_items[].tax_lines` | `array \| null` |  |
| `line_items[].duties` | `array \| null` |  |
| `line_items[].discount_allocations` | `array \| null` |  |
| `tracking_number` | `string \| null` |  |
| `tracking_numbers` | `array \| null` |  |
| `tracking_url` | `string \| null` |  |
| `tracking_urls` | `array \| null` |  |
| `receipt` | `object \| null` |  |
| `name` | `string \| null` |  |
| `admin_graphql_api_id` | `string \| null` |  |


</details>

### Fulfillments Context Store Search

Search and filter fulfillments records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await shopify.fulfillments.context_store_search(
    query={"filter": {"eq": {"id": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "fulfillments",
    "action": "context_store_search",
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
| `id` | `integer` | Unique identifier for the fulfillment |
| `order_id` | `integer` | Identifier of the parent order |
| `status` | `string` | Fulfillment status (e.g. `pending`, `open`, `success`, `cancelled`) |
| `shipment_status` | `string` | Carrier shipment status (e.g. `delivered`, `in_transit`) |
| `tracking_company` | `string` | Name of the shipping carrier |
| `tracking_number` | `string` | Primary tracking number for the shipment |
| `location_id` | `integer` | Identifier of the fulfilling location |
| `created_at` | `string` | ISO 8601 timestamp when the fulfillment was created |
| `updated_at` | `string` | ISO 8601 timestamp when the fulfillment was last updated |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].id` | `integer` | Unique identifier for the fulfillment |
| `data[].order_id` | `integer` | Identifier of the parent order |
| `data[].status` | `string` | Fulfillment status (e.g. `pending`, `open`, `success`, `cancelled`) |
| `data[].shipment_status` | `string` | Carrier shipment status (e.g. `delivered`, `in_transit`) |
| `data[].tracking_company` | `string` | Name of the shipping carrier |
| `data[].tracking_number` | `string` | Primary tracking number for the shipment |
| `data[].location_id` | `integer` | Identifier of the fulfilling location |
| `data[].created_at` | `string` | ISO 8601 timestamp when the fulfillment was created |
| `data[].updated_at` | `string` | ISO 8601 timestamp when the fulfillment was last updated |

</details>

## Order Refunds

### Order Refunds List

Returns a list of refunds for an order

#### Python SDK

```python
await shopify.order_refunds.list(
    order_id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "order_refunds",
    "action": "list",
    "params": {
        "order_id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `order_id` | `integer` | Yes | The order ID |
| `limit` | `integer` | No | Maximum number of results to return (max 250) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `order_id` | `integer \| null` |  |
| `created_at` | `string \| null` |  |
| `note` | `string \| null` |  |
| `user_id` | `integer \| null` |  |
| `processed_at` | `string \| null` |  |
| `restock` | `boolean \| null` |  |
| `duties` | `array \| null` |  |
| `total_duties_set` | `object \| null` |  |
| `return` | `object \| null` |  |
| `refund_line_items` | `array \| null` |  |
| `transactions` | `array \| null` |  |
| `transactions[].id` | `integer` |  |
| `transactions[].order_id` | `integer \| null` |  |
| `transactions[].kind` | `string \| null` |  |
| `transactions[].gateway` | `string \| null` |  |
| `transactions[].status` | `string \| null` |  |
| `transactions[].message` | `string \| null` |  |
| `transactions[].created_at` | `string \| null` |  |
| `transactions[].test` | `boolean \| null` |  |
| `transactions[].authorization` | `string \| null` |  |
| `transactions[].location_id` | `integer \| null` |  |
| `transactions[].user_id` | `integer \| null` |  |
| `transactions[].parent_id` | `integer \| null` |  |
| `transactions[].processed_at` | `string \| null` |  |
| `transactions[].device_id` | `integer \| null` |  |
| `transactions[].error_code` | `string \| null` |  |
| `transactions[].source_name` | `string \| null` |  |
| `transactions[].receipt` | `object \| null` |  |
| `transactions[].currency_exchange_adjustment` | `object \| null` |  |
| `transactions[].amount` | `string \| null` |  |
| `transactions[].currency` | `string \| null` |  |
| `transactions[].payment_id` | `string \| null` |  |
| `transactions[].total_unsettled_set` | `object \| null` |  |
| `transactions[].manual_payment_gateway` | `boolean \| null` |  |
| `transactions[].admin_graphql_api_id` | `string \| null` |  |
| `order_adjustments` | `array \| null` |  |
| `admin_graphql_api_id` | `string \| null` |  |
| `refund_shipping_lines` | `array \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page_url` | `string` |  |

</details>

### Order Refunds Get

Retrieves a single refund by ID

#### Python SDK

```python
await shopify.order_refunds.get(
    order_id=0,
    refund_id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "order_refunds",
    "action": "get",
    "params": {
        "order_id": 0,
        "refund_id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `order_id` | `integer` | Yes | The order ID |
| `refund_id` | `integer` | Yes | The refund ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `order_id` | `integer \| null` |  |
| `created_at` | `string \| null` |  |
| `note` | `string \| null` |  |
| `user_id` | `integer \| null` |  |
| `processed_at` | `string \| null` |  |
| `restock` | `boolean \| null` |  |
| `duties` | `array \| null` |  |
| `total_duties_set` | `object \| null` |  |
| `return` | `object \| null` |  |
| `refund_line_items` | `array \| null` |  |
| `transactions` | `array \| null` |  |
| `transactions[].id` | `integer` |  |
| `transactions[].order_id` | `integer \| null` |  |
| `transactions[].kind` | `string \| null` |  |
| `transactions[].gateway` | `string \| null` |  |
| `transactions[].status` | `string \| null` |  |
| `transactions[].message` | `string \| null` |  |
| `transactions[].created_at` | `string \| null` |  |
| `transactions[].test` | `boolean \| null` |  |
| `transactions[].authorization` | `string \| null` |  |
| `transactions[].location_id` | `integer \| null` |  |
| `transactions[].user_id` | `integer \| null` |  |
| `transactions[].parent_id` | `integer \| null` |  |
| `transactions[].processed_at` | `string \| null` |  |
| `transactions[].device_id` | `integer \| null` |  |
| `transactions[].error_code` | `string \| null` |  |
| `transactions[].source_name` | `string \| null` |  |
| `transactions[].receipt` | `object \| null` |  |
| `transactions[].currency_exchange_adjustment` | `object \| null` |  |
| `transactions[].amount` | `string \| null` |  |
| `transactions[].currency` | `string \| null` |  |
| `transactions[].payment_id` | `string \| null` |  |
| `transactions[].total_unsettled_set` | `object \| null` |  |
| `transactions[].manual_payment_gateway` | `boolean \| null` |  |
| `transactions[].admin_graphql_api_id` | `string \| null` |  |
| `order_adjustments` | `array \| null` |  |
| `admin_graphql_api_id` | `string \| null` |  |
| `refund_shipping_lines` | `array \| null` |  |


</details>

### Order Refunds Context Store Search

Search and filter order refunds records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await shopify.order_refunds.context_store_search(
    query={"filter": {"eq": {"id": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "order_refunds",
    "action": "context_store_search",
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
| `id` | `integer` | Unique identifier for the refund |
| `order_id` | `integer` | Identifier of the refunded order |
| `user_id` | `integer` | Identifier of the staff user who processed the refund |
| `note` | `string` | Merchant-provided note explaining the refund |
| `created_at` | `string` | ISO 8601 timestamp when the refund was created |
| `processed_at` | `string` | ISO 8601 timestamp when the refund was processed |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].id` | `integer` | Unique identifier for the refund |
| `data[].order_id` | `integer` | Identifier of the refunded order |
| `data[].user_id` | `integer` | Identifier of the staff user who processed the refund |
| `data[].note` | `string` | Merchant-provided note explaining the refund |
| `data[].created_at` | `string` | ISO 8601 timestamp when the refund was created |
| `data[].processed_at` | `string` | ISO 8601 timestamp when the refund was processed |

</details>

## Transactions

### Transactions List

Returns a list of transactions for an order

#### Python SDK

```python
await shopify.transactions.list(
    order_id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "transactions",
    "action": "list",
    "params": {
        "order_id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `order_id` | `integer` | Yes | The order ID |
| `since_id` | `integer` | No | Restrict results to after the specified ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `order_id` | `integer \| null` |  |
| `kind` | `string \| null` |  |
| `gateway` | `string \| null` |  |
| `status` | `string \| null` |  |
| `message` | `string \| null` |  |
| `created_at` | `string \| null` |  |
| `test` | `boolean \| null` |  |
| `authorization` | `string \| null` |  |
| `location_id` | `integer \| null` |  |
| `user_id` | `integer \| null` |  |
| `parent_id` | `integer \| null` |  |
| `processed_at` | `string \| null` |  |
| `device_id` | `integer \| null` |  |
| `error_code` | `string \| null` |  |
| `source_name` | `string \| null` |  |
| `receipt` | `object \| null` |  |
| `currency_exchange_adjustment` | `object \| null` |  |
| `amount` | `string \| null` |  |
| `currency` | `string \| null` |  |
| `payment_id` | `string \| null` |  |
| `total_unsettled_set` | `object \| null` |  |
| `manual_payment_gateway` | `boolean \| null` |  |
| `admin_graphql_api_id` | `string \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page_url` | `string` |  |

</details>

### Transactions Get

Retrieves a single transaction by ID

#### Python SDK

```python
await shopify.transactions.get(
    order_id=0,
    transaction_id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "transactions",
    "action": "get",
    "params": {
        "order_id": 0,
        "transaction_id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `order_id` | `integer` | Yes | The order ID |
| `transaction_id` | `integer` | Yes | The transaction ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `order_id` | `integer \| null` |  |
| `kind` | `string \| null` |  |
| `gateway` | `string \| null` |  |
| `status` | `string \| null` |  |
| `message` | `string \| null` |  |
| `created_at` | `string \| null` |  |
| `test` | `boolean \| null` |  |
| `authorization` | `string \| null` |  |
| `location_id` | `integer \| null` |  |
| `user_id` | `integer \| null` |  |
| `parent_id` | `integer \| null` |  |
| `processed_at` | `string \| null` |  |
| `device_id` | `integer \| null` |  |
| `error_code` | `string \| null` |  |
| `source_name` | `string \| null` |  |
| `receipt` | `object \| null` |  |
| `currency_exchange_adjustment` | `object \| null` |  |
| `amount` | `string \| null` |  |
| `currency` | `string \| null` |  |
| `payment_id` | `string \| null` |  |
| `total_unsettled_set` | `object \| null` |  |
| `manual_payment_gateway` | `boolean \| null` |  |
| `admin_graphql_api_id` | `string \| null` |  |


</details>

## Tender Transactions

### Tender Transactions List

Returns a list of tender transactions

#### Python SDK

```python
await shopify.tender_transactions.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "tender_transactions",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `limit` | `integer` | No | Maximum number of results to return (max 250) |
| `since_id` | `integer` | No | Restrict results to after the specified ID |
| `processed_at_min` | `string` | No | Show tender transactions processed after date (ISO 8601 format) |
| `processed_at_max` | `string` | No | Show tender transactions processed before date (ISO 8601 format) |
| `order` | `"processed_at ASC" \| "processed_at DESC"` | No | Order of results |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `order_id` | `integer \| null` |  |
| `amount` | `string \| null` |  |
| `currency` | `string \| null` |  |
| `user_id` | `integer \| null` |  |
| `test` | `boolean \| null` |  |
| `processed_at` | `string \| null` |  |
| `remote_reference` | `string \| null` |  |
| `payment_details` | `object \| null` |  |
| `payment_method` | `string \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page_url` | `string` |  |

</details>

### Tender Transactions Context Store Search

Search and filter tender transactions records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await shopify.tender_transactions.context_store_search(
    query={"filter": {"eq": {"id": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "tender_transactions",
    "action": "context_store_search",
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
| `id` | `integer` | Unique identifier for the tender transaction |
| `order_id` | `integer` | Identifier of the order the transaction belongs to |
| `user_id` | `integer` | Identifier of the staff user who processed the transaction |
| `amount` | `string` | Amount of the transaction in the shop's currency |
| `currency` | `string` | ISO 4217 currency code for the transaction amount |
| `payment_method` | `string` | Payment method used (e.g. `credit_card`, `paypal`) |
| `test` | `boolean` | Whether the transaction was a test transaction |
| `processed_at` | `string` | ISO 8601 timestamp when the transaction was processed |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].id` | `integer` | Unique identifier for the tender transaction |
| `data[].order_id` | `integer` | Identifier of the order the transaction belongs to |
| `data[].user_id` | `integer` | Identifier of the staff user who processed the transaction |
| `data[].amount` | `string` | Amount of the transaction in the shop's currency |
| `data[].currency` | `string` | ISO 4217 currency code for the transaction amount |
| `data[].payment_method` | `string` | Payment method used (e.g. `credit_card`, `paypal`) |
| `data[].test` | `boolean` | Whether the transaction was a test transaction |
| `data[].processed_at` | `string` | ISO 8601 timestamp when the transaction was processed |

</details>

## Countries

### Countries List

Returns a list of countries

#### Python SDK

```python
await shopify.countries.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "countries",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `since_id` | `integer` | No | Restrict results to after the specified ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `name` | `string \| null` |  |
| `code` | `string \| null` |  |
| `tax_name` | `string \| null` |  |
| `tax` | `number \| null` |  |
| `provinces` | `array \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page_url` | `string` |  |

</details>

### Countries Get

Retrieves a single country by ID

#### Python SDK

```python
await shopify.countries.get(
    country_id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "countries",
    "action": "get",
    "params": {
        "country_id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `country_id` | `integer` | Yes | The country ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `name` | `string \| null` |  |
| `code` | `string \| null` |  |
| `tax_name` | `string \| null` |  |
| `tax` | `number \| null` |  |
| `provinces` | `array \| null` |  |


</details>

### Countries Context Store Search

Search and filter countries records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await shopify.countries.context_store_search(
    query={"filter": {"eq": {"id": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "countries",
    "action": "context_store_search",
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
| `id` | `integer` | Unique identifier for the country tax row |
| `name` | `string` | Human-readable country name |
| `code` | `string` | ISO 3166-1 alpha-2 country code |
| `tax_name` | `string` | Localized name of the tax applied in this country |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].id` | `integer` | Unique identifier for the country tax row |
| `data[].name` | `string` | Human-readable country name |
| `data[].code` | `string` | ISO 3166-1 alpha-2 country code |
| `data[].tax_name` | `string` | Localized name of the tax applied in this country |

</details>

## Metafield Shops

### Metafield Shops List

Returns a list of metafields for the shop

#### Python SDK

```python
await shopify.metafield_shops.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "metafield_shops",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `limit` | `integer` | No | Maximum number of results to return (max 250) |
| `since_id` | `integer` | No | Restrict results to after the specified ID |
| `namespace` | `string` | No | Filter by namespace |
| `key` | `string` | No | Filter by key |
| `type` | `string` | No | Filter by type |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `namespace` | `string \| null` |  |
| `key` | `string \| null` |  |
| `value` | `string \| integer \| boolean \| null` |  |
| `type` | `string \| null` |  |
| `description` | `string \| null` |  |
| `owner_id` | `integer \| null` |  |
| `created_at` | `string \| null` |  |
| `updated_at` | `string \| null` |  |
| `owner_resource` | `string \| null` |  |
| `admin_graphql_api_id` | `string \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page_url` | `string` |  |

</details>

### Metafield Shops Get

Retrieves a single metafield by ID

#### Python SDK

```python
await shopify.metafield_shops.get(
    metafield_id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "metafield_shops",
    "action": "get",
    "params": {
        "metafield_id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `metafield_id` | `integer` | Yes | The metafield ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `namespace` | `string \| null` |  |
| `key` | `string \| null` |  |
| `value` | `string \| integer \| boolean \| null` |  |
| `type` | `string \| null` |  |
| `description` | `string \| null` |  |
| `owner_id` | `integer \| null` |  |
| `created_at` | `string \| null` |  |
| `updated_at` | `string \| null` |  |
| `owner_resource` | `string \| null` |  |
| `admin_graphql_api_id` | `string \| null` |  |


</details>

### Metafield Shops Context Store Search

Search and filter metafield shops records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await shopify.metafield_shops.context_store_search(
    query={"filter": {"eq": {"id": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "metafield_shops",
    "action": "context_store_search",
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
| `id` | `integer` | Unique identifier for the metafield |
| `namespace` | `string` | Namespace group for the metafield |
| `key` | `string` | Key of the metafield within its namespace |
| `value` | `string` | Serialized value stored in the metafield |
| `type` | `string` | Shopify metafield type (e.g. `single_line_text_field`, `json`) |
| `description` | `string` | Human-readable description of the metafield |
| `owner_id` | `integer` | Identifier of the resource that owns this metafield |
| `owner_resource` | `string` | Resource type that owns this metafield (e.g. `product`, `customer`) |
| `created_at` | `string` | ISO 8601 timestamp when the metafield was created |
| `updated_at` | `string` | ISO 8601 timestamp when the metafield was last updated |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].id` | `integer` | Unique identifier for the metafield |
| `data[].namespace` | `string` | Namespace group for the metafield |
| `data[].key` | `string` | Key of the metafield within its namespace |
| `data[].value` | `string` | Serialized value stored in the metafield |
| `data[].type` | `string` | Shopify metafield type (e.g. `single_line_text_field`, `json`) |
| `data[].description` | `string` | Human-readable description of the metafield |
| `data[].owner_id` | `integer` | Identifier of the resource that owns this metafield |
| `data[].owner_resource` | `string` | Resource type that owns this metafield (e.g. `product`, `customer`) |
| `data[].created_at` | `string` | ISO 8601 timestamp when the metafield was created |
| `data[].updated_at` | `string` | ISO 8601 timestamp when the metafield was last updated |

</details>

## Metafield Customers

### Metafield Customers List

Returns a list of metafields for a customer

#### Python SDK

```python
await shopify.metafield_customers.list(
    customer_id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "metafield_customers",
    "action": "list",
    "params": {
        "customer_id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `customer_id` | `integer` | Yes | The customer ID |
| `limit` | `integer` | No | Maximum number of results to return (max 250) |
| `since_id` | `integer` | No | Restrict results to after the specified ID |
| `namespace` | `string` | No | Filter by namespace |
| `key` | `string` | No | Filter by key |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `namespace` | `string \| null` |  |
| `key` | `string \| null` |  |
| `value` | `string \| integer \| boolean \| null` |  |
| `type` | `string \| null` |  |
| `description` | `string \| null` |  |
| `owner_id` | `integer \| null` |  |
| `created_at` | `string \| null` |  |
| `updated_at` | `string \| null` |  |
| `owner_resource` | `string \| null` |  |
| `admin_graphql_api_id` | `string \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page_url` | `string` |  |

</details>

### Metafield Customers Context Store Search

Search and filter metafield customers records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await shopify.metafield_customers.context_store_search(
    query={"filter": {"eq": {"id": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "metafield_customers",
    "action": "context_store_search",
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
| `id` | `integer` | Unique identifier for the metafield |
| `namespace` | `string` | Namespace group for the metafield |
| `key` | `string` | Key of the metafield within its namespace |
| `value` | `string` | Serialized value stored in the metafield |
| `type` | `string` | Shopify metafield type (e.g. `single_line_text_field`, `json`) |
| `description` | `string` | Human-readable description of the metafield |
| `owner_id` | `integer` | Identifier of the resource that owns this metafield |
| `owner_resource` | `string` | Resource type that owns this metafield (e.g. `product`, `customer`) |
| `created_at` | `string` | ISO 8601 timestamp when the metafield was created |
| `updated_at` | `string` | ISO 8601 timestamp when the metafield was last updated |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].id` | `integer` | Unique identifier for the metafield |
| `data[].namespace` | `string` | Namespace group for the metafield |
| `data[].key` | `string` | Key of the metafield within its namespace |
| `data[].value` | `string` | Serialized value stored in the metafield |
| `data[].type` | `string` | Shopify metafield type (e.g. `single_line_text_field`, `json`) |
| `data[].description` | `string` | Human-readable description of the metafield |
| `data[].owner_id` | `integer` | Identifier of the resource that owns this metafield |
| `data[].owner_resource` | `string` | Resource type that owns this metafield (e.g. `product`, `customer`) |
| `data[].created_at` | `string` | ISO 8601 timestamp when the metafield was created |
| `data[].updated_at` | `string` | ISO 8601 timestamp when the metafield was last updated |

</details>

## Metafield Products

### Metafield Products List

Returns a list of metafields for a product

#### Python SDK

```python
await shopify.metafield_products.list(
    product_id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "metafield_products",
    "action": "list",
    "params": {
        "product_id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `product_id` | `integer` | Yes | The product ID |
| `limit` | `integer` | No | Maximum number of results to return (max 250) |
| `since_id` | `integer` | No | Restrict results to after the specified ID |
| `namespace` | `string` | No | Filter by namespace |
| `key` | `string` | No | Filter by key |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `namespace` | `string \| null` |  |
| `key` | `string \| null` |  |
| `value` | `string \| integer \| boolean \| null` |  |
| `type` | `string \| null` |  |
| `description` | `string \| null` |  |
| `owner_id` | `integer \| null` |  |
| `created_at` | `string \| null` |  |
| `updated_at` | `string \| null` |  |
| `owner_resource` | `string \| null` |  |
| `admin_graphql_api_id` | `string \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page_url` | `string` |  |

</details>

### Metafield Products Context Store Search

Search and filter metafield products records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await shopify.metafield_products.context_store_search(
    query={"filter": {"eq": {"id": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "metafield_products",
    "action": "context_store_search",
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
| `id` | `integer` | Unique identifier for the metafield |
| `namespace` | `string` | Namespace group for the metafield |
| `key` | `string` | Key of the metafield within its namespace |
| `value` | `string` | Serialized value stored in the metafield |
| `type` | `string` | Shopify metafield type (e.g. `single_line_text_field`, `json`) |
| `description` | `string` | Human-readable description of the metafield |
| `owner_id` | `integer` | Identifier of the resource that owns this metafield |
| `owner_resource` | `string` | Resource type that owns this metafield (e.g. `product`, `customer`) |
| `created_at` | `string` | ISO 8601 timestamp when the metafield was created |
| `updated_at` | `string` | ISO 8601 timestamp when the metafield was last updated |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].id` | `integer` | Unique identifier for the metafield |
| `data[].namespace` | `string` | Namespace group for the metafield |
| `data[].key` | `string` | Key of the metafield within its namespace |
| `data[].value` | `string` | Serialized value stored in the metafield |
| `data[].type` | `string` | Shopify metafield type (e.g. `single_line_text_field`, `json`) |
| `data[].description` | `string` | Human-readable description of the metafield |
| `data[].owner_id` | `integer` | Identifier of the resource that owns this metafield |
| `data[].owner_resource` | `string` | Resource type that owns this metafield (e.g. `product`, `customer`) |
| `data[].created_at` | `string` | ISO 8601 timestamp when the metafield was created |
| `data[].updated_at` | `string` | ISO 8601 timestamp when the metafield was last updated |

</details>

## Metafield Orders

### Metafield Orders List

Returns a list of metafields for an order

#### Python SDK

```python
await shopify.metafield_orders.list(
    order_id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "metafield_orders",
    "action": "list",
    "params": {
        "order_id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `order_id` | `integer` | Yes | The order ID |
| `limit` | `integer` | No | Maximum number of results to return (max 250) |
| `since_id` | `integer` | No | Restrict results to after the specified ID |
| `namespace` | `string` | No | Filter by namespace |
| `key` | `string` | No | Filter by key |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `namespace` | `string \| null` |  |
| `key` | `string \| null` |  |
| `value` | `string \| integer \| boolean \| null` |  |
| `type` | `string \| null` |  |
| `description` | `string \| null` |  |
| `owner_id` | `integer \| null` |  |
| `created_at` | `string \| null` |  |
| `updated_at` | `string \| null` |  |
| `owner_resource` | `string \| null` |  |
| `admin_graphql_api_id` | `string \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page_url` | `string` |  |

</details>

### Metafield Orders Context Store Search

Search and filter metafield orders records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await shopify.metafield_orders.context_store_search(
    query={"filter": {"eq": {"id": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "metafield_orders",
    "action": "context_store_search",
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
| `id` | `integer` | Unique identifier for the metafield |
| `namespace` | `string` | Namespace group for the metafield |
| `key` | `string` | Key of the metafield within its namespace |
| `value` | `string` | Serialized value stored in the metafield |
| `type` | `string` | Shopify metafield type (e.g. `single_line_text_field`, `json`) |
| `description` | `string` | Human-readable description of the metafield |
| `owner_id` | `integer` | Identifier of the resource that owns this metafield |
| `owner_resource` | `string` | Resource type that owns this metafield (e.g. `product`, `customer`) |
| `created_at` | `string` | ISO 8601 timestamp when the metafield was created |
| `updated_at` | `string` | ISO 8601 timestamp when the metafield was last updated |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].id` | `integer` | Unique identifier for the metafield |
| `data[].namespace` | `string` | Namespace group for the metafield |
| `data[].key` | `string` | Key of the metafield within its namespace |
| `data[].value` | `string` | Serialized value stored in the metafield |
| `data[].type` | `string` | Shopify metafield type (e.g. `single_line_text_field`, `json`) |
| `data[].description` | `string` | Human-readable description of the metafield |
| `data[].owner_id` | `integer` | Identifier of the resource that owns this metafield |
| `data[].owner_resource` | `string` | Resource type that owns this metafield (e.g. `product`, `customer`) |
| `data[].created_at` | `string` | ISO 8601 timestamp when the metafield was created |
| `data[].updated_at` | `string` | ISO 8601 timestamp when the metafield was last updated |

</details>

## Metafield Draft Orders

### Metafield Draft Orders List

Returns a list of metafields for a draft order

#### Python SDK

```python
await shopify.metafield_draft_orders.list(
    draft_order_id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "metafield_draft_orders",
    "action": "list",
    "params": {
        "draft_order_id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `draft_order_id` | `integer` | Yes | The draft order ID |
| `limit` | `integer` | No | Maximum number of results to return (max 250) |
| `since_id` | `integer` | No | Restrict results to after the specified ID |
| `namespace` | `string` | No | Filter by namespace |
| `key` | `string` | No | Filter by key |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `namespace` | `string \| null` |  |
| `key` | `string \| null` |  |
| `value` | `string \| integer \| boolean \| null` |  |
| `type` | `string \| null` |  |
| `description` | `string \| null` |  |
| `owner_id` | `integer \| null` |  |
| `created_at` | `string \| null` |  |
| `updated_at` | `string \| null` |  |
| `owner_resource` | `string \| null` |  |
| `admin_graphql_api_id` | `string \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page_url` | `string` |  |

</details>

### Metafield Draft Orders Context Store Search

Search and filter metafield draft orders records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await shopify.metafield_draft_orders.context_store_search(
    query={"filter": {"eq": {"id": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "metafield_draft_orders",
    "action": "context_store_search",
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
| `id` | `integer` | Unique identifier for the metafield |
| `namespace` | `string` | Namespace group for the metafield |
| `key` | `string` | Key of the metafield within its namespace |
| `value` | `string` | Serialized value stored in the metafield |
| `type` | `string` | Shopify metafield type (e.g. `single_line_text_field`, `json`) |
| `description` | `string` | Human-readable description of the metafield |
| `owner_id` | `integer` | Identifier of the resource that owns this metafield |
| `owner_resource` | `string` | Resource type that owns this metafield (e.g. `product`, `customer`) |
| `created_at` | `string` | ISO 8601 timestamp when the metafield was created |
| `updated_at` | `string` | ISO 8601 timestamp when the metafield was last updated |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].id` | `integer` | Unique identifier for the metafield |
| `data[].namespace` | `string` | Namespace group for the metafield |
| `data[].key` | `string` | Key of the metafield within its namespace |
| `data[].value` | `string` | Serialized value stored in the metafield |
| `data[].type` | `string` | Shopify metafield type (e.g. `single_line_text_field`, `json`) |
| `data[].description` | `string` | Human-readable description of the metafield |
| `data[].owner_id` | `integer` | Identifier of the resource that owns this metafield |
| `data[].owner_resource` | `string` | Resource type that owns this metafield (e.g. `product`, `customer`) |
| `data[].created_at` | `string` | ISO 8601 timestamp when the metafield was created |
| `data[].updated_at` | `string` | ISO 8601 timestamp when the metafield was last updated |

</details>

## Metafield Locations

### Metafield Locations List

Returns a list of metafields for a location

#### Python SDK

```python
await shopify.metafield_locations.list(
    location_id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "metafield_locations",
    "action": "list",
    "params": {
        "location_id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `location_id` | `integer` | Yes | The location ID |
| `limit` | `integer` | No | Maximum number of results to return (max 250) |
| `since_id` | `integer` | No | Restrict results to after the specified ID |
| `namespace` | `string` | No | Filter by namespace |
| `key` | `string` | No | Filter by key |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `namespace` | `string \| null` |  |
| `key` | `string \| null` |  |
| `value` | `string \| integer \| boolean \| null` |  |
| `type` | `string \| null` |  |
| `description` | `string \| null` |  |
| `owner_id` | `integer \| null` |  |
| `created_at` | `string \| null` |  |
| `updated_at` | `string \| null` |  |
| `owner_resource` | `string \| null` |  |
| `admin_graphql_api_id` | `string \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page_url` | `string` |  |

</details>

### Metafield Locations Context Store Search

Search and filter metafield locations records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await shopify.metafield_locations.context_store_search(
    query={"filter": {"eq": {"id": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "metafield_locations",
    "action": "context_store_search",
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
| `id` | `integer` | Unique identifier for the metafield |
| `namespace` | `string` | Namespace group for the metafield |
| `key` | `string` | Key of the metafield within its namespace |
| `value` | `string` | Serialized value stored in the metafield |
| `type` | `string` | Shopify metafield type (e.g. `single_line_text_field`, `json`) |
| `description` | `string` | Human-readable description of the metafield |
| `owner_id` | `integer` | Identifier of the resource that owns this metafield |
| `owner_resource` | `string` | Resource type that owns this metafield (e.g. `product`, `customer`) |
| `created_at` | `string` | ISO 8601 timestamp when the metafield was created |
| `updated_at` | `string` | ISO 8601 timestamp when the metafield was last updated |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].id` | `integer` | Unique identifier for the metafield |
| `data[].namespace` | `string` | Namespace group for the metafield |
| `data[].key` | `string` | Key of the metafield within its namespace |
| `data[].value` | `string` | Serialized value stored in the metafield |
| `data[].type` | `string` | Shopify metafield type (e.g. `single_line_text_field`, `json`) |
| `data[].description` | `string` | Human-readable description of the metafield |
| `data[].owner_id` | `integer` | Identifier of the resource that owns this metafield |
| `data[].owner_resource` | `string` | Resource type that owns this metafield (e.g. `product`, `customer`) |
| `data[].created_at` | `string` | ISO 8601 timestamp when the metafield was created |
| `data[].updated_at` | `string` | ISO 8601 timestamp when the metafield was last updated |

</details>

## Metafield Product Variants

### Metafield Product Variants List

Returns a list of metafields for a product variant

#### Python SDK

```python
await shopify.metafield_product_variants.list(
    variant_id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "metafield_product_variants",
    "action": "list",
    "params": {
        "variant_id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `variant_id` | `integer` | Yes | The variant ID |
| `limit` | `integer` | No | Maximum number of results to return (max 250) |
| `since_id` | `integer` | No | Restrict results to after the specified ID |
| `namespace` | `string` | No | Filter by namespace |
| `key` | `string` | No | Filter by key |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `namespace` | `string \| null` |  |
| `key` | `string \| null` |  |
| `value` | `string \| integer \| boolean \| null` |  |
| `type` | `string \| null` |  |
| `description` | `string \| null` |  |
| `owner_id` | `integer \| null` |  |
| `created_at` | `string \| null` |  |
| `updated_at` | `string \| null` |  |
| `owner_resource` | `string \| null` |  |
| `admin_graphql_api_id` | `string \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page_url` | `string` |  |

</details>

### Metafield Product Variants Context Store Search

Search and filter metafield product variants records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await shopify.metafield_product_variants.context_store_search(
    query={"filter": {"eq": {"id": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "metafield_product_variants",
    "action": "context_store_search",
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
| `id` | `integer` | Unique identifier for the metafield |
| `namespace` | `string` | Namespace group for the metafield |
| `key` | `string` | Key of the metafield within its namespace |
| `value` | `string` | Serialized value stored in the metafield |
| `type` | `string` | Shopify metafield type (e.g. `single_line_text_field`, `json`) |
| `description` | `string` | Human-readable description of the metafield |
| `owner_id` | `integer` | Identifier of the resource that owns this metafield |
| `owner_resource` | `string` | Resource type that owns this metafield (e.g. `product`, `customer`) |
| `created_at` | `string` | ISO 8601 timestamp when the metafield was created |
| `updated_at` | `string` | ISO 8601 timestamp when the metafield was last updated |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].id` | `integer` | Unique identifier for the metafield |
| `data[].namespace` | `string` | Namespace group for the metafield |
| `data[].key` | `string` | Key of the metafield within its namespace |
| `data[].value` | `string` | Serialized value stored in the metafield |
| `data[].type` | `string` | Shopify metafield type (e.g. `single_line_text_field`, `json`) |
| `data[].description` | `string` | Human-readable description of the metafield |
| `data[].owner_id` | `integer` | Identifier of the resource that owns this metafield |
| `data[].owner_resource` | `string` | Resource type that owns this metafield (e.g. `product`, `customer`) |
| `data[].created_at` | `string` | ISO 8601 timestamp when the metafield was created |
| `data[].updated_at` | `string` | ISO 8601 timestamp when the metafield was last updated |

</details>

## Metafield Smart Collections

### Metafield Smart Collections List

Returns a list of metafields for a smart collection

#### Python SDK

```python
await shopify.metafield_smart_collections.list(
    collection_id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "metafield_smart_collections",
    "action": "list",
    "params": {
        "collection_id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `collection_id` | `integer` | Yes | The collection ID |
| `limit` | `integer` | No | Maximum number of results to return (max 250) |
| `since_id` | `integer` | No | Restrict results to after the specified ID |
| `namespace` | `string` | No | Filter by namespace |
| `key` | `string` | No | Filter by key |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `namespace` | `string \| null` |  |
| `key` | `string \| null` |  |
| `value` | `string \| integer \| boolean \| null` |  |
| `type` | `string \| null` |  |
| `description` | `string \| null` |  |
| `owner_id` | `integer \| null` |  |
| `created_at` | `string \| null` |  |
| `updated_at` | `string \| null` |  |
| `owner_resource` | `string \| null` |  |
| `admin_graphql_api_id` | `string \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page_url` | `string` |  |

</details>

### Metafield Smart Collections Context Store Search

Search and filter metafield smart collections records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await shopify.metafield_smart_collections.context_store_search(
    query={"filter": {"eq": {"id": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "metafield_smart_collections",
    "action": "context_store_search",
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
| `id` | `integer` | Unique identifier for the metafield |
| `namespace` | `string` | Namespace group for the metafield |
| `key` | `string` | Key of the metafield within its namespace |
| `value` | `string` | Serialized value stored in the metafield |
| `type` | `string` | Shopify metafield type (e.g. `single_line_text_field`, `json`) |
| `description` | `string` | Human-readable description of the metafield |
| `owner_id` | `integer` | Identifier of the resource that owns this metafield |
| `owner_resource` | `string` | Resource type that owns this metafield (e.g. `product`, `customer`) |
| `created_at` | `string` | ISO 8601 timestamp when the metafield was created |
| `updated_at` | `string` | ISO 8601 timestamp when the metafield was last updated |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].id` | `integer` | Unique identifier for the metafield |
| `data[].namespace` | `string` | Namespace group for the metafield |
| `data[].key` | `string` | Key of the metafield within its namespace |
| `data[].value` | `string` | Serialized value stored in the metafield |
| `data[].type` | `string` | Shopify metafield type (e.g. `single_line_text_field`, `json`) |
| `data[].description` | `string` | Human-readable description of the metafield |
| `data[].owner_id` | `integer` | Identifier of the resource that owns this metafield |
| `data[].owner_resource` | `string` | Resource type that owns this metafield (e.g. `product`, `customer`) |
| `data[].created_at` | `string` | ISO 8601 timestamp when the metafield was created |
| `data[].updated_at` | `string` | ISO 8601 timestamp when the metafield was last updated |

</details>

## Metafield Product Images

### Metafield Product Images List

Returns a list of metafields for a product image

#### Python SDK

```python
await shopify.metafield_product_images.list(
    product_id=0,
    image_id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "metafield_product_images",
    "action": "list",
    "params": {
        "product_id": 0,
        "image_id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `product_id` | `integer` | Yes | The product ID |
| `image_id` | `integer` | Yes | The image ID |
| `limit` | `integer` | No | Maximum number of results to return (max 250) |
| `since_id` | `integer` | No | Restrict results to after the specified ID |
| `namespace` | `string` | No | Filter by namespace |
| `key` | `string` | No | Filter by key |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `namespace` | `string \| null` |  |
| `key` | `string \| null` |  |
| `value` | `string \| integer \| boolean \| null` |  |
| `type` | `string \| null` |  |
| `description` | `string \| null` |  |
| `owner_id` | `integer \| null` |  |
| `created_at` | `string \| null` |  |
| `updated_at` | `string \| null` |  |
| `owner_resource` | `string \| null` |  |
| `admin_graphql_api_id` | `string \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page_url` | `string` |  |

</details>

### Metafield Product Images Context Store Search

Search and filter metafield product images records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await shopify.metafield_product_images.context_store_search(
    query={"filter": {"eq": {"id": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "metafield_product_images",
    "action": "context_store_search",
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
| `id` | `integer` | Unique identifier for the metafield |
| `namespace` | `string` | Namespace group for the metafield |
| `key` | `string` | Key of the metafield within its namespace |
| `value` | `string` | Serialized value stored in the metafield |
| `type` | `string` | Shopify metafield type (e.g. `single_line_text_field`, `json`) |
| `description` | `string` | Human-readable description of the metafield |
| `owner_id` | `integer` | Identifier of the resource that owns this metafield |
| `owner_resource` | `string` | Resource type that owns this metafield (e.g. `product`, `customer`) |
| `created_at` | `string` | ISO 8601 timestamp when the metafield was created |
| `updated_at` | `string` | ISO 8601 timestamp when the metafield was last updated |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].id` | `integer` | Unique identifier for the metafield |
| `data[].namespace` | `string` | Namespace group for the metafield |
| `data[].key` | `string` | Key of the metafield within its namespace |
| `data[].value` | `string` | Serialized value stored in the metafield |
| `data[].type` | `string` | Shopify metafield type (e.g. `single_line_text_field`, `json`) |
| `data[].description` | `string` | Human-readable description of the metafield |
| `data[].owner_id` | `integer` | Identifier of the resource that owns this metafield |
| `data[].owner_resource` | `string` | Resource type that owns this metafield (e.g. `product`, `customer`) |
| `data[].created_at` | `string` | ISO 8601 timestamp when the metafield was created |
| `data[].updated_at` | `string` | ISO 8601 timestamp when the metafield was last updated |

</details>

## Customer Address

### Customer Address List

Returns a list of addresses for a customer

#### Python SDK

```python
await shopify.customer_address.list(
    customer_id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "customer_address",
    "action": "list",
    "params": {
        "customer_id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `customer_id` | `integer` | Yes | The customer ID |
| `limit` | `integer` | No | Maximum number of results to return (max 250) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `customer_id` | `integer \| null` |  |
| `first_name` | `string \| null` |  |
| `last_name` | `string \| null` |  |
| `company` | `string \| null` |  |
| `address1` | `string \| null` |  |
| `address2` | `string \| null` |  |
| `city` | `string \| null` |  |
| `province` | `string \| null` |  |
| `country` | `string \| null` |  |
| `zip` | `string \| null` |  |
| `phone` | `string \| null` |  |
| `name` | `string \| null` |  |
| `province_code` | `string \| null` |  |
| `country_code` | `string \| null` |  |
| `country_name` | `string \| null` |  |
| `default` | `boolean \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page_url` | `string` |  |

</details>

### Customer Address Get

Retrieves a single customer address by ID

#### Python SDK

```python
await shopify.customer_address.get(
    customer_id=0,
    address_id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "customer_address",
    "action": "get",
    "params": {
        "customer_id": 0,
        "address_id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `customer_id` | `integer` | Yes | The customer ID |
| `address_id` | `integer` | Yes | The address ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `customer_id` | `integer \| null` |  |
| `first_name` | `string \| null` |  |
| `last_name` | `string \| null` |  |
| `company` | `string \| null` |  |
| `address1` | `string \| null` |  |
| `address2` | `string \| null` |  |
| `city` | `string \| null` |  |
| `province` | `string \| null` |  |
| `country` | `string \| null` |  |
| `zip` | `string \| null` |  |
| `phone` | `string \| null` |  |
| `name` | `string \| null` |  |
| `province_code` | `string \| null` |  |
| `country_code` | `string \| null` |  |
| `country_name` | `string \| null` |  |
| `default` | `boolean \| null` |  |


</details>

## Fulfillment Orders

### Fulfillment Orders List

Returns a list of fulfillment orders for a specific order

#### Python SDK

```python
await shopify.fulfillment_orders.list(
    order_id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "fulfillment_orders",
    "action": "list",
    "params": {
        "order_id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `order_id` | `integer` | Yes | The order ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `shop_id` | `integer \| null` |  |
| `order_id` | `integer \| null` |  |
| `assigned_location_id` | `integer \| null` |  |
| `request_status` | `string \| null` |  |
| `status` | `string \| null` |  |
| `supported_actions` | `array \| null` |  |
| `destination` | `object \| null` |  |
| `line_items` | `array \| null` |  |
| `fulfill_at` | `string \| null` |  |
| `fulfill_by` | `string \| null` |  |
| `international_duties` | `object \| null` |  |
| `fulfillment_holds` | `array \| null` |  |
| `delivery_method` | `object \| null` |  |
| `assigned_location` | `object \| null` |  |
| `merchant_requests` | `array \| null` |  |
| `created_at` | `string \| null` |  |
| `updated_at` | `string \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page_url` | `string` |  |

</details>

### Fulfillment Orders Get

Retrieves a single fulfillment order by ID

#### Python SDK

```python
await shopify.fulfillment_orders.get(
    fulfillment_order_id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "fulfillment_orders",
    "action": "get",
    "params": {
        "fulfillment_order_id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `fulfillment_order_id` | `integer` | Yes | The fulfillment order ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `shop_id` | `integer \| null` |  |
| `order_id` | `integer \| null` |  |
| `assigned_location_id` | `integer \| null` |  |
| `request_status` | `string \| null` |  |
| `status` | `string \| null` |  |
| `supported_actions` | `array \| null` |  |
| `destination` | `object \| null` |  |
| `line_items` | `array \| null` |  |
| `fulfill_at` | `string \| null` |  |
| `fulfill_by` | `string \| null` |  |
| `international_duties` | `object \| null` |  |
| `fulfillment_holds` | `array \| null` |  |
| `delivery_method` | `object \| null` |  |
| `assigned_location` | `object \| null` |  |
| `merchant_requests` | `array \| null` |  |
| `created_at` | `string \| null` |  |
| `updated_at` | `string \| null` |  |


</details>

### Fulfillment Orders Context Store Search

Search and filter fulfillment orders records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await shopify.fulfillment_orders.context_store_search(
    query={"filter": {"eq": {"id": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "fulfillment_orders",
    "action": "context_store_search",
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
| `id` | `integer` | Unique identifier for the fulfillment order |
| `order_id` | `integer` | Identifier of the parent order |
| `shop_id` | `integer` | Identifier of the shop that owns the fulfillment order |
| `assigned_location_id` | `integer` | Identifier of the location assigned to fulfill the order |
| `status` | `string` | Fulfillment order status (e.g. `open`, `in_progress`, `closed`) |
| `request_status` | `string` | Status of the fulfillment request (e.g. `unsubmitted`, `submitted`) |
| `created_at` | `string` | ISO 8601 timestamp when the fulfillment order was created |
| `updated_at` | `string` | ISO 8601 timestamp when the fulfillment order was last updated |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].id` | `integer` | Unique identifier for the fulfillment order |
| `data[].order_id` | `integer` | Identifier of the parent order |
| `data[].shop_id` | `integer` | Identifier of the shop that owns the fulfillment order |
| `data[].assigned_location_id` | `integer` | Identifier of the location assigned to fulfill the order |
| `data[].status` | `string` | Fulfillment order status (e.g. `open`, `in_progress`, `closed`) |
| `data[].request_status` | `string` | Status of the fulfillment request (e.g. `unsubmitted`, `submitted`) |
| `data[].created_at` | `string` | ISO 8601 timestamp when the fulfillment order was created |
| `data[].updated_at` | `string` | ISO 8601 timestamp when the fulfillment order was last updated |

</details>

