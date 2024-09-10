# Orb (Connector Builder)
Testing

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `start_date` | `string` | Start date.  |  |
| `api_key` | `string` | API Key.  |  |
| `event_ids` | `array` | event_ids. [&#39;event_id1&#39;,&#39;event_id2&#39;,&#39;event_id3&#39;] |  |
| `timeframe_end` | `string` | timeframe_end.  |  |
| `timeframe_start` | `string` | timeframe_start.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| customers | id | DefaultPaginator | ✅ |  ❌  |
| credits_ledger_entries | id | DefaultPaginator | ✅ |  ❌  |
| events | id | DefaultPaginator | ✅ |  ❌  |
| balances | id | DefaultPaginator | ✅ |  ❌  |
| plans | id | DefaultPaginator | ✅ |  ✅  |
| subscriptions | id | DefaultPaginator | ✅ |  ✅  |
| credits_ledger_entries_decrements | id | DefaultPaginator | ✅ |  ❌  |
| event_history | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date       | Subject        |
|------------------|------------|----------------|
| 0.0.1 | 2024-09-10 | Initial release by [@nataliekwong](https://github.com/nataliekwong) via Connector Builder|

</details>