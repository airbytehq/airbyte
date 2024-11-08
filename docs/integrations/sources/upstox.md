# upstox
upstox source

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `instrument_key` | `string` | instrument_key.  |  |
| `expiry_date` | `string` | expiry_date.  |  |
| `quote_interval` | `string` | quote_interval.  |  |
| `end_date` | `string` | end_date.  |  |
| `start_date` | `string` | start_date.  |  |
| `candle_interval` | `string` | candle_interval.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| marketholidays |  | No pagination | ✅ |  ❌  |
| option_chain |  | No pagination | ✅ |  ❌  |
| fullmarketquotes |  | No pagination | ✅ |  ❌  |
| ohlcquotes |  | No pagination | ✅ |  ❌  |
| ltpquotes |  | No pagination | ✅ |  ❌  |
| holdings |  | No pagination | ✅ |  ❌  |
| orderdetails |  | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-11-08 | | Initial release by [@bala-ceg](https://github.com/bala-ceg) via Connector Builder |

</details>
