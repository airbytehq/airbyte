# Amazon Grafana API
Website: https://broker-app.alpaca.markets/dashboard
API reference: https://docs.alpaca.markets/reference/getallaccounts

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | Grafana API key |  |
| `workspace_id` | `string` | ID of Grafana workspace |  |
| `region` | `string` | AWS region | eu-central-1 |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| users | id | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.1.0 | 2025-10-13 | [56962](https://github.com/airbytehq/airbyte/pull/56962) | Initial release |

</details>
