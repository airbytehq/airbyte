# PayPal Transaction

This page contains the setup guide and reference information for the PayPal Transaction source connector.

The connector reads from PayPal's REST APIs and authenticates with the [OAuth 2.0 client credentials grant](https://developer.paypal.com/api/rest/authentication/), exchanging your client ID and secret for a short-lived access token on every sync.

## Prerequisites

- A PayPal business account. Personal accounts can't call the business-level APIs this connector reads from.
- A REST API app in the PayPal Developer Dashboard. The app provides the client ID and client secret the connector uses.
- The **Transaction Search** feature enabled on that app. The `transactions` and `balances` streams call the [Transaction Search API](https://developer.paypal.com/docs/api/transaction-search/v1/), which requires the `https://uri.paypal.com/services/reporting/search/read` scope. Without it, PayPal rejects those streams with `NOT_AUTHORIZED`.

:::warning

If the app already made other PayPal API requests before you enabled **Transaction Search**, PayPal says the new permission can take up to nine hours to apply to newly issued access tokens. Until it does, the `transactions` and `balances` streams keep failing with permission errors.

:::

## Setup guide

### Step 1: Get your PayPal credentials

1. Log in to the [PayPal Developer Dashboard](https://developer.paypal.com/dashboard/).
2. Go to **Apps & Credentials** and switch to **Live** or **Sandbox**, depending on the environment you want to sync. To test the connector first, use **Sandbox** and create test accounts in [Sandbox accounts](https://developer.paypal.com/tools/sandbox/accounts/).
3. Open your REST API app, then copy the **Client ID** and **Secret**.
4. In the app's feature list, select **Transaction Search** and save.

### Step 2: Set up the PayPal Transaction connector in Airbyte

1. In the Airbyte UI, click **Sources**, then search for and select **PayPal Transaction**.
2. Name the source.
3. Enter your **Client ID** and **Client secret**.
4. For **Start Date**, enter a UTC timestamp in the format `YYYY-MM-DDTHH:MM:SSZ`. PayPal serves at most three years of history, so `transactions` and `balances` clamp anything older to three years before the sync. Because transactions can take up to three hours to appear in the reporting API, choose a start date at least 12 hours in the past.
5. Turn the **Sandbox** toggle on to read from `api-m.sandbox.paypal.com`. It's off by default, which reads from production (`api-m.paypal.com`).
6. Optional: for **Dispute Start Date Range**, enter a UTC timestamp with exactly three digits of milliseconds, such as `2021-06-11T23:59:59.000Z`. This applies only to `list_disputes`. PayPal returns disputes updated within the last 180 days, so the connector falls back to 180 days ago when you leave this empty or enter an older timestamp.
7. Optional: for **End Date**, enter a UTC timestamp in the format `YYYY-MM-DDTHH:MM:SSZ` to stop syncing at a fixed point instead of the current time. This is mainly useful for backfills and data integrity checks. It doesn't apply to `list_disputes`, `list_products`, or `show_product_details`.
8. Leave **Refresh token** empty. The connector requests tokens with the client credentials grant and doesn't read this field.
9. Optional: set **Number of days per request** to change the size of the date window the connector requests at a time. Valid values are 1 to 31, and the default is 7. This applies to `transactions`, `list_disputes`, and `list_payments`.
10. Click **Set up source**.

:::info

PayPal returns at most 10,000 records per request. If a sync fails with `RESULTSET_TOO_LARGE` or the message `Result set size is greater than the maximum limit`, one of your date windows contains more records than that. Lower **Number of days per request**, and if a one-day window still exceeds the limit, sync more frequently so each window covers less data.

:::

## Supported sync modes

The PayPal Transaction source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature                   | Supported? |
| :------------------------ | :--------- |
| Full Refresh Sync         | Yes        |
| Incremental - Append Sync | Yes        |
| Namespaces                | No         |

## Supported streams

| Stream                                                                             | PayPal endpoint                      | Sync modes                | Cursor field               | Page size              | Date window                         |
| :--------------------------------------------------------------------------------- | :----------------------------------- | :------------------------ | :------------------------- | :--------------------- | :---------------------------------- |
| [Transactions](https://developer.paypal.com/docs/api/transaction-search/v1/)       | `GET /v1/reporting/transactions`     | Full refresh, incremental | `transaction_updated_date` | 500                    | 1 to 31 days (default 7)            |
| [Balances](https://developer.paypal.com/docs/api/transaction-search/v1/)           | `GET /v1/reporting/balances`         | Full refresh, incremental | `as_of_time`               | Not paginated          | One request per cursor value        |
| [List Products](https://developer.paypal.com/docs/api/catalog-products/v1/)        | `GET /v1/catalogs/products`          | Full refresh              | None                       | 20                     | Not applicable                      |
| [Show Product Details](https://developer.paypal.com/docs/api/catalog-products/v1/) | `GET /v1/catalogs/products/{id}`     | Full refresh              | None                       | One record per request | Not applicable                      |
| [List Disputes](https://developer.paypal.com/docs/api/customer-disputes/v1/)       | `GET /v1/customer/disputes`          | Full refresh, incremental | `updated_time_cut`         | 50                     | 1 to 31 days (default 7)            |
| [Search Invoices](https://developer.paypal.com/docs/api/invoicing/v2/)             | `POST /v2/invoicing/search-invoices` | Full refresh              | None                       | 100                    | Start Date to End Date in one range |
| [List Payments](https://developer.paypal.com/api/deprecated/payments/v1)           | `GET /v1/payments/payment`           | Full refresh, incremental | `update_time`              | 20                     | 1 to 31 days (default 7)            |

Page sizes are fixed and can't be configured.

### Stream details

- **Transactions** requests `fields=all`, so each record contains every transaction detail section PayPal exposes. PayPal caps each request at a 31-day range and 10,000 records, and needs up to three hours to make an executed transaction available.
- **Balances** requests one `as_of_time` per cursor value rather than a date range, so **Number of days per request** has no effect on it.
- **Show Product Details** reads one product per request, using the IDs from `list_products` as partitions. Because `list_products` pages 20 products at a time and PayPal serves these requests sequentially, a large catalog takes a long time to sync: a catalog of 30,000 products can take 10 to 15 minutes to list, and syncing the details for every product can take hours. Schedule these two streams when a long-running sync is acceptable.
- **List Disputes** uses millisecond precision throughout. It reads disputes updated between **Dispute Start Date Range** (or 180 days ago) and 30 minutes before the sync starts, which avoids PayPal's `INVALID_DATE_TIME_FORMAT` and `INVALID_DATE_RANGE` errors.
- **Search Invoices** sends `creation_date_range` in the request body, from **Start Date** to **End Date** or the current time. It filters on invoice creation date, so invoices created before **Start Date** never appear even if they were paid or updated later.

:::warning

PayPal has [deprecated the `/v1/payments` API](https://developer.paypal.com/api/deprecated/payments/v1) that backs the `list_payments` stream, in favor of `/v2/payments`. PayPal hasn't published a shutdown date. Expect this stream to change or be removed in a future connector version, and prefer `transactions` if you only need transaction-level data.

:::

## Performance considerations

- **Rate limits**: PayPal [doesn't publish rate limits](https://developer.paypal.com/api/rest/reference/rate-limiting/) and throttles traffic it considers abusive with HTTP 429 `RATE_LIMIT_REACHED`. Every stream except `transactions` waits a fixed 100 seconds before retrying a retryable response, including 429 and 5XX. Token requests retry 429 and 5XX responses with exponential backoff. **Number of days per request** trades request size against request count: a larger window means fewer, larger requests but a higher chance of hitting the 10,000-record limit, and a smaller window means more requests.
- **Historical data**: `transactions` and `balances` can't read more than three years of history. `list_disputes` can't read more than 180 days.
- **Failing early on unavailable data**: `transactions` fails the sync when PayPal answers `Data for the given start date is not available`, rather than skipping the window silently. This usually means the start date is outside PayPal's three-year window.

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

| Version | Date       | Pull Request                                                        | Subject                                                                                                                                                                |
| :------ | :--------- | :------------------------------------------------------------------ | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2.6.46  | 2026-08-26 | [79676](https://github.com/airbytehq/airbyte/pull/79676)            | Fix `transaction_id` primary key emitted as null for IDs resembling scientific notation                                                                                |
| 2.6.45  | 2026-08-18 | [84690](https://github.com/airbytehq/airbyte/pull/84690)            | Update dependencies                                                                                                                                                    |
| 2.6.44  | 2026-08-11 | [84075](https://github.com/airbytehq/airbyte/pull/84075)            | Update dependencies                                                                                                                                                    |
| 2.6.43  | 2026-07-28 | [83194](https://github.com/airbytehq/airbyte/pull/83194)            | Update to CDK 7.23.8 (fixes AirbyteCustomCodeNotPermittedError for bundled custom components) and remove the temporary Cloud version override                          |
| 2.6.42  | 2026-07-28 | [1082](https://github.com/airbytehq/airbyte-python-cdk/issues/1082) | Roll Cloud back to 2.6.40 — 2.6.41 is built on SDM 7.23.7, which breaks bundled custom components                                                                      |
| 2.6.41  | 2026-07-28 | [83052](https://github.com/airbytehq/airbyte/pull/83052)            | Update dependencies                                                                                                                                                    |
| 2.6.40  | 2026-07-21 | [82533](https://github.com/airbytehq/airbyte/pull/82533)            | Update dependencies                                                                                                                                                    |
| 2.6.39  | 2026-07-14 | [81962](https://github.com/airbytehq/airbyte/pull/81962)            | Update dependencies                                                                                                                                                    |
| 2.6.38  | 2026-06-30 | [81175](https://github.com/airbytehq/airbyte/pull/81175)            | Update dependencies                                                                                                                                                    |
| 2.6.37  | 2026-06-23 | [80610](https://github.com/airbytehq/airbyte/pull/80610)            | Update dependencies                                                                                                                                                    |
| 2.6.36  | 2026-06-16 | [79986](https://github.com/airbytehq/airbyte/pull/79986)            | Update dependencies                                                                                                                                                    |
| 2.6.35  | 2026-06-09 | [79456](https://github.com/airbytehq/airbyte/pull/79456)            | Update dependencies                                                                                                                                                    |
| 2.6.34  | 2026-06-02 | [78907](https://github.com/airbytehq/airbyte/pull/78907)            | Update dependencies                                                                                                                                                    |
| 2.6.33  | 2026-04-28 | [77335](https://github.com/airbytehq/airbyte/pull/77335)            | Update dependencies                                                                                                                                                    |
| 2.6.32  | 2026-04-21 | [76710](https://github.com/airbytehq/airbyte/pull/76710)            | Update dependencies                                                                                                                                                    |
| 2.6.31  | 2026-04-07 | [76135](https://github.com/airbytehq/airbyte/pull/76135)            | Fix undefined `security_context` variable in payments generator utility script                                                                                         |
| 2.6.30  | 2026-03-31 | [75850](https://github.com/airbytehq/airbyte/pull/75850)            | Update dependencies                                                                                                                                                    |
| 2.6.29  | 2026-03-24 | [75396](https://github.com/airbytehq/airbyte/pull/75396)            | Update dependencies                                                                                                                                                    |
| 2.6.28  | 2026-03-10 | [74484](https://github.com/airbytehq/airbyte/pull/74484)            | Update dependencies                                                                                                                                                    |
| 2.6.27  | 2026-03-03 | [73875](https://github.com/airbytehq/airbyte/pull/73875)            | Update dependencies                                                                                                                                                    |
| 2.6.26  | 2026-02-27 | [74027](https://github.com/airbytehq/airbyte/pull/74027)            | Fix INVALID_DATE_TIME_FORMAT error on disputes stream by using 3-digit milliseconds                                                                                    |
| 2.6.25  | 2026-02-17 | [73574](https://github.com/airbytehq/airbyte/pull/73574)            | Update dependencies                                                                                                                                                    |
| 2.6.24  | 2026-02-10 | [73171](https://github.com/airbytehq/airbyte/pull/73171)            | Update dependencies                                                                                                                                                    |
| 2.6.23  | 2026-02-06 | [72637](https://github.com/airbytehq/airbyte/pull/72637)            | Update dependencies                                                                                                                                                    |
| 2.6.22  | 2026-01-22 | [71846](https://github.com/airbytehq/airbyte/pull/71846)            | Update HTTP response action for 400 error transactions from IGNORE to FAIL                                                                                             |
| 2.6.21  | 2026-01-20 | [71652](https://github.com/airbytehq/airbyte/pull/71652)            | Update dependencies                                                                                                                                                    |
| 2.6.20  | 2025-12-18 | [70505](https://github.com/airbytehq/airbyte/pull/70505)            | Update dependencies                                                                                                                                                    |
| 2.6.19  | 2025-11-25 | [69974](https://github.com/airbytehq/airbyte/pull/69974)            | Update dependencies                                                                                                                                                    |
| 2.6.18  | 2025-11-18 | [69668](https://github.com/airbytehq/airbyte/pull/69668)            | Update dependencies                                                                                                                                                    |
| 2.6.17  | 2025-10-29 | [69044](https://github.com/airbytehq/airbyte/pull/69044)            | Update dependencies                                                                                                                                                    |
| 2.6.16  | 2025-10-21 | [68286](https://github.com/airbytehq/airbyte/pull/68286)            | Update dependencies                                                                                                                                                    |
| 2.6.15  | 2025-10-14 | [67760](https://github.com/airbytehq/airbyte/pull/67760)            | Update dependencies                                                                                                                                                    |
| 2.6.14  | 2025-10-07 | [67348](https://github.com/airbytehq/airbyte/pull/67348)            | Update dependencies                                                                                                                                                    |
| 2.6.13  | 2025-09-30 | [66378](https://github.com/airbytehq/airbyte/pull/66378)            | Update dependencies                                                                                                                                                    |
| 2.6.12  | 2025-09-09 | [65835](https://github.com/airbytehq/airbyte/pull/65835)            | Update dependencies                                                                                                                                                    |
| 2.6.11  | 2025-08-23 | [65171](https://github.com/airbytehq/airbyte/pull/65171)            | Update dependencies                                                                                                                                                    |
| 2.6.10  | 2025-08-09 | [64716](https://github.com/airbytehq/airbyte/pull/64716)            | Update dependencies                                                                                                                                                    |
| 2.6.9   | 2025-08-02 | [64258](https://github.com/airbytehq/airbyte/pull/64258)            | Update dependencies                                                                                                                                                    |
| 2.6.8   | 2025-07-26 | [63821](https://github.com/airbytehq/airbyte/pull/63821)            | Update dependencies                                                                                                                                                    |
| 2.6.7   | 2025-07-19 | [63449](https://github.com/airbytehq/airbyte/pull/63449)            | Update dependencies                                                                                                                                                    |
| 2.6.6   | 2025-07-12 | [63255](https://github.com/airbytehq/airbyte/pull/63255)            | Update dependencies                                                                                                                                                    |
| 2.6.5   | 2025-07-05 | [62625](https://github.com/airbytehq/airbyte/pull/62625)            | Update dependencies                                                                                                                                                    |
| 2.6.4   | 2025-06-28 | [62390](https://github.com/airbytehq/airbyte/pull/62390)            | Update dependencies                                                                                                                                                    |
| 2.6.3   | 2025-06-21 | [61932](https://github.com/airbytehq/airbyte/pull/61932)            | Update dependencies                                                                                                                                                    |
| 2.6.2   | 2025-06-16 | [51848](https://github.com/airbytehq/airbyte/pull/51848)            | Update dependencies                                                                                                                                                    |
| 2.6.1   | 2025-06-05 | [58674](https://github.com/airbytehq/airbyte/pull/58674)            | Update CDK to fix complex datatype errors with interpolation                                                                                                           |
| 2.6.0   | 2025-03-05 | [47282](https://github.com/airbytehq/airbyte/pull/47282)            | Migrate to Manifest-only                                                                                                                                               |
| 2.5.8   | 2025-01-15 | [43797](https://github.com/airbytehq/airbyte/pull/43797)            | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 2.5.7   | 2024-06-25 | [40269](https://github.com/airbytehq/airbyte/pull/40269)            | Update dependencies                                                                                                                                                    |
| 2.5.6   | 2024-06-22 | [40110](https://github.com/airbytehq/airbyte/pull/40110)            | Update dependencies                                                                                                                                                    |
| 2.5.5   | 2024-06-04 | [38983](https://github.com/airbytehq/airbyte/pull/38983)            | [autopull] Upgrade base image to v1.2.1                                                                                                                                |
| 2.5.4   | 2024-05-20 | [38265](https://github.com/airbytehq/airbyte/pull/38265)            | Replace AirbyteLogger with logging.Logger                                                                                                                              |
| 2.5.3   | 2024-04-24 | [36654](https://github.com/airbytehq/airbyte/pull/36654)            | Schema descriptions                                                                                                                                                    |
| 2.5.2   | 2024-04-19 | [37435](https://github.com/airbytehq/airbyte/pull/37435)            | Updated `manifest.yaml` to use the latest CDK Manifest version to fix the Incremental STATE values                                                                     |
| 2.5.1   | 2024-03-15 | [36165](https://github.com/airbytehq/airbyte/pull/36165)            | Unpin CDK Version                                                                                                                                                      |
| 2.5.0   | 2024-03-15 | [36173](https://github.com/airbytehq/airbyte/pull/36173)            | Extended `Disputes` stream schema with missing properties                                                                                                              |
| 2.4.0   | 2024-02-20 | [35465](https://github.com/airbytehq/airbyte/pull/35465)            | Per-error reporting and continue sync on stream failures                                                                                                               |
| 2.3.0   | 2024-02-14 | [34510](https://github.com/airbytehq/airbyte/pull/34510)            | Silver certified. New Streams Added                                                                                                                                    |
| 2.2.2   | 2024-02-09 | [35075](https://github.com/airbytehq/airbyte/pull/35075)            | Manage dependencies with Poetry.                                                                                                                                       |
| 2.2.1   | 2024-01-11 | [34155](https://github.com/airbytehq/airbyte/pull/34155)            | prepare for airbyte-lib                                                                                                                                                |
| 2.2.0   | 2023-10-25 | [31852](https://github.com/airbytehq/airbyte/pull/31852)            | The size of the time_window can be configured                                                                                                                          |
| 2.1.2   | 2023-10-23 | [31759](https://github.com/airbytehq/airbyte/pull/31759)            | Keep transaction_id as a string and fetch data in 7-day batches                                                                                                        |
| 2.1.1   | 2023-10-19 | [31599](https://github.com/airbytehq/airbyte/pull/31599)            | Base image migration: remove Dockerfile and use the python-connector-base image                                                                                        |
| 2.1.0   | 2023-08-14 | [29223](https://github.com/airbytehq/airbyte/pull/29223)            | Migrate Python CDK to Low Code schema                                                                                                                                  |
| 2.0.0   | 2023-07-05 | [27916](https://github.com/airbytehq/airbyte/pull/27916)            | Update `Balances` schema                                                                                                                                               |
| 1.0.0   | 2023-07-03 | [27968](https://github.com/airbytehq/airbyte/pull/27968)            | mark `Client ID` and `Client Secret` as required fields                                                                                                                |
| 0.1.13  | 2023-02-20 | [22916](https://github.com/airbytehq/airbyte/pull/22916)            | Specified date formatting in specification                                                                                                                             |
| 0.1.12  | 2023-02-18 | [23211](https://github.com/airbytehq/airbyte/pull/23211)            | Fix error handler                                                                                                                                                      |
| 0.1.11  | 2023-01-27 | [22019](https://github.com/airbytehq/airbyte/pull/22019)            | Set `AvailabilityStrategy` for streams explicitly to `None`                                                                                                            |
| 0.1.10  | 2022-09-04 | [17554](https://github.com/airbytehq/airbyte/pull/17554)            | Made the spec and source config to be consistent                                                                                                                       |
| 0.1.9   | 2022-08-18 | [15741](https://github.com/airbytehq/airbyte/pull/15741)            | Removed `OAuth2.0` option                                                                                                                                              |
| 0.1.8   | 2022-07-25 | [15000](https://github.com/airbytehq/airbyte/pull/15000)            | Added support of `OAuth2.0` authentication, fixed bug when normalization couldn't handle nested cursor field and primary key                                           |
| 0.1.7   | 2022-07-18 | [14804](https://github.com/airbytehq/airbyte/pull/14804)            | Added `RESULTSET_TOO_LARGE` error validation                                                                                                                           |
| 0.1.6   | 2022-06-10 | [13682](https://github.com/airbytehq/airbyte/pull/13682)            | Updated paypal transaction schema                                                                                                                                      |
| 0.1.5   | 2022-04-27 | [12335](https://github.com/airbytehq/airbyte/pull/12335)            | Added fixtures to mock time.sleep for connectors that explicitly sleep                                                                                                 |
| 0.1.4   | 2021-12-22 | [9034](https://github.com/airbytehq/airbyte/pull/9034)              | Updated connector fields title/description                                                                                                                             |
| 0.1.3   | 2021-12-16 | [8580](https://github.com/airbytehq/airbyte/pull/8580)              | Added more logs during `check connection` stage                                                                                                                        |
| 0.1.2   | 2021-11-08 | [7499](https://github.com/airbytehq/airbyte/pull/7499)              | Removed base-python dependencies                                                                                                                                       |
| 0.1.1   | 2021-08-03 | [5155](https://github.com/airbytehq/airbyte/pull/5155)              | Fixed start_date_min limit                                                                                                                                             |
| 0.1.0   | 2021-06-10 | [4240](https://github.com/airbytehq/airbyte/pull/4240)              | PayPal Transaction Search API                                                                                                                                          |

</details>
