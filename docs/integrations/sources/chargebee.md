# Chargebee

<HideInUI>

This page contains the setup guide and reference information for the Chargebee source connector.

</HideInUI>

## Prerequisites

To set up the Chargebee source connector, you will need:
 - [Chargebee API key](https://apidocs.chargebee.com/docs/api/auth)
 - [Product Catalog version](https://www.chargebee.com/docs/1.0/upgrade-product-catalog.html) of the Chargebee site you are syncing.

:::info
All Chargebee sites created from May 5, 2021 onward will have [Product Catalog 2.0](https://www.chargebee.com/docs/2.0/product-catalog.html) enabled by default. Sites created prior to this date will use [Product Catalog 1.0](https://www.chargebee.com/docs/1.0/product-catalog.html).
:::

## Set up the Chargebee connector in Airbyte

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account or navigate to the Airbyte Open Source dashboard.
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select **Chargebee** from the Source type dropdown.
4. Enter the name for the Chargebee connector.
5. For **Site**, enter the site prefix for your Chargebee instance.
6. For **Start Date**, enter the date in YYYY-MM-DDTHH:mm:ssZ format. The data added on and after this date will be replicated.
7. For **API Key**, enter the [Chargebee API key](https://apidocs.chargebee.com/docs/api?prod_cat_ver=2#api_authentication).
8. For **Product Catalog**, enter the Chargebee [Product Catalog version](https://apidocs.chargebee.com/docs/api?prod_cat_ver=2). Connector defaults to Product Catalog 2.0 unless otherwise specified.
9. Click **Set up source**.

<HideInUI>

## Supported sync modes

The Chargebee source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

* [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
* [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
* [Incremental - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)
* [Incremental - Append + Deduped](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append-deduped)

## Supported streams

Most streams are supported regardless of your Chargebee site's [Product Catalog version](https://www.chargebee.com/docs/1.0/upgrade-product-catalog.html), with a few version-specific exceptions.

| Stream                                                                                                 | Product Catalog 1.0 | Product Catalog 2.0 |
| ------------------------------------------------------------------------------------------------------ | ------------------- | ------------------- |
| [Addons](https://apidocs.chargebee.com/docs/api/addons?prod_cat_ver=1)                                 | ✔                   |                     |
| [Attached Items](https://apidocs.chargebee.com/docs/api/attached_items?prod_cat_ver=2)                 |                     | ✔                   |
| [Comments](https://apidocs.chargebee.com/docs/api/comments?prod_cat_ver=2)                             | ✔                   | ✔                   |
| [Contacts](https://apidocs.chargebee.com/docs/api/customers?lang=curl#list_of_contacts_for_a_customer) | ✔                   | ✔                   |
| [Coupons](https://apidocs.chargebee.com/docs/api/coupons)                                              | ✔                   | ✔                   |
| [Credit Notes](https://apidocs.chargebee.com/docs/api/credit_notes)                                    | ✔                   | ✔                   |
| [Customers](https://apidocs.chargebee.com/docs/api/customers)                                          | ✔                   | ✔                   |
| [Differential Prices](https://apidocs.chargebee.com/docs/api/differential_prices)                      | ✔                   | ✔                   |
| [Events](https://apidocs.chargebee.com/docs/api/events)                                                | ✔                   | ✔                   |
| [Gifts](https://apidocs.chargebee.com/docs/api/gifts)                                                  | ✔                   | ✔                   |
| [Hosted Pages](https://apidocs.chargebee.com/docs/api/hosted_pages)                                    | ✔                   | ✔                   |
| [Invoices](https://apidocs.chargebee.com/docs/api/invoices)                                            | ✔                   | ✔                   |
| [Items](https://apidocs.chargebee.com/docs/api/items?prod_cat_ver=2)                                   |                     | ✔                   |
| [Item Prices](https://apidocs.chargebee.com/docs/api/item_prices?prod_cat_ver=2)                       |                     | ✔                   |
| [Item Families](https://apidocs.chargebee.com/docs/api/item_families?prod_cat_ver=2)                   |                     | ✔                   |
| [Orders](https://apidocs.chargebee.com/docs/api/orders)                                                | ✔                   | ✔                   |
| [Payment Sources](https://apidocs.chargebee.com/docs/api/payment_sources)                              | ✔                   | ✔                   |
| [Plans](https://apidocs.chargebee.com/docs/api/plans?prod_cat_ver=1)                                   | ✔                   |                     |
| [Promotional Credits](https://apidocs.chargebee.com/docs/api/promotional_credits)                      | ✔                   | ✔                   |
| [Quotes](https://apidocs.chargebee.com/docs/api/quotes)                                                | ✔                   | ✔                   |
| [Quote Line Groups](https://apidocs.chargebee.com/docs/api/quote_line_groups)                          | ✔                   | ✔                   |
| [Site Migration Details](https://apidocs.chargebee.com/docs/api/site_migration_details)                | ✔                   | ✔                   |
| [Subscriptions](https://apidocs.chargebee.com/docs/api/subscriptions)                                  | ✔                   | ✔                   |
| [Transactions](https://apidocs.chargebee.com/docs/api/transactions)                                    | ✔                   | ✔                   |
| [Unbilled Charges](https://apidocs.chargebee.com/docs/api/unbilled_charges)                            | ✔                   | ✔                   |
| [Virtual Bank Accounts](https://apidocs.chargebee.com/docs/api/virtual_bank_accounts)                  | ✔                   | ✔                   |

:::note
When using incremental sync mode, the `Attached Items` stream behaves differently than the other streams. Whereas other incremental streams read and output _only new_ records, the `Attached Items` stream reads _all_ records but only outputs _new_ records, making it more demanding on your Chargebee API quota. Each sync incurs API calls equal to the total number of attached items in your Chargebee instance divided by 100, regardless of the actual number of `Attached Items` changed or synced.
:::

## Limitations & Troubleshooting

<details>
<summary>
Expand to see details about the Chargebee connector limitations and troubleshooting.
</summary>

### Connector limitations

#### Rate limiting

The Chargebee connector should not run into [Chargebee API](https://apidocs.chargebee.com/docs/api?prod_cat_ver=2#api_rate_limits) limitations under normal usage. [Create an issue](https://github.com/airbytehq/airbyte/issues) if you encounter any rate limit issues that are not automatically retried successfully.

### Troubleshooting

* Check out common troubleshooting issues for the Instagram source connector on our [Airbyte Forum](https://github.com/airbytehq/airbyte/discussions).

</details>

## Changelog

| Version | Date       | Pull Request                                             | Subject                                                                                             |
| :------ | :--------- | :------------------------------------------------------- | :-------------------------------------------------------------------------------------------------- |
| 0.4.1   | 2024-03-03 | [35509](https://github.com/airbytehq/airbyte/pull/35509) | Updates CDK version to latest (0.67.1), updates `site_migration_detail` record filtering                                                   |
| 0.4.0   | 2024-02-12 | [34053](https://github.com/airbytehq/airbyte/pull/34053) | Add missing fields to and cleans up schemas, adds incremental support for `gift`, `site_migration_detail`, and `unbilled_charge` streams.` |
| 0.3.1   | 2024-02-12 | [35169](https://github.com/airbytehq/airbyte/pull/35169) | Manage dependencies with Poetry.                                                                    |
| 0.3.0   | 2023-12-26 | [33696](https://github.com/airbytehq/airbyte/pull/33696) | Add new stream, add fields to existing streams                                                      |
| 0.2.6   | 2023-12-19 | [32100](https://github.com/airbytehq/airbyte/pull/32100) | Add new fields in streams                                                                           |
| 0.2.5   | 2023-10-19 | [31599](https://github.com/airbytehq/airbyte/pull/31599) | Base image migration: remove Dockerfile and use the python-connector-base image                     |
| 0.2.4   | 2023-08-01 | [28905](https://github.com/airbytehq/airbyte/pull/28905) | Updated the connector to use latest CDK version                                                     |
| 0.2.3   | 2023-03-22 | [24370](https://github.com/airbytehq/airbyte/pull/24370) | Ignore 404 errors for `Contact` stream                                                              |
| 0.2.2   | 2023-02-17 | [21688](https://github.com/airbytehq/airbyte/pull/21688) | Migrate to CDK beta 0.29; fix schemas                                                               |
| 0.2.1   | 2023-02-17 | [23207](https://github.com/airbytehq/airbyte/pull/23207) | Edited stream schemas to get rid of unnecessary `enum`                                              |
| 0.2.0   | 2023-01-21 | [21688](https://github.com/airbytehq/airbyte/pull/21688) | Migrate to YAML; add new streams                                                                    |
| 0.1.16  | 2022-10-06 | [17661](https://github.com/airbytehq/airbyte/pull/17661) | Make `transaction` stream to be consistent with `S3` by using type transformer                      |
| 0.1.15  | 2022-09-28 | [17304](https://github.com/airbytehq/airbyte/pull/17304) | Migrate to per-stream state.                                                                        |
| 0.1.14  | 2022-09-23 | [17056](https://github.com/airbytehq/airbyte/pull/17056) | Add "custom fields" to the relevant Chargebee source data streams                                   |
| 0.1.13  | 2022-08-18 | [15743](https://github.com/airbytehq/airbyte/pull/15743) | Fix transaction `exchange_rate` field type                                                          |
| 0.1.12  | 2022-07-13 | [14672](https://github.com/airbytehq/airbyte/pull/14672) | Fix transaction sort by                                                                             |
| 0.1.11  | 2022-03-03 | [10827](https://github.com/airbytehq/airbyte/pull/10827) | Fix Credit Note stream                                                                              |
| 0.1.10  | 2022-03-02 | [10795](https://github.com/airbytehq/airbyte/pull/10795) | Add support for Credit Note stream                                                                  |
| 0.1.9   | 2022-0224  | [10312](https://github.com/airbytehq/airbyte/pull/10312) | Add support for Transaction Stream                                                                  |
| 0.1.8   | 2022-02-22 | [10366](https://github.com/airbytehq/airbyte/pull/10366) | Fix broken `coupon` stream + add unit tests                                                         |
| 0.1.7   | 2022-02-14 | [10269](https://github.com/airbytehq/airbyte/pull/10269) | Add support for Coupon stream                                                                       |
| 0.1.6   | 2022-02-10 | [10143](https://github.com/airbytehq/airbyte/pull/10143) | Add support for Event stream                                                                        |
| 0.1.5   | 2021-12-23 | [8434](https://github.com/airbytehq/airbyte/pull/8434)   | Update fields in source-connectors specifications                                                   |
| 0.1.4   | 2021-09-27 | [6454](https://github.com/airbytehq/airbyte/pull/6454)   | Fix examples in spec file                                                                           |
| 0.1.3   | 2021-08-17 | [5421](https://github.com/airbytehq/airbyte/pull/5421)   | Add support for "Product Catalog 2.0" specific streams: `Items`, `Item prices` and `Attached Items` |
| 0.1.2   | 2021-07-30 | [5067](https://github.com/airbytehq/airbyte/pull/5067)   | Prepare connector for publishing                                                                    |
| 0.1.1   | 2021-07-07 | [4539](https://github.com/airbytehq/airbyte/pull/4539)   | Add entrypoint and bump version for connector                                                       |
| 0.1.0   | 2021-06-30 | [3410](https://github.com/airbytehq/airbyte/pull/3410)   | New Source: Chargebee                                                                               |

</HideInUI>
