# Shopify Migration Guide

## Upgrading to 3.0.0

This version contains schema changes for the following streams:

### Countries
Due to API deprecation of [Admin REST endpoint](https://shopify.dev/docs/api/admin-rest/2024-04/resources/country) Countries stream now uses [Admin GrapthQl to retrieve all countries](https://shopify.dev/docs/api/admin-graphql/latest/queries/deliveryProfiles).

**Important**: now stream requires `read_shipping` access scope. The source returns list of available streams according to existing scopes.
To obtain the scope follow this steps:
If you are using **OAuth2.0** authorization method, you need to Re-authenticate the source on Settings page to fetch new scope. 
If you are using **API password** authorization method, ensure that your custom app have `read_shipping` access scope, if not add the scope and Re-authenticate the source on Settings page.

Fields **removed** from schema:
* `country.tax`
* `country.tax_name`
* `country.provinces[].tax`
* `country.provinces[].tax_name`
* `country.provinces[].tax_type`
* `country.provinces[].tax_percentage`

Fields **added** to schema:
* `country.translated_name`
* `country.rest_of_world`
* `country.provinces[].translated_name`

### Product Variants

Fields **removed** from schema:
* `product_variant.fulfillment_service` - API v2025-01 doesn't return this info as part product variant data as of now. Please contact us if you're interested in this info, data can be replaced by [Fulfillment Service](https://shopify.dev/docs/api/admin-graphql/latest/queries/fulfillmentservice) stream.
* `product_variant.inventory_management` - The fulfillment service that tracks the number of items in stock for the product variant. Use `inventoryItem.tracked` instead.

Fields **added** to schema:
* `product_variant.tracked`

### Orders

Fields **added** to schema:
* `order.duties_included`
* `order.merchant_business_entity_id`
* `order.total_cash_rounding_payment_adjustment_set`

### Articles, Blogs and Pages

Due to API version upgrade `admin_graphql_api_id` now contains `gid://shopify/OnlineStore<StreamEntity>/<ID>`(Updated naming to reflect actual purpose) instead `gid://shopify/<StreamEntity>/<ID>`(Legacy naming from older Admin API).

**Important**: if you rely on `admin_graphql_api_id` field value in your destination, please clear affected streams and re-sync the data.

### Refresh affected schemas

1. Select **Connections** in the main navbar and select the connection(s) affected by the update.
2. Select the **Schema** tab.
   1. Select **Refresh source schema** to bring in any schema changes. Any detected schema changes will be listed for your review.
   2. Select **OK** to approve changes.
3. Select **Save changes** at the bottom of the page.
   1. Ensure the **Clear affected streams** option is checked to ensure your streams continue syncing successfully with the new schema.
4. Select **Save connection**.

### Steps to Clear Streams

To clear your data for the impacted streams, follow the steps below:

1. Select **Connections** in the main nav bar.
   1. Select the connection(s) affected by the update.
2. Select the **Status** tab.
   1. In the **Enabled streams** list, click the three dots on the right side of the stream and select **Clear Data**.

After the clear succeeds, trigger a sync by clicking **Sync Now**. For more information on clearing your data in Airbyte, see [this page](/platform/operator-guides/clear).

## Upgrading to 2.6.1

This version completely deprecates the following streams, because Shopify no longer supports them after Shopify API version `2024-04`:

- `Products Graph QL`
- `Customer Saved Search`

Please use `Products` to replace the old `Products Graph QL` stream.

## Upgrading to 2.2.0

This version updates the schema for countries as our testing caught that `provinces.tax_percentage` is a number and not an integer.

### Action items required for 2.2.0

- `Refresh Schema` + `Reset` is required for this stream after the upgrade from previous version.

## Upgrading to 2.1.0

This version implements `Shopify GraphQL BULK Operations` to speed up the following streams:

- `Products`
- `Product Images`
- `Product Variants`

* In the `Products` stream, the `published_scope` property is no longer available.
* In the `Products` stream, the `images` property now contains only the `id` of the image. Refer to the `Product Images` stream instead.
* In the `Products` stream, the `variants` property now contains only the `id` of the variant. Refer to the `Product Variants` stream instead.
* In the `Products` stream, the `position` property is no longer available.
* The `Product Variants` stream now has the cursor field `updated_at` instead of `id`.
* In the `Product Variants` stream, the date-time fields, such as `created_at` and `updated_at`, now use `UTC` format without a timezone component.
* In the `Product Variants` stream, the `presentment_prices.compare_at_price` property has changed from a `number` to an `object of strings`. This field was not populated in the `REST API` stream version, but it is correctly covered in the GraphQL stream version.
* The `Product Variants` stream's `inventory_policy` and `inventory_management` properties now contain `uppercase string` values, instead of `lowercase`.
* In the `Product Images` stream, the date-time fields, such as `created_at` and `updated_at`, now use `UTC` format without a timezone component.
* In the `Product Images` stream, the `variant_ids` and `position` properties are no longer available. Refer to the `Product variants` stream instead.
* Retrieving the `deleted` records for `Products`, `Product Images` and `Product Variants` streams are no longer available, due to the `GraphQL` limitations.

### Action items required for 2.1.0

- `Refresh Schema` + `Reset` is required for this stream after the upgrade from previous version.

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
