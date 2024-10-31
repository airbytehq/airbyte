# Pretix
The Airbyte connector for Pretix enables seamless data integration with the Pretix event ticketing platform, allowing users to sync ticket sales, attendee information, event data, and other metrics directly into their data warehouse or analytics tools. This connector supports automated data extraction for efficient, reporting and data-driven insights across events managed in Pretix.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_token` | `string` | API Token. API token to use. Obtain it from the pretix web interface by creating a new token under your team settings. |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| orgainzers |  | DefaultPaginator | ✅ |  ❌  |
| events |  | DefaultPaginator | ✅ |  ❌  |
| tax_rules |  | DefaultPaginator | ✅ |  ❌  |
| categories |  | DefaultPaginator | ✅ |  ❌  |
| items |  | DefaultPaginator | ✅ |  ❌  |
| orders | code | DefaultPaginator | ✅ |  ❌  |
| vouchers |  | DefaultPaginator | ✅ |  ❌  |
| discounts |  | DefaultPaginator | ✅ |  ❌  |
| checkin_lists | id | DefaultPaginator | ✅ |  ❌  |
| sales_channels | identifier | DefaultPaginator | ✅ |  ❌  |
| giftcards | id | DefaultPaginator | ✅ |  ❌  |
| teams |  | DefaultPaginator | ✅ |  ❌  |
| devices | device_id | DefaultPaginator | ✅ |  ❌  |
| webhooks | id | DefaultPaginator | ✅ |  ❌  |
| seating_plans | id | DefaultPaginator | ✅ |  ❌  |
| shredders |  | DefaultPaginator | ✅ |  ❌  |
| exporters |  | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-10-31 | | Initial release by [@parthiv11](https://github.com/parthiv11) via Connector Builder |

</details>
