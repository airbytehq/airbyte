# MoneyBird
Airbyte connector for MoneyBird

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_token` | `string` | API Token. A MoneyBird personal access token or OAuth token. Create one at https://moneybird.com/user/applications/new.  |  |
| `start_date` | `string` | Start Date. ISO-8601 UTC datetime (e.g. 2024-01-01T00:00:00.000Z). Only records updated on or after this date are synced on incremental runs. Defaults to 2020-01-01 if omitted. Must be within 10 years of today due to a MoneyBird API period limit.  |  |
| `administration_id` | `string` | Administration ID. The numeric ID of your MoneyBird administration. Visible in the URL after logging in: moneybird.com/&lt;administration_id&gt;.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| contacts | id | DefaultPaginator | ✅ |  ✅  |
| ledger_accounts | id | No pagination | ✅ |  ❌  |
| sales_invoices | id | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2026-06-26 | | Initial release by [@dgommers](https://github.com/dgommers) via Connector Builder |

</details>
