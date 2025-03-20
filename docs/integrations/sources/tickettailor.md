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
| 0.0.14 | 2025-03-08 | [55578](https://github.com/airbytehq/airbyte/pull/55578) | Update dependencies |
| 0.0.13 | 2025-03-01 | [55115](https://github.com/airbytehq/airbyte/pull/55115) | Update dependencies |
| 0.0.12 | 2025-02-22 | [54519](https://github.com/airbytehq/airbyte/pull/54519) | Update dependencies |
| 0.0.11 | 2025-02-15 | [54068](https://github.com/airbytehq/airbyte/pull/54068) | Update dependencies |
| 0.0.10 | 2025-02-08 | [53544](https://github.com/airbytehq/airbyte/pull/53544) | Update dependencies |
| 0.0.9 | 2025-02-01 | [53055](https://github.com/airbytehq/airbyte/pull/53055) | Update dependencies |
| 0.0.8 | 2025-01-25 | [52404](https://github.com/airbytehq/airbyte/pull/52404) | Update dependencies |
| 0.0.7 | 2025-01-18 | [51952](https://github.com/airbytehq/airbyte/pull/51952) | Update dependencies |
| 0.0.6 | 2025-01-11 | [51414](https://github.com/airbytehq/airbyte/pull/51414) | Update dependencies |
| 0.0.5 | 2024-12-28 | [50750](https://github.com/airbytehq/airbyte/pull/50750) | Update dependencies |
| 0.0.4 | 2024-12-21 | [50327](https://github.com/airbytehq/airbyte/pull/50327) | Update dependencies |
| 0.0.3 | 2024-12-14 | [49784](https://github.com/airbytehq/airbyte/pull/49784) | Update dependencies |
| 0.0.2 | 2024-12-12 | [49374](https://github.com/airbytehq/airbyte/pull/49374) | Update dependencies |
| 0.0.1 | 2024-11-06 | | Initial release by [@parthiv11](https://github.com/parthiv11) via Connector Builder |

</details>
