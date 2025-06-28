# Recharge

This document guides you through setting up the Recharge source connector in Airbyte, allowing you to sync data from the [Recharge API](https://developer.rechargepayments.com/).

**Key Features:**
*   **Sync Modes:** Supports `Full Refresh` and `Incremental` syncs for core streams.
*   **API Version:** Primarily uses the `2021-11` API version. Includes an option to use the deprecated `2021-01` API for the `Orders` stream.
*   **Lookback Window:** Supports a configurable lookback window for most streams to re-fetch recent data.

## Prerequisites

Before setting up the Recharge source, ensure you have the following:

1.  **Recharge Account:**
    *   Permissions within your Recharge account to generate API tokens and access the data for the streams you intend to sync.
2.  **Recharge API Access Token:**
    *   You'll need an API Access Token with the appropriate permissions (scopes) for the data streams you wish to sync.
    *   Instructions for generating a token can be found here: [Recharge API Key Guide](https://developer.rechargepayments.com/docs/api-key-guide).
3.  **Recharge Plan:**
    *   Some streams are only available on specific Recharge plans (e.g., Pro, Custom). Ensure your plan supports the streams you need. See the [Permissions & Plan Requirements](#api-token-permissions-scopes--plan-requirements) section for details.

## Setup guide

### Step 1: Generate your Recharge API Access Token

1.  Follow the official Recharge documentation to [generate an API Access Token](https://developer.rechargepayments.com/docs/api-key-guide).
2.  When configuring the token, ensure you grant it the necessary **read permissions (scopes)** for all the data streams you plan to sync with Airbyte. Refer to the [API Token Permissions (Scopes) & Plan Requirements](#api-token-permissions-scopes--plan-requirements) section below for a detailed list of required scopes per stream.

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
The Recharge source connector supports the following sync modes:

| Feature           | Supported? | Description                                                                                                |
| :---------------- | :--------- | :--------------------------------------------------------------------------------------------------------- |
| Full Refresh Sync | ✅ Yes     | Replicates all available data from the source for selected streams.                                        |
| Incremental Sync  | ✅ Yes     | Replicates new or modified data since the last sync, based on a cursor field (datetime).                   |
| SSL Connection    | ✅ Yes     | All requests to the Recharge API are made over HTTPS, ensuring data is encrypted in transit.               |

## Streams

| Stream Name        | API Docs                                                                                                                                         | Primary Key | Supports Full Refresh | Supports Incremental | Plan Requirement             |
| :----------------- | :----------------------------------------------------------------------------------------------------------------------------------------------- | :---------- | :-------------------- | :------------------- | :--------------------------- |
| Addresses          | [2021-11](https://developer.rechargepayments.com/2021-11/addresses)                                                                              | id          | ✅                    | ✅                   | ✅ Standard Plan             |
| Bundle Selections  | [2021-11](https://developer.rechargepayments.com/2021-11/bundle_selections)                                                                      | id          | ✅                    | ✅                   | 🎯 Pro and Custom plans only |
| Charges            | [2021-11](https://developer.rechargepayments.com/2021-11/charges)                                                                                | id          | ✅                    | ✅                   | ✅ Standard Plan             |
| Collections        | [2021-11](https://developer.rechargepayments.com/2021-11/collections)                                                                            | id          | ✅                    | ❌                   | ✅ Standard Plan             |
| Credit Adjustments | [2021-11](https://developer.rechargepayments.com/2021-11/credits)                                                                                | id          | ✅                    | ✅                   | 🎯 Pro and Custom plans only |
| Customers          | [2021-11](https://developer.rechargepayments.com/2021-11/customers)                                                                              | id          | ✅                    | ✅                   | ✅ Standard Plan             |
| Discounts          | [2021-11](https://developer.rechargepayments.com/2021-11/discounts)                                                                              | id          | ✅                    | ✅                   | ✅ Standard Plan             |
| Events             | [2021-11](https://developer.rechargepayments.com/2021-11/events)                                                                                 | id          | ✅                    | ✅                   | ✅ Standard Plan             |
| Metafields         | [2021-11](https://developer.rechargepayments.com/2021-11/metafields)                                                                             | id          | ✅                    | ❌                   | ✅ Standard Plan             |
| Onetimes           | [2021-11](https://developer.rechargepayments.com/2021-11/onetimes)                                                                               | id          | ✅                    | ✅                   | ✅ Standard Plan             |
| Orders             | [2021-11](https://developer.rechargepayments.com/2021-11/orders) / [2021-01 (Deprecated)](https://developer.rechargepayments.com/2021-01/orders) | id          | ✅                    | ✅                   | ✅ Standard Plan             |
| Payment Methods    | [2021-11](https://developer.rechargepayments.com/2021-11/payment_methods)                                                                        | id          | ✅                    | ❌                   | 🎯 Pro and Custom plans only |
| Products           | [2021-11](https://developer.rechargepayments.com/2021-11/products)                                                                               | id          | ✅                    | ❌                   | ✅ Standard Plan             |
| Shop               | [2021-01 (Deprecated)](https://developer.rechargepayments.com/2021-01#shop)                                                                      | id          | ✅                    | ❌                   | ✅ Standard Plan             |
| Subscriptions      | [2021-11](https://developer.rechargepayments.com/2021-11/subscriptions)                                                                          | id          | ✅                    | ✅                   | ✅ Standard Plan             |

**Notes on Streams:**
*   **Orders Stream:** The connector uses the `2021-11` API for the `Orders` stream. If you need to use the deprecated `2021-01` API for orders, enable the **Use `Orders` Deprecated API** toggle in the connector configuration.
*   **Shop Stream:** The `Shop` stream currently utilizes the deprecated `2021-01` API version. An updated stream (`Store`) using a newer API version has not yet been implemented in this connector.

If there are more endpoints you'd like Airbyte to support, please [create an issue](https://github.com/airbytehq/airbyte/issues/new/choose).

### Lookback Window

The connector supports a configurable **Lookback Window (days)**. This feature allows the connector to re-fetch data from the specified number of days in the past during each incremental sync. This can be useful for capturing late-arriving or updated records.

**Lookback Window for `events` Stream:**
*   The `events` stream API has a limitation where it does not support querying data older than 7 days. At present, the lookback window setting does not affect the `events` stream.

## API Token Permissions (Scopes) & Plan Requirements

To successfully sync data from specific streams, your Recharge API Access Token must have the corresponding read permissions (scopes). Additionally, some streams are only available if your Recharge account is on a specific plan.

### **Error Handling for Permissions & Plans:**
> 403 - The request was authenticated but not authorized for the requested resource (permission scope error)


This error from Recharge can occur due to:

*   **Missing Scope:** This is the primary cause for the 403 error. If your API token lacks the necessary scope for a selected stream, the sync will fail.
*   **Missing Plan:** If your Recharge account is not on the required plan for a selected stream, the sync for that stream will also fail. 

The following table lists the required read scopes and plan requirements for each stream:

| Stream Name        | Required Read Scope(s)                                                                                                                                | Plan Requirement         |
| :----------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------- | :----------------------- |
| Addresses          | `read_customers`                                                                                                                                      | Standard Plan            |
| Bundle Selections  | `read_subscriptions`                                                                                                                                  | Pro or Custom plans only |
| Charges            | `read_orders`                                                                                                                                         | Standard Plan            |
| Collections        | `read_products`                                                                                                                                       | Standard Plan            |
| Credit Adjustments | `read_credit_adjustments`                                                                                                                             | Pro and Custom only      |
| Customers          | `read_customers`                                                                                                                                      | Standard Plan            |
| Discounts          | `read_discounts`                                                                                                                                      | Standard Plan            |
| Events             | `read_events`                                                                                                                                         | Standard Plan            |
| Metafields         | `read_address`, `read_customer`, `read_subscription`, `read_order`, `read_charge` (Enable scopes for the resources whose metafields you want to sync) | Standard Plan            |
| Onetimes           | `read_subscriptions`                                                                                                                                  | Standard Plan            |
| Orders             | `read_orders`                                                                                                                                         | Standard Plan            |
| Payment Methods    | `read_payment_methods`                                                                                                                                | Pro or Custom plans only |
| Products           | `read_products`                                                                                                                                       | Standard Plan            |
| Shop               | `read_shop`                                                                                                                                           | Standard Plan            |
| Subscriptions      | `read_subscriptions`                                                                                                                                  | Standard Plan            |

## Performance Considerations

The Recharge connector is designed to handle Recharge API limitations under normal usage.

### Rate Limiting

Recharge implements rate limits to ensure API stability and fair usage. The API uses a "leaky bucket" algorithm, which allows for infrequent bursts of calls but maintains a sustainable request rate over time.
*   If the request rate exceeds the limit, the API will return a `429 - The request has been rate limited` error.
*   When a `429` error is received, this Airbyte connector will automatically:
    *   Pause for 2 seconds.
    *   Retry the request.
    *   This retry process can happen up to 10 times.

For more details, see [Recharge API Rate Limits](https://developer.rechargepayments.com/docs/api-rate-limits).

### Error Handling

*   **Transient HTTP Errors:** Common transient errors (e.g., `500 - Internal server error`, `503 - A 3rd party service on which the request depends has timed out`) are handled by Airbyte's `DefaultErrorHandler`. This mechanism retries requests with an exponential backoff strategy, up to a maximum of 10 retries.
*   **Persistent Issues:** If you consistently encounter rate limit issues or other errors that are not automatically resolved by the connector's retry mechanisms, please [create an issue](https://github.com/airbytehq/airbyte/issues/new/choose) on GitHub with relevant logs and details.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                                                                        |
|:--------|:-----------| :------------------------------------------------------- |:-------------------------------------------------------------------------------------------------------------------------------|
| 2.10.1 | 2025-06-14 | [61073](https://github.com/airbytehq/airbyte/pull/61073) | Update dependencies |
| 2.10.0 | 2025-05-29 | [60810](https://github.com/airbytehq/airbyte/pull/60810) | Add new `payment_methods` stream |
| 2.9.1 | 2025-05-24 | [60151](https://github.com/airbytehq/airbyte/pull/60151) | Update dependencies |
| 2.9.0 | 2025-05-16 | [60317](https://github.com/airbytehq/airbyte/pull/60317) | Improve 429 error handler |
| 2.8.0 | 2025-05-14 | [60265](https://github.com/airbytehq/airbyte/pull/60265) | Added `credit_adjustments` stream |
| 2.7.0 | 2025-05-08 | [59734](https://github.com/airbytehq/airbyte/pull/59734) | Added lookback window to connector manifest configuration |
| 2.6.14 | 2025-05-04 | [59512](https://github.com/airbytehq/airbyte/pull/59512) | Update dependencies |
| 2.6.13 | 2025-04-27 | [59114](https://github.com/airbytehq/airbyte/pull/59114) | Update dependencies |
| 2.6.12 | 2025-04-19 | [58454](https://github.com/airbytehq/airbyte/pull/58454) | Update dependencies |
| 2.6.11 | 2025-04-12 | [57867](https://github.com/airbytehq/airbyte/pull/57867) | Update dependencies |
| 2.6.10 | 2025-04-05 | [57369](https://github.com/airbytehq/airbyte/pull/57369) | Update dependencies |
| 2.6.9 | 2025-03-29 | [56739](https://github.com/airbytehq/airbyte/pull/56739) | Update dependencies |
| 2.6.8 | 2025-03-22 | [56218](https://github.com/airbytehq/airbyte/pull/56218) | Update dependencies |
| 2.6.7 | 2025-03-08 | [55068](https://github.com/airbytehq/airbyte/pull/55068) | Update dependencies |
| 2.6.6 | 2025-02-22 | [54547](https://github.com/airbytehq/airbyte/pull/54547) | Update dependencies |
| 2.6.5 | 2025-02-15 | [53943](https://github.com/airbytehq/airbyte/pull/53943) | Update dependencies |
| 2.6.4 | 2025-02-01 | [53018](https://github.com/airbytehq/airbyte/pull/53018) | Update dependencies |
| 2.6.3 | 2025-01-25 | [52468](https://github.com/airbytehq/airbyte/pull/52468) | Update dependencies |
| 2.6.2 | 2025-01-18 | [51914](https://github.com/airbytehq/airbyte/pull/51914) | Update dependencies |
| 2.6.1 | 2025-01-11 | [51333](https://github.com/airbytehq/airbyte/pull/51333) | Update dependencies |
| 2.6.0 | 2025-01-02 | [48382](https://github.com/airbytehq/airbyte/pull/49926) | Add new stream `bundle_selections` |
| 2.5.4 | 2025-01-04 | [50927](https://github.com/airbytehq/airbyte/pull/50927) | Update dependencies |
| 2.5.3 | 2024-12-28 | [50724](https://github.com/airbytehq/airbyte/pull/50724) | Update dependencies |
| 2.5.2 | 2024-12-21 | [50265](https://github.com/airbytehq/airbyte/pull/50265) | Update dependencies |
| 2.5.1 | 2024-12-14 | [49081](https://github.com/airbytehq/airbyte/pull/49081) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 2.5.0 | 2024-11-26 | [48382](https://github.com/airbytehq/airbyte/pull/48382) | Add new stream `events` |
| 2.4.15 | 2024-11-04 | [48242](https://github.com/airbytehq/airbyte/pull/48242) | Update dependencies |
| 2.4.14 | 2024-10-29 | [47890](https://github.com/airbytehq/airbyte/pull/47890) | Update dependencies |
| 2.4.13 | 2024-10-28 | [47037](https://github.com/airbytehq/airbyte/pull/47037) | Update dependencies |
| 2.4.12 | 2024-10-12 | [46797](https://github.com/airbytehq/airbyte/pull/46797) | Update dependencies |
| 2.4.11 | 2024-10-05 | [46510](https://github.com/airbytehq/airbyte/pull/46510) | Update dependencies |
| 2.4.10 | 2024-09-28 | [46110](https://github.com/airbytehq/airbyte/pull/46110) | Update dependencies |
| 2.4.9 | 2024-09-21 | [45739](https://github.com/airbytehq/airbyte/pull/45739) | Update dependencies |
| 2.4.8 | 2024-09-14 | [45520](https://github.com/airbytehq/airbyte/pull/45520) | Update dependencies |
| 2.4.7 | 2024-09-07 | [45321](https://github.com/airbytehq/airbyte/pull/45321) | Update dependencies |
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
