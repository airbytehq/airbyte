# TicketTailor
The Airbyte connector for [TicketTailor](https://tickettailor.com) enables seamless extraction of key event data, including details on events, products, vouchers, discounts, check-ins, issued tickets, orders, and waitlists. This integration allows businesses to analyze ticket sales, attendance, and customer interactions, streamlining event management insights.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. API key to use. Find it at https://www.getdrip.com/user/edit |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| events_series | id | DefaultPaginator | ✅ |  ❌  |
| events | id | DefaultPaginator | ✅ |  ❌  |
| products | id | DefaultPaginator | ✅ |  ❌  |
| vouchers | id | DefaultPaginator | ✅ |  ❌  |
| discounts | id | DefaultPaginator | ✅ |  ❌  |
| check_ins | id | DefaultPaginator | ✅ |  ❌  |
| issued_tickets | id | DefaultPaginator | ✅ |  ❌  |
| orders | id | DefaultPaginator | ✅ |  ❌  |
| waitlists | id | DefaultPaginator | ✅ |  ❌  |
| vouchers_codes | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-11-06 | | Initial release by [@parthiv11](https://github.com/parthiv11) via Connector Builder |

</details>
