# Stockdata
Stockdata provides access to market news for global exchanges, and trading data for US stocks.
With this connector we can extract data from EOD , Intraday and news feeds streams



## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `exchanges` | `string` | Exchanges.  | NASDAQ |
| `from` | `string` | From.  |  |
| `to` | `string` | To.  |  |
| `symbols` | `string` | Symbols.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| Stock Search |  | DefaultPaginator | ✅ |  ❌  |
| News Feeds | uuid | DefaultPaginator | ✅ |  ❌  |
| EOD Data |  | DefaultPaginator | ✅ |  ❌  |
| Intraday Unadjusted Data |  | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-10-26 | | Initial release by [@ombhardwajj](https://github.com/ombhardwajj) via Connector Builder |

</details>
