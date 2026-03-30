# Perk
Sync travel and spend data from Perk into your data warehouse.
This source connector syncs users, trips, bookings, cost centers, invoices, invoice lines, and profiles.
Configuration requires your Perk API key and a start date from which to sync data.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `start_date` | `string` | Start Date. ISO8601 Date-time (e.g. 2024-09-19T00:00:00Z) |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| users |  | DefaultPaginator | ✅ |  ❌  |
| trips |  | DefaultPaginator | ✅ |  ✅  |
| bookings |  | DefaultPaginator | ✅ |  ✅  |
| cost_centers |  | DefaultPaginator | ✅ |  ❌  |
| invoices |  | DefaultPaginator | ✅ |  ✅  |
| profiles |  | DefaultPaginator | ✅ |  ❌  |
| invoices_lines |  | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2026-02-16 | | Initial release by [@claudiangr](https://github.com/claudiangr) via Connector Builder |

</details>
