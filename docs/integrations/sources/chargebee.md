# Chargebee

This page contains the setup guide and reference information for the Chargebee source connector.

## Prerequisites

This Chargebee source uses the [Chargebee Python Client Library](https://github.com/chargebee/chargebee-python/).

## Setup guide
### Step 1: Set up Chargebee

Log into Chargebee and then generate an [API Key](https://apidocs.chargebee.com/docs/api?prod_cat_ver=2#api_authentication). 
Then follow [these](https://apidocs.chargebee.com/docs/api?prod_cat_ver=2) instructions, under `API Version` section, on how to find your Product Catalog version.

## Step 2: Set up the Chargebee connector in Airbyte

### For Airbyte Cloud:
1. [Log into your Airbyte Cloud](https://cloud.airbyte.io/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+new source**.
3. On the Set up the source page, enter the name for the Harvest connector and select **Chargebee** from the Source type dropdown. 
4. Set the name for your source 
5. Enter your `site_api_key`
6. Enter your `site` 
7. Enter your `product_catalog` 
8. Enter the `start_date` you want your sync to start from
9. Click **Set up source**

### For Airbyte OSS:
1. Navigate to the Airbyte Open Source dashboard
2. Set the name for your source 
3. Enter your `site_api_key`
4. Enter your `site` 
5. Enter your `product_catalog` 
6. Enter the `start_date` you want your sync to start from
7. Click **Set up source**

## Supported sync modes

The Chargebee source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental - Append Sync | Yes |
| Replicate Incremental Deletes | No |
| SSL connection | Yes |
| Namespaces | No |

## Supported Streams

* [Subscriptions](https://apidocs.chargebee.com/docs/api/subscriptions?prod_cat_ver=2#list_subscriptions)
* [Customers](https://apidocs.chargebee.com/docs/api/customers?prod_cat_ver=2#list_customers)
* [Invoices](https://apidocs.chargebee.com/docs/api/invoices?prod_cat_ver=2#list_invoices)
* [Orders](https://apidocs.chargebee.com/docs/api/orders?prod_cat_ver=2#list_orders)
* [Plans](https://apidocs.chargebee.com/docs/api/plans?prod_cat_ver=1&lang=curl#list_plans)
* [Addons](https://apidocs.chargebee.com/docs/api/addons?prod_cat_ver=1&lang=curl#list_addons)
* [Items](https://apidocs.chargebee.com/docs/api/items?prod_cat_ver=2#list_items)
* [Item Prices](https://apidocs.chargebee.com/docs/api/item_prices?prod_cat_ver=2#list_item_prices)
* [Attached Items](https://apidocs.chargebee.com/docs/api/attached_items?prod_cat_ver=2#list_attached_items)

## Performance considerations

The Chargebee connector should not run into [Chargebee API](https://apidocs.chargebee.com/docs/api?prod_cat_ver=2#api_rate_limits) limitations under normal usage. 
Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Tutorials

Some streams may depend on Product Catalog version and be accessible only on sites with specific Product Catalog version. This means that we have following streams:

1. presented in both `Product Catalog 1.0` and `Product Catalog 2.0`:
   * Customers
   * Events
   * Invoices
   * Credit Notes
   * Orders
   * Coupons
   * Subscriptions
   * Transactions
2. presented only in `Product Catalog 1.0`:
   * Plans
   * Addons
3. presented only in `Product Catalog 2.0`:
   * Items
   * Item Prices
   * Attached Items

Also, 12 streams from the above 13 incremental streams are pure incremental meaning that they:

* read only new records;
* output only new records.

`Attached Items` incremental stream is also incremental but with one difference, it:

* read all records;
* output only new records.

This means that syncing the `Attached Items` stream, even in incremental mode, is expensive in terms of your Chargebee API quota. 
Generally speaking, it incurs a number of API calls equal to the total number of attached items in your chargebee instance divided by 100, 
regardless of how many AttachedItems were actually changed or synced in a particular sync job.

## Changelog

| Version | Date | Pull Request | Subject |
| :--- | :--- | :--- | :--- |
| 0.1.13 | 2022-08-18 | [15743](https://github.com/airbytehq/airbyte/pull/15743) | Fix transaction `exchange_rate` field type |
| 0.1.12 | 2022-07-13 | [14672](https://github.com/airbytehq/airbyte/pull/14672) | Fix transaction sort by |
| 0.1.11 | 2022-03-03 | [10827](https://github.com/airbytehq/airbyte/pull/10827) | Fix Credit Note stream |
| 0.1.10 | 2022-03-02 | [10795](https://github.com/airbytehq/airbyte/pull/10795) | Add support for Credit Note stream |
| 0.1.9 | 2022-0224  | [10312](https://github.com/airbytehq/airbyte/pull/10312) | Add support for Transaction Stream |
| 0.1.8 | 2022-02-22 | [10366](https://github.com/airbytehq/airbyte/pull/10366) | Fix broken `coupon` stream + add unit tests |
| 0.1.7 | 2022-02-14 | [10269](https://github.com/airbytehq/airbyte/pull/10269) | Add support for Coupon stream |
| 0.1.6 | 2022-02-10 | [10143](https://github.com/airbytehq/airbyte/pull/10143) | Add support for Event stream |
| 0.1.5 | 2021-12-23 | [8434](https://github.com/airbytehq/airbyte/pull/8434) | Update fields in source-connectors specifications |
| 0.1.4 | 2021-09-27 | [6454](https://github.com/airbytehq/airbyte/pull/6454) | Fix examples in spec file |
| 0.1.3 | 2021-08-17 | [5421](https://github.com/airbytehq/airbyte/pull/5421) | Add support for "Product Catalog 2.0" specific streams: `Items`, `Item prices` and `Attached Items` |
| 0.1.2 | 2021-07-30 | [5067](https://github.com/airbytehq/airbyte/pull/5067) | Prepare connector for publishing |
| 0.1.1 | 2021-07-07 | [4539](https://github.com/airbytehq/airbyte/pull/4539) | Add entrypoint and bump version for connector |
| 0.1.0 | 2021-06-30 | [3410](https://github.com/airbytehq/airbyte/pull/3410) | New Source: Chargebee |

