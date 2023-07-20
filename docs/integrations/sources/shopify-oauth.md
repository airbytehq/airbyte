---
description: >-
  Shopify is a proprietary e-commerce platform for online stores and retail point-of-sale systems.
---

# Shopify

:::note

Our Shopify Source Connector does not support OAuth at this time due to limitations outside of our control. If OAuth for Shopify is critical to your business, [please reach out to us](mailto:product@airbyte.io) to discuss how we may be able to partner on this effort.

:::

## Getting started

This connector supports the `OAuth2.0` only athentication method.

### Connect using `OAuth2.0`

1. Click `Authenticate your Shopify account` to start the autentication.
2. Click `Add App` to install Airbyte application.
3. Log in to your account, if not already.
4. Select the store youu want to sync and review the consent.
5. Click on `Install` to finish the Installation.
6. Reveiew the `Shop Name` field for the chosen store for a sync.
7. Set the `Start Date` as the starting point for your data replication.
8. Click `Test and Save` to finish the source set up.
6. You're ready to set up Shopify in Airbyte!

### Scopes Required for Custom App

Add the following scopes to your custom app to ensure Airbyte can sync all available data. To see a list of streams this source supports, see our full [Shopify documentation](https://docs.airbyte.com/integrations/sources/shopify/).

- `read_analytics`
- `read_assigned_fulfillment_orders`
- `read_gdpr_data_request`
- `read_locations`
- `read_price_rules`
- `read_product_listings`
- `read_products`
- `read_reports`
- `read_resource_feedbacks`
- `read_script_tags`
- `read_shipping`
- `read_locales`
- `read_shopify_payments_accounts`
- `read_shopify_payments_bank_accounts`
- `read_shopify_payments_disputes`
- `read_shopify_payments_payouts`
- `read_content`
- `read_themes`
- `read_third_party_fulfillment_orders`
- `read_translations`
- `read_customers`
- `read_discounts`
- `read_draft_orders`
- `read_fulfillments`
- `read_gift_cards`
- `read_inventory`
- `read_legal_policies`
- `read_marketing_events`
- `read_merchant_managed_fulfillment_orders`
- `read_online_store_pages`
- `read_order_edits`
- `read_orders`

## Supported sync modes

The Shopify source supports both Full Refresh and Incremental syncs. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

This source can sync data for the [Shopify REST API](https://shopify.dev/api/admin-rest) and the [Shopify GraphQl API](https://shopify.dev/api/admin-graphql).

## Troubleshooting tips

Check out common troubleshooting issues for the Shopify source connector on our Airbyte Forum [here](https://github.com/airbytehq/airbyte/discussions).

## Supported Streams

This Source is capable of syncing the following core Streams:

- [Articles](https://shopify.dev/api/admin-rest/2022-01/resources/article)
- [Blogs](https://shopify.dev/api/admin-rest/2022-01/resources/blog)
- [Abandoned Checkouts](https://shopify.dev/api/admin-rest/2022-01/resources/abandoned-checkouts#top)
- [Collects](https://shopify.dev/api/admin-rest/2022-01/resources/collect#top)
- [Collections](https://shopify.dev/api/admin-rest/2022-01/resources/collection)
- [Countries](https://shopify.dev/docs/api/admin-rest/2023-04/resources/country)
- [Custom Collections](https://shopify.dev/api/admin-rest/2022-01/resources/customcollection#top)
- [CustomerAddress](https://shopify.dev/docs/api/admin-rest/2023-04/resources/customer-address)
- [CustomerSavedSearch](https://shopify.dev/docs/api/admin-rest/2023-04/resources/customersavedsearch)
- [Smart Collections](https://shopify.dev/api/admin-rest/2022-01/resources/smartcollection)
- [Customers](https://shopify.dev/api/admin-rest/2022-01/resources/customer#top)
- [Draft Orders](https://shopify.dev/api/admin-rest/2022-01/resources/draftorder#top)
- [Discount Codes](https://shopify.dev/api/admin-rest/2022-01/resources/discountcode#top)
- [Metafields](https://shopify.dev/api/admin-rest/2022-01/resources/metafield#top)
- [Orders](https://shopify.dev/api/admin-rest/2022-01/resources/order#top)
- [Orders Refunds](https://shopify.dev/api/admin-rest/2022-01/resources/refund#top)
- [Orders Risks](https://shopify.dev/api/admin-rest/2022-01/resources/order-risk#top)
- [Products](https://shopify.dev/api/admin-rest/2022-01/resources/product#top)
- [Products (GraphQL)](https://shopify.dev/api/admin-graphql/2022-10/queries/products)
- [Product Images](https://shopify.dev/api/admin-rest/2022-01/resources/product-image)
- [Product Variants](https://shopify.dev/api/admin-rest/2022-01/resources/product-variant)
- [Transactions](https://shopify.dev/api/admin-rest/2022-01/resources/transaction#top)
- [Tender Transactions](https://shopify.dev/api/admin-rest/2022-01/resources/tendertransaction)
- [Pages](https://shopify.dev/api/admin-rest/2022-01/resources/page#top)
- [Price Rules](https://shopify.dev/api/admin-rest/2022-01/resources/pricerule#top)
- [Locations](https://shopify.dev/api/admin-rest/2022-01/resources/location)
- [InventoryItems](https://shopify.dev/api/admin-rest/2022-01/resources/inventoryItem)
- [InventoryLevels](https://shopify.dev/api/admin-rest/2021-01/resources/inventorylevel)
- [Fulfillment Orders](https://shopify.dev/api/admin-rest/2022-01/resources/fulfillmentorder)
- [Fulfillments](https://shopify.dev/api/admin-rest/2022-01/resources/fulfillment)
- [Shop](https://shopify.dev/api/admin-rest/2022-01/resources/shop)

### Stream sync recommendations

For better experience with `Incremental Refresh` the following is recommended:

- `Order Refunds`, `Order Risks`, `Transactions` should be synced along with `Orders` stream.
- `Discount Codes` should be synced along with `Price Rules` stream.

If child streams are synced alone from the parent stream - the full sync will take place, and the records are filtered out afterwards.

## Data type mapping

| Integration Type | Airbyte Type |
| :--------------- | :----------- |
| `string`         | `string`     |
| `number`         | `number`     |
| `array`          | `array`      |
| `object`         | `object`     |
| `boolean`        | `boolean`    |

## Features

| Feature                   | Supported?\(Yes/No\) |
| :------------------------ | :------------------- |
| Full Refresh Sync         | Yes                  |
| Incremental - Append Sync | Yes                  |
| Namespaces                | No                   |

## Performance considerations

Shopify has some [rate limit restrictions](https://shopify.dev/concepts/about-apis/rate-limits). Typically, there should not be issues with throttling or exceeding the rate limits but in some edge cases, user can receive the warning message as follows:

```text
"Caught retryable error '<some_error> or null' after <some_number> tries. Waiting <some_number> seconds then retrying..."
```

This is expected when the connector hits the 429 - Rate Limit Exceeded HTTP Error. With given error message the sync operation is still goes on, but will require more time to finish.

## Changelog

| Version | Date       | Pull Request                                             | Subject                                                                                                                         |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------ |
| 0.1.0   | 2023-07-20 | [28507](https://github.com/airbytehq/airbyte/pull/28507) | Initial OAuth version connector release |
