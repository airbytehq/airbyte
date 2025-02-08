# Clockify (Holidays and Scheduling)
Added holidays and scheduling streams to fetching

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. You can get your api access_key &lt;a href=&quot;https://app.clockify.me/user/settings&quot;&gt;here&lt;/a&gt; This API is Case Sensitive. |  |
| `api_url` | `string` | API Url. The URL for the Clockify API. This should only need to be modified if connecting to an enterprise version of Clockify. | https://api.clockify.me |
| `workspace_id` | `string` | Workspace Id. WorkSpace Id |  |
| `start` | `string` | Start Date . Represents start date in yyyy-MM-ddThh:mm:ssZ format. | 2024-01-01T00:00:00Z |
| `end` | `string` | End Date. Represents start date in yyyy-MM-ddThh:mm:ssZ format. | 2024-12-31T00:00:00Z |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| users | id | DefaultPaginator | ✅ |  ❌  |
| projects |  | DefaultPaginator | ✅ |  ❌  |
| clients | id | DefaultPaginator | ✅ |  ❌  |
| tags | id | DefaultPaginator | ✅ |  ❌  |
| user_groups | id | DefaultPaginator | ✅ |  ❌  |
| time_entries |  | DefaultPaginator | ✅ |  ❌  |
| tasks |  | DefaultPaginator | ✅ |  ❌  |
| scheduling |  | DefaultPaginator | ✅ |  ❌  |
| holidays | id | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2025-02-08 | | Initial release by [@73R3WY](https://github.com/73R3WY) via Connector Builder |

</details>
