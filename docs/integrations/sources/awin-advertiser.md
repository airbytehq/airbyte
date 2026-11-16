# AWIN Advertiser

Website: https://www.awin.com/
Documentation: https://help.awin.com/apidocs/for-advertisers

## Prerequisites

- An Awin advertiser account with API access. Accelerate and Advanced plans include API access. See [Awin's API overview](https://help.awin.com/docs/awins-apis-overview) for plan availability and exceptions.
- An Awin user with access to that advertiser account. The API requires at least viewer access to retrieve account data. Review [Awin's authentication guide](https://help.awin.com/apidocs/api-authentication) for the permissions needed to obtain a token.

## Setup

1. Sign in to Awin and open [API Credentials](https://ui.awin.com/awin-api) from the user menu.
2. Enter your Awin password and click **Show my API token**.
3. In the Airbyte source configuration, paste the token into **API Key** (`api_key`), without the `Bearer` prefix. The connector adds this prefix automatically. Use the user token, not a Conversion API key.
4. Enter the advertiser account ID in `advertiserId`. You can find it in your Awin dashboard or account settings.
5. Set **Start Date**, **Lookback Days**, and **Step Increment** as described below. To sync `creative_performance`, also select **Creative performance regions**.

The token grants access to the accounts associated with your Awin user, rather than a single advertiser account. Changes to account access can take up to 10 minutes to appear in the API.

## Configuration

`advertiserId`, `api_key`, `step_increment`, `lookback_days`, and `start_date` are required. `regions` is optional unless you want records from `creative_performance`.

| Input | Type | Description | Default Value |
| --- | --- | --- | --- |
| `advertiserId` | `string` | Your Awin advertiser account ID. You can find this in your Awin dashboard or account settings. | |
| `api_key` | `string` | API Key. Your Awin user API token from **API Credentials**. The connector uses Bearer token authentication. | |
| `step_increment` | `string` | Step Increment. Request window for `campaign_performance` and `transactions`, in ISO 8601 duration format. For example, `P30D` requests 30-day windows. The campaign report allows at most 400 days per request. This setting doesn't affect `publisher_performance` or `creative_performance`, which always request one day at a time. | P400D |
| `lookback_days` | `integer` | Lookback Days. Number of days to look back on each sync to catch any updates to existing records. | |
| `start_date` | `string` | Start Date. Start date for data replication in YYYY-MM-DD format | |
| `regions` | `array<string>` | Creative performance regions. Awin regions to request for the `creative_performance` stream. The Awin creative report requires a region, so the stream reads one report per selected region and returns no records when none are selected. A region added after this stream has synced data is read only from the last synced date minus `lookback_days`, so refresh the `creative_performance` stream after adding a region to backfill its earlier history. | |

## Streams

| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
| --- | --- | --- | --- | --- |
| `campaign_performance` | `date`, `publisherId`, `campaign` | No pagination | ✅ | ✅ |
| `transactions` | `id` | No pagination | ✅ | ✅ |
| `publisher_performance` | `date`, `publisherId`, `region`, `currency` | No pagination | ✅ | ✅ |
| `creative_performance` | `date`, `region`, `creativeId`, `publisherId` | No pagination | ✅ | ✅ |
| `publishers` | `id` | No pagination | ✅ | ❌ |
| `accounts` | `accountId` | No pagination | ✅ | ❌ |

- `campaign_performance` aggregates clicks and transactions by campaign and publisher, with daily intervals. It uses Awin's default `includeNumbersWithoutCampaign=false`, so it excludes activity without a campaign parameter.
- `transactions` returns individual transactions.
- `publisher_performance` aggregates transactions, clicks, and impressions by publisher. Awin omits publishers with no activity in the requested period.
- `creative_performance` aggregates transactions, clicks, and impressions by creative for each selected region.
- `publishers` returns publishers with an active relationship with the configured advertiser, including their regions and promotion types.
- `accounts` returns all advertiser accounts associated with your API token's user. Unlike the other streams, it isn't limited to `advertiserId`.

### Transaction updates and deletions

The `transactions` stream requests basket products, so records include `basketProducts` when Awin returns product-level tracking data. Each transaction also has an `is_deleted` field, which is `true` when `commissionStatus` was `deleted` the last time the transaction was read.

After the initial sync, incremental syncs re-read transactions from the saved cursor minus `lookback_days`, based on `transactionDate`, not the date of an amendment or deletion. A transaction deleted after it leaves that window can retain `is_deleted: false` in your destination. Set `lookback_days` to cover your programs' validation period. The stream sends no `status` filter, so `is_deleted` can only be `true` for deleted transactions that Awin includes in its default response. This field doesn't remove destination records automatically.

### Daily reports and rate limits

The `publisher_performance` and `creative_performance` streams use transaction dates in UTC, request one day at a time, and add the report day as the `date` field. A first sync sends one request per day since `start_date` (per selected region for `creative_performance`).

[Awin limits API requests](https://help.awin.com/apidocs/introduction-to-awins-apis) to 20 calls per minute per user, shared with any other integrations using that user. The connector limits its requests to 20 per minute across all streams. A year of history therefore requires about 365 requests per daily report (per selected region for `creative_performance`), before lookback reads or retries.

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
| --- | --- | --- | --- |
| 0.1.0 | 2026-11-15 | [91539](https://github.com/airbytehq/airbyte/pull/91539) | Add `publisher_performance`, `creative_performance`, `publishers` and `accounts` streams, add basket products and an `is_deleted` field to `transactions` |
| 0.0.43 | 2026-11-10 | [91364](https://github.com/airbytehq/airbyte/pull/91364) | Update dependencies |
| 0.0.42 | 2026-11-03 | [90448](https://github.com/airbytehq/airbyte/pull/90448) | Update dependencies |
| 0.0.41 | 2026-10-27 | [89797](https://github.com/airbytehq/airbyte/pull/89797) | Update dependencies |
| 0.0.40 | 2026-10-20 | [89137](https://github.com/airbytehq/airbyte/pull/89137) | Update dependencies |
| 0.0.39 | 2026-10-13 | [88529](https://github.com/airbytehq/airbyte/pull/88529) | Update dependencies |
| 0.0.38 | 2026-10-06 | [87751](https://github.com/airbytehq/airbyte/pull/87751) | Update dependencies |
| 0.0.37 | 2026-09-29 | [87093](https://github.com/airbytehq/airbyte/pull/87093) | Update dependencies |
| 0.0.36 | 2026-09-22 | [86547](https://github.com/airbytehq/airbyte/pull/86547) | Update dependencies |
| 0.0.35 | 2026-09-15 | [85944](https://github.com/airbytehq/airbyte/pull/85944) | Update dependencies |
| 0.0.34 | 2026-09-08 | [84473](https://github.com/airbytehq/airbyte/pull/84473) | Update dependencies |
| 0.0.33 | 2026-08-11 | [83822](https://github.com/airbytehq/airbyte/pull/83822) | Update dependencies |
| 0.0.32 | 2026-08-04 | [83355](https://github.com/airbytehq/airbyte/pull/83355) | Update dependencies |
| 0.0.31 | 2026-07-28 | [82811](https://github.com/airbytehq/airbyte/pull/82811) | Update dependencies |
| 0.0.30 | 2026-07-21 | [82332](https://github.com/airbytehq/airbyte/pull/82332) | Update dependencies |
| 0.0.29 | 2026-07-14 | [81720](https://github.com/airbytehq/airbyte/pull/81720) | Update dependencies |
| 0.0.28 | 2026-06-30 | [80977](https://github.com/airbytehq/airbyte/pull/80977) | Update dependencies |
| 0.0.27 | 2026-06-23 | [80361](https://github.com/airbytehq/airbyte/pull/80361) | Update dependencies |
| 0.0.26 | 2026-06-16 | [79758](https://github.com/airbytehq/airbyte/pull/79758) | Update dependencies |
| 0.0.25 | 2026-06-09 | [79209](https://github.com/airbytehq/airbyte/pull/79209) | Update dependencies |
| 0.0.24 | 2026-06-02 | [78592](https://github.com/airbytehq/airbyte/pull/78592) | Update dependencies |
| 0.0.23 | 2026-04-28 | [77154](https://github.com/airbytehq/airbyte/pull/77154) | Update dependencies |
| 0.0.22 | 2026-04-21 | [76491](https://github.com/airbytehq/airbyte/pull/76491) | Update dependencies |
| 0.0.21 | 2026-03-24 | [75313](https://github.com/airbytehq/airbyte/pull/75313) | Update dependencies |
| 0.0.20 | 2026-03-10 | [74511](https://github.com/airbytehq/airbyte/pull/74511) | Update dependencies |
| 0.0.19 | 2026-02-24 | [73820](https://github.com/airbytehq/airbyte/pull/73820) | Update dependencies |
| 0.0.18 | 2026-02-17 | [73393](https://github.com/airbytehq/airbyte/pull/73393) | Update dependencies |
| 0.0.17 | 2026-02-03 | [72722](https://github.com/airbytehq/airbyte/pull/72722) | Update dependencies |
| 0.0.16 | 2026-01-20 | [71895](https://github.com/airbytehq/airbyte/pull/71895) | Update dependencies |
| 0.0.15 | 2026-01-14 | [71440](https://github.com/airbytehq/airbyte/pull/71440) | Update dependencies |
| 0.0.14 | 2025-12-18 | [70790](https://github.com/airbytehq/airbyte/pull/70790) | Update dependencies |
| 0.0.13 | 2025-11-25 | [69874](https://github.com/airbytehq/airbyte/pull/69874) | Update dependencies |
| 0.0.12 | 2025-11-18 | [69520](https://github.com/airbytehq/airbyte/pull/69520) | Update dependencies |
| 0.0.11 | 2025-10-29 | [68899](https://github.com/airbytehq/airbyte/pull/68899) | Update dependencies |
| 0.0.10 | 2025-10-21 | [68381](https://github.com/airbytehq/airbyte/pull/68381) | Update dependencies |
| 0.0.9 | 2025-10-14 | [68006](https://github.com/airbytehq/airbyte/pull/68006) | Update dependencies |
| 0.0.8 | 2025-10-07 | [67167](https://github.com/airbytehq/airbyte/pull/67167) | Update dependencies |
| 0.0.7 | 2025-09-30 | [65646](https://github.com/airbytehq/airbyte/pull/65646) | Update dependencies |
| 0.0.6 | 2025-08-09 | [64645](https://github.com/airbytehq/airbyte/pull/64645) | Update dependencies |
| 0.0.5 | 2025-08-02 | [64430](https://github.com/airbytehq/airbyte/pull/64430) | Update dependencies |
| 0.0.4 | 2025-06-25 | [62059](https://github.com/airbytehq/airbyte/pull/62059) | source-awin-advertiser contribution from navneetmaharishi |
| 0.0.3 | 2025-06-21 | [60733](https://github.com/airbytehq/airbyte/pull/60733) | Update dependencies |
| 0.0.2 | 2025-05-10 | [59902](https://github.com/airbytehq/airbyte/pull/59902) | Update dependencies |
| 0.0.1 | 2025-04-29 | | Initial release by [@ryanmcg2203](https://github.com/ryanmcg2203) via Connector Builder |

</details>
