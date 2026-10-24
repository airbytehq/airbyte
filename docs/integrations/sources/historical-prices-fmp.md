# Historical Prices FMP
FMP provides financial data for historical stock prices using the stable endpoint. Correctly configured to use the symbol as a path parameter.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| stock_historical_price |  | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2025-09-03 | | Initial release by [@dvdzapata](https://github.com/dvdzapata) via Connector Builder |

</details>
