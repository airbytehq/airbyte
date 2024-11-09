# upstox
Upstox is a leading online brokerage platform in India that offers a seamless way to trade and invest in stocks, commodities, currencies, and mutual funds. Known for its user-friendly interface and affordable pricing, Upstox provides advanced charting tools, real-time market data, and analytics to help investors and traders make informed decisions.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `to_date` | `string` | to_date.  |  |
| `interval` | `string` | interval.  |  |
| `from_date` | `string` | from_date.  |  |
| `instrumentKey` | `array` | instrumentKey.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| marketholidays | date | No pagination | ✅ |  ❌  |
| historicalcandle |  | No pagination | ✅ |  ❌  |
| intradaycandle |  | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-11-09 | | Initial release by [@bala-ceg](https://github.com/bala-ceg) via Connector Builder |

</details>
