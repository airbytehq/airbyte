# StockData
Stockdata provides access to market news for global exchanges, and trading data for US stocks.
With this connector we can extract data from EOD , Intraday and news feeds streams

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `symbols` | `array` | Symbols.  |  |
| `industries` | `array` | Industries. Specify the industries of entities which have been identified within the article. |  |
| `filter_entities` | `boolean` | By default all entities for each article are returned - by setting this to true, only the relevant entities to your query will be returned with each article. For example, if you set symbols=TSLA and filter_entities=true, only "TSLA" entities will be returned with the articles.  | false |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| news_feeds_per_symbol | uuid | DefaultPaginator | ✅ |  ✅  |
| news_feeds_per_industry | uuid | DefaultPaginator | ✅ |  ✅  |
| eod_data | date.ticker | No pagination | ✅ |  ✅  |
| intraday_unadjusted_data | date.ticker | No pagination | ✅ |  ✅  |


## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.23 | 2025-05-25 | [60479](https://github.com/airbytehq/airbyte/pull/60479) | Update dependencies |
| 0.0.22 | 2025-05-10 | [60132](https://github.com/airbytehq/airbyte/pull/60132) | Update dependencies |
| 0.0.21 | 2025-05-04 | [59643](https://github.com/airbytehq/airbyte/pull/59643) | Update dependencies |
| 0.0.20 | 2025-04-27 | [59008](https://github.com/airbytehq/airbyte/pull/59008) | Update dependencies |
| 0.0.19 | 2025-04-19 | [58451](https://github.com/airbytehq/airbyte/pull/58451) | Update dependencies |
| 0.0.18 | 2025-04-12 | [57973](https://github.com/airbytehq/airbyte/pull/57973) | Update dependencies |
| 0.0.17 | 2025-04-05 | [57450](https://github.com/airbytehq/airbyte/pull/57450) | Update dependencies |
| 0.0.16 | 2025-03-29 | [56825](https://github.com/airbytehq/airbyte/pull/56825) | Update dependencies |
| 0.0.15 | 2025-03-22 | [56278](https://github.com/airbytehq/airbyte/pull/56278) | Update dependencies |
| 0.0.14 | 2025-03-08 | [55572](https://github.com/airbytehq/airbyte/pull/55572) | Update dependencies |
| 0.0.13 | 2025-03-01 | [55091](https://github.com/airbytehq/airbyte/pull/55091) | Update dependencies |
| 0.0.12 | 2025-02-22 | [54525](https://github.com/airbytehq/airbyte/pull/54525) | Update dependencies |
| 0.0.11 | 2025-02-15 | [54095](https://github.com/airbytehq/airbyte/pull/54095) | Update dependencies |
| 0.0.10 | 2025-02-08 | [53523](https://github.com/airbytehq/airbyte/pull/53523) | Update dependencies |
| 0.0.9 | 2025-02-01 | [53043](https://github.com/airbytehq/airbyte/pull/53043) | Update dependencies |
| 0.0.8 | 2025-01-25 | [52409](https://github.com/airbytehq/airbyte/pull/52409) | Update dependencies |
| 0.0.7 | 2025-01-18 | [51978](https://github.com/airbytehq/airbyte/pull/51978) | Update dependencies |
| 0.0.6 | 2025-01-11 | [51447](https://github.com/airbytehq/airbyte/pull/51447) | Update dependencies |
| 0.0.5 | 2024-12-28 | [50789](https://github.com/airbytehq/airbyte/pull/50789) | Update dependencies |
| 0.0.4 | 2024-12-21 | [50357](https://github.com/airbytehq/airbyte/pull/50357) | Update dependencies |
| 0.0.3 | 2024-12-14 | [49745](https://github.com/airbytehq/airbyte/pull/49745) | Update dependencies |
| 0.0.2 | 2024-12-12 | [49442](https://github.com/airbytehq/airbyte/pull/49442) | Update dependencies |
| 0.0.1 | 2024-11-08 | | Initial release by [@ombhardwajj](https://github.com/ombhardwajj) via Connector Builder |

</details>
