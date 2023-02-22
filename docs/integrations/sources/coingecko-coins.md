# CoinGecko Coins

## Sync overview

This source can sync market chart and historical data for a single coin listed on the
[CoinGecko](https://coingecko.com) API. It currently supports only Full Refresh syncing.

### Output schema

This source is capable of syncing the following streams:

* `market_chart`
* `history`

### Features

| Feature           | Supported? \(Yes/No\) | Notes                                                  |
|:------------------|:----------------------|:-------------------------------------------------------|
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

| Version | Date       | Pull Request                                             | Subject    |
|:--------|:-----------|:---------------------------------------------------------|:-----------|
| 0.1.0   | 2022-10-20 | [18248](https://github.com/airbytehq/airbyte/pull/18248) | New source |

