# JustCall
JustCall connector enables seamless data integration by syncing call logs, contacts, and analytics from JustCall to various data destinations. This connector ensures businesses can centralize communication data for better reporting and analysis

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key_2` | `string` | API Key.  |  |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| users | id | DefaultPaginator | ✅ |  ❌  |
| calls | id | DefaultPaginator | ✅ |  ✅  |
| sms | id | DefaultPaginator | ✅ |  ✅  |
| contacts | id | No pagination | ✅ |  ❌  |
| phone_numbers | id | No pagination | ✅ |  ❌  |
| agent_analytics | agent_id | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-10-21 | | Initial release by [@bishalbera](https://github.com/bishalbera) via Connector Builder |

</details>
