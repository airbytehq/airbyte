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
By default, syncs use a 7-day slice period. If you see errors with the message `Result set size is greater than the maximum limit` or the error code `RESULTSET_TOO_LARGE`, reduce the **Number of days per request** in your connection configuration. You can also increase the sync frequency so each sync covers a shorter time range.
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

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                                                                      |
| :------ | :--------- | :------------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------- |
| 2.6.31 | 2026-04-08 | [76135](https://github.com/airbytehq/airbyte/pull/76135) | Fix undefined `security_context` variable in payments generator utility script |
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