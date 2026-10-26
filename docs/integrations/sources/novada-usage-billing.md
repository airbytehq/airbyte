# Novada Usage &amp; Billing
Read-only Novada source connector for syncing daily capture usage, wallet usage records, and wallet balance to Airbyte destinations for cost monitoring and billing reconciliation. Uses a Bearer API key; no external resources are modified.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `start_date` | `string` | Start Date. UTC ISO 8601, for example 2026-09-20T00:00:00Z |  |
| `wallet_page_size` | `integer` | Wallet Page Size.  | 10 |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| capture_usage_daily | time_label | No pagination | ✅ |  ✅  |
| wallet_usage_records | id | DefaultPaginator | ✅ |  ❌  |
| wallet_balance_snapshot |  | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2026-09-22 | | Initial release by [@Novada-proxy](https://github.com/Novada-proxy) via Connector Builder |

</details>
