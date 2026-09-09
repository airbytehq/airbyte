# PayPal

This page contains the setup guide and reference information for the PayPal Transaction source connector.

The connector authenticates with the [PayPal REST APIs](https://developer.paypal.com/api/rest/authentication/) using an OAuth 2.0 access token that it requests from your app's client ID and client secret.

## Prerequisites

- A PayPal business account and a REST API app. To create them, follow the [PayPal getting started guide](https://developer.paypal.com/docs/platforms/get-started/). The same page explains how to set up a Sandbox so you can test the connector before using it in production.
- The **Transaction Search** feature enabled on the REST API app. In the [PayPal Developer Dashboard](https://developer.paypal.com/dashboard/applications/live), open your app, select **Transaction Search** under the app's features, and save. Without it, the `transactions` and `balances` streams fail with a permission error. PayPal notes that if the app was already used for other API requests, it can take up to 9 hours for the new permission to apply to new access tokens. See the [Transaction Search integration guide](https://developer.paypal.com/docs/transaction-search/).

## Setup guide

### Step 1: Get your PayPal credentials

In the [Apps & Credentials page](https://developer.paypal.com/dashboard/applications/live), open your REST API app and copy its `Client ID` and `Secret`. Toggle the dashboard to **Sandbox** or **Live** to get the credentials for the environment you want to sync.

### Step 2: Set up the PayPal Transaction connector in Airbyte

1. Log into your Airbyte account.

   - For Cloud, [log in here](https://cloud.airbyte.com/workspaces).

2. In the left navigation bar, click **Sources**.

   a. If this is your first time creating a source, use the search bar and enter **PayPal Transaction** and select it.

   b. If you already have sources configured, go to the top-right corner and click **+ New source**. Then enter **PayPal Transaction** in the search bar and select the connector.

3. Set the name for your source.
4. Enter your `Client ID`.
5. Enter your `Client secret`.
6. `Start Date`: Use the date picker or enter a UTC date and time in the format `YYYY-MM-DDTHH:MM:SSZ`. PayPal only keeps three years of transaction history, so the `transactions` and `balances` streams never request data older than three years before the sync, even if you enter an earlier date. The `search_invoices` and `list_payments` streams use this date as-is.
7. `Sandbox`: Turn the toggle on to sync a Sandbox account. By default the toggle is off and the connector reads from the production (`api-m.paypal.com`) environment. Use credentials from the matching environment.
8. _(Optional)_ `Dispute Start Date Range`: Use the date picker or enter a UTC date and time in the format `YYYY-MM-DDTHH:MM:SS.sssZ`. Milliseconds are required.
   - This option only affects the `list_disputes` stream.
   - PayPal only returns disputes updated in the last 180 days. If you leave this empty, or enter a date more than 180 days in the past, the stream starts 180 days before the sync.
9. _(Optional)_ `End Date`: Use the date picker or enter a UTC date and time in the format `YYYY-MM-DDTHH:MM:SSZ`. Only the `transactions`, `search_invoices`, and `list_payments` streams use it. The `balances` stream doesn't: it requests balances as of a single point in time and never sends an end date. If you leave it empty, those streams sync up to the time of the sync.
10. _(Optional)_ `Refresh Token`: Leave this empty. The connector obtains and refreshes its access token from the client ID and client secret and doesn't use this field.
11. _(Optional)_ `Number of days per request`: The date range, in days, that the `transactions`, `list_disputes`, and `list_payments` streams request from PayPal in each call. The default is 7 and the maximum is 31, which is the largest range PayPal's Transaction Search API accepts.
12. Click **Set up source**.

:::info Oversized transaction search results

PayPal rejects a transaction search whose result set exceeds 10,000 records with an HTTP 400 `RESULTSET_TOO_LARGE` error instead of paginating through it. When this happens, the `transactions` stream automatically re-reads the rejected date range as two smaller ranges, and keeps halving them until PayPal accepts each request. No records are skipped, and the sync only fails if a one-second date range still exceeds 10,000 transactions, which is reported as a configuration error.

You don't need to change anything for this to work. If your account has a high transaction volume, lowering `Number of days per request` reduces the number of rejected requests and retries, which makes syncs faster.

:::

## Supported sync modes

The PayPal Transaction source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature                   | Supported? |
| :------------------------ | :--------- |
| Full Refresh Sync         | Yes        |
| Incremental - Append Sync | Yes        |
| Namespaces                | No         |

## Supported streams

| Stream                 | PayPal endpoint                                                                                                                            | Incremental | Cursor field               | Page size               |
| :--------------------- | :----------------------------------------------------------------------------------------------------------------------------------------- | :---------- | :------------------------- | :---------------------- |
| `transactions`         | [List transactions](https://developer.paypal.com/docs/api/transaction-search/v1/#transactions) (`GET /v1/reporting/transactions`)          | Yes         | `transaction_updated_date` | 500                     |
| `balances`             | [List all balances](https://developer.paypal.com/docs/api/transaction-search/v1/#balances) (`GET /v1/reporting/balances`)                  | Yes         | `as_of_time`               | Not applicable          |
| `list_products`        | [List products](https://developer.paypal.com/docs/api/catalog-products/v1/#products_list) (`GET /v1/catalogs/products`)                    | No          | None                       | 20                      |
| `show_product_details` | [Show product details](https://developer.paypal.com/docs/api/catalog-products/v1/#products_get) (`GET /v1/catalogs/products/{id}`)         | No          | None                       | One request per product |
| `list_disputes`        | [List disputes](https://developer.paypal.com/docs/api/customer-disputes/v1/#disputes_list) (`GET /v1/customer/disputes`)                   | Yes         | `updated_time_cut`         | 50                      |
| `search_invoices`      | [Search for invoices](https://developer.paypal.com/docs/api/invoicing/v2/#invoices_search-invoices) (`POST /v2/invoicing/search-invoices`) | No          | None                       | 100                     |
| `list_payments`        | [List payments](https://developer.paypal.com/docs/api/payments/v1/#payment_list) (`GET /v1/payments/payment`)                              | Yes         | `update_time`              | 20                      |

Page sizes aren't configurable. Where an endpoint is paginated, the connector requests the largest page PayPal allows. The `balances` endpoint isn't paginated, and `show_product_details` makes one request per product.

### Stream notes

- **`transactions`**: Requests are made in date ranges of `Number of days per request` days, between `Start Date` and `End Date` (or the sync time). Each range is split further automatically if PayPal rejects it as too large. See the info box in the setup guide.
- **`balances`**: Reads the account balance as of `Start Date` and, on later incremental syncs, as of the last synced `as_of_time`.
- **`list_products`** and **`show_product_details`**: `show_product_details` makes one request for every product returned by `list_products`, and `list_products` pages through the catalog 20 products at a time, which is the maximum PayPal allows. PayPal API calls aren't made concurrently, so a large catalog can take a long time to sync. For example, a catalog of more than 30,000 products can take 10 to 15 minutes to list and several hours to fetch details for. Consider scheduling syncs that include these streams at a time when the delay isn't a problem.
- **`list_disputes`**: Requests disputes updated between `Dispute Start Date Range` (or 180 days before the sync) and 30 minutes before the sync, in ranges of `Number of days per request` days. `Start Date` and `End Date` don't apply to this stream.
- **`search_invoices`**: Sends `Start Date` and `End Date` as the `creation_date_range` in the request body, so the stream returns invoices created in that range. It's a full refresh stream and reads the whole range on every sync.
- **`list_payments`**: Requests payments updated between `Start Date` and `End Date` (or the sync time) in ranges of `Number of days per request` days.

## Performance considerations

- **Data availability:** PayPal states it can take up to 3 hours for a completed transaction to appear in the `transactions` stream.
- **Historical data:** PayPal's Transaction Search API returns transactions for the previous 3 years only. The Disputes API returns disputes updated in the last 180 days only.
- **Result set size:** A single transaction search can't return more than 10,000 records. The `transactions` stream handles this automatically by splitting date ranges, as described in the setup guide.
- **Rate limits:** PayPal doesn't publish a rate limiting policy, but it may temporarily rate limit traffic it considers abusive and respond with HTTP 429 `RATE_LIMIT_REACHED`. Every stream except `transactions` waits 100 seconds before retrying a retryable response, such as a 429 or 5XX. The `transactions` stream configures no backoff of its own and uses the CDK's default retry behavior. See [PayPal's rate limiting guidelines](https://developer.paypal.com/api/rest/reference/rate-limiting/).

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
| 2.6.48  | 2026-09-09 | [84916](https://github.com/airbytehq/airbyte/pull/84916)            | Retry oversized `transactions` date slices as smaller date ranges instead of failing the sync on the first `RESULTSET_TOO_LARGE` response                              |
| 2.6.47  | 2026-09-08 | [85594](https://github.com/airbytehq/airbyte/pull/85594)            | Update dependencies                                                                                                                                                    |
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
| 2.6.26  | 2026-02-26 | [74027](https://github.com/airbytehq/airbyte/pull/74027)            | Fix INVALID_DATE_TIME_FORMAT error on disputes stream by using 3-digit milliseconds                                                                                    |
| 2.6.25  | 2026-02-17 | [73574](https://github.com/airbytehq/airbyte/pull/73574)            | Update dependencies                                                                                                                                                    |
| 2.6.24  | 2026-02-10 | [73171](https://github.com/airbytehq/airbyte/pull/73171)            | Update dependencies                                                                                                                                                    |
| 2.6.23  | 2026-02-03 | [72637](https://github.com/airbytehq/airbyte/pull/72637)            | Update dependencies                                                                                                                                                    |
| 2.6.22  | 2026-01-22 | [70967](https://github.com/airbytehq/airbyte/pull/70967)            | Update HTTP response action for 400 error transactions from IGNORE to FAIL                                                                                             |
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
| 2.6.2   | 2025-06-14 | [51848](https://github.com/airbytehq/airbyte/pull/51848)            | Update dependencies                                                                                                                                                    |
| 2.6.1   | 2025-06-05 | [58674](https://github.com/airbytehq/airbyte/pull/58674)            | Update CDK to fix complex datatype errors with interpolation                                                                                                           |
| 2.6.0   | 2024-10-23 | [47282](https://github.com/airbytehq/airbyte/pull/47282)            | Migrate to Manifest-only                                                                                                                                               |
| 2.5.8   | 2025-01-11 | [43797](https://github.com/airbytehq/airbyte/pull/43797)            | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
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
