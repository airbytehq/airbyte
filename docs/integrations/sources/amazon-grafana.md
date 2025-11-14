# Amazon Grafana API
Website: https://broker-app.alpaca.markets/dashboard
API reference: https://docs.alpaca.markets/reference/getallaccounts

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `workspace_id` | `string` | ID of Grafana workspace |  |
| `region` | `string` | AWS region | eu-central-1 |
| `service_account_id` | `string` | AWS Grafana Service Account ID |  |
| `aws_access_key_id` | `string` | AWS IAM Access Key ID |  |
| `aws_secret_access_key` | `string` | AWS IAM Secret Key |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| users | id | No pagination | ✅ |  ❌  |
| teams | id | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.1.0 | 2025-10-13 | [56962](https://github.com/airbytehq/airbyte/pull/56962) | Initial release |

</details>
