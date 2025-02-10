# CoinGecko Coins

## Sync overview

This source can sync market chart and historical data for a single coin listed on the
[CoinGecko](https://coingecko.com) API. It currently supports only Full Refresh syncing.

### Output schema

This source is capable of syncing the following streams:

- `market_chart`
- `history`

### Features

| Feature           | Supported? \(Yes/No\) | Notes                                                  |
| :---------------- | :-------------------- | :----------------------------------------------------- |
| Full Refresh Sync | Yes                   |                                                        |
| Incremental Sync  | No                    |                                                        |
| CoinGecko Pro API | Yes                   | Will default to free API unless an API key is provided |

### Performance considerations

The CoinGecko API has a rate limit of 10-50 requests per minute. The connector should not run into this
under normal operation.

CoinGecko also request that free users provide attribution when using CoinGecko data. Please read more about
this [here](https://www.coingecko.com/en/branding).

## Getting started

### Requirements

1. Choose a coin to pull data from. The coin must be listed on CoinGecko, and can be listed via the `/coins/list` endpoint.
2. Choose a `vs_currency` to pull data in. This can be any currency listed on CoinGecko, and can be listed via the `/simple/supported_vs_currencies` endpoint.

### Setup guide

The following fields are required fields for the connector to work:

- `coin_id`: The ID of the coin to pull data for. This can be found via the `/coins/list` endpoint.
- `vs_currency`: The currency to pull data for. This can be found via the `/simple/supported_vs_currencies` endpoint.
- `days`: The number of days to pull `market_chart` data for.
- `start_date`: The start date to pull `history` data from.
- (optional) `end_date`: The end date to pull `history` data until.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                       |
| :------ | :--------- | :------------------------------------------------------- | :-------------------------------------------- |
| 0.2.14 | 2025-02-08 | [53332](https://github.com/airbytehq/airbyte/pull/53332) | Update dependencies |
| 0.2.13 | 2025-02-01 | [52849](https://github.com/airbytehq/airbyte/pull/52849) | Update dependencies |
| 0.2.12 | 2025-01-25 | [52299](https://github.com/airbytehq/airbyte/pull/52299) | Update dependencies |
| 0.2.11 | 2025-01-18 | [51644](https://github.com/airbytehq/airbyte/pull/51644) | Update dependencies |
| 0.2.10 | 2025-01-11 | [51060](https://github.com/airbytehq/airbyte/pull/51060) | Update dependencies |
| 0.2.9 | 2024-12-28 | [50572](https://github.com/airbytehq/airbyte/pull/50572) | Update dependencies |
| 0.2.8 | 2024-12-21 | [49995](https://github.com/airbytehq/airbyte/pull/49995) | Update dependencies |
| 0.2.7 | 2024-12-14 | [49527](https://github.com/airbytehq/airbyte/pull/49527) | Update dependencies |
| 0.2.6 | 2024-12-12 | [49208](https://github.com/airbytehq/airbyte/pull/49208) | Update dependencies |
| 0.2.5 | 2024-12-11 | [48937](https://github.com/airbytehq/airbyte/pull/48937) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.2.4 | 2024-11-05 | [48363](https://github.com/airbytehq/airbyte/pull/48363) | Revert to source-declarative-manifest v5.17.0 |
| 0.2.3 | 2024-11-05 | [48330](https://github.com/airbytehq/airbyte/pull/48330) | Update dependencies |
| 0.2.2 | 2024-10-29 | [47804](https://github.com/airbytehq/airbyte/pull/47804) | Update dependencies |
| 0.2.1 | 2024-10-28 | [47559](https://github.com/airbytehq/airbyte/pull/47559) | Update dependencies |
| 0.2.0 | 2024-08-22 | [44565](https://github.com/airbytehq/airbyte/pull/44565) | Refactor connector to manifest-only format |
| 0.1.13 | 2024-08-17 | [44306](https://github.com/airbytehq/airbyte/pull/44306) | Update dependencies |
| 0.1.12 | 2024-08-12 | [43911](https://github.com/airbytehq/airbyte/pull/43911) | Update dependencies |
| 0.1.11 | 2024-08-10 | [43537](https://github.com/airbytehq/airbyte/pull/43537) | Update dependencies |
| 0.1.10 | 2024-08-03 | [43113](https://github.com/airbytehq/airbyte/pull/43113) | Update dependencies |
| 0.1.9 | 2024-07-27 | [42625](https://github.com/airbytehq/airbyte/pull/42625) | Update dependencies |
| 0.1.8 | 2024-07-20 | [42335](https://github.com/airbytehq/airbyte/pull/42335) | Update dependencies |
| 0.1.7 | 2024-07-13 | [41707](https://github.com/airbytehq/airbyte/pull/41707) | Update dependencies |
| 0.1.6 | 2024-07-10 | [41262](https://github.com/airbytehq/airbyte/pull/41262) | Update dependencies |
| 0.1.5 | 2024-07-06 | [40879](https://github.com/airbytehq/airbyte/pull/40879) | Update dependencies |
| 0.1.4 | 2024-06-25 | [40292](https://github.com/airbytehq/airbyte/pull/40292) | Update dependencies |
| 0.1.3 | 2024-06-22 | [40035](https://github.com/airbytehq/airbyte/pull/40035) | Update dependencies |
| 0.1.2 | 2024-06-04 | [38971](https://github.com/airbytehq/airbyte/pull/38971) | [autopull] Upgrade base image to v1.2.1 |
| 0.1.1 | 2024-05-21 | [38515](https://github.com/airbytehq/airbyte/pull/38515) | [autopull] base image + poetry + up_to_date |
| 0.1.1 | 2023-04-30 | [25558](https://github.com/airbytehq/airbyte/pull/25558) | Make manifest.yaml connector builder-friendly |
| 0.1.0 | 2022-10-20 | [18248](https://github.com/airbytehq/airbyte/pull/18248) | New source |

</details>
