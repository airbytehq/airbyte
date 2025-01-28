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
| 0.0.8 | 2025-01-25 | [52279](https://github.com/airbytehq/airbyte/pull/52279) | Update dependencies |
| 0.0.7 | 2025-01-18 | [51781](https://github.com/airbytehq/airbyte/pull/51781) | Update dependencies |
| 0.0.6 | 2025-01-11 | [51177](https://github.com/airbytehq/airbyte/pull/51177) | Update dependencies |
| 0.0.5 | 2024-12-28 | [50620](https://github.com/airbytehq/airbyte/pull/50620) | Update dependencies |
| 0.0.4 | 2024-12-21 | [50084](https://github.com/airbytehq/airbyte/pull/50084) | Update dependencies |
| 0.0.3 | 2024-12-14 | [49626](https://github.com/airbytehq/airbyte/pull/49626) | Update dependencies |
| 0.0.2 | 2024-12-12 | [48963](https://github.com/airbytehq/airbyte/pull/48963) | Update dependencies |
| 0.0.1 | 2024-11-07 | | Initial release by [@ombhardwajj](https://github.com/ombhardwajj) via Connector Builder |

</details>
