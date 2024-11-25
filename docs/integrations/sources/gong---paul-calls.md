# Gong - paul calls
Add an optional users_to_fetch filter to only retriever calls from a subset of users

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `access_key` | `string` | Gong Access Key. Gong Access Key |  |
| `access_key_secret` | `string` | Gong Access Key Secret. Gong Access Key Secret |  |
| `start_date` | `string` | Start date. The date from which to list calls, in the ISO-8601 format; if not specified, the calls start with the earliest recorded call. For web-conference calls recorded by Gong, the date denotes its scheduled time, otherwise, it denotes its actual start time. |  |
| `users_to_fetch` | `array` | users_to_fetch.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| users | id | DefaultPaginator | ✅ |  ❌  |
| calls | id | DefaultPaginator | ✅ |  ❌  |
| extensiveCalls | id | DefaultPaginator | ✅ |  ❌  |
| scorecards | scorecardId | DefaultPaginator | ✅ |  ❌  |
| answeredScorecards | answeredScorecardId | DefaultPaginator | ✅ |  ❌  |
| transcripts | callId | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-11-25 | | Initial release by [@girarda](https://github.com/girarda) via Connector Builder |

</details>
