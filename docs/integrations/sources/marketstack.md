# Marketstack
Marketstack provides data from 72 global stock exchanges.
Using this connector we can extract Historical Data , Splits and Dividends data !

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `start_date` | `string` | Start Date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| Exchanges | mic | DefaultPaginator | ✅ |  ❌  |
| Tickers | symbol | DefaultPaginator | ✅ |  ❌  |
| Historical Data |  | DefaultPaginator | ✅ |  ✅  |
| Splits |  | DefaultPaginator | ✅ |  ❌  |
| Dividends |  | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-11-07 | | Initial release by [@ombhardwajj](https://github.com/ombhardwajj) via Connector Builder |

</details>
