# Shopify

<HideInUI>

This page contains the setup guide and reference information for the [Shopify](https://www.shopify.com/) source connector.

</HideInUI>

## Prerequisites

* An active [Shopify store](https://www.shopify.com).
* If you are syncing data from a store that you do not own, you will need to [request access to your client's store](https://help.shopify.com/en/partners/dashboard/managing-stores/request-access#request-access) (not required for account owners).
<!-- env:oss  -->
* For **Airbyte Open Source** users: A custom Shopify application with [`read_` scopes enabled](#scopes-required-for-custom-app).
<!-- /env:oss -->

## Setup guide

This connector supports **OAuth2.0** and **API Password** (for private applications) authentication methods.

<!-- env:cloud -->
:::note
For existing **Airbyte Cloud** customers, if you are currently using the **API Password** authentication method, please switch to **OAuth2.0**, as the API Password will be deprecated shortly. This change will not affect **Airbyte Open Source** connections.
:::

### Airbyte Cloud

#### Connect using OAuth2.0

1. Select a **Source name**.
2. Click **Authenticate your Shopify account**.
3. Click **Install** to install the Airbyte application.
4. Log in to your account, if you are not already logged in.
5. Select the store you want to sync and review the consent form. Click **Install app** to finish the installation.
6. The **Shopify Store** field will be automatically filled based on the store you selected. Confirm the value is accurate.
7. (Optional) You may set a **Replication Start Date** as the starting point for your data replication. Any data created before this date will not be synced. Defaults to January 1st, 2020.
8. Click **Set up source** and wait for the connection test to complete.
<!-- /env:cloud -->

<!-- env:oss -->
### Airbyte Open Source

#### Create a custom app

Authentication to the Shopify API requires a [custom application](https://help.shopify.com/en/manual/apps/app-types/custom-apps). Follow these instructions to create a custom app and find your Admin API Access Token.

1. Log in to your Shopify account.
2. In the dashboard, navigate to **Settings** > **App and sales channels** > **Develop apps** > **Create an app**.
3. Select a name for your new app.
4. Select **Configure Admin API scopes**.
5. Grant access to the [following list of scopes](#scopes-required-for-custom-app). Only select scopes prefixed with `read_`, not `write_` (e.g. `read_locations`,`read_price_rules`, etc ).
6. Click **Install app** to give this app access to your data.
7. Once installed, go to **API Credentials** to copy the **Admin API Access Token**. You are now ready to set up the source in Airbyte!

#### Connect using API Password

1. Enter a **Source name**.
2. Enter your **Shopify Store** name. You can find this in your URL when logged in to Shopify or within the Store details section of your Settings.
3. For **API Password**, enter your custom application's Admin API access token.
4. (Optional) You may set a **Replication Start Date** as the starting point for your data replication. Any data created before this date will not be synced. Please note that this defaults to January 1st, 2020.
5. Click **Set up source** and wait for the connection test to complete.

### Custom app scopes

Add the following scopes to your custom app to ensure Airbyte can sync all available data. For more information on access scopes, see the [Shopify docs](https://shopify.dev/docs/api/usage/access-scopes).

* `read_analytics`
* `read_assigned_fulfillment_orders`
* `read_content`
* `read_customers`
* `read_discounts`
* `read_draft_orders`
* `read_fulfillments`
* `read_gdpr_data_request`
* `read_gift_cards`
* `read_inventory`
* `read_legal_policies`
* `read_locations`
* `read_locales`
* `read_marketing_events`
* `read_merchant_managed_fulfillment_orders`
* `read_online_store_pages`
* `read_order_edits`
* `read_orders`
* `read_price_rules`
* `read_product_listings`
* `read_products`
* `read_reports`
* `read_resource_feedbacks`
* `read_script_tags`
* `read_shipping`
* `read_shopify_payments_accounts`
* `read_shopify_payments_bank_accounts`
* `read_shopify_payments_disputes`
* `read_shopify_payments_payouts`
* `read_themes`
* `read_third_party_fulfillment_orders`
* `read_translations`

<!-- env:oss -->

<HideInUI>

## Supported sync modes

The Shopify source supports both Full Refresh and Incremental syncs. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

This source can sync data for the [Shopify REST API](https://shopify.dev/api/admin-rest) and the [Shopify GraphQl API](https://shopify.dev/api/admin-graphql).

## Supported streams

- [Abandoned Checkouts](https://shopify.dev/api/admin-rest/2022-01/resources/abandoned-checkouts#top)
- [Articles](https://shopify.dev/api/admin-rest/2022-01/resources/article)
- [Blogs](https://shopify.dev/api/admin-rest/2022-01/resources/blog)
- [Collects](https://shopify.dev/api/admin-rest/2022-01/resources/collect#top)
- [Collections](https://shopify.dev/api/admin-rest/2022-01/resources/collection)
- [Countries](https://shopify.dev/docs/api/admin-rest/2023-04/resources/country)
- [Custom Collections](https://shopify.dev/api/admin-rest/2022-01/resources/customcollection#top)
- [Customers](https://shopify.dev/api/admin-rest/2022-01/resources/customer#top)
- [Customer Address](https://shopify.dev/docs/api/admin-rest/2023-04/resources/customer-address)
- [Customer Saved Search](https://shopify.dev/docs/api/admin-rest/2023-04/resources/customersavedsearch)
- [Draft Orders](https://shopify.dev/api/admin-rest/2022-01/resources/draftorder#top)
- [Discount Codes](https://shopify.dev/api/admin-rest/2022-01/resources/discountcode#top)
- [Disputes](https://shopify.dev/docs/api/admin-rest/2023-07/resources/dispute)
- [Fulfillments](https://shopify.dev/api/admin-rest/2022-01/resources/fulfillment)
- [Fulfillment Orders](https://shopify.dev/api/admin-rest/2022-01/resources/fulfillmentorder)
- [Inventory Items](https://shopify.dev/api/admin-rest/2022-01/resources/inventoryItem)
- [Inventory Levels](https://shopify.dev/api/admin-rest/2021-01/resources/inventorylevel)
- [Locations](https://shopify.dev/api/admin-rest/2022-01/resources/location)
- [Metafields](https://shopify.dev/api/admin-rest/2022-01/resources/metafield#top)
- [Orders](https://shopify.dev/api/admin-rest/2022-01/resources/order#top)
- [Order Refunds](https://shopify.dev/api/admin-rest/2022-01/resources/refund#top)
- [Order Risks](https://shopify.dev/api/admin-rest/2022-01/resources/order-risk#top)
- [Pages](https://shopify.dev/api/admin-rest/2022-01/resources/page#top)
- [Price Rules](https://shopify.dev/api/admin-rest/2022-01/resources/pricerule#top)
- [Products](https://shopify.dev/api/admin-rest/2022-01/resources/product#top)
- [Products (GraphQL)](https://shopify.dev/api/admin-graphql/2022-10/queries/products)
- [Product Images](https://shopify.dev/api/admin-rest/2022-01/resources/product-image)
- [Product Variants](https://shopify.dev/api/admin-rest/2022-01/resources/product-variant)
- [Shop](https://shopify.dev/api/admin-rest/2022-01/resources/shop)
- [Smart Collections](https://shopify.dev/api/admin-rest/2022-01/resources/smartcollection)
- [Transactions](https://shopify.dev/api/admin-rest/2022-01/resources/transaction#top)
- [Tender Transactions](https://shopify.dev/api/admin-rest/2022-01/resources/tendertransaction)

## Capturing deleted records

The connector captures deletions for records in the `Articles`, `Blogs`, `CustomCollections`, `Orders`, `Pages`, `PriceRules` and `Products` streams.

When a record is deleted, the connector outputs a record with the `ID` of that record and the `deleted_at`, `deleted_message`, and `deleted_description` fields filled out. No other fields are filled out for the deleted records.

Check the following Shopify documentation for more information about [retrieving deleted records](https://shopify.dev/docs/api/admin-rest/2023-07/resources/event).

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

## Limitations & Troubleshooting

<details>
<summary>

Expand to see details about Shopify connector limitations and troubleshooting

</summary>

### Connector limitations

#### Rate limiting

Shopify has some [rate limit restrictions](https://shopify.dev/concepts/about-apis/rate-limits). Typically, there should not be issues with throttling or exceeding the rate limits but, in some edge cases, you may encounter the following warning message:

```text
"Caught retryable error '<some_error> or null' after <some_number> tries. 
Waiting <some_number> seconds then retrying..."
```

This is expected when the connector hits a `429 - Rate Limit Exceeded` HTTP Error. The sync operation will continue successfully after a short backoff period.

#### Incremental sync recommendations

For the smoothest experience with Incremental Refresh sync mode, the following is recommended:

- The `Order Refunds`, `Order Risks`, `Transactions` should be synced along with `Orders` stream.
- `Discount Codes` should be synced along with `Price Rules` stream.

If a child stream is synced independently of its parent stream, a full sync will occur, followed by a filtering out of records. This process may be less efficient compared to syncing child streams alongside their respective parent streams.

### Troubleshooting

* If you encounter access errors while using **OAuth2.0** authentication, please make sure you've followed this [Shopify Article](https://help.shopify.com/en/partners/dashboard/managing-stores/request-access#request-access) to request the access to the client's store first. Once the access is granted, you should be able to proceed with **OAuth2.0** authentication.
* Check out common troubleshooting issues for the Shopify source connector on our Airbyte Forum [here](https://github.com/airbytehq/airbyte/discussions).

</details>

## Changelog

| Version | Date       | Pull Request                                             | Subject                                                                                                                         |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------ |
| 1.1.4 | 2023-10-19 | [31599](https://github.com/airbytehq/airbyte/pull/31599) | Base image migration: remove Dockerfile and use the python-connector-base image |
| 1.1.3   | 2023-10-17 | [31500](https://github.com/airbytehq/airbyte/pull/31500) | Fixed the issue caused by the `missing access token` while setup the new source and not yet authenticated |
| 1.1.2   | 2023-10-13 | [31381](https://github.com/airbytehq/airbyte/pull/31381) | Fixed the issue caused by the `state` presence while fetching the `deleted events` with pagination |
| 1.1.1   | 2023-09-18 | [30560](https://github.com/airbytehq/airbyte/pull/30560) | Performance testing - include socat binary in docker image |
| 1.1.0   | 2023-09-07 | [30246](https://github.com/airbytehq/airbyte/pull/30246) | Added ability to fetch `destroyed` records for `Articles, Blogs, CustomCollections, Orders, Pages, PriceRules, Products` |
| 1.0.0   | 2023-08-11 | [29361](https://github.com/airbytehq/airbyte/pull/29361) | Migrate to the `2023-07` Shopify API Version  |
| 0.6.2   | 2023-08-09 | [29302](https://github.com/airbytehq/airbyte/pull/29302) | Handle the `Internal Server Error` when entity could be fetched                 |
| 0.6.1   | 2023-08-08 | [28291](https://github.com/airbytehq/airbyte/pull/28291) | Allow `shop` field to accept `*.myshopify.com` shop names, updated `OAuth Spec`                  |
| 0.6.0   | 2023-08-02 | [28770](https://github.com/airbytehq/airbyte/pull/28770) | Added `Disputes` stream  |
| 0.5.1   | 2023-07-13 | [28700](https://github.com/airbytehq/airbyte/pull/28700) | Improved `error messages` with more user-friendly description, refactored code  |
| 0.5.0   | 2023-06-13 | [27732](https://github.com/airbytehq/airbyte/pull/27732) | License Update: Elv2                                                                                                            |
| 0.4.0   | 2023-06-13 | [27083](https://github.com/airbytehq/airbyte/pull/27083) | Added `CustomerSavedSearch`, `CustomerAddress` and `Countries` streams                                                          |
| 0.3.4   | 2023-05-10 | [25961](https://github.com/airbytehq/airbyte/pull/25961) | Added validation for `shop` in input configuration (accepts non-url-like inputs)                                                |
| 0.3.3   | 2023-04-12 | [25110](https://github.com/airbytehq/airbyte/pull/25110) | Fixed issue when `cursor_field` is `"None"`, added missing properties to stream schemas, fixed `access_scopes` validation error |
| 0.3.2   | 2023-02-27 | [23473](https://github.com/airbytehq/airbyte/pull/23473) | Fixed OOM / Memory leak issue for Airbyte Cloud                                                                                 |
| 0.3.1   | 2023-01-16 | [21461](https://github.com/airbytehq/airbyte/pull/21461) | Added `discount_applications` to `orders` stream                                                                                |
| 0.3.0   | 2022-11-16 | [19492](https://github.com/airbytehq/airbyte/pull/19492) | Added support for graphql and add a graphql products stream                                                                     |
| 0.2.0   | 2022-10-21 | [18298](https://github.com/airbytehq/airbyte/pull/18298) | Updated API version to the `2022-10`, make stream schemas backward cpmpatible                                                   |
| 0.1.39  | 2022-10-13 | [17962](https://github.com/airbytehq/airbyte/pull/17962) | Added metafield streams; support for nested list streams                                                                        |
| 0.1.38  | 2022-10-10 | [17777](https://github.com/airbytehq/airbyte/pull/17777) | Fixed `404` for configured streams, fix missing `cursor` error for old records                                                  |
| 0.1.37  | 2022-04-30 | [12500](https://github.com/airbytehq/airbyte/pull/12500) | Improve input configuration copy                                                                                                |
| 0.1.36  | 2022-03-22 | [9850](https://github.com/airbytehq/airbyte/pull/9850)   | Added `BalanceTransactions` stream                                                                                              |
| 0.1.35  | 2022-03-07 | [10915](https://github.com/airbytehq/airbyte/pull/10915) | Fixed a bug which caused `full-refresh` syncs of child REST entities configured for `incremental`                               |
| 0.1.34  | 2022-03-02 | [10794](https://github.com/airbytehq/airbyte/pull/10794) | Minor specification re-order, fixed links in documentation                                                                      |
| 0.1.33  | 2022-02-17 | [10419](https://github.com/airbytehq/airbyte/pull/10419) | Fixed wrong field type for tax_exemptions for `Abandoned_checkouts` stream                                                      |
| 0.1.32  | 2022-02-18 | [10449](https://github.com/airbytehq/airbyte/pull/10449) | Added `tender_transactions` stream                                                                                              |
| 0.1.31  | 2022-02-08 | [10175](https://github.com/airbytehq/airbyte/pull/10175) | Fixed compatibility issues for legacy user config                                                                               |
| 0.1.30  | 2022-01-24 | [9648](https://github.com/airbytehq/airbyte/pull/9648)   | Added permission validation before sync                                                                                         |
| 0.1.29  | 2022-01-20 | [9049](https://github.com/airbytehq/airbyte/pull/9248)   | Added `shop_url` to the record for all streams                                                                                  |
| 0.1.28  | 2022-01-19 | [9591](https://github.com/airbytehq/airbyte/pull/9591)   | Implemented `OAuth2.0` authentication method for Airbyte Cloud                                                                  |
| 0.1.27  | 2021-12-22 | [9049](https://github.com/airbytehq/airbyte/pull/9049)   | Updated connector fields title/description                                                                                      |
| 0.1.26  | 2021-12-14 | [8597](https://github.com/airbytehq/airbyte/pull/8597)   | Fixed `mismatched number of tables` for base-normalization, increased performance of `order_refunds` stream                     |
| 0.1.25  | 2021-12-02 | [8297](https://github.com/airbytehq/airbyte/pull/8297)   | Added Shop stream                                                                                                               |
| 0.1.24  | 2021-11-30 | [7783](https://github.com/airbytehq/airbyte/pull/7783)   | Reviewed and corrected schemas for all streams                                                                                  |
| 0.1.23  | 2021-11-15 | [7973](https://github.com/airbytehq/airbyte/pull/7973)   | Added `InventoryItems`                                                                                                          |
| 0.1.22  | 2021-10-18 | [7101](https://github.com/airbytehq/airbyte/pull/7107)   | Added FulfillmentOrders, Fulfillments streams                                                                                   |
| 0.1.21  | 2021-10-14 | [7382](https://github.com/airbytehq/airbyte/pull/7382)   | Fixed `InventoryLevels` primary key                                                                                             |
| 0.1.20  | 2021-10-14 | [7063](https://github.com/airbytehq/airbyte/pull/7063)   | Added `Location` and `InventoryLevels` as streams                                                                               |
| 0.1.19  | 2021-10-11 | [6951](https://github.com/airbytehq/airbyte/pull/6951)   | Added support of `OAuth 2.0` authorisation option                                                                               |
| 0.1.18  | 2021-09-21 | [6056](https://github.com/airbytehq/airbyte/pull/6056)   | Added `pre_tax_price` to the `orders/line_items` schema                                                                         |
| 0.1.17  | 2021-09-17 | [5244](https://github.com/airbytehq/airbyte/pull/5244)   | Created data type enforcer for converting prices into numbers                                                                   |
| 0.1.16  | 2021-09-09 | [5965](https://github.com/airbytehq/airbyte/pull/5945)   | Fixed the connector's performance for `Incremental refresh`                                                                     |
| 0.1.15  | 2021-09-02 | [5853](https://github.com/airbytehq/airbyte/pull/5853)   | Fixed `amount` type in `order_refund` schema                                                                                    |
| 0.1.14  | 2021-09-02 | [5801](https://github.com/airbytehq/airbyte/pull/5801)   | Fixed `line_items/discount allocations` & `duties` parts of `orders` schema                                                     |
| 0.1.13  | 2021-08-17 | [5470](https://github.com/airbytehq/airbyte/pull/5470)   | Fixed rate limits throttling                                                                                                    |
| 0.1.12  | 2021-08-09 | [5276](https://github.com/airbytehq/airbyte/pull/5276)   | Added status property to product schema                                                                                         |
| 0.1.11  | 2021-07-23 | [4943](https://github.com/airbytehq/airbyte/pull/4943)   | Fixed products schema up to API 2021-07                                                                                         |
| 0.1.10  | 2021-07-19 | [4830](https://github.com/airbytehq/airbyte/pull/4830)   | Fixed for streams json schemas, upgrade to API version 2021-07                                                                  |
| 0.1.9   | 2021-07-04 | [4472](https://github.com/airbytehq/airbyte/pull/4472)   | Incremental sync is now using updated_at instead of since_id by default                                                         |
| 0.1.8   | 2021-06-29 | [4121](https://github.com/airbytehq/airbyte/pull/4121)   | Added draft orders stream                                                                                                       |
| 0.1.7   | 2021-06-26 | [4290](https://github.com/airbytehq/airbyte/pull/4290)   | Fixed the bug when limiting output records to 1 caused infinity loop                                                            |
| 0.1.6   | 2021-06-24 | [4009](https://github.com/airbytehq/airbyte/pull/4009)   | Added pages, price rules and discount codes streams                                                                             |
| 0.1.5   | 2021-06-10 | [3973](https://github.com/airbytehq/airbyte/pull/3973)   | Added `AIRBYTE_ENTRYPOINT` for Kubernetes support                                                                               |
| 0.1.4   | 2021-06-09 | [3926](https://github.com/airbytehq/airbyte/pull/3926)   | New attributes to Orders schema                                                                                                 |
| 0.1.3   | 2021-06-08 | [3787](https://github.com/airbytehq/airbyte/pull/3787)   | Added Native Shopify Source Connector                                                                                           |

</HideInUI>
