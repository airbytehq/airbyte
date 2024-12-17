# Capsule CRM
Capsule CRM connector  enables seamless data syncing from Capsule CRM to various data warehouses, helping businesses centralize and analyze customer data efficiently. It supports real-time data extraction of contacts, opportunities, and custom fields, making it ideal for comprehensive CRM analytics and reporting.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `bearer_token` | `string` | Bearer Token. Bearer token to authenticate API requests. Generate it from the &#39;My Preferences&#39; &gt; &#39;API Authentication Tokens&#39; page in your Capsule account. |  |
| `start_date` | `string` | Start date.  |  |
| `entity` | `string` | Entity.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| users | id | DefaultPaginator | ✅ |  ❌  |
| parties | id | DefaultPaginator | ✅ |  ❌  |
| tasks | id | DefaultPaginator | ✅ |  ❌  |
| employees | id | DefaultPaginator | ✅ |  ❌  |
| projects | id | DefaultPaginator | ✅ |  ❌  |
| opportunities | id | DefaultPaginator | ✅ |  ✅  |
| pipelines | id | DefaultPaginator | ✅ |  ❌  |
| milestones | id | DefaultPaginator | ✅ |  ❌  |
| site |  | DefaultPaginator | ✅ |  ❌  |
| tags | id | DefaultPaginator | ✅ |  ❌  |
| custom_fields | id | DefaultPaginator | ✅ |  ❌  |
| lost_reasons | id | DefaultPaginator | ✅ |  ❌  |
| board | id | DefaultPaginator | ✅ |  ❌  |
| categories | id | DefaultPaginator | ✅ |  ❌  |
| activity_types | id | DefaultPaginator | ✅ |  ❌  |
| stages | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-11-09 | | Initial release by [@bishalbera](https://github.com/bishalbera) via Connector Builder |

</details>
