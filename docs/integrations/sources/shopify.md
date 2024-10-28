# Shopify

<HideInUI>

This page contains the setup guide and reference information for the [Shopify](https://www.shopify.com/) source connector.

</HideInUI>

## Prerequisites

- An active [Shopify store](https://www.shopify.com).
- If you are syncing data from a store that you do not own, you will need to [request access to your client's store](https://help.shopify.com/en/partners/dashboard/managing-stores/request-access#request-access) (not required for account owners).
<!-- env:oss  -->
- For **Airbyte Open Source** users: A custom Shopify application with [`read_` scopes enabled](#scopes-required-for-custom-app).
<!-- /env:oss -->

## Setup guide

This connector supports **OAuth2.0** and **API Password** (for private applications) authentication methods.

### Set up Shopify

<!-- env:cloud -->

:::note
For existing **Airbyte Cloud** customers, if you are currently using the **API Password** authentication method, please switch to **OAuth2.0**, as the API Password will be deprecated shortly. This change will not affect **Airbyte Open Source** connections.
:::

<HideInUI>

### For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. Click Sources and then click + New source.
3. On the Set up the source page, select Shopify from the Source type dropdown.
4. Enter a name for the Shopify connector.
</HideInUI>

#### Connect using OAuth2.0

1. Choose a **Source name**.
2. Click **Authenticate your Shopify account**.
3. Click **Install** to install the Airbyte application. Log in to your account, if you are not already logged in. Select the store you want to sync and review the consent form. Click **Install app** to finish the installation.
<FieldAnchor field="shop">
4. The **Shopify Store** field will be automatically filled after you authenticate your Shopify account based on the store you selected. Once populated, confirm the value is accurate.
</FieldAnchor>
<FieldAnchor field="start_date">
5. (Optional) You may set a **Replication Start Date** as the starting point for your data replication. Any data created before this date will not be synced. Defaults to January 1st, 2020.
</FieldAnchor>
6. Click **Set up source** and wait for the connection test to complete.
<!-- /env:cloud -->

<!-- env:oss -->

### For Airbyte Open Source:

1. Navigate to the Airbyte Open Source dashboard.
2. Click Sources and then click + New source.
3. On the Set up the source page, select Shopify from the Source type dropdown.
4. Enter a name for the Shopify connector.

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

- `read_analytics`
- `read_assigned_fulfillment_orders`
- `read_content`
- `read_customers`
- `read_discounts`
- `read_draft_orders`
- `read_fulfillments`
- `read_gdpr_data_request`
- `read_gift_cards`
- `read_inventory`
- `read_legal_policies`
- `read_locations`
- `read_locales`
- `read_marketing_events`
- `read_merchant_managed_fulfillment_orders`
- `read_online_store_pages`
- `read_order_edits`
- `read_orders`
- `read_price_rules`
- `read_product_listings`
- `read_products`
- `read_publications`
- `read_reports`
- `read_resource_feedbacks`
- `read_script_tags`
- `read_shipping`
- `read_shopify_payments_accounts`
- `read_shopify_payments_bank_accounts`
- `read_shopify_payments_disputes`
- `read_shopify_payments_payouts`
- `read_themes`
- `read_third_party_fulfillment_orders`
- `read_translations`

<!-- env:oss -->

<HideInUI>

## Supported sync modes

The Shopify source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts/#connection-sync-modes):

| Feature           | Supported? |
|:------------------|:-----------|
| Full Refresh Sync | Yes        |
| Incremental Sync  | Yes        |

The Shopify source supports both Full Refresh and Incremental syncs. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

This source can sync data for the [Shopify REST API](https://shopify.dev/api/admin-rest) and the [Shopify GraphQL API](https://shopify.dev/api/admin-graphql) and the [Shopify GraphQL BULK API](https://shopify.dev/docs/api/usage/bulk-operations/queries)

## Supported Streams

- [Abandoned Checkouts](https://shopify.dev/api/admin-rest/2024-04/resources/abandoned-checkouts#top)
- [Articles](https://shopify.dev/api/admin-rest/2024-04/resources/article)
- [Balance Transactions](https://shopify.dev/docs/api/admin-rest/2024-04/resources/transactions)
- [Blogs](https://shopify.dev/api/admin-rest/2024-04/resources/blog)
- [Collects](https://shopify.dev/api/admin-rest/2024-04/resources/collect#top)
- [Collections (GraphQL)](https://shopify.dev/docs/api/admin-graphql/2024-04/objects/Collection)
- [Countries](https://shopify.dev/docs/api/admin-rest/2024-04/resources/country)
- [Custom Collections](https://shopify.dev/api/admin-rest/2024-04/resources/customcollection#top)
- [Customers](https://shopify.dev/api/admin-rest/2024-04/resources/customer#top)
- [Customer Journey Summary (GraphQL)](https://shopify.dev/docs/api/admin-graphql/2024-04/objects/customerjourneysummary)
- [Customer Address (GraphQL)](https://shopify.dev/docs/api/admin-graphql/2024-04/objects/Customer#field-customer-addresses)
- [Customer Saved Search](https://shopify.dev/docs/api/admin-rest/2024-04/resources/customersavedsearch)
- [Draft Orders](https://shopify.dev/api/admin-rest/2024-04/resources/draftorder#top)
- [Discount Codes (GraphQL)](https://shopify.dev/docs/api/admin-graphql/2024-04/unions/DiscountCode)
- [Disputes](https://shopify.dev/docs/api/admin-rest/2024-04/resources/dispute)
- [Fulfillments](https://shopify.dev/api/admin-rest/2024-04/resources/fulfillment)
- [Fulfillment Orders (GraphQL)](https://shopify.dev/docs/api/admin-graphql/2024-04/objects/FulfillmentOrder)
- [Inventory Items (GraphQL)](https://shopify.dev/docs/api/admin-graphql/2024-04/objects/InventoryItem)
- [Inventory Levels (GraphQL)](https://shopify.dev/docs/api/admin-graphql/2024-04/objects/InventoryLevel)
- [Locations](https://shopify.dev/api/admin-rest/2024-04/resources/location)
- [Metafields (GraphQL)](https://shopify.dev/docs/api/admin-graphql/2024-04/objects/Metafield)
- [Order Agreements (GraphQL)](https://shopify.dev/docs/api/admin-graphql/2024-04/objects/OrderAgreement)
- [Orders](https://shopify.dev/api/admin-rest/2024-04/resources/order#top)
- [Order Refunds](https://shopify.dev/api/admin-rest/2024-04/resources/refund#top)
- [Order Risks (GraphQL)](https://shopify.dev/api/admin-rest/2024-04/resources/order-risk#top)
- [Pages](https://shopify.dev/api/admin-rest/2024-04/resources/page#top)
- [Price Rules](https://shopify.dev/api/admin-rest/2024-04/resources/pricerule#top)
- [Products (GraphQL)](https://shopify.dev/docs/api/admin-graphql/2024-04/queries/products)
- [Product Images (GraphQL)](https://shopify.dev/docs/api/admin-graphql/2024-04/objects/Image)
- [Product Variants (GraphQL)](https://shopify.dev/docs/api/admin-graphql/2024-04/queries/productVariant)
- [Shop](https://shopify.dev/api/admin-rest/2024-04/resources/shop)
- [Smart Collections](https://shopify.dev/api/admin-rest/2024-04/resources/smartcollection)
- [Transactions](https://shopify.dev/api/admin-rest/2024-04/resources/transaction#top)
- [Transactions (GraphQL)](https://shopify.dev/docs/api/admin-graphql/2024-04/objects/OrderTransaction)
- [Tender Transactions](https://shopify.dev/api/admin-rest/2024-04/resources/tendertransaction)

### Entity-Relationship Diagram (ERD)
<EntityRelationshipDiagram></EntityRelationshipDiagram>

## Capturing deleted records

The connector captures deletions for records in the `Articles`, `Blogs`, `CustomCollections`, `Orders`, `Pages`, `PriceRules` and `Products` streams.

When a record is deleted, the connector outputs a record with the `ID` of that record and the `deleted_at`, `deleted_message`, and `deleted_description` fields filled out. No other fields are filled out for the deleted records.

Check the following Shopify documentation for more information about [retrieving deleted records](https://shopify.dev/docs/api/admin-rest/2024-04/resources/event).

## Marketing Attribution data
Data related to [marketing attribution](https://www.shopify.com/au/blog/marketing-attribution) can be found across a few different streams. Sync these streams to understand marketing performance:
- `Customer Journey Summary` (firstVisit.source, firstVisit.sourcetype)
- `Orders` (referring_site, source_name)
- `Abandoned Checkouts` (referring_site, source_name)

## Features

| Feature                   | Supported?\(Yes/No\) |
| :------------------------ | :------------------- |
| Full Refresh Sync         | Yes                  |
| Incremental - Append Sync | Yes                  |
| Namespaces                | No                   |

## Data type map

| Integration Type | Airbyte Type |
|:-----------------|:-------------|
| `string`         | `string`     |
| `number`         | `number`     |
| `array`          | `array`      |
| `object`         | `object`     |
| `boolean`        | `boolean`    |

## Limitations & Troubleshooting

</HideInUI>
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

For all `Shopify GraphQL BULK` api requests these limitations are applied: https://shopify.dev/docs/api/usage/bulk-operations/queries#operation-restrictions

### Troubleshooting

- If you encounter access errors while using **OAuth2.0** authentication, please make sure you've followed this [Shopify Article](https://help.shopify.com/en/partners/dashboard/managing-stores/request-access#request-access) to request the access to the client's store first. Once the access is granted, you should be able to proceed with **OAuth2.0** authentication.
- Check out common troubleshooting issues for the Shopify source connector on our Airbyte Forum [here](https://github.com/airbytehq/airbyte/discussions).

</details>


## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                                                                                                                                                                                                                                                                                                                                   |
|:--------|:-----------|:---------------------------------------------------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 2.5.7 | 2024-10-14 | [46552](https://github.com/airbytehq/airbyte/pull/46552) | Add `parent state` tracking for BULK sub-streams |
| 2.5.6 | 2024-10-12 | [46844](https://github.com/airbytehq/airbyte/pull/46844) | Update dependencies |
| 2.5.5 | 2024-10-05 | [46578](https://github.com/airbytehq/airbyte/pull/46578) | Raise exception on missing stream |
| 2.5.4 | 2024-10-05 | [45759](https://github.com/airbytehq/airbyte/pull/45759) | Update dependencies |
| 2.5.3 | 2024-09-27 | [46095](https://github.com/airbytehq/airbyte/pull/46095) | Fixed duplicates for `Product Images`, `Metafield Product Images` and `Metafield Products` streams for Incremental syncs |
| 2.5.2 | 2024-09-17 | [45633](https://github.com/airbytehq/airbyte/pull/45633) | Adds `read_inventory` as a required scope for `product_variants` stream |
| 2.5.1 | 2024-09-14 | [45255](https://github.com/airbytehq/airbyte/pull/45255) | Update dependencies |
| 2.5.0 | 2024-09-06 | [45190](https://github.com/airbytehq/airbyte/pull/45190) | Migrate to CDK v5 |
| 2.4.24 | 2024-09-03 | [45116](https://github.com/airbytehq/airbyte/pull/45116) | Have message and description be nullable for custom_collections deleted events |
| 2.4.23 | 2024-08-31 | [44971](https://github.com/airbytehq/airbyte/pull/44971) | Update dependencies |
| 2.4.22 | 2024-08-24 | [44723](https://github.com/airbytehq/airbyte/pull/44723) | Update dependencies |
| 2.4.21 | 2024-08-17 | [44318](https://github.com/airbytehq/airbyte/pull/44318) | Update dependencies |
| 2.4.20 | 2024-08-12 | [43834](https://github.com/airbytehq/airbyte/pull/43834) | Update dependencies |
| 2.4.19 | 2024-08-10 | [43194](https://github.com/airbytehq/airbyte/pull/43194) | Update dependencies |
| 2.4.18 | 2024-08-06 | [43326](https://github.com/airbytehq/airbyte/pull/43326) | Added missing `type` type for `customer_journey_summary` field for `Customer Journey Summary` stream schema |
| 2.4.17 | 2024-08-02 | [42973](https://github.com/airbytehq/airbyte/pull/42973) | Fixed `FAILED` Job handling for `no-checkpointing` BULK Streams, fixed STATE collision for REST Streams with `Deleted Events` |
| 2.4.16 | 2024-07-21 | [42095](https://github.com/airbytehq/airbyte/pull/42095) | Added the `Checkpointing` for the `BULK` streams, fixed the `store` redirection |
| 2.4.15 | 2024-07-27 | [42806](https://github.com/airbytehq/airbyte/pull/42806) | Update dependencies |
| 2.4.14 | 2024-07-20 | [42150](https://github.com/airbytehq/airbyte/pull/42150) | Update dependencies |
| 2.4.13 | 2024-07-13 | [41809](https://github.com/airbytehq/airbyte/pull/41809) | Update dependencies |
| 2.4.12 | 2024-07-10 | [41103](https://github.com/airbytehq/airbyte/pull/41103) | Update dependencies |
| 2.4.11 | 2024-07-09 | [41068](https://github.com/airbytehq/airbyte/pull/41068) | Added `options` field to `Product Variants` stream |
| 2.4.10 | 2024-07-09 | [41042](https://github.com/airbytehq/airbyte/pull/41042) | Use latest `CDK`: 3.0.0 |
| 2.4.9 | 2024-07-06 | [40768](https://github.com/airbytehq/airbyte/pull/40768) | Update dependencies |
| 2.4.8 | 2024-07-03 | [40707](https://github.com/airbytehq/airbyte/pull/40707) | Fixed the bug when `product_images` stream emitted records with no `primary_key` |
| 2.4.7 | 2024-06-27 | [40593](https://github.com/airbytehq/airbyte/pull/40593) | Use latest `CDK` version possible |
| 2.4.6 | 2024-06-26 | [40526](https://github.com/airbytehq/airbyte/pull/40526) | Made `BULK Job termination threshold` limit adjustable from `input configuration`, increased the default value to `1 hour`. |
| 2.4.5 | 2024-06-25 | [40484](https://github.com/airbytehq/airbyte/pull/40484) | Update dependencies |
| 2.4.4 | 2024-06-19 | [39594](https://github.com/airbytehq/airbyte/pull/39594) | Extended the `Discount Codes`, `Fulfillment Orders`, `Inventory Items`, `Inventory Levels`, `Products`, `Product Variants` and `Transactions` stream schemas |
| 2.4.3 | 2024-06-06 | [38084](https://github.com/airbytehq/airbyte/pull/38084) | add resiliency on some transient errors using the HttpClient |
| 2.4.1 | 2024-06-20 | [39651](https://github.com/airbytehq/airbyte/pull/39651) | Update dependencies |
| 2.4.0 | 2024-06-17 | [39527](https://github.com/airbytehq/airbyte/pull/39527) | Added new stream `Order Agreements` |
| 2.3.0 | 2024-06-14 | [39487](https://github.com/airbytehq/airbyte/pull/39487) | Added new stream `Customer Journey Summary` |
| 2.2.3 | 2024-06-06 | [38084](https://github.com/airbytehq/airbyte/pull/38084) | add resiliency on some transient errors using the HttpClient |
| 2.2.2 | 2024-06-04 | [39019](https://github.com/airbytehq/airbyte/pull/39019) | [autopull] Upgrade base image to v1.2.1 |
| 2.2.1 | 2024-05-30 | [38769](https://github.com/airbytehq/airbyte/pull/38769) | Have products stream return all the tags comma separated |
| 2.2.0 | 2024-05-29 | [38746](https://github.com/airbytehq/airbyte/pull/38746) | Updated countries schema |
| 2.1.4 | 2024-05-24 | [38610](https://github.com/airbytehq/airbyte/pull/38610) | Updated the source `API Version` to `2024-04` |
| 2.1.3 | 2024-05-23 | [38464](https://github.com/airbytehq/airbyte/pull/38464) | Added missing fields to `Products` stream |
| 2.1.2 | 2024-05-23 | [38352](https://github.com/airbytehq/airbyte/pull/38352) | Migrated `Order Risks` stream to `GraphQL BULK` |
| 2.1.1 | 2024-05-20 | [38251](https://github.com/airbytehq/airbyte/pull/38251) | Replace AirbyteLogger with logging.Logger |
| 2.1.0 | 2024-05-02 | [37767](https://github.com/airbytehq/airbyte/pull/37767) | Migrated `Products`, `Product Images` and `Product Variants` to `GraphQL BULK` |
| 2.0.8 | 2024-05-02 | [37589](https://github.com/airbytehq/airbyte/pull/37589) | Added retry for known HTTP Errors for BULK streams |
| 2.0.7 | 2024-04-24 | [36660](https://github.com/airbytehq/airbyte/pull/36660) | Schema descriptions |
| 2.0.6 | 2024-04-22 | [37468](https://github.com/airbytehq/airbyte/pull/37468) | Fixed one time retry for `Internal Server Error` for BULK streams |
| 2.0.5 | 2024-04-03 | [36788](https://github.com/airbytehq/airbyte/pull/36788) | Added ability to dynamically adjust the size of the `slice` |
| 2.0.4 | 2024-03-22 | [36355](https://github.com/airbytehq/airbyte/pull/36355) | Update CDK version to ensure Per-Stream Error Messaging and Record Counts In State (features were already there so just upping the version) |
| 2.0.3 | 2024-03-15 | [36170](https://github.com/airbytehq/airbyte/pull/36170) | Fixed the `STATE` messages emittion frequency for the `nested` sub-streams |
| 2.0.2 | 2024-03-12 | [36000](https://github.com/airbytehq/airbyte/pull/36000) | Fix and issue where invalid shop name causes index out of bounds error |
| 2.0.1 | 2024-03-11 | [35952](https://github.com/airbytehq/airbyte/pull/35952) | Fixed the issue when `start date` is missing but the `stream` required it |
| 2.0.0 | 2024-02-12 | [32345](https://github.com/airbytehq/airbyte/pull/32345) | Fixed the issue with `state` causing the `substreams` to skip the records, made `metafield_*`: `collections, customers, draft_orders, locations, orders, product_images, product_variants, products`, and `fulfillment_orders, collections, discount_codes, inventory_levels, inventory_items, transactions_graphql, customer_address` streams to use `BULK Operations` instead of `REST` |
| 1.1.8 | 2024-02-12 | [35166](https://github.com/airbytehq/airbyte/pull/35166) | Manage dependencies with Poetry. |
| 1.1.7 | 2024-01-19 | [33804](https://github.com/airbytehq/airbyte/pull/33804) | Updated documentation with list of all supported streams |
| 1.1.6 | 2024-01-04 | [33414](https://github.com/airbytehq/airbyte/pull/33414) | Prepare for airbyte-lib |
| 1.1.5 | 2023-12-28 | [33827](https://github.com/airbytehq/airbyte/pull/33827) | Fix GraphQL query |
| 1.1.4 | 2023-10-19 | [31599](https://github.com/airbytehq/airbyte/pull/31599) | Base image migration: remove Dockerfile and use the python-connector-base image |
| 1.1.3 | 2023-10-17 | [31500](https://github.com/airbytehq/airbyte/pull/31500) | Fixed the issue caused by the `missing access token` while setup the new source and not yet authenticated |
| 1.1.2 | 2023-10-13 | [31381](https://github.com/airbytehq/airbyte/pull/31381) | Fixed the issue caused by the `state` presence while fetching the `deleted events` with pagination |
| 1.1.1 | 2023-09-18 | [30560](https://github.com/airbytehq/airbyte/pull/30560) | Performance testing - include socat binary in docker image |
| 1.1.0 | 2023-09-07 | [30246](https://github.com/airbytehq/airbyte/pull/30246) | Added ability to fetch `destroyed` records for `Articles, Blogs, CustomCollections, Orders, Pages, PriceRules, Products` |
| 1.0.0 | 2023-08-11 | [29361](https://github.com/airbytehq/airbyte/pull/29361) | Migrate to the `2023-07` Shopify API Version |
| 0.6.2 | 2023-08-09 | [29302](https://github.com/airbytehq/airbyte/pull/29302) | Handle the `Internal Server Error` when entity could be fetched |
| 0.6.1 | 2023-08-08 | [28291](https://github.com/airbytehq/airbyte/pull/28291) | Allow `shop` field to accept `*.myshopify.com` shop names, updated `OAuth Spec` |
| 0.6.0 | 2023-08-02 | [28770](https://github.com/airbytehq/airbyte/pull/28770) | Added `Disputes` stream |
| 0.5.1 | 2023-07-13 | [28700](https://github.com/airbytehq/airbyte/pull/28700) | Improved `error messages` with more user-friendly description, refactored code |
| 0.5.0 | 2023-06-13 | [27732](https://github.com/airbytehq/airbyte/pull/27732) | License Update: Elv2 |
| 0.4.0 | 2023-06-13 | [27083](https://github.com/airbytehq/airbyte/pull/27083) | Added `CustomerSavedSearch`, `CustomerAddress` and `Countries` streams |
| 0.3.4 | 2023-05-10 | [25961](https://github.com/airbytehq/airbyte/pull/25961) | Added validation for `shop` in input configuration (accepts non-url-like inputs) |
| 0.3.3 | 2023-04-12 | [25110](https://github.com/airbytehq/airbyte/pull/25110) | Fixed issue when `cursor_field` is `"None"`, added missing properties to stream schemas, fixed `access_scopes` validation error |
| 0.3.2 | 2023-02-27 | [23473](https://github.com/airbytehq/airbyte/pull/23473) | Fixed OOM / Memory leak issue for Airbyte Cloud |
| 0.3.1 | 2023-01-16 | [21461](https://github.com/airbytehq/airbyte/pull/21461) | Added `discount_applications` to `orders` stream |
| 0.3.0 | 2022-11-16 | [19492](https://github.com/airbytehq/airbyte/pull/19492) | Added support for graphql and add a graphql products stream |
| 0.2.0 | 2022-10-21 | [18298](https://github.com/airbytehq/airbyte/pull/18298) | Updated API version to the `2022-10`, make stream schemas backward cpmpatible |
| 0.1.39 | 2022-10-13 | [17962](https://github.com/airbytehq/airbyte/pull/17962) | Added metafield streams; support for nested list streams |
| 0.1.38 | 2022-10-10 | [17777](https://github.com/airbytehq/airbyte/pull/17777) | Fixed `404` for configured streams, fix missing `cursor` error for old records |
| 0.1.37 | 2022-04-30 | [12500](https://github.com/airbytehq/airbyte/pull/12500) | Improve input configuration copy |
| 0.1.36 | 2022-03-22 | [9850](https://github.com/airbytehq/airbyte/pull/9850) | Added `BalanceTransactions` stream |
| 0.1.35 | 2022-03-07 | [10915](https://github.com/airbytehq/airbyte/pull/10915) | Fixed a bug which caused `full-refresh` syncs of child REST entities configured for `incremental` |
| 0.1.34 | 2022-03-02 | [10794](https://github.com/airbytehq/airbyte/pull/10794) | Minor specification re-order, fixed links in documentation |
| 0.1.33 | 2022-02-17 | [10419](https://github.com/airbytehq/airbyte/pull/10419) | Fixed wrong field type for tax_exemptions for `Abandoned_checkouts` stream |
| 0.1.32 | 2022-02-18 | [10449](https://github.com/airbytehq/airbyte/pull/10449) | Added `tender_transactions` stream |
| 0.1.31 | 2022-02-08 | [10175](https://github.com/airbytehq/airbyte/pull/10175) | Fixed compatibility issues for legacy user config |
| 0.1.30 | 2022-01-24 | [9648](https://github.com/airbytehq/airbyte/pull/9648) | Added permission validation before sync |
| 0.1.29  | 2022-01-20 | [9049](https://github.com/airbytehq/airbyte/pull/9248)   | Added `shop_url` to the record for all streams                                                                                                                                                                                                                                                                                                                                            |
| 0.1.28  | 2022-01-19 | [9591](https://github.com/airbytehq/airbyte/pull/9591)   | Implemented `OAuth2.0` authentication method for Airbyte Cloud                                                                                                                                                                                                                                                                                                                            |
| 0.1.27  | 2021-12-22 | [9049](https://github.com/airbytehq/airbyte/pull/9049)   | Updated connector fields title/description                                                                                                                                                                                                                                                                                                                                                |
| 0.1.26  | 2021-12-14 | [8597](https://github.com/airbytehq/airbyte/pull/8597)   | Fixed `mismatched number of tables` for base-normalization, increased performance of `order_refunds` stream                                                                                                                                                                                                                                                                               |
| 0.1.25  | 2021-12-02 | [8297](https://github.com/airbytehq/airbyte/pull/8297)   | Added Shop stream                                                                                                                                                                                                                                                                                                                                                                         |
| 0.1.24  | 2021-11-30 | [7783](https://github.com/airbytehq/airbyte/pull/7783)   | Reviewed and corrected schemas for all streams                                                                                                                                                                                                                                                                                                                                            |
| 0.1.23  | 2021-11-15 | [7973](https://github.com/airbytehq/airbyte/pull/7973)   | Added `InventoryItems`                                                                                                                                                                                                                                                                                                                                                                    |
| 0.1.22  | 2021-10-18 | [7101](https://github.com/airbytehq/airbyte/pull/7107)   | Added FulfillmentOrders, Fulfillments streams                                                                                                                                                                                                                                                                                                                                             |
| 0.1.21  | 2021-10-14 | [7382](https://github.com/airbytehq/airbyte/pull/7382)   | Fixed `InventoryLevels` primary key                                                                                                                                                                                                                                                                                                                                                       |
| 0.1.20  | 2021-10-14 | [7063](https://github.com/airbytehq/airbyte/pull/7063)   | Added `Location` and `InventoryLevels` as streams                                                                                                                                                                                                                                                                                                                                         |
| 0.1.19  | 2021-10-11 | [6951](https://github.com/airbytehq/airbyte/pull/6951)   | Added support of `OAuth 2.0` authorisation option                                                                                                                                                                                                                                                                                                                                         |
| 0.1.18  | 2021-09-21 | [6056](https://github.com/airbytehq/airbyte/pull/6056)   | Added `pre_tax_price` to the `orders/line_items` schema                                                                                                                                                                                                                                                                                                                                   |
| 0.1.17  | 2021-09-17 | [5244](https://github.com/airbytehq/airbyte/pull/5244)   | Created data type enforcer for converting prices into numbers                                                                                                                                                                                                                                                                                                                             |
| 0.1.16  | 2021-09-09 | [5965](https://github.com/airbytehq/airbyte/pull/5945)   | Fixed the connector's performance for `Incremental refresh`                                                                                                                                                                                                                                                                                                                               |
| 0.1.15  | 2021-09-02 | [5853](https://github.com/airbytehq/airbyte/pull/5853)   | Fixed `amount` type in `order_refund` schema                                                                                                                                                                                                                                                                                                                                              |
| 0.1.14  | 2021-09-02 | [5801](https://github.com/airbytehq/airbyte/pull/5801)   | Fixed `line_items/discount allocations` & `duties` parts of `orders` schema                                                                                                                                                                                                                                                                                                               |
| 0.1.13  | 2021-08-17 | [5470](https://github.com/airbytehq/airbyte/pull/5470)   | Fixed rate limits throttling                                                                                                                                                                                                                                                                                                                                                              |
| 0.1.12  | 2021-08-09 | [5276](https://github.com/airbytehq/airbyte/pull/5276)   | Added status property to product schema                                                                                                                                                                                                                                                                                                                                                   |
| 0.1.11  | 2021-07-23 | [4943](https://github.com/airbytehq/airbyte/pull/4943)   | Fixed products schema up to API 2021-07                                                                                                                                                                                                                                                                                                                                                   |
| 0.1.10  | 2021-07-19 | [4830](https://github.com/airbytehq/airbyte/pull/4830)   | Fixed for streams json schemas, upgrade to API version 2021-07                                                                                                                                                                                                                                                                                                                            |
| 0.1.9   | 2021-07-04 | [4472](https://github.com/airbytehq/airbyte/pull/4472)   | Incremental sync is now using updated_at instead of since_id by default                                                                                                                                                                                                                                                                                                                   |
| 0.1.8   | 2021-06-29 | [4121](https://github.com/airbytehq/airbyte/pull/4121)   | Added draft orders stream                                                                                                                                                                                                                                                                                                                                                                 |
| 0.1.7   | 2021-06-26 | [4290](https://github.com/airbytehq/airbyte/pull/4290)   | Fixed the bug when limiting output records to 1 caused infinity loop                                                                                                                                                                                                                                                                                                                      |
| 0.1.6   | 2021-06-24 | [4009](https://github.com/airbytehq/airbyte/pull/4009)   | Added pages, price rules and discount codes streams                                                                                                                                                                                                                                                                                                                                       |
| 0.1.5   | 2021-06-10 | [3973](https://github.com/airbytehq/airbyte/pull/3973)   | Added `AIRBYTE_ENTRYPOINT` for Kubernetes support                                                                                                                                                                                                                                                                                                                                         |
| 0.1.4   | 2021-06-09 | [3926](https://github.com/airbytehq/airbyte/pull/3926)   | New attributes to Orders schema                                                                                                                                                                                                                                                                                                                                                           |
| 0.1.3   | 2021-06-08 | [3787](https://github.com/airbytehq/airbyte/pull/3787)   | Added Native Shopify Source Connector                                                                                                                                                                                                                                                                                                                                                     |

</details>
