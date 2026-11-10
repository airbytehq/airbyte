# Paddle

This page contains the setup guide and reference information for the [Paddle](https://www.paddle.com/) source connector. The connector uses the [Paddle Billing API](https://developer.paddle.com/api-reference/overview) to sync customers, catalog, subscription, transaction, and event data.

## Prerequisites

- A Paddle Billing account. The connector calls the Paddle Billing API and doesn't support Paddle Classic.
- A Paddle API key for the environment you want to sync from. Sandbox and live accounts have separate API keys, and a key only works with the environment it was created in.

## Set up Paddle

### Create an API key

1. In the Paddle dashboard, go to **Developer tools** > **Authentication**.
2. Create a new API key. If Paddle prompts you to choose permissions, grant read access to every entity you want to sync, such as customers, addresses, businesses, discounts, prices, products, events, reports, subscriptions, transactions, and adjustments. Requests that lack a required permission fail with a `403` error.
3. Copy the key and store it securely. Paddle shows the full key only once.

For more information, see [Paddle's authentication documentation](https://developer.paddle.com/api-reference/about/authentication).

### Set up the connector in Airbyte

1. In Airbyte, create a new source and select **Paddle**.
2. Enter your **API Key**.
3. Select the **Environment**:
   - `api` for your live Paddle account (`https://api.paddle.com`). This is the default.
   - `sandbox-api` for your Paddle sandbox account (`https://sandbox-api.paddle.com`).
4. Enter a **Start date** in the format `YYYY-MM-DDTHH:MM:SSZ`, for example `2024-01-01T00:00:00Z`. The connector only replicates records with an `updated_at` value (or `occurred_at` for the `events` stream) on or after this date. The `event_types` and `ip_addresses` streams ignore this setting.
5. Click **Set up source**.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. Your Paddle API key. You can generate it by navigating to Paddle &gt; Developer tools &gt; Authentication &gt; Generate API key. Treat this key like a password and keep it secure. |  |
| `environment` | `string` | Environment. The Paddle API environment: `api` for live or `sandbox-api` for sandbox. | api |
| `start_date` | `string` | Start date. The date-time, in the format `YYYY-MM-DDTHH:MM:SSZ`, from which to replicate data. |  |

## Supported sync modes

The Paddle source connector supports the following sync modes:

- Full Refresh - Overwrite
- Full Refresh - Append
- Incremental Sync - Append
- Incremental Sync - Append + Deduped

## Streams

| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| adjustments | id | DefaultPaginator | ✅ |  ✅  |
| customers | id | DefaultPaginator | ✅ |  ✅  |
| customer_addresses | id | DefaultPaginator | ✅ |  ✅  |
| discounts | id | DefaultPaginator | ✅ |  ✅  |
| prices | id | DefaultPaginator | ✅ |  ✅  |
| products | id | DefaultPaginator | ✅ |  ✅  |
| businesses | id | DefaultPaginator | ✅ |  ✅  |
| events | event_id | DefaultPaginator | ✅ |  ✅  |
| event_types | uuid | DefaultPaginator | ✅ |  ❌  |
| reports | id | DefaultPaginator | ✅ |  ✅  |
| ip_addresses | uuid | DefaultPaginator | ✅ |  ❌  |
| subscriptions | id | DefaultPaginator | ✅ |  ✅  |
| transactions | id | DefaultPaginator | ✅ |  ✅  |

Incremental streams use `updated_at` as the cursor, except `events`, which uses `occurred_at`. The connector doesn't send date filters to the Paddle API. It reads every page of each stream and filters records by the cursor value after it receives them, so incremental syncs make the same number of API requests as full refresh syncs.

The `customer_addresses` and `businesses` streams are child streams of `customers`. The connector requests addresses and businesses separately for each customer, so syncs of these streams take longer for accounts with many customers.

## Limitations and rate limits

Paddle limits most API requests to 240 requests per minute per IP address. For details, see [Paddle's rate limiting documentation](https://developer.paddle.com/api-reference/about/rate-limiting). When the API returns a rate limit or server error, the connector waits 62 seconds and retries, up to 5 times per request.

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.2.39-rc.1 | 2026-11-10 | [90926](https://github.com/airbytehq/airbyte/pull/90926) | Simplify error handling while preserving retry behavior. |
| 0.2.38 | 2026-11-10 | [91640](https://github.com/airbytehq/airbyte/pull/91640) | Update dependencies |
| 0.2.37 | 2026-11-03 | [90688](https://github.com/airbytehq/airbyte/pull/90688) | Update dependencies |
| 0.2.36 | 2026-10-27 | [90003](https://github.com/airbytehq/airbyte/pull/90003) | Update dependencies |
| 0.2.35 | 2026-10-20 | [89328](https://github.com/airbytehq/airbyte/pull/89328) | Update dependencies |
| 0.2.34 | 2026-10-13 | [88727](https://github.com/airbytehq/airbyte/pull/88727) | Update dependencies |
| 0.2.33 | 2026-10-06 | [87972](https://github.com/airbytehq/airbyte/pull/87972) | Update dependencies |
| 0.2.32 | 2026-09-29 | [87293](https://github.com/airbytehq/airbyte/pull/87293) | Update dependencies |
| 0.2.31 | 2026-09-22 | [86733](https://github.com/airbytehq/airbyte/pull/86733) | Update dependencies |
| 0.2.30 | 2026-09-15 | [86187](https://github.com/airbytehq/airbyte/pull/86187) | Update dependencies |
| 0.2.29 | 2026-09-08 | [85612](https://github.com/airbytehq/airbyte/pull/85612) | Update dependencies |
| 0.2.28 | 2026-08-18 | [84705](https://github.com/airbytehq/airbyte/pull/84705) | Update dependencies |
| 0.2.27 | 2026-08-11 | [84040](https://github.com/airbytehq/airbyte/pull/84040) | Update dependencies |
| 0.2.26 | 2026-08-04 | [83556](https://github.com/airbytehq/airbyte/pull/83556) | Update dependencies |
| 0.2.25 | 2026-07-28 | [83055](https://github.com/airbytehq/airbyte/pull/83055) | Update dependencies |
| 0.2.24 | 2026-07-21 | [82523](https://github.com/airbytehq/airbyte/pull/82523) | Update dependencies |
| 0.2.23 | 2026-07-14 | [81941](https://github.com/airbytehq/airbyte/pull/81941) | Update dependencies |
| 0.2.22 | 2026-06-30 | [81187](https://github.com/airbytehq/airbyte/pull/81187) | Update dependencies |
| 0.2.21 | 2026-06-23 | [80605](https://github.com/airbytehq/airbyte/pull/80605) | Update dependencies |
| 0.2.20 | 2026-06-16 | [79985](https://github.com/airbytehq/airbyte/pull/79985) | Update dependencies |
| 0.2.19 | 2026-06-09 | [79450](https://github.com/airbytehq/airbyte/pull/79450) | Update dependencies |
| 0.2.18 | 2026-06-02 | [78916](https://github.com/airbytehq/airbyte/pull/78916) | Update dependencies |
| 0.2.17 | 2026-04-28 | [77336](https://github.com/airbytehq/airbyte/pull/77336) | Update dependencies |
| 0.2.16 | 2026-04-21 | [76702](https://github.com/airbytehq/airbyte/pull/76702) | Update dependencies |
| 0.2.15 | 2026-03-17 | [74984](https://github.com/airbytehq/airbyte/pull/74984) | Update dependencies |
| 0.2.14 | 2026-03-03 | [74237](https://github.com/airbytehq/airbyte/pull/74237) | Update dependencies |
| 0.2.13 | 2026-02-10 | [73106](https://github.com/airbytehq/airbyte/pull/73106) | Update dependencies |
| 0.2.12 | 2026-01-20 | [71651](https://github.com/airbytehq/airbyte/pull/71651) | Update dependencies |
| 0.2.11 | 2025-12-18 | [70506](https://github.com/airbytehq/airbyte/pull/70506) | Update dependencies |
| 0.2.10 | 2025-11-25 | [70089](https://github.com/airbytehq/airbyte/pull/70089) | Update dependencies |
| 0.2.9 | 2025-11-18 | [69694](https://github.com/airbytehq/airbyte/pull/69694) | Update dependencies |
| 0.2.8 | 2025-10-29 | [69016](https://github.com/airbytehq/airbyte/pull/69016) | Update dependencies |
| 0.2.7 | 2025-10-21 | [68291](https://github.com/airbytehq/airbyte/pull/68291) | Update dependencies |
| 0.2.6 | 2025-10-14 | [67785](https://github.com/airbytehq/airbyte/pull/67785) | Update dependencies |
| 0.2.5 | 2025-10-07 | [67336](https://github.com/airbytehq/airbyte/pull/67336) | Update dependencies |
| 0.2.4 | 2025-09-30 | [66390](https://github.com/airbytehq/airbyte/pull/66390) | Update dependencies |
| 0.2.3 | 2025-09-09 | [65806](https://github.com/airbytehq/airbyte/pull/65806) | Update dependencies |
| 0.2.2 | 2025-08-23 | [65194](https://github.com/airbytehq/airbyte/pull/65194) | Update dependencies |
| 0.2.1 | 2025-08-09 | [64749](https://github.com/airbytehq/airbyte/pull/64749) | Update dependencies |
| 0.2.0 | 2025-08-05 | [62891](https://github.com/airbytehq/airbyte/pull/62891) | Remove `custom_data` property constraints and add it to `customers` stream |
| 0.1.5 | 2025-08-02 | [64300](https://github.com/airbytehq/airbyte/pull/64300) | Update dependencies |
| 0.1.4 | 2025-07-26 | [63842](https://github.com/airbytehq/airbyte/pull/63842) | Update dependencies |
| 0.1.3 | 2025-07-19 | [63388](https://github.com/airbytehq/airbyte/pull/63388) | Update dependencies |
| 0.1.2 | 2025-07-12 | [63195](https://github.com/airbytehq/airbyte/pull/63195) | Update dependencies |
| 0.1.1 | 2025-07-05 | [62566](https://github.com/airbytehq/airbyte/pull/62566) | Update dependencies |
| 0.1.0 | 2025-07-02 | [62479](https://github.com/airbytehq/airbyte/pull/62479) | Add adjustments stream |
| 0.0.11 | 2025-07-01 | [62461](https://github.com/airbytehq/airbyte/pull/62461) | Add constant retry backoff per Paddle API Docs |
| 0.0.10 | 2025-06-28 | [62318](https://github.com/airbytehq/airbyte/pull/62318) | Update dependencies |
| 0.0.9 | 2025-06-21 | [61917](https://github.com/airbytehq/airbyte/pull/61917) | Update dependencies |
| 0.0.8 | 2025-06-16 | [60485](https://github.com/airbytehq/airbyte/pull/60485) | Update dependencies |
| 0.0.7 | 2025-05-11 | [60059](https://github.com/airbytehq/airbyte/pull/60059) | Update dependencies |
| 0.0.6 | 2025-05-04 | [59518](https://github.com/airbytehq/airbyte/pull/59518) | Update dependencies |
| 0.0.5 | 2025-04-27 | [59085](https://github.com/airbytehq/airbyte/pull/59085) | Update dependencies |
| 0.0.4 | 2025-04-20 | [58515](https://github.com/airbytehq/airbyte/pull/58515) | Update dependencies |
| 0.0.3 | 2025-04-13 | [57847](https://github.com/airbytehq/airbyte/pull/57847) | Update dependencies |
| 0.0.2 | 2025-04-06 | [57338](https://github.com/airbytehq/airbyte/pull/57338) | Update dependencies |
| 0.0.1 | 2025-04-04 | [57003](https://github.com/airbytehq/airbyte/pull/57003) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>
