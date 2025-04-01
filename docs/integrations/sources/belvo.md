# Belvo
Website: https://dashboard.belvo.com/
API Reference: https://developers.belvo.com/reference/using-the-api-reference

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `secret_id` | `string` | Secret ID. Your Belvo Secret ID. You can generate it by following the instructions at https://developers.belvo.com/docs/get-started-in-10-minutes#generate-your-api-keys. |  |
| `subdomain` | `string` | Subdomain. The subdomain for the Belvo API environment, such as &#39;sandbox&#39; or &#39;api&#39;. | api |
| `secret_password` | `string` | Secret Password. Your Belvo Secret Password. You can generate it by following the instructions at https://developers.belvo.com/docs/get-started-in-10-minutes#generate-your-api-keys. |  |
| `limit` | `string` | Limit. Limit for each response objects | 10 |

## Streams
| Stream Name            | Primary Key | Pagination       | Supports Full Sync | Supports Incremental |
|------------------------|-------------|----------------|---------------------|----------------------|
| institutions          | id          | DefaultPaginator | ✅                  | ❌                  |
| links                 | id          | DefaultPaginator | ✅                  | ❌                  |
| accounts              | id          | DefaultPaginator | ✅                  | ❌                  |
| transactions          | id          | DefaultPaginator | ❌                  | ❌                  |
| owners                | id          | DefaultPaginator | ✅                  | ❌                  |
| bills                 | id          | DefaultPaginator | ❌                  | ❌                  |
| tax_compliance_status | id          | DefaultPaginator | ✅                  | ❌                  |
| invoices              | id          | DefaultPaginator | ✅                  | ❌                  |
| financial_statements  | id          | DefaultPaginator | ✅                  | ❌                  |
| tax_retentions        | id          | DefaultPaginator | ✅                  | ❌                  |
| tax_returns           | id          | DefaultPaginator | ✅                  | ❌                  |
| tax_status            | id          | DefaultPaginator | ✅                  | ❌                  |
| incomes               | id          | DefaultPaginator | ✅                  | ❌                  |
| recurring_expenses    | id          | DefaultPaginator | ✅                  | ❌                  |
| risk_insights         | id          | DefaultPaginator | ✅                  | ❌                  |
| employment_metrics    | id          | DefaultPaginator | ✅                  | ❌                  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2025-04-01 | [56949](https://github.com/airbytehq/airbyte/pull/56949) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>
