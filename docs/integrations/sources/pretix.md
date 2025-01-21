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
| 0.0.8 | 2025-01-18 | [51883](https://github.com/airbytehq/airbyte/pull/51883) | Update dependencies |
| 0.0.7 | 2025-01-11 | [51338](https://github.com/airbytehq/airbyte/pull/51338) | Update dependencies |
| 0.0.6 | 2024-12-28 | [50706](https://github.com/airbytehq/airbyte/pull/50706) | Update dependencies |
| 0.0.5 | 2024-12-21 | [50284](https://github.com/airbytehq/airbyte/pull/50284) | Update dependencies |
| 0.0.4 | 2024-12-14 | [49720](https://github.com/airbytehq/airbyte/pull/49720) | Update dependencies |
| 0.0.3 | 2024-12-12 | [49357](https://github.com/airbytehq/airbyte/pull/49357) | Update dependencies |
| 0.0.2 | 2024-12-11 | [49073](https://github.com/airbytehq/airbyte/pull/49073) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.1 | 2024-11-09 | | Initial release by [@parthiv11](https://github.com/parthiv11) via Connector Builder |

</details>
