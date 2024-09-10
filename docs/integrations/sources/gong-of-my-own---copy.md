# Gong of my own - copy
its new

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `access_key` | `string` | Gong Access Key. Gong Access Key |  |
| `access_key_secret` | `string` | Gong Access Key Secret. Gong Access Key Secret |  |
| `start_date` | `string` | Start date. The date from which to list calls, in the ISO-8601 format; if not specified, the calls start with the earliest recorded call. For web-conference calls recorded by Gong, the date denotes its scheduled time, otherwise, it denotes its actual start time. |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| users | id | DefaultPaginator | ✅ |  ❌  |
| calls | id | DefaultPaginator | ✅ |  ❌  |
| extensiveCalls | id | DefaultPaginator | ✅ |  ❌  |
| scorecards | scorecardId | DefaultPaginator | ✅ |  ❌  |
| answeredScorecards | answeredScorecardId | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date       | Subject        |
|------------------|------------|----------------|
| 0.0.1 | 2024-09-10 | Initial release by [@erohmensing](https://github.com/erohmensing) via Connector Builder|

</details>