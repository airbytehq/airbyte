# Oura Ring
Oura Ring connector pulls health data from Oura&#39;s public API with a token you generate for your user account

Endpoints: 
Sleep Score
Heartrate
Daily Activities

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. API key or access token |  |
| `end_date` | `string` | End Date. Optional end date in ISO 8601 format (e.g., 2024-04-15T00:00:00+00:00). If not set, defaults to now. |  |
| `start_date` | `string` | Start Date. The start date in ISO 8601 format (e.g., 2024-01-01T00:00:00+00:00) |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| Sleep Score by day | id | DefaultPaginator | ✅ |  ❌  |
| Heartrates by start date | timestamp | DefaultPaginator | ✅ |  ✅  |
| daily_activities | id | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2025-05-18 | | Initial release by [@rwask](https://github.com/rwask) via Connector Builder |

</details>
