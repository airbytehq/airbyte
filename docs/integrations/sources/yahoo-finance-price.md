# Yahoo Finance Price

This source syncs historical and intraday price data for stocks, ETFs, and other instruments listed on [Yahoo Finance](https://finance.yahoo.com/). It reads from the Yahoo Finance chart endpoint (`https://query1.finance.yahoo.com/v8/finance/chart/{ticker}`).

## Prerequisites

You don't need a Yahoo account or API key. The connector calls a public, unauthenticated endpoint.

Yahoo doesn't officially document or support this endpoint. Yahoo can change its behavior, limits, or availability without notice.

## Set up the Yahoo Finance Price connector

1. In Airbyte, create a new source and select **Yahoo Finance Price**.
2. Enter a **Source name**.
3. In **Tickers**, enter one or more Yahoo Finance ticker symbols separated by commas, for example `AAPL, MSFT, ^GSPC`. Spaces around each symbol are allowed. Use the symbol exactly as it appears on Yahoo Finance, including any exchange suffix such as `.L` or `.TO`.
4. Select an **Interval**. This is the time between price points, from `1m` (one minute) to `3mo` (three months).
5. Select a **Range**. This is how far back from the current time to fetch prices, from `1d` to `max`.
6. Click **Set up source**.

### Interval and range limits

Yahoo Finance limits how far back you can request intraday data. If the interval and range you select exceed these limits, Yahoo returns an error and the sync fails.

| Interval                        | Maximum range                                    |
| :------------------------------ | :----------------------------------------------- |
| `1m`                            | About 8 days. Use the `1d`, `5d`, or `7d` range. |
| `5m`, `15m`, `30m`, `90m`       | Last 60 days. Use a range of `1mo` or less.      |
| `1h`                            | Last 730 days. Use a range of `2y` or less.      |
| `1d`, `5d`, `1wk`, `1mo`, `3mo` | No limit. Any range works.                       |

## Supported sync modes

The Yahoo Finance Price source supports the following sync modes:

- [Full Refresh - Overwrite](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-overwrite)
- [Full Refresh - Append](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-append)

The connector doesn't support incremental syncs. Each sync fetches the full selected range again.

## Supported streams

| Stream  | Description                                                                                       |
| :------ | :------------------------------------------------------------------------------------------------ |
| `price` | One record per ticker per sync. Each record contains the complete chart response for that ticker. |

Each `price` record has a single top-level `chart` object. Prices are in `chart.result[].indicators.quote[]`, where `open`, `high`, `low`, `close`, and `volume` are parallel arrays. The `chart.result[].timestamp` array holds the matching Unix timestamps, in seconds. Ticker metadata, such as `symbol`, `currency`, `exchangeName`, and trading periods, is in `chart.result[].meta`.

Because prices are stored as arrays inside one record, you typically need to unnest these arrays in your destination to get one row per price point.

## Limitations and troubleshooting

- **Invalid tickers fail the sync.** The connector requests each ticker separately. If any ticker doesn't exist or is delisted, Yahoo returns `404 Not Found` and the sync fails. Check each symbol on Yahoo Finance before adding it.
- **Interval and range errors.** If you see an error such as `1m data not available ... Only 8 days worth of 1m granularity data are allowed`, choose a shorter range or a longer interval. See [Interval and range limits](#interval-and-range-limits).

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                         |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------------------------------------------------------ |
| 0.3.24 | 2026-10-03 | [87643](https://github.com/airbytehq/airbyte/pull/87643) | Replace sentinel pagination with per-ticker partitions (final request returned 404) |
| 0.3.23 | 2025-05-24 | [60760](https://github.com/airbytehq/airbyte/pull/60760) | Update dependencies |
| 0.3.22 | 2025-05-10 | [59990](https://github.com/airbytehq/airbyte/pull/59990) | Update dependencies |
| 0.3.21 | 2025-05-04 | [59526](https://github.com/airbytehq/airbyte/pull/59526) | Update dependencies |
| 0.3.20 | 2025-04-26 | [58948](https://github.com/airbytehq/airbyte/pull/58948) | Update dependencies |
| 0.3.19 | 2025-04-19 | [58557](https://github.com/airbytehq/airbyte/pull/58557) | Update dependencies |
| 0.3.18 | 2025-04-13 | [58059](https://github.com/airbytehq/airbyte/pull/58059) | Update dependencies |
| 0.3.17 | 2025-04-05 | [57385](https://github.com/airbytehq/airbyte/pull/57385) | Update dependencies |
| 0.3.16 | 2025-03-29 | [56887](https://github.com/airbytehq/airbyte/pull/56887) | Update dependencies |
| 0.3.15 | 2025-03-22 | [56287](https://github.com/airbytehq/airbyte/pull/56287) | Update dependencies |
| 0.3.14 | 2025-03-08 | [55623](https://github.com/airbytehq/airbyte/pull/55623) | Update dependencies |
| 0.3.13 | 2025-03-01 | [55130](https://github.com/airbytehq/airbyte/pull/55130) | Update dependencies |
| 0.3.12 | 2025-02-22 | [54531](https://github.com/airbytehq/airbyte/pull/54531) | Update dependencies |
| 0.3.11 | 2025-02-15 | [54056](https://github.com/airbytehq/airbyte/pull/54056) | Update dependencies |
| 0.3.10 | 2025-02-08 | [53091](https://github.com/airbytehq/airbyte/pull/53091) | Update dependencies |
| 0.3.9 | 2025-01-25 | [52417](https://github.com/airbytehq/airbyte/pull/52417) | Update dependencies |
| 0.3.8 | 2025-01-18 | [51984](https://github.com/airbytehq/airbyte/pull/51984) | Update dependencies |
| 0.3.7 | 2025-01-11 | [51381](https://github.com/airbytehq/airbyte/pull/51381) | Update dependencies |
| 0.3.6 | 2024-12-28 | [50794](https://github.com/airbytehq/airbyte/pull/50794) | Update dependencies |
| 0.3.5 | 2024-12-21 | [50339](https://github.com/airbytehq/airbyte/pull/50339) | Update dependencies |
| 0.3.4 | 2024-12-14 | [49792](https://github.com/airbytehq/airbyte/pull/49792) | Update dependencies |
| 0.3.3 | 2024-12-12 | [49407](https://github.com/airbytehq/airbyte/pull/49407) | Update dependencies |
| 0.3.2 | 2024-10-29 | [47726](https://github.com/airbytehq/airbyte/pull/47726) | Update dependencies |
| 0.3.1 | 2024-10-28 | [47497](https://github.com/airbytehq/airbyte/pull/47497) | Update dependencies |
| 0.3.0 | 2024-10-06 | [46526](https://github.com/airbytehq/airbyte/pull/46526) | Converting to manifest-only format |
| 0.2.23 | 2024-10-05 | [46468](https://github.com/airbytehq/airbyte/pull/46468) | Update dependencies |
| 0.2.22 | 2024-09-28 | [45792](https://github.com/airbytehq/airbyte/pull/45792) | Update dependencies |
| 0.2.21 | 2024-09-14 | [45484](https://github.com/airbytehq/airbyte/pull/45484) | Update dependencies |
| 0.2.20 | 2024-09-07 | [45236](https://github.com/airbytehq/airbyte/pull/45236) | Update dependencies |
| 0.2.19 | 2024-08-31 | [45011](https://github.com/airbytehq/airbyte/pull/45011) | Update dependencies |
| 0.2.18 | 2024-08-24 | [44704](https://github.com/airbytehq/airbyte/pull/44704) | Update dependencies |
| 0.2.17 | 2024-08-17 | [44225](https://github.com/airbytehq/airbyte/pull/44225) | Update dependencies |
| 0.2.16 | 2024-08-10 | [43634](https://github.com/airbytehq/airbyte/pull/43634) | Update dependencies |
| 0.2.15 | 2024-08-03 | [43204](https://github.com/airbytehq/airbyte/pull/43204) | Update dependencies |
| 0.2.14 | 2024-07-27 | [42788](https://github.com/airbytehq/airbyte/pull/42788) | Update dependencies |
| 0.2.13 | 2024-07-20 | [42136](https://github.com/airbytehq/airbyte/pull/42136) | Update dependencies |
| 0.2.12 | 2024-07-13 | [41735](https://github.com/airbytehq/airbyte/pull/41735) | Update dependencies |
| 0.2.11 | 2024-07-10 | [41409](https://github.com/airbytehq/airbyte/pull/41409) | Update dependencies |
| 0.2.10 | 2024-07-09 | [41266](https://github.com/airbytehq/airbyte/pull/41266) | Update dependencies |
| 0.2.9 | 2024-07-06 | [40866](https://github.com/airbytehq/airbyte/pull/40866) | Update dependencies |
| 0.2.8 | 2024-06-25 | [40433](https://github.com/airbytehq/airbyte/pull/40433) | Update dependencies |
| 0.2.7 | 2024-06-21 | [39928](https://github.com/airbytehq/airbyte/pull/39928) | Update dependencies |
| 0.2.6 | 2024-06-06 | [39274](https://github.com/airbytehq/airbyte/pull/39274) | [autopull] Upgrade base image to v1.2.2 |
| 0.2.5 | 2024-05-28 | [38602](https://github.com/airbytehq/airbyte/pull/38602) | Remove parameters macro and make compatible with builder |
| 0.2.4 | 2024-04-19 | [37295](https://github.com/airbytehq/airbyte/pull/37295) | Updating to 0.80.0 CDK |
| 0.2.3 | 2024-04-18 | [37295](https://github.com/airbytehq/airbyte/pull/37295) | Manage dependencies with Poetry. |
| 0.2.2 | 2024-04-15 | [37295](https://github.com/airbytehq/airbyte/pull/37295) | Base image migration: remove Dockerfile and use the python-connector-base image |
| 0.2.1 | 2024-04-12 | [37295](https://github.com/airbytehq/airbyte/pull/37295) | schema descriptions |
| 0.2.0 | 2023-08-22 | [29355](https://github.com/airbytehq/airbyte/pull/29355) | Migrate to no-code framework |
| 0.1.3 | 2022-03-23 | [10563](https://github.com/airbytehq/airbyte/pull/10563) | 🎉 Source Yahoo Finance Price |

</details>
