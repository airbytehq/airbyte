# CoinAPI

## Sync overview

This source can sync OHLCV and trades historical data for a single coin listed on 
[CoinAPI](https://www.coinapi.io/). It currently only supports Full Refresh
syncs.

### Output schema

This source is capable of syncing the following streams:

* `ohlcv_historical_data`
* `trades_historical_data`

### Features

| Feature           | Supported? \(Yes/No\) | Notes                                                   |
|:------------------|:----------------------|:--------------------------------------------------------|
| Full Refresh Sync | Yes                   |                                                         |
| Incremental Sync  | No                    |                                                         |
| API Environments  | Yes                   | Both sandbox and production environments are supported. |

### Performance considerations

CoinAPI allows only 100 daily requests on the free plan. Use of this connector
may require a paid plan.

## Getting started

### Requirements

1. Obtain an API key from [CoinAPI](https://www.coinapi.io/).
2. Choose a symbol to pull data for. You can find a list of symbols [here](https://docs.coinapi.io/#list-all-symbols-get). 
3. Choose a time interval to pull data for. You can find a list of intervals [here](https://docs.coinapi.io/#list-all-periods-get).

### Setup guide

The following fields are required fields for the connector to work:

- `api_key`: Your CoinAPI API key.
- `environment`: The environment to use. Can be either `sandbox` or `production`.
- `symbol_id`: The symbol to pull data for.
- `period`: The time interval to pull data for.
- `start_date`: The start date to pull `history` data from.
- (optional) `end_date`: The end date to pull `history` data until.
- (optional) `limit`: The maximum number of records to pull per request. Defaults to 100.

## Changelog

| Version | Date       | Pull Request                                             | Subject    |
|:--------|:-----------|:---------------------------------------------------------|:-----------|
| 0.1.1   | 2022-12-19 | [20600](https://github.com/airbytehq/airbyte/pull/20600) | Add quotes historical data stream|
| 0.1.0   | 2022-10-21 | [18302](https://github.com/airbytehq/airbyte/pull/18302) | New source |
