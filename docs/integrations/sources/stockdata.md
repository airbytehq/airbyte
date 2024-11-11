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
| 0.0.1 | 2024-11-08 | | Initial release by [@ombhardwajj](https://github.com/ombhardwajj) via Connector Builder |

</details>
