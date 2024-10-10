# Branch
Branch Connector

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `branch_secret` | `string` | branch_secret. branch secret |  |
| `export_date` | `string` | export_date. export date |  |
| `app_id` | `string` | app_id. The App Id |  |
| `branch_key` | `string` | branch_key. branch key |  |
| `access_token` | `string` | access-token. Access Token  |  |
| `start_date` | `string` | start_date. The start of the interval time range represented as an ISO-8601 complete datetime including Hours, Minutes, Seconds, and Milliseconds. Datetime must be within the last 120 days. |  |
| `end_date` | `string` | end_date. The end of the interval time range represented as an ISO-8601 complete datetime including Hours, Minutes, Seconds, and Milliseconds. |  |
| `report_type` | `string` | report_type. An array representing event type of your report. |  |
| `limit` | `integer` | limit. The maximum number of results to return. | 1 |
| `fields` | `array` | fields. An array representing fields/columns available in your report |  |
| `request_handle` | `string` | request_handle. The ID returned by the log export queue. |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| GET Export Request |  | No pagination | ✅ |  ❌  |
| Create Export Request |  | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-10-10 | | Initial release by [@itsxdamdam](https://github.com/itsxdamdam) via Connector Builder |

</details>
