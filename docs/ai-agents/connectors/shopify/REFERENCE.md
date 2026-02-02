# Shopify full reference

This is the full reference documentation for the Shopify agent connector.

## Supported entities and actions

The Shopify connector supports the following entities and actions.

| Entity | Actions |
|--------|---------|
| Customers | [List](#customers-list), [Get](#customers-get) |
| Orders | [List](#orders-list), [Get](#orders-get) |
| Products | [List](#products-list), [Get](#products-get) |
| Product Variants | [List](#product-variants-list), [Get](#product-variants-get) |
| Product Images | [List](#product-images-list), [Get](#product-images-get) |
| Abandoned Checkouts | [List](#abandoned-checkouts-list) |
| Locations | [List](#locations-list), [Get](#locations-get) |
| Inventory Levels | [List](#inventory-levels-list) |
| Inventory Items | [List](#inventory-items-list), [Get](#inventory-items-get) |
| Shop | [Get](#shop-get) |
| Price Rules | [List](#price-rules-list), [Get](#price-rules-get) |
| Discount Codes | [List](#discount-codes-list), [Get](#discount-codes-get) |
| Custom Collections | [List](#custom-collections-list), [Get](#custom-collections-get) |
| Smart Collections | [List](#smart-collections-list), [Get](#smart-collections-get) |
| Collects | [List](#collects-list), [Get](#collects-get) |
| Draft Orders | [List](#draft-orders-list), [Get](#draft-orders-get) |
| Fulfillments | [List](#fulfillments-list), [Get](#fulfillments-get) |
| Order Refunds | [List](#order-refunds-list), [Get](#order-refunds-get) |
| Transactions | [List](#transactions-list), [Get](#transactions-get) |
| Tender Transactions | [List](#tender-transactions-list) |
| Countries | [List](#countries-list), [Get](#countries-get) |
| Metafield Shops | [List](#metafield-shops-list), [Get](#metafield-shops-get) |
| Metafield Customers | [List](#metafield-customers-list) |
| Metafield Products | [List](#metafield-products-list) |
| Metafield Orders | [List](#metafield-orders-list) |
| Metafield Draft Orders | [List](#metafield-draft-orders-list) |
| Metafield Locations | [List](#metafield-locations-list) |
| Metafield Product Variants | [List](#metafield-product-variants-list) |
| Metafield Smart Collections | [List](#metafield-smart-collections-list) |
| Metafield Product Images | [List](#metafield-product-images-list) |
| Customer Address | [List](#customer-address-list), [Get](#customer-address-get) |
| Fulfillment Orders | [List](#fulfillment-orders-list), [Get](#fulfillment-orders-get) |

## Customers

### Customers List

Returns a list of customers from the store

#### Python SDK

```python
await shopify.customers.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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

## Orders

### Orders List

Returns a list of orders from the store

#### Python SDK

```python
await shopify.orders.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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

## Abandoned Checkouts

### Abandoned Checkouts List

Returns a list of abandoned checkouts

#### Python SDK

```python
await shopify.abandoned_checkouts.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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

## Locations

### Locations List

Returns a list of locations for the store

#### Python SDK

```python
await shopify.locations.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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

## Shop

### Shop Get

Retrieves the shop's configuration

#### Python SDK

```python
await shopify.shop.get()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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

## Price Rules

### Price Rules List

Returns a list of price rules

#### Python SDK

```python
await shopify.price_rules.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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

## Custom Collections

### Custom Collections List

Returns a list of custom collections

#### Python SDK

```python
await shopify.custom_collections.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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

## Smart Collections

### Smart Collections List

Returns a list of smart collections

#### Python SDK

```python
await shopify.smart_collections.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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

## Collects

### Collects List

Returns a list of collects (links between products and collections)

#### Python SDK

```python
await shopify.collects.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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

## Draft Orders

### Draft Orders List

Returns a list of draft orders

#### Python SDK

```python
await shopify.draft_orders.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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

## Countries

### Countries List

Returns a list of countries

#### Python SDK

```python
await shopify.countries.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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

## Metafield Shops

### Metafield Shops List

Returns a list of metafields for the shop

#### Python SDK

```python
await shopify.metafield_shops.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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

