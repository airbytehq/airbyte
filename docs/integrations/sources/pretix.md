# Pretix
[Pretix](https://pretix.eu/about/en/) connector enables seamless data integration with the Pretix event ticketing platform, allowing users to sync ticket sales, attendee information, event data, and other metrics directly into their data warehouse or analytics tools. This connector supports automated data extraction for efficient, reporting and data-driven insights across events managed in Pretix.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_token` | `string` | API Token. API token to use. Obtain it from the pretix web interface by creating a new token under your team settings. |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| orgainzers | slug | DefaultPaginator | ✅ |  ❌  |
| events | slug | DefaultPaginator | ✅ |  ❌  |
| tax_rules | id | DefaultPaginator | ✅ |  ❌  |
| categories | id | DefaultPaginator | ✅ |  ❌  |
| items | id | DefaultPaginator | ✅ |  ❌  |
| orders | code | DefaultPaginator | ✅ |  ❌  |
| vouchers | id | DefaultPaginator | ✅ |  ❌  |
| discounts | id | DefaultPaginator | ✅ |  ❌  |
| checkin_lists | id | DefaultPaginator | ✅ |  ❌  |
| waiting_list_entries | id | DefaultPaginator | ✅ |  ❌  |
| customers | identifier | DefaultPaginator | ✅ |  ❌  |
| sales_channels | identifier | DefaultPaginator | ✅ |  ❌  |
| membership_types |  | DefaultPaginator | ✅ |  ❌  |
| memberships |  | DefaultPaginator | ✅ |  ❌  |
| giftcards | id | DefaultPaginator | ✅ |  ❌  |
| reusable_media | id | DefaultPaginator | ✅ |  ❌  |
| teams | id | DefaultPaginator | ✅ |  ❌  |
| devices | device_id | DefaultPaginator | ✅ |  ❌  |
| webhooks | id | DefaultPaginator | ✅ |  ❌  |
| seating_plans | id | DefaultPaginator | ✅ |  ❌  |
| auto_checkin_rules | id | DefaultPaginator | ✅ |  ❌  |
| shredders |  | No pagination | ✅ |  ❌  |
| exporters |  | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-11-09 | | Initial release by [@parthiv11](https://github.com/parthiv11) via Connector Builder |

</details>
