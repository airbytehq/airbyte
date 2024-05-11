# Shopify Migration Guide

## Upgrading to 2.0.0

This version implements `Shopify GraphQL BULK Operations` to speed up the following streams:

- `Collections`
- `Customer Address`
- `Discount Codes`
- `Fulfillment Orders`
- `Inventory Items`
- `Inventory Levels`
- `Metafield Collections`
- `Metafield Customers`
- `Metafield Draft_orders`
- `Metafield Locations`
- `Metafield Orders`
- `Metafield Product Images`
- `Metafield Product Variants`
- `Transactions Graphql` (duplicated `Transactions` stream to provide faster fetch)

Increased the performance for the following streams:

- `Fulfillments`
- `Order Refunds`
- `Product Images`
- `Product Variants`

Other bug fixes and improvements, more info: `https://github.com/airbytehq/airbyte/pull/32345`

### Action items required for 2.0.0

- The `Fulfillments` stream now has the cursor field `updated_at`, instead of the `id`.
- The `Order Refunds` stream, now has the schema `refund_line_items.line_item.properties` to array of `strings`, instead of `object` with properties.
- The `Fulfillment Orders` stream now has the `supported_actions` schema as `array of objects` instead of `array of strings`.
- The `Collections` stream now requires additional api scope `read_publications` to fetch the `published_at` field with `GraphQL BULK Operations`.

  - if `API_PASSWORD` is used for authentication:
    - BEFORE UPDATING to the `2.0.0`: update your `Private Developer Application` scopes with `read_publications` and save the changes, in your Shopify Account.
  - if `OAuth2.0` is used for authentication:
    - `re-auth` in order to obtain new scope automatically, after the upgrade.
  - `Refresh Schema` + `Reset` is required for these streams after the upgrade from previous version.

## Upgrading to 1.0.0

This version uses Shopify API version `2023-07` which brings changes to the following streams:

- removed `gateway, payment_details, processing_method` properties from `Order` stream, they are no longer supplied.
- added `company, confirmation_number, current_total_additional_fees_set, original_total_additional_fees_set, tax_exempt, po_number` properties to `Orders` stream
- added `total_unsettled_set, payment_id` to `Transactions` stream
- added `return` property to `Order Refund` stream
- added `created_at, updated_at` to `Fulfillment Order` stream

### Action items required for 1.0.0

- The `reset` and `full-refresh` for `Orders` stream is required after upgrading to this version.
