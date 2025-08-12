# Nexiopay
Website: https://dashboard.nexiopay.com/
API Reference: https://docs.nexiopay.com/reference/api-reference

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. Your Nexio API key (password). You can find it in the Nexio Dashboard under Settings &gt; User Management. Select the API user and copy the API key. |  |
| `username` | `string` | API Username. Your Nexio API username. You can find it in the Nexio Dashboard under Settings &gt; User Management. Select the API user and copy the username. |  |
| `subdomain` | `string` | Subdomain. The subdomain for the Nexio API environment, such as &#39;nexiopaysandbox&#39; or &#39;nexiopay&#39;. | nexiopay |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| terminal_list | terminalId | No pagination | ✅ |  ❌  |
| recipients | recipientId | DefaultPaginator | ✅ |  ✅  |
| payment_types | id | DefaultPaginator | ✅ |  ❌  |
| user | accountId | No pagination | ✅ |  ✅  |
| spendbacks | id | DefaultPaginator | ✅ |  ✅  |
| card_tokens | key | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.15 | 2025-08-09 | [64690](https://github.com/airbytehq/airbyte/pull/64690) | Update dependencies |
| 0.0.14 | 2025-08-02 | [64176](https://github.com/airbytehq/airbyte/pull/64176) | Update dependencies |
| 0.0.13 | 2025-07-26 | [63881](https://github.com/airbytehq/airbyte/pull/63881) | Update dependencies |
| 0.0.12 | 2025-07-19 | [63431](https://github.com/airbytehq/airbyte/pull/63431) | Update dependencies |
| 0.0.11 | 2025-07-12 | [63171](https://github.com/airbytehq/airbyte/pull/63171) | Update dependencies |
| 0.0.10 | 2025-07-05 | [62611](https://github.com/airbytehq/airbyte/pull/62611) | Update dependencies |
| 0.0.9 | 2025-06-28 | [62335](https://github.com/airbytehq/airbyte/pull/62335) | Update dependencies |
| 0.0.8 | 2025-06-21 | [61934](https://github.com/airbytehq/airbyte/pull/61934) | Update dependencies |
| 0.0.7 | 2025-06-14 | [61039](https://github.com/airbytehq/airbyte/pull/61039) | Update dependencies |
| 0.0.6 | 2025-05-24 | [60494](https://github.com/airbytehq/airbyte/pull/60494) | Update dependencies |
| 0.0.5 | 2025-05-10 | [60173](https://github.com/airbytehq/airbyte/pull/60173) | Update dependencies |
| 0.0.4 | 2025-05-03 | [59046](https://github.com/airbytehq/airbyte/pull/59046) | Update dependencies |
| 0.0.3 | 2025-04-19 | [58505](https://github.com/airbytehq/airbyte/pull/58505) | Update dependencies |
| 0.0.2 | 2025-04-12 | [57873](https://github.com/airbytehq/airbyte/pull/57873) | Update dependencies |
| 0.0.1 | 2025-04-09 | [57530](https://github.com/airbytehq/airbyte/pull/57530) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>
