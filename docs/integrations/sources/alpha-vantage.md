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
| 0.2.1 | 2025-02-08 | [53421](https://github.com/airbytehq/airbyte/pull/53421) | Update dependencies |
| 0.2.0 | 2025-01-07 | [47275](https://github.com/airbytehq/airbyte/pull/47275) | Migrate to Manifest-only |
| 0.1.30 | 2025-02-01 | [52896](https://github.com/airbytehq/airbyte/pull/52896) | Update dependencies |
| 0.1.29 | 2025-01-25 | [52172](https://github.com/airbytehq/airbyte/pull/52172) | Update dependencies |
| 0.1.28 | 2025-01-18 | [51749](https://github.com/airbytehq/airbyte/pull/51749) | Update dependencies |
| 0.1.27 | 2025-01-11 | [51266](https://github.com/airbytehq/airbyte/pull/51266) | Update dependencies |
| 0.1.26 | 2025-01-04 | [50903](https://github.com/airbytehq/airbyte/pull/50903) | Update dependencies |
| 0.1.25 | 2024-12-28 | [50491](https://github.com/airbytehq/airbyte/pull/50491) | Update dependencies |
| 0.1.24 | 2024-12-21 | [50204](https://github.com/airbytehq/airbyte/pull/50204) | Update dependencies |
| 0.1.23 | 2024-12-14 | [47113](https://github.com/airbytehq/airbyte/pull/47113) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.1.22 | 2024-10-12 | [46820](https://github.com/airbytehq/airbyte/pull/46820) | Update dependencies |
| 0.1.21 | 2024-10-05 | [46488](https://github.com/airbytehq/airbyte/pull/46488) | Update dependencies |
| 0.1.20 | 2024-09-28 | [46152](https://github.com/airbytehq/airbyte/pull/46152) | Update dependencies |
| 0.1.19 | 2024-09-21 | [45750](https://github.com/airbytehq/airbyte/pull/45750) | Update dependencies |
| 0.1.18 | 2024-09-14 | [45554](https://github.com/airbytehq/airbyte/pull/45554) | Update dependencies |
| 0.1.17 | 2024-09-07 | [45253](https://github.com/airbytehq/airbyte/pull/45253) | Update dependencies |
| 0.1.16 | 2024-08-31 | [44972](https://github.com/airbytehq/airbyte/pull/44972) | Update dependencies |
| 0.1.15 | 2024-08-24 | [44359](https://github.com/airbytehq/airbyte/pull/44359) | Update dependencies |
| 0.1.14 | 2024-08-12 | [43848](https://github.com/airbytehq/airbyte/pull/43848) | Update dependencies |
| 0.1.13 | 2024-08-10 | [43606](https://github.com/airbytehq/airbyte/pull/43606) | Update dependencies |
| 0.1.12 | 2024-08-03 | [43286](https://github.com/airbytehq/airbyte/pull/43286) | Update dependencies |
| 0.1.11 | 2024-07-27 | [42597](https://github.com/airbytehq/airbyte/pull/42597) | Update dependencies |
| 0.1.10 | 2024-07-20 | [42169](https://github.com/airbytehq/airbyte/pull/42169) | Update dependencies |
| 0.1.9 | 2024-07-13 | [41847](https://github.com/airbytehq/airbyte/pull/41847) | Update dependencies |
| 0.1.8 | 2024-07-10 | [41369](https://github.com/airbytehq/airbyte/pull/41369) | Update dependencies |
| 0.1.7 | 2024-07-09 | [41229](https://github.com/airbytehq/airbyte/pull/41229) | Update dependencies |
| 0.1.6 | 2024-07-06 | [40888](https://github.com/airbytehq/airbyte/pull/40888) | Update dependencies |
| 0.1.5 | 2024-06-25 | [40338](https://github.com/airbytehq/airbyte/pull/40338) | Update dependencies |
| 0.1.4 | 2024-06-21 | [39939](https://github.com/airbytehq/airbyte/pull/39939) | Update dependencies |
| 0.1.3 | 2024-06-04 | [38938](https://github.com/airbytehq/airbyte/pull/38938) | [autopull] Upgrade base image to v1.2.1 |
| 0.1.2 | 2024-05-21 | [38512](https://github.com/airbytehq/airbyte/pull/38512) | [autopull] base image + poetry + up_to_date |
| 0.1.1 | 2022-12-16 | [20564](https://github.com/airbytehq/airbyte/pull/20564) | add quote stream to alpha-vantage |
| 0.1.0 | 2022-10-21 | [18320](https://github.com/airbytehq/airbyte/pull/18320) | New source |

</details>
