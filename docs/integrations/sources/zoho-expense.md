# Zoho Expense
Zoho Expense connector enables seamless data synchronization between Zoho Expense and various destinations. This connector automates expense tracking workflows by extracting financial data efficiently, ensuring accurate reporting and streamlined operations.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `client_id` | `string` | OAuth Client ID.  |  |
| `client_secret` | `string` | OAuth Client Secret.  |  |
| `refresh_token` | `string` | OAuth Refresh Token.  |  |
| `data_center` | `string` | Data Center. The domain suffix for the Zoho Expense API based on your data center location (e.g., `com`, `in`, `jp` etc.) | `com` |


## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| users | user_id | DefaultPaginator | ✅ |  ❌  |
| trips | trip_id | DefaultPaginator | ✅ |  ❌  |
| expense_reports | report_id | DefaultPaginator | ✅ |  ❌  |
| projects |  | DefaultPaginator | ✅ |  ❌  |
| customers | contact_id | DefaultPaginator | ✅ |  ❌  |
| organizations | organization_id | DefaultPaginator | ✅ |  ❌  |
| expense_categories | category_id | DefaultPaginator | ✅ |  ❌  |
| currencies | currency_id | DefaultPaginator | ✅ |  ❌  |
| taxes | tax_id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.6 | 2025-01-18 | [51935](https://github.com/airbytehq/airbyte/pull/51935) | Update dependencies |
| 0.0.5 | 2025-01-11 | [51461](https://github.com/airbytehq/airbyte/pull/51461) | Update dependencies |
| 0.0.4 | 2024-12-28 | [50831](https://github.com/airbytehq/airbyte/pull/50831) | Update dependencies |
| 0.0.3 | 2024-12-21 | [50385](https://github.com/airbytehq/airbyte/pull/50385) | Update dependencies |
| 0.0.2 | 2024-12-14 | [49453](https://github.com/airbytehq/airbyte/pull/49453) | Update dependencies |
| 0.0.1 | 2024-10-26 | | Initial release by [@bishalbera](https://github.com/bishalbera) via Connector Builder |

</details>
