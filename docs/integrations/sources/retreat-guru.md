# Retreat Guru
A source connector for Retreat Booking Guru, a retreat center management platform. Syncs registrations, programs, transactions, payments, items, leads, people, teachers, lodgings, venues, and venue_uses.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `token` | `string` | Token. The token to use for authentication |  |
| `start_date` | `string` | Start Date. Start date for data sync in YYYY-MM-DD format (e.g. 2020-01-01) |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| registrations | id | DefaultPaginator | ✅ |  ✅  |
| programs | id | DefaultPaginator | ✅ |  ✅  |
| venues | id | No pagination | ✅ |  ❌  |
| transactions | id | DefaultPaginator | ✅ |  ✅  |
| payments | id | DefaultPaginator | ✅ |  ✅  |
| items | id | DefaultPaginator | ✅ |  ✅  |
| leads | id | DefaultPaginator | ✅ |  ❌  |
| people | id | DefaultPaginator | ✅ |  ❌  |
| teachers | id | DefaultPaginator | ✅ |  ❌  |
| lodgings | id | No pagination | ✅ |  ❌  |
| venue_uses | id | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2026-03-28 | | Initial release by [@chrisokoko](https://github.com/chrisokoko) via Connector Builder |

</details>
