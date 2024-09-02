# Recharge

This source can sync data for the [Recharge API](https://developer.rechargepayments.com/).
This page guides you through the process of setting up the Recharge source connector.

## Prerequisites

- A Recharge account with permission to access data from accounts you want to sync.
- Recharge API Token

## Setup guide

### Step 1: Set up Recharge

Please read [How to generate your API token](https://support.rechargepayments.com/hc/en-us/articles/360008829993-ReCharge-API).

### Step 2: Set up the source connector in Airbyte

<!-- env:cloud -->

**For Airbyte Cloud:**

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ new source**.
3. On the source setup page, select **Recharge** from the Source type dropdown and enter a name for this connector.
4. Choose required `Start date`
5. Enter your `Access Token`.
6. click `Set up source`.
<!-- /env:cloud -->

<!-- env:oss -->

**For Airbyte Open Source:**

1. Go to local Airbyte page.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ new source**.
3. On the source setup page, select **Recharge** from the Source type dropdown and enter a name for this connector.
4. Choose required `Start date`
5. Enter your `Access Token` generated from `Step 1`.
6. click `Set up source`.
<!-- /env:oss -->

## Supported sync modes

The Recharge supports full refresh and incremental sync.

| Feature           | Supported? |
| :---------------- | :--------- |
| Full Refresh Sync | Yes        |
| Incremental Sync  | Yes        |
| SSL connection    | Yes        |

## Supported Streams

Several output streams are available from this source:

- [Addresses](https://developer.rechargepayments.com/v1-shopify?python#list-addresses) \(Incremental sync\)
- [Charges](https://developer.rechargepayments.com/v1-shopify?python#list-charges) \(Incremental sync\)
- [Collections](https://developer.rechargepayments.com/v1-shopify)
- [Customers](https://developer.rechargepayments.com/v1-shopify?python#list-customers) \(Incremental sync\)
- [Discounts](https://developer.rechargepayments.com/v1-shopify?python#list-discounts) \(Incremental sync\)
- [Metafields](https://developer.rechargepayments.com/v1-shopify?python#list-metafields)
- [Onetimes](https://developer.rechargepayments.com/v1-shopify?python#list-onetimes) \(Incremental sync\)
- [Orders](https://developer.rechargepayments.com/v1-shopify?python#list-orders) \(Incremental sync\)
- [Products](https://developer.rechargepayments.com/v1-shopify?python#list-products)
- [Shop](https://developer.rechargepayments.com/v1-shopify?python#shop)
- [Subscriptions](https://developer.rechargepayments.com/v1-shopify?python#list-subscriptions) \(Incremental sync\)

If there are more endpoints you'd like Airbyte to support, please [create an issue.](https://github.com/airbytehq/airbyte/issues/new/choose)

### Performance considerations

The Recharge connector should gracefully handle Recharge API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                                                                        |
|:--------|:-----------| :------------------------------------------------------- |:-------------------------------------------------------------------------------------------------------------------------------|
| 2.4.6 | 2024-08-31 | [44995](https://github.com/airbytehq/airbyte/pull/44995) | Update dependencies |
| 2.4.5 | 2024-08-24 | [44731](https://github.com/airbytehq/airbyte/pull/44731) | Update dependencies |
| 2.4.4 | 2024-08-17 | [44205](https://github.com/airbytehq/airbyte/pull/44205) | Update dependencies |
| 2.4.3 | 2024-08-12 | [43837](https://github.com/airbytehq/airbyte/pull/43837) | Update dependencies |
| 2.4.2 | 2024-08-10 | [43703](https://github.com/airbytehq/airbyte/pull/43703) | Update dependencies |
| 2.4.1 | 2024-08-03 | [43171](https://github.com/airbytehq/airbyte/pull/43171) | Update dependencies |
| 2.4.0 | 2024-08-02 | [*PR_NUMBER_PLACEHOLDER*](https://github.com/airbytehq/airbyte/pull/*PR_NUMBER_PLACEHOLDER*) | Migrate to CDK v4.3.0 |
| 2.3.2 | 2024-07-27 | [42723](https://github.com/airbytehq/airbyte/pull/42723) | Update dependencies |
| 2.3.1 | 2024-07-20 | [42336](https://github.com/airbytehq/airbyte/pull/42336) | Update dependencies |
| 2.3.0 | 2024-07-17 | [42076](https://github.com/airbytehq/airbyte/pull/42076) | Migrate to CDK v3.7.0 |
| 2.2.0 | 2024-07-17 | [42075](https://github.com/airbytehq/airbyte/pull/42075) | Migrate to CDK v2.4.0 |
| 2.1.0 | 2024-07-17 | [42069](https://github.com/airbytehq/airbyte/pull/42069) | Migrate to CDK v1.8.0 |
| 2.0.6 | 2024-07-13 | [41748](https://github.com/airbytehq/airbyte/pull/41748) | Update dependencies |
| 2.0.5 | 2024-07-10 | [41475](https://github.com/airbytehq/airbyte/pull/41475) | Update dependencies |
| 2.0.4 | 2024-07-09 | [41167](https://github.com/airbytehq/airbyte/pull/41167) | Update dependencies |
| 2.0.3 | 2024-07-06 | [40849](https://github.com/airbytehq/airbyte/pull/40849) | Update dependencies |
| 2.0.2 | 2024-06-25 | [40387](https://github.com/airbytehq/airbyte/pull/40387) | Update dependencies |
| 2.0.1 | 2024-06-22 | [40042](https://github.com/airbytehq/airbyte/pull/40042) | Update dependencies |
| 2.0.0 | 2024-06-14 | [39491](https://github.com/airbytehq/airbyte/pull/39491) | Update primary key for Shop stream from shop, store(object, object) to id(integer) |
| 1.2.0 | 2024-03-13 | [35450](https://github.com/airbytehq/airbyte/pull/35450) | Migrated to low-code |
| 1.1.6 | 2024-03-12 | [35982](https://github.com/airbytehq/airbyte/pull/35982) | Added additional `query param` to guarantee the records are in `asc` order |
| 1.1.5 | 2024-02-12 | [35182](https://github.com/airbytehq/airbyte/pull/35182) | Manage dependencies with Poetry. |
| 1.1.4 | 2024-02-02 | [34772](https://github.com/airbytehq/airbyte/pull/34772) | Fix airbyte-lib distribution |
| 1.1.3 | 2024-01-31 | [34707](https://github.com/airbytehq/airbyte/pull/34707) | Added the UI toggle `Use 'Orders' Deprecated API` to switch between `deprecated` and `modern` api versions for `Orders` stream |
| 1.1.2 | 2023-11-03 | [32132](https://github.com/airbytehq/airbyte/pull/32132) | Reduced `period in days` value for `Subscriptions` stream, to avoid `504 - Gateway TimeOut` error |
| 1.1.1 | 2023-09-26 | [30782](https://github.com/airbytehq/airbyte/pull/30782) | For the new style pagination, pass only limit along with cursor |
| 1.1.0 | 2023-09-26 | [30756](https://github.com/airbytehq/airbyte/pull/30756) | Fix pagination and slicing |
| 1.0.1 | 2023-08-30 | [29992](https://github.com/airbytehq/airbyte/pull/29992) | Revert for orders stream to use old API version 2021-01 |
| 1.0.0 | 2023-06-22 | [27612](https://github.com/airbytehq/airbyte/pull/27612) | Change data type of the `shopify_variant_id_not_found` field of the `Charges` stream |
| 0.2.10 | 2023-06-20 | [27503](https://github.com/airbytehq/airbyte/pull/27503) | Update API version to 2021-11 |
| 0.2.9 | 2023-04-10 | [25009](https://github.com/airbytehq/airbyte/pull/25009) | Fix owner slicing for `Metafields` stream |
| 0.2.8 | 2023-04-07 | [24990](https://github.com/airbytehq/airbyte/pull/24990) | Add slicing to connector |
| 0.2.7 | 2023-02-13 | [22901](https://github.com/airbytehq/airbyte/pull/22901) | Specified date formatting in specification |
| 0.2.6 | 2023-02-21 | [22473](https://github.com/airbytehq/airbyte/pull/22473) | Use default availability strategy |
| 0.2.5 | 2023-01-27 | [22021](https://github.com/airbytehq/airbyte/pull/22021) | Set `AvailabilityStrategy` for streams explicitly to `None` |
| 0.2.4 | 2022-10-11 | [17822](https://github.com/airbytehq/airbyte/pull/17822) | Do not parse JSON in `should_retry` |
| 0.2.3 | 2022-10-11 | [17822](https://github.com/airbytehq/airbyte/pull/17822) | Do not parse JSON in `should_retry` |
| 0.2.2 | 2022-10-05 | [17608](https://github.com/airbytehq/airbyte/pull/17608) | Skip stream if we receive 403 error |
| 0.2.2 | 2022-09-28 | [17304](https://github.com/airbytehq/airbyte/pull/17304) | Migrate to per-stream state. |
| 0.2.1 | 2022-09-23 | [17080](https://github.com/airbytehq/airbyte/pull/17080) | Fix `total_weight` value to be `int` instead of `float` |
| 0.2.0 | 2022-09-21 | [16959](https://github.com/airbytehq/airbyte/pull/16959) | Use TypeTransformer to reliably convert to schema declared data types |
| 0.1.8 | 2022-08-27 | [16045](https://github.com/airbytehq/airbyte/pull/16045) | Force total_weight to be an integer |
| 0.1.7 | 2022-07-24 | [14978](https://github.com/airbytehq/airbyte/pull/14978) | Set `additionalProperties` to True, to guarantee backward cababilities |
| 0.1.6 | 2022-07-21 | [14902](https://github.com/airbytehq/airbyte/pull/14902) | Increased test coverage, fixed broken `charges`, `orders` schemas, added state checkpoint |
| 0.1.5 | 2022-01-26 | [9808](https://github.com/airbytehq/airbyte/pull/9808) | Update connector fields title/description |
| 0.1.4 | 2021-11-05 | [7626](https://github.com/airbytehq/airbyte/pull/7626) | Improve 'backoff' for HTTP requests |
| 0.1.3 | 2021-09-17 | [6149](https://github.com/airbytehq/airbyte/pull/6149) | Update `discount` and `order` schema |
| 0.1.2 | 2021-09-17 | [6149](https://github.com/airbytehq/airbyte/pull/6149) | Change `cursor_field` for Incremental streams |

</details>
