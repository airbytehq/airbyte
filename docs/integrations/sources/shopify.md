---
description: >-
  Shopify is a proprietary e-commerce platform for online stores and retail point-of-sale systems.
---

# Shopify


:::note

Our Shopify Source Connector does not support OAuth at this time due to limitations outside of our control. If OAuth for Shopify is critical to your business, [please reach out to us](mailto:product@airbyte.io) to discuss how we may be able to partner on this effort.

:::

## Sync overview

The Shopify source supports both Full Refresh and Incremental syncs. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

This source can sync data for the [Shopify REST API](https://shopify.dev/api/admin-rest) and the [Shopify GraphQl API](https://shopify.dev/api/admin-graphql).

## Troubleshooting

Check out common troubleshooting issues for the Shopify source connector on our Discourse [here](https://discuss.airbyte.io/tags/c/connector/11/source-shopify).

### Output schema

This Source is capable of syncing the following core Streams:

* [Abandoned Checkouts](https://help.shopify.com/en/api/reference/orders/abandoned_checkouts)
* [Collects](https://help.shopify.com/en/api/reference/products/collect)
* [Custom Collections](https://help.shopify.com/en/api/reference/products/customcollection)
* [Customers](https://help.shopify.com/en/api/reference/customers)
* [Draft Orders](https://help.shopify.com/en/api/reference/orders/draftorder)
* [Discount Codes](https://shopify.dev/docs/admin-api/rest/reference/discounts/discountcode)
* [Metafields](https://help.shopify.com/en/api/reference/metafield)
* [Orders](https://help.shopify.com/en/api/reference/order)
* [Orders Refunds](https://shopify.dev/api/admin/rest/reference/orders/refund)
* [Orders Risks](https://shopify.dev/api/admin/rest/reference/orders/order-risk)
* [Products](https://help.shopify.com/en/api/reference/products)
* [Products (GraphQL)](https://shopify.dev/api/admin-graphql/2022-10/queries/products)
* [Transactions](https://help.shopify.com/en/api/reference/orders/transaction)
* [Balance Transactions](https://shopify.dev/api/admin-rest/2021-07/resources/transactions)
* [Pages](https://help.shopify.com/en/api/reference/online-store/page)
* [Price Rules](https://help.shopify.com/en/api/reference/discounts/pricerule)
* [Locations](https://shopify.dev/api/admin-rest/2021-10/resources/location)
* [InventoryItems](https://shopify.dev/api/admin-rest/2021-10/resources/inventoryItem)
* [InventoryLevels](https://shopify.dev/api/admin-rest/2021-10/resources/inventorylevel)
* [Fulfillment Orders](https://shopify.dev/api/admin-rest/2021-07/resources/fulfillmentorder)
* [Fulfillments](https://shopify.dev/api/admin-rest/2021-07/resources/fulfillment)
* [Shop](https://shopify.dev/api/admin-rest/2021-07/resources/shop)

#### NOTE

For better experience with `Incremental Refresh` the following is recommended:

* `Order Refunds`, `Order Risks`, `Transactions` should be synced along with `Orders` stream.
* `Discount Codes` should be synced along with `Price Rules` stream.

If child streams are synced alone from the parent stream - the full sync will take place, and the records are filtered out afterwards.

### Data type mapping

| Integration Type | Airbyte Type |
| :--- | :--- |
| `string` | `string` |
| `number` | `number` |
| `array` | `array` |
| `object` | `object` |
| `boolean` | `boolean` |

### Features

| Feature | Supported?\(Yes/No\) |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental - Append Sync | Yes |
| Namespaces | No |

## Getting started

This connector support both: `OAuth 2.0` and `API PASSWORD` (for private applications) athentication methods.

### Connect using `API PASSWORD` option

1. Go to `https://YOURSTORE.myshopify.com/admin/apps/private`
2. Enable private development if it isn't enabled.
3. Create a private application.
4. Select the resources you want to allow access to. Airbyte only needs read-level access.
   * Note: The UI will show all possible data sources and will show errors when syncing if it doesn't have permissions to access a resource.
5. The password under the `Admin API` section is what you'll use as the `API PASSWORD` for the integration.
6. You're ready to set up Shopify in Airbyte!

### Output Streams Schemas

This Source is capable of syncing the following core Streams:

* [Articles](https://shopify.dev/api/admin-rest/2022-01/resources/article)
* [Blogs](https://shopify.dev/api/admin-rest/2022-01/resources/blog)
* [Abandoned Checkouts](https://shopify.dev/api/admin-rest/2022-01/resources/abandoned-checkouts#top)
* [Collects](https://shopify.dev/api/admin-rest/2022-01/resources/collect#top)
* [Collections](https://shopify.dev/api/admin-rest/2022-01/resources/collection)
* [Custom Collections](https://shopify.dev/api/admin-rest/2022-01/resources/customcollection#top)
* [Smart Collections](https://shopify.dev/api/admin-rest/2022-01/resources/smartcollection)
* [Customers](https://shopify.dev/api/admin-rest/2022-01/resources/customer#top)
* [Draft Orders](https://shopify.dev/api/admin-rest/2022-01/resources/draftorder#top)
* [Discount Codes](https://shopify.dev/api/admin-rest/2022-01/resources/discountcode#top)
* [Metafields](https://shopify.dev/api/admin-rest/2022-01/resources/metafield#top)
* [Orders](https://shopify.dev/api/admin-rest/2022-01/resources/order#top)
* [Orders Refunds](https://shopify.dev/api/admin-rest/2022-01/resources/refund#top)
* [Orders Risks](https://shopify.dev/api/admin-rest/2022-01/resources/order-risk#top)
* [Products](https://shopify.dev/api/admin-rest/2022-01/resources/product#top)
* [Products (GraphQL)](https://shopify.dev/api/admin-graphql/2022-10/queries/products)
* [Product Images](https://shopify.dev/api/admin-rest/2022-01/resources/product-image)
* [Product Variants](https://shopify.dev/api/admin-rest/2022-01/resources/product-variant)
* [Transactions](https://shopify.dev/api/admin-rest/2022-01/resources/transaction#top)
* [Tender Transactions](https://shopify.dev/api/admin-rest/2022-01/resources/tendertransaction)
* [Pages](https://shopify.dev/api/admin-rest/2022-01/resources/page#top)
* [Price Rules](https://shopify.dev/api/admin-rest/2022-01/resources/pricerule#top)
* [Locations](https://shopify.dev/api/admin-rest/2022-01/resources/location)
* [InventoryItems](https://shopify.dev/api/admin-rest/2022-01/resources/inventoryItem)
* [InventoryLevels](https://shopify.dev/api/admin-rest/2021-01/resources/inventorylevel)
* [Fulfillment Orders](https://shopify.dev/api/admin-rest/2022-01/resources/fulfillmentorder)
* [Fulfillments](https://shopify.dev/api/admin-rest/2022-01/resources/fulfillment)
* [Shop](https://shopify.dev/api/admin-rest/2022-01/resources/shop)

#### Notes

For better experience with `Incremental Refresh` the following is recommended:

* `Order Refunds`, `Order Risks`, `Transactions` should be synced along with `Orders` stream.
* `Discount Codes` should be synced along with `Price Rules` stream.

If child streams are synced alone from the parent stream - the full sync will take place, and the records are filtered out afterwards.

### Performance considerations

Shopify has some [rate limit restrictions](https://shopify.dev/concepts/about-apis/rate-limits). Typically, there should not be issues with throttling or exceeding the rate limits but in some edge cases, user can receive the warning message as follows:

```text
"Caught retryable error '<some_error> or null' after <some_number> tries. Waiting <some_number> seconds then retrying..."
```

This is expected when the connector hits the 429 - Rate Limit Exceeded HTTP Error. With given error message the sync operation is still goes on, but will require more time to finish.

## Changelog

| Version | Date       | Pull Request                                              | Subject                                                                                                   |
|:--------|:-----------|:----------------------------------------------------------|:----------------------------------------------------------------------------------------------------------|
| 0.3.3   | 2023-04-12 | [25110](https://github.com/airbytehq/airbyte/pull/25110)  | Fix issue when `cursor_field` is `"None"`, added missing properties to stream schemas, fixed `access_scopes` validation error                                                           |
| 0.3.2   | 2023-02-27 | [23473](https://github.com/airbytehq/airbyte/pull/23473)  | Fixed OOM / Memory leak issue for Airbyte Cloud                                                           |
| 0.3.1   | 2023-01-16 | [21461](https://github.com/airbytehq/airbyte/pull/21461)  | Add `discount_applications` to `orders` stream                                                            |
| 0.3.0   | 2022-11-16 | [19492](https://github.com/airbytehq/airbyte/pull/19492)  | Add support for graphql and add a graphql products stream                                                 |
| 0.2.0   | 2022-10-21 | [18298](https://github.com/airbytehq/airbyte/pull/18298)  | Updated API version to the `2022-10`, make stream schemas backward cpmpatible                             |
| 0.1.39  | 2022-10-13 | [17962](https://github.com/airbytehq/airbyte/pull/17962)  | Add metafield streams; support for nested list streams                                                    |
| 0.1.38  | 2022-10-10 | [17777](https://github.com/airbytehq/airbyte/pull/17777)  | Fixed `404` for configured streams, fix missing `cursor` error for old records                            |
| 0.1.37  | 2022-04-30 | [12500](https://github.com/airbytehq/airbyte/pull/12500)  | Improve input configuration copy                                                                          |
| 0.1.36  | 2022-03-22 | [9850](https://github.com/airbytehq/airbyte/pull/9850)    | Added `BalanceTransactions` stream                                                                        |
| 0.1.35  | 2022-03-07 | [10915](https://github.com/airbytehq/airbyte/pull/10915)  | Fix a bug which caused `full-refresh` syncs of child REST entities configured for `incremental`           |
| 0.1.34  | 2022-03-02 | [10794](https://github.com/airbytehq/airbyte/pull/10794)  | Minor specification re-order, fixed links in documentation                                                |
| 0.1.33  | 2022-02-17 | [10419](https://github.com/airbytehq/airbyte/pull/10419)  | Fixed wrong field type for tax_exemptions for `Abandoned_checkouts` stream                                |
| 0.1.32  | 2022-02-18 | [10449](https://github.com/airbytehq/airbyte/pull/10449)  | Added `tender_transactions` stream                                                                        |
| 0.1.31  | 2022-02-08 | [10175](https://github.com/airbytehq/airbyte/pull/10175)  | Fixed compatibility issues for legacy user config                                                         |
| 0.1.30  | 2022-01-24 | [9648](https://github.com/airbytehq/airbyte/pull/9648)    | Added permission validation before sync                                                                   |
| 0.1.29  | 2022-01-20 | [9049](https://github.com/airbytehq/airbyte/pull/9248)    | Added `shop_url` to the record for all streams                                                            |
| 0.1.28  | 2022-01-19 | [9591](https://github.com/airbytehq/airbyte/pull/9591)    | Implemented `OAuth2.0` authentication method for Airbyte Cloud                                            |
| 0.1.27  | 2021-12-22 | [9049](https://github.com/airbytehq/airbyte/pull/9049)    | Update connector fields title/description                                                                 |
| 0.1.26  | 2021-12-14 | [8597](https://github.com/airbytehq/airbyte/pull/8597)    | Fix `mismatched number of tables` for base-normalization, increased performance of `order_refunds` stream |
| 0.1.25  | 2021-12-02 | [8297](https://github.com/airbytehq/airbyte/pull/8297)    | Added Shop stream                                                                                         |
| 0.1.24  | 2021-11-30 | [7783](https://github.com/airbytehq/airbyte/pull/7783)    | Reviewed and corrected schemas for all streams                                                            |
| 0.1.23  | 2021-11-15 | [7973](https://github.com/airbytehq/airbyte/pull/7973)    | Added `InventoryItems`                                                                                    |
| 0.1.22  | 2021-10-18 | [7101](https://github.com/airbytehq/airbyte/pull/7107)    | Added FulfillmentOrders, Fulfillments streams                                                             |
| 0.1.21  | 2021-10-14 | [7382](https://github.com/airbytehq/airbyte/pull/7382)    | Fixed `InventoryLevels` primary key                                                                       |
| 0.1.20  | 2021-10-14 | [7063](https://github.com/airbytehq/airbyte/pull/7063)    | Added `Location` and `InventoryLevels` as streams                                                         |
| 0.1.19  | 2021-10-11 | [6951](https://github.com/airbytehq/airbyte/pull/6951)    | Added support of `OAuth 2.0` authorisation option                                                         |
| 0.1.18  | 2021-09-21 | [6056](https://github.com/airbytehq/airbyte/pull/6056)    | Added `pre_tax_price` to the `orders/line_items` schema                                                   |
| 0.1.17  | 2021-09-17 | [5244](https://github.com/airbytehq/airbyte/pull/5244)    | Created data type enforcer for converting prices into numbers                                             |
| 0.1.16  | 2021-09-09 | [5965](https://github.com/airbytehq/airbyte/pull/5945)    | Fixed the connector's performance for `Incremental refresh`                                               |
| 0.1.15  | 2021-09-02 | [5853](https://github.com/airbytehq/airbyte/pull/5853)    | Fixed `amount` type in `order_refund` schema                                                              |
| 0.1.14  | 2021-09-02 | [5801](https://github.com/airbytehq/airbyte/pull/5801)    | Fixed `line_items/discount allocations` & `duties` parts of `orders` schema                               |
| 0.1.13  | 2021-08-17 | [5470](https://github.com/airbytehq/airbyte/pull/5470)    | Fixed rate limits throttling                                                                              |
| 0.1.12  | 2021-08-09 | [5276](https://github.com/airbytehq/airbyte/pull/5276)    | Add status property to product schema                                                                     |
| 0.1.11  | 2021-07-23 | [4943](https://github.com/airbytehq/airbyte/pull/4943)    | Fix products schema up to API 2021-07                                                                     |
| 0.1.10  | 2021-07-19 | [4830](https://github.com/airbytehq/airbyte/pull/4830)    | Fix for streams json schemas, upgrade to API version 2021-07                                              |
| 0.1.9   | 2021-07-04 | [4472](https://github.com/airbytehq/airbyte/pull/4472)    | Incremental sync is now using updated\_at instead of since\_id by default                                 |
| 0.1.8   | 2021-06-29 | [4121](https://github.com/airbytehq/airbyte/pull/4121)    | Add draft orders stream                                                                                   |
| 0.1.7   | 2021-06-26 | [4290](https://github.com/airbytehq/airbyte/pull/4290)    | Fixed the bug when limiting output records to 1 caused infinity loop                                      |
| 0.1.6   | 2021-06-24 | [4009](https://github.com/airbytehq/airbyte/pull/4009)    | Add pages, price rules and discount codes streams                                                         |
| 0.1.5   | 2021-06-10 | [3973](https://github.com/airbytehq/airbyte/pull/3973)    | Add `AIRBYTE_ENTRYPOINT` for Kubernetes support                                                           |
| 0.1.4   | 2021-06-09 | [3926](https://github.com/airbytehq/airbyte/pull/3926)    | New attributes to Orders schema                                                                           |
| 0.1.3   | 2021-06-08 | [3787](https://github.com/airbytehq/airbyte/pull/3787)    | Add Native Shopify Source Connector                                                                       |
