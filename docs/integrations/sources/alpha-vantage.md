# Alpha Vantage

## Sync overview

This source retrieves time series data from the free
[Alpha Vantage](https://www.alphavantage.co/) API. It supports intraday, daily,
weekly and monthly time series data.

### Output schema

This source is capable of syncing the following streams:

- `time_series_intraday`
- `time_series_daily`
- `time_series_daily_adjusted` (premium only)
- `time_series_weekly`
- `time_series_weekly_adjusted`
- `time_series_monthly`
- `time_series_monthly_adjusted`

### Features

| Feature           | Supported? \(Yes/No\) | Notes                                                   |
| :---------------- | :-------------------- | :------------------------------------------------------ |
| Full Refresh Sync | Yes                   |                                                         |
| Incremental Sync  | No                    |                                                         |
| API Environments  | Yes                   | Both sandbox and production environments are supported. |

### Performance considerations

Since a single API call returns the full history of a time series if
configured, it is recommended to use `Full Refresh` with `Overwrite` to avoid
storing duplicate data.

Also, the data returned can be quite large.

## Getting started

### Requirements

1. Obtain an API key from [Alpha Vantage](https://www.alphavantage.co/support/#api-key).

### Setup guide

The following fields are required fields for the connector to work:

- `api_key`: Your Alpha Vantage API key.
- `symbol`: The symbol of the time series to retrieve, with exchange code if
  applicable. For example, `MSFT` or `TSCO.LON`.
- (optional) `interval`: The time-series data point interval. Defaults to 1 minute.
- (optional) `Adjusted?`: Whether the `intraday` endpoint should return adjusted
  data. Defaults to `false`.
- (optional) `outputsize`: The size of the time series to retrieve. Defaults to
  `compact`, which returns the last 100 data points. `full` returns the full
  history.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                           |
| :------ | :--------- | :------------------------------------------------------- | :-------------------------------- |
| 0.1.3 | 2024-06-04 | [38938](https://github.com/airbytehq/airbyte/pull/38938) | [autopull] Upgrade base image to v1.2.1 |
| 0.1.2 | 2024-05-21 | [38512](https://github.com/airbytehq/airbyte/pull/38512) | [autopull] base image + poetry + up_to_date |
| 0.1.1 | 2022-12-16 | [20564](https://github.com/airbytehq/airbyte/pull/20564) | add quote stream to alpha-vantage |
| 0.1.0 | 2022-10-21 | [18320](https://github.com/airbytehq/airbyte/pull/18320) | New source |

</details>