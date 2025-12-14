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
| 0.0.18 | 2025-12-09 | [70561](https://github.com/airbytehq/airbyte/pull/70561) | Update dependencies |
| 0.0.17 | 2025-11-25 | [69918](https://github.com/airbytehq/airbyte/pull/69918) | Update dependencies |
| 0.0.16 | 2025-10-29 | [69061](https://github.com/airbytehq/airbyte/pull/69061) | Update dependencies |
| 0.0.15 | 2025-10-14 | [67807](https://github.com/airbytehq/airbyte/pull/67807) | Update dependencies |
| 0.0.14 | 2025-09-30 | [66245](https://github.com/airbytehq/airbyte/pull/66245) | Update dependencies |
| 0.0.13 | 2025-09-09 | [66036](https://github.com/airbytehq/airbyte/pull/66036) | Update dependencies |
| 0.0.12 | 2025-08-23 | [65338](https://github.com/airbytehq/airbyte/pull/65338) | Update dependencies |
| 0.0.11 | 2025-08-02 | [64421](https://github.com/airbytehq/airbyte/pull/64421) | Update dependencies |
| 0.0.10 | 2025-07-26 | [63794](https://github.com/airbytehq/airbyte/pull/63794) | Update dependencies |
| 0.0.9 | 2025-07-12 | [63046](https://github.com/airbytehq/airbyte/pull/63046) | Update dependencies |
| 0.0.8 | 2025-06-28 | [62152](https://github.com/airbytehq/airbyte/pull/62152) | Update dependencies |
| 0.0.7 | 2025-06-15 | [60706](https://github.com/airbytehq/airbyte/pull/60706) | Update dependencies |
| 0.0.6 | 2025-05-10 | [59828](https://github.com/airbytehq/airbyte/pull/59828) | Update dependencies |
| 0.0.5 | 2025-05-03 | [58739](https://github.com/airbytehq/airbyte/pull/58739) | Update dependencies |
| 0.0.4 | 2025-04-19 | [58245](https://github.com/airbytehq/airbyte/pull/58245) | Update dependencies |
| 0.0.3 | 2025-04-12 | [57646](https://github.com/airbytehq/airbyte/pull/57646) | Update dependencies |
| 0.0.2 | 2025-04-05 | [57186](https://github.com/airbytehq/airbyte/pull/57186) | Update dependencies |
| 0.0.1 | 2025-04-02 | [56962](https://github.com/airbytehq/airbyte/pull/56962) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>
