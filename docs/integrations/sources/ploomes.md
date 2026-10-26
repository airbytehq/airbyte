# Ploomes
Connector to the Brazilian CRM Ploomes

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| contacts |  | DefaultPaginator | ✅ |  ✅  |
| deals |  | DefaultPaginator | ✅ |  ✅  |
| quotes |  | DefaultPaginator | ✅ |  ✅  |
| tasks |  | DefaultPaginator | ✅ |  ✅  |
| fields |  | DefaultPaginator | ✅ |  ❌  |
| fields_options_tables |  | DefaultPaginator | ✅ |  ❌  |
| fields_options_tables_options |  | DefaultPaginator | ✅ |  ❌  |
| contact_status |  | DefaultPaginator | ✅ |  ❌  |
| contact_types |  | DefaultPaginator | ✅ |  ❌  |
| deal_pipelines |  | DefaultPaginator | ✅ |  ❌  |
| deal_stages |  | DefaultPaginator | ✅ |  ❌  |
| deals_status |  | DefaultPaginator | ✅ |  ❌  |
| cities |  | DefaultPaginator | ✅ |  ❌  |
| states |  | DefaultPaginator | ✅ |  ❌  |
| tags |  | DefaultPaginator | ✅ |  ❌  |
| task_email_reminders |  | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2026-07-15 | | Initial release by [@thaynatheodoro](https://github.com/thaynatheodoro) via Connector Builder |

</details>
