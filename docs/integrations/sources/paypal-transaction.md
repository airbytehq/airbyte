# PayPal Transaction

This page contains the setup guide and reference information for the PayPal Transaction source connector.

This connector uses [PayPal REST API](https://developer.paypal.com/api/rest/) OAuth 2.0 access tokens to authenticate requests.

## Prerequisites

- A PayPal Business account. You can create one by following the [PayPal get started guide](https://developer.paypal.com/api/rest/).
- A REST API app registered in the [PayPal Developer Dashboard](https://developer.paypal.com/dashboard/applications/live) to obtain your **Client ID** and **Client Secret**.
- **Transaction Search** enabled for your REST API app. In the PayPal Developer Dashboard, select your app and enable the **Transaction Search** checkbox under app settings. If your app was previously used for other API requests, it can take up to 9 hours for the new permission to take effect.

You can also set up a [sandbox environment](https://developer.paypal.com/tools/sandbox/) to test the connector before using it in production.

## Setup guide

### Step 1: Get your PayPal credentials

1. Log in to the [PayPal Developer Dashboard](https://developer.paypal.com/dashboard/applications/live).
2. Under **Apps & Credentials**, select your REST API app.
3. Copy your **Client ID** and **Client Secret**.

### Step 2: Set up the PayPal Transaction connector in Airbyte

1. Log in to your [Airbyte Cloud](https://cloud.airbyte.com/workspaces) account or open your Airbyte OSS instance.
2. In the left navigation bar, click **Sources**.
3. Search for **PayPal Transaction** and select it.
4. Enter a name for your source.
5. Enter your **Client ID**.
6. Enter your **Client Secret**.
7. Enter a **Start Date** in UTC format (`YYYY-MM-DDTHH:MM:SSZ`). The connector retrieves data from this date onward.
8. Toggle **Sandbox** on or off. The default is off, which targets the production PayPal environment.
9. (Optional) Enter a **Dispute Start Date Range** in UTC format with milliseconds (`YYYY-MM-DDTHH:MM:SS.sssZ`). This applies only to the `list_disputes` stream. If omitted, it defaults to 180 days in the past. The milliseconds component is required if you enter a value.
10. (Optional) Enter an **End Date** in UTC format (`YYYY-MM-DDTHH:MM:SSZ`). When omitted, the connector syncs up to the current time. This does not apply to the Disputes or Products streams.
11. (Optional) Enter a **Refresh Token**. The connector handles token refresh automatically, so this is not required in most cases.
12. (Optional) Set the **Number of days per request** to control the date range window per API call. The default is 7 days and the maximum is 31 days. Reducing this value can help avoid the PayPal API's 10,000-record limit per request.
13. Click **Set up source**.

:::info

By default, syncs are run with a slice period of 7 days. PayPal caps a transaction search at 10K records, and the `transactions` stream automatically retries a rejected slice as smaller date ranges. The sync only fails if a one-second date range is still rejected. If a sync fails with `Result set size is greater than the maximum limit` or `RESULTSET_TOO_LARGE`:

- Try lower the size of the slice period in your optional parameters in your connection configuration.
- You can try to lower the scheduling sync window in case a day slice period is not enough. Lowering the sync period it may help avoid reaching the 10K limit.

:::

## Supported sync modes

The PayPal Transaction source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature                   | Supported? |
| :------------------------ | :--------- |
| Full Refresh Sync         | Yes        |
| Incremental - Append Sync | Yes        |
| Namespaces                | No         |

## Supported streams

This connector syncs the following streams:

- [Transactions](https://developer.paypal.com/docs/api/transaction-search/v1/#transactions) (incremental)
- [Balances](https://developer.paypal.com/docs/api/transaction-search/v1/#balances) (incremental)
- [List Products](https://developer.paypal.com/docs/api/catalog-products/v1/#products_list) (full refresh)
- [Show Product Details](https://developer.paypal.com/docs/api/catalog-products/v1/#products_get) (full refresh)
- [List Disputes](https://developer.paypal.com/docs/api/customer-disputes/v1/#disputes_list) (incremental)
- [Search Invoices](https://developer.paypal.com/docs/api/invoicing/v2/#invoices_search-invoices) (full refresh)
- [List Payments](https://developer.paypal.com/docs/api/payments/v1/#payment_list) (incremental)

:::caution
The List Payments stream uses the [PayPal Payments API v1](https://developer.paypal.com/docs/api/payments/v1/), which PayPal has deprecated. This stream continues to work for accounts with existing v1 integrations, but PayPal recommends the [Orders API v2](https://developer.paypal.com/docs/api/orders/v2/) for new integrations. If this stream stops returning data, verify that your PayPal account still has access to the v1 Payments API.
:::

### Stream details

The following tables describe the configuration behavior and sync capabilities for each stream.

**Legend:** **(D)** = Default sync mode. **(F)** = Fixed value, not configurable.

#### Transactions

| Parameter                  | Value                     |
| :------------------------- | :------------------------ |
| Start Date                 | Timestamp with TZ (no ms) |
| Number of days per request | Max 31, default 7         |
| Pagination                 | Page increment            |
| Page size                  | 500 (F)                   |
| Full Refresh               | Yes                       |
| Incremental                | Yes (D)                   |

#### Balances

| Parameter                  | Value                     |
| :------------------------- | :------------------------ |
| Start Date                 | Timestamp with TZ (no ms) |
| Number of days per request | N/A                       |
| Pagination                 | N/A                       |
| Page size                  | N/A                       |
| Full Refresh               | Yes                       |
| Incremental                | Yes (D)                   |

#### List Products

| Parameter                  | Value          |
| :------------------------- | :------------- |
| Start Date                 | N/A            |
| Number of days per request | N/A            |
| Pagination                 | Page increment |
| Page size                  | 20 (F)         |
| Full Refresh               | Yes (D)        |
| Incremental                | No             |

:::caution
The PayPal Catalog Products API limits page size to 20 items. For large catalogs with more than 30,000 products, syncs can take 10-15 minutes or longer.
:::

#### Show Product Details

| Parameter                  | Value   |
| :------------------------- | :------ |
| Start Date                 | N/A     |
| Number of days per request | N/A     |
| Pagination                 | N/A     |
| Page size                  | N/A     |
| Full Refresh               | Yes (D) |
| Incremental                | No      |

:::caution
This stream retrieves details for each product individually using the parent `list_products` stream. Because the PayPal API processes requests sequentially and the parent stream paginates at 20 items per page, syncing large catalogs can take several hours.
:::

#### List Disputes

| Parameter                  | Value                       |
| :------------------------- | :-------------------------- |
| Dispute Start Date Range   | Timestamp with TZ (with ms) |
| Number of days per request | Max 180, default 7          |
| Pagination                 | Page token                  |
| Page size                  | 50 (F)                      |
| Full Refresh               | Yes                         |
| Incremental                | Yes (D)                     |

#### Search Invoices

| Parameter                  | Value                     |
| :------------------------- | :------------------------ |
| Start Date                 | Timestamp with TZ (no ms) |
| Number of days per request | N/A                       |
| Pagination                 | Page number               |
| Page size                  | 100 (F)                   |
| Full Refresh               | Yes (D)                   |
| Incremental                | No                        |

:::info
The `start_date` from the connector configuration is passed to the PayPal API as `creation_date_range.start` and `creation_date_range.end`. For more information, see the [PayPal Invoicing API documentation](https://developer.paypal.com/docs/api/invoicing/v2/#invoices_search-invoices).
:::

#### List Payments

| Parameter                  | Value                     |
| :------------------------- | :------------------------ |
| Start Date                 | Timestamp with TZ (no ms) |
| Number of days per request | Default 7                 |
| Pagination                 | Cursor-based              |
| Page size                  | 20 (F)                    |
| Full Refresh               | Yes                       |
| Incremental                | Yes (D)                   |

## Performance considerations

- **Data availability:** Executed transactions can take up to 3 hours to appear in the Transaction Search API.
- **Date range:** The maximum supported date range per request is 31 days for the Transactions stream.
- **Historical data:** The Transactions stream can retrieve up to 3 years of historical data. The List Disputes stream can retrieve up to 180 days.
- **Records per request:** The PayPal API limits responses to 10,000 records per request.
- **Page size:** Each stream uses the maximum page size allowed by its respective PayPal API endpoint. These values are fixed and not configurable.
- **Rate limiting:** PayPal does not publish specific rate limits but may temporarily throttle requests that appear abusive. If you encounter HTTP 429 errors, reduce your sync frequency or increase the **Number of days per request** to reduce the total number of API calls. For more details, see PayPal's [rate limiting guidelines](https://developer.paypal.com/reference/guidelines/rate-limiting/).

## Data type map

| Integration Type | Airbyte Type |
| :--------------- | :----------- |
| `string`         | `string`     |
| `number`         | `number`     |
| `array`          | `array`      |
| `object`         | `object`     |

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
| :------ | :--------- | :------------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------- |
| 2.6.61 | 2026-11-10 | [91676](https://github.com/airbytehq/airbyte/pull/91676) | Update dependencies |
| 2.6.60 | 2026-11-03 | [90673](https://github.com/airbytehq/airbyte/pull/90673) | Update dependencies |
| 2.6.59 | 2026-11-01 | [90328](https://github.com/airbytehq/airbyte/pull/90328) | Simplify error handling configuration with no change to retry, backoff, or window-splitting behavior |
| 2.6.58 | 2026-10-27 | [89998](https://github.com/airbytehq/airbyte/pull/89998) | Update dependencies |
| 2.6.57 | 2026-10-20 | [89356](https://github.com/airbytehq/airbyte/pull/89356) | Update dependencies |
| 2.6.56 | 2026-10-14 | [85249](https://github.com/airbytehq/airbyte/pull/85249) | Wait 100 seconds before each retry of a failed `transactions` request, such as on HTTP 429 or 5xx, as the other streams already do |
| 2.6.55 | 2026-10-13 | [88730](https://github.com/airbytehq/airbyte/pull/88730) | Update dependencies |
| 2.6.54 | 2026-10-06 | [87974](https://github.com/airbytehq/airbyte/pull/87974) | Update dependencies |
| 2.6.53 | 2026-09-29 | [87441](https://github.com/airbytehq/airbyte/pull/87441) | Keep the `list_disputes` start date inside PayPal's 180-day window to fix `INVALID_DATE_RANGE` 400 errors on first syncs |
| 2.6.52 | 2026-09-29 | [86920](https://github.com/airbytehq/airbyte/pull/86920) | feat(source-paypal-transaction): adopt declarative request_window_red… |
| 2.6.51 | 2026-09-29 | [87311](https://github.com/airbytehq/airbyte/pull/87311) | Update dependencies |
| 2.6.51 | 2026-09-22 | [86920](https://github.com/airbytehq/airbyte/pull/86920) | Replace the `transactions` stream's custom `DateWindowSplittingRetriever`/`ResultSetTooLargeErrorHandler` components with the CDK's declarative `request_window_splitting` feature; the stream's failure type when a window is rejected even at its smallest split changes from `config_error` to `transient_error` |
| 2.6.50 | 2026-09-22 | [86765](https://github.com/airbytehq/airbyte/pull/86765) | Update dependencies |
| 2.6.49 | 2026-09-15 | [86180](https://github.com/airbytehq/airbyte/pull/86180) | Update dependencies |
| 2.6.48 | 2026-09-08 | [84916](https://github.com/airbytehq/airbyte/pull/84916) | Retry oversized `transactions` date slices as smaller date ranges instead of failing the sync on the first `RESULTSET_TOO_LARGE` response |
| 2.6.47 | 2026-09-08 | [85594](https://github.com/airbytehq/airbyte/pull/85594) | Update dependencies |
| 2.6.46 | 2026-08-26 | [79676](https://github.com/airbytehq/airbyte/pull/79676) | Fix `transaction_id` primary key emitted as null for IDs resembling scientific notation |
| 2.6.45 | 2026-08-18 | [84690](https://github.com/airbytehq/airbyte/pull/84690) | Update dependencies |
| 2.6.44 | 2026-08-11 | [84075](https://github.com/airbytehq/airbyte/pull/84075) | Update dependencies |
| 2.6.43 | 2026-07-28 | [83194](https://github.com/airbytehq/airbyte/pull/83194) | Update to CDK 7.23.8 (fixes AirbyteCustomCodeNotPermittedError for bundled custom components) and remove the temporary Cloud version override |
| 2.6.42 | 2026-07-28 | [1082](https://github.com/airbytehq/airbyte-python-cdk/issues/1082) | Roll Cloud back to 2.6.40 — 2.6.41 is built on SDM 7.23.7, which breaks bundled custom components |
| 2.6.41 | 2026-07-28 | [83052](https://github.com/airbytehq/airbyte/pull/83052) | Update dependencies |
| 2.6.40 | 2026-07-21 | [82533](https://github.com/airbytehq/airbyte/pull/82533) | Update dependencies |
| 2.6.39 | 2026-07-14 | [81962](https://github.com/airbytehq/airbyte/pull/81962) | Update dependencies |
| 2.6.38 | 2026-06-30 | [81175](https://github.com/airbytehq/airbyte/pull/81175) | Update dependencies |
| 2.6.37 | 2026-06-23 | [80610](https://github.com/airbytehq/airbyte/pull/80610) | Update dependencies |
| 2.6.36 | 2026-06-16 | [79986](https://github.com/airbytehq/airbyte/pull/79986) | Update dependencies |
| 2.6.35 | 2026-06-09 | [79456](https://github.com/airbytehq/airbyte/pull/79456) | Update dependencies |
| 2.6.34 | 2026-06-02 | [78907](https://github.com/airbytehq/airbyte/pull/78907) | Update dependencies |
| 2.6.33 | 2026-04-28 | [77335](https://github.com/airbytehq/airbyte/pull/77335) | Update dependencies |
| 2.6.32 | 2026-04-21 | [76710](https://github.com/airbytehq/airbyte/pull/76710) | Update dependencies |
| 2.6.31 | 2026-04-09 | [76135](https://github.com/airbytehq/airbyte/pull/76135) | Fix undefined `security_context` variable in payments generator utility script |
| 2.6.30 | 2026-03-31 | [75850](https://github.com/airbytehq/airbyte/pull/75850) | Update dependencies |
| 2.6.29 | 2026-03-24 | [75396](https://github.com/airbytehq/airbyte/pull/75396) | Update dependencies |
| 2.6.28 | 2026-03-10 | [74484](https://github.com/airbytehq/airbyte/pull/74484) | Update dependencies |
| 2.6.27 | 2026-03-03 | [73875](https://github.com/airbytehq/airbyte/pull/73875) | Update dependencies |
| 2.6.26 | 2026-02-26 | [74027](https://github.com/airbytehq/airbyte/pull/74027) | Fix INVALID_DATE_TIME_FORMAT error on disputes stream by using 3-digit milliseconds |
| 2.6.25 | 2026-02-17 | [73574](https://github.com/airbytehq/airbyte/pull/73574) | Update dependencies |
| 2.6.24 | 2026-02-10 | [73171](https://github.com/airbytehq/airbyte/pull/73171) | Update dependencies |
| 2.6.23 | 2026-02-03 | [72637](https://github.com/airbytehq/airbyte/pull/72637) | Update dependencies |
| 2.6.22 | 2026-01-22 | [70967](https://github.com/airbytehq/airbyte/pull/70967) | Update HTTP response action for 400 error transactions from IGNORE to FAIL |
| 2.6.21 | 2026-01-20 | [71652](https://github.com/airbytehq/airbyte/pull/71652) | Update dependencies |
| 2.6.20 | 2025-12-18 | [70505](https://github.com/airbytehq/airbyte/pull/70505) | Update dependencies |
| 2.6.19 | 2025-11-25 | [69974](https://github.com/airbytehq/airbyte/pull/69974) | Update dependencies |
| 2.6.18 | 2025-11-18 | [69668](https://github.com/airbytehq/airbyte/pull/69668) | Update dependencies |
| 2.6.17 | 2025-10-29 | [69044](https://github.com/airbytehq/airbyte/pull/69044) | Update dependencies |
| 2.6.16 | 2025-10-21 | [68286](https://github.com/airbytehq/airbyte/pull/68286) | Update dependencies |
| 2.6.15 | 2025-10-14 | [67760](https://github.com/airbytehq/airbyte/pull/67760) | Update dependencies |
| 2.6.14 | 2025-10-07 | [67348](https://github.com/airbytehq/airbyte/pull/67348) | Update dependencies |
| 2.6.13 | 2025-09-30 | [66378](https://github.com/airbytehq/airbyte/pull/66378) | Update dependencies |
| 2.6.12 | 2025-09-09 | [65835](https://github.com/airbytehq/airbyte/pull/65835) | Update dependencies |
| 2.6.11 | 2025-08-23 | [65171](https://github.com/airbytehq/airbyte/pull/65171) | Update dependencies |
| 2.6.10 | 2025-08-09 | [64716](https://github.com/airbytehq/airbyte/pull/64716) | Update dependencies |
| 2.6.9 | 2025-08-02 | [64258](https://github.com/airbytehq/airbyte/pull/64258) | Update dependencies |
| 2.6.8 | 2025-07-26 | [63821](https://github.com/airbytehq/airbyte/pull/63821) | Update dependencies |
| 2.6.7 | 2025-07-19 | [63449](https://github.com/airbytehq/airbyte/pull/63449) | Update dependencies |
| 2.6.6 | 2025-07-12 | [63255](https://github.com/airbytehq/airbyte/pull/63255) | Update dependencies |
| 2.6.5 | 2025-07-05 | [62625](https://github.com/airbytehq/airbyte/pull/62625) | Update dependencies |
| 2.6.4 | 2025-06-28 | [62390](https://github.com/airbytehq/airbyte/pull/62390) | Update dependencies |
| 2.6.3 | 2025-06-21 | [61932](https://github.com/airbytehq/airbyte/pull/61932) | Update dependencies |
| 2.6.2 | 2025-06-14 | [51848](https://github.com/airbytehq/airbyte/pull/51848) | Update dependencies |
| 2.6.1 | 2025-06-05 | [58674](https://github.com/airbytehq/airbyte/pull/58674) | Update CDK to fix complex datatype errors with interpolation |
| 2.6.0 | 2024-10-23 | [47282](https://github.com/airbytehq/airbyte/pull/47282) | Migrate to Manifest-only |
| 2.5.8 | 2025-01-11 | [43797](https://github.com/airbytehq/airbyte/pull/43797) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 2.5.7 | 2024-06-25 | [40269](https://github.com/airbytehq/airbyte/pull/40269) | Update dependencies |
| 2.5.6 | 2024-06-22 | [40110](https://github.com/airbytehq/airbyte/pull/40110) | Update dependencies |
| 2.5.5 | 2024-06-04 | [38983](https://github.com/airbytehq/airbyte/pull/38983) | [autopull] Upgrade base image to v1.2.1 |
| 2.5.4 | 2024-05-20 | [38265](https://github.com/airbytehq/airbyte/pull/38265) | Replace AirbyteLogger with logging.Logger |
| 2.5.3 | 2024-04-24 | [36654](https://github.com/airbytehq/airbyte/pull/36654) | Schema descriptions |
| 2.5.2 | 2024-04-19 | [37435](https://github.com/airbytehq/airbyte/pull/37435) | Updated `manifest.yaml` to use the latest CDK Manifest version to fix the Incremental STATE values |
| 2.5.1 | 2024-03-15 | [36165](https://github.com/airbytehq/airbyte/pull/36165) | Unpin CDK Version |
| 2.5.0 | 2024-03-15 | [36173](https://github.com/airbytehq/airbyte/pull/36173) | Extended `Disputes` stream schema with missing properties |
| 2.4.0 | 2024-02-20 | [35465](https://github.com/airbytehq/airbyte/pull/35465) | Per-error reporting and continue sync on stream failures |
| 2.3.0 | 2024-02-14 | [34510](https://github.com/airbytehq/airbyte/pull/34510) | Silver certified. New Streams Added |
| 2.2.2 | 2024-02-09 | [35075](https://github.com/airbytehq/airbyte/pull/35075) | Manage dependencies with Poetry. |
| 2.2.1 | 2024-01-11 | [34155](https://github.com/airbytehq/airbyte/pull/34155) | prepare for airbyte-lib |
| 2.2.0 | 2023-10-25 | [31852](https://github.com/airbytehq/airbyte/pull/31852) | The size of the time_window can be configured |
| 2.1.2 | 2023-10-23 | [31759](https://github.com/airbytehq/airbyte/pull/31759) | Keep transaction_id as a string and fetch data in 7-day batches |
| 2.1.1 | 2023-10-19 | [31599](https://github.com/airbytehq/airbyte/pull/31599) | Base image migration: remove Dockerfile and use the python-connector-base image |
| 2.1.0 | 2023-08-14 | [29223](https://github.com/airbytehq/airbyte/pull/29223) | Migrate Python CDK to Low Code schema |
| 2.0.0 | 2023-07-05 | [27916](https://github.com/airbytehq/airbyte/pull/27916) | Update `Balances` schema |
| 1.0.0 | 2023-07-03 | [27968](https://github.com/airbytehq/airbyte/pull/27968) | mark `Client ID` and `Client Secret` as required fields |
| 0.1.13 | 2023-02-20 | [22916](https://github.com/airbytehq/airbyte/pull/22916) | Specified date formatting in specification |
| 0.1.12 | 2023-02-18 | [23211](https://github.com/airbytehq/airbyte/pull/23211) | Fix error handler |
| 0.1.11 | 2023-01-27 | [22019](https://github.com/airbytehq/airbyte/pull/22019) | Set `AvailabilityStrategy` for streams explicitly to `None` |
| 0.1.10 | 2022-09-04 | [17554](https://github.com/airbytehq/airbyte/pull/17554) | Made the spec and source config to be consistent |
| 0.1.9 | 2022-08-18 | [15741](https://github.com/airbytehq/airbyte/pull/15741) | Removed `OAuth2.0` option |
| 0.1.8 | 2022-07-25 | [15000](https://github.com/airbytehq/airbyte/pull/15000) | Added support of `OAuth2.0` authentication, fixed bug when normalization couldn't handle nested cursor field and primary key |
| 0.1.7 | 2022-07-18 | [14804](https://github.com/airbytehq/airbyte/pull/14804) | Added `RESULTSET_TOO_LARGE` error validation |
| 0.1.6 | 2022-06-10 | [13682](https://github.com/airbytehq/airbyte/pull/13682) | Updated paypal transaction schema |
| 0.1.5 | 2022-04-27 | [12335](https://github.com/airbytehq/airbyte/pull/12335) | Added fixtures to mock time.sleep for connectors that explicitly sleep |
| 0.1.4 | 2021-12-22 | [9034](https://github.com/airbytehq/airbyte/pull/9034) | Updated connector fields title/description |
| 0.1.3 | 2021-12-16 | [8580](https://github.com/airbytehq/airbyte/pull/8580) | Added more logs during `check connection` stage |
| 0.1.2 | 2021-11-08 | [7499](https://github.com/airbytehq/airbyte/pull/7499) | Removed base-python dependencies |
| 0.1.1 | 2021-08-03 | [5155](https://github.com/airbytehq/airbyte/pull/5155) | Fixed start_date_min limit |
| 0.1.0 | 2021-06-10 | [4240](https://github.com/airbytehq/airbyte/pull/4240) | PayPal Transaction Search API |

</details>
