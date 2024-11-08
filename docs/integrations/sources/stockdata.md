# StockData
Stockdata provides access to market news for global exchanges, and trading data for US stocks.
With this connector we can extract data from EOD , Intraday and news feeds streams



## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `exchanges` | `string` | Exchanges.  | NASDAQ |
| `from` | `string` | From.  |  |
| `to` | `string` | To.  |  |
| `symbols` | `array` | Symbols.  |  |
| `industries` | `string` | Industries. Specify the industries of entities which have been identified within the article. |  |
| `filter_entities` | `boolean` | Filter Entities.  | false |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| Stock Search |  | DefaultPaginator | ✅ |  ❌  |
| News Feeds | uuid | DefaultPaginator | ✅ |  ❌  |
| EOD Data |  | No pagination | ✅ |  ✅  |
| Intraday Unadjusted Data | date.ticker | No pagination | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-11-08 | | Initial release by [@ombhardwajj](https://github.com/ombhardwajj) via Connector Builder |

</details>
