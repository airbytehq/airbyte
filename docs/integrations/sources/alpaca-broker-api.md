# Alpaca Broker API
Website: https://broker-app.alpaca.markets/dashboard
API reference: https://docs.alpaca.markets/reference/getallaccounts

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `environment` | `string` | Environment. The trading environment, either &#39;live&#39;, &#39;paper&#39; or &#39;broker-api.sandbox&#39;. | broker-api.sandbox |
| `username` | `string` | Username. API Key ID for the alpaca market |  |
| `password` | `string` | Password. Your Alpaca API Secret Key. You can find this in the Alpaca developer web console under your account settings. |  |
| `start_date` | `string` | Start date.  |  |
| `limit` | `string` | Limit. Limit for each response objects | 20 |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| assets | id | No pagination | ✅ |  ❌  |
| accounts_activities | id | DefaultPaginator | ✅ |  ✅  |
| accounts | id | No pagination | ✅ |  ✅  |
| account_documents | id | No pagination | ✅ |  ✅  |
| calendar | uuid | No pagination | ✅ |  ✅  |
| clock | uuid | No pagination | ✅ |  ❌  |
| country-info | uuid | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2025-04-02 | | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>
