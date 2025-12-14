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

| Version | Date              | Pull Request | Subject        |
|---------|-------------------|--------------|----------------|
| 0.0.43 | 2025-12-09 | [70614](https://github.com/airbytehq/airbyte/pull/70614) | Update dependencies |
| 0.0.42 | 2025-11-25 | [70008](https://github.com/airbytehq/airbyte/pull/70008) | Update dependencies |
| 0.0.41 | 2025-11-18 | [69599](https://github.com/airbytehq/airbyte/pull/69599) | Update dependencies |
| 0.0.40 | 2025-10-29 | [68948](https://github.com/airbytehq/airbyte/pull/68948) | Update dependencies |
| 0.0.39 | 2025-10-21 | [68219](https://github.com/airbytehq/airbyte/pull/68219) | Update dependencies |
| 0.0.38 | 2025-10-14 | [67488](https://github.com/airbytehq/airbyte/pull/67488) | Update dependencies |
| 0.0.37 | 2025-09-30 | [66959](https://github.com/airbytehq/airbyte/pull/66959) | Update dependencies |
| 0.0.36 | 2025-09-23 | [66418](https://github.com/airbytehq/airbyte/pull/66418) | Update dependencies |
| 0.0.35 | 2025-09-09 | [65875](https://github.com/airbytehq/airbyte/pull/65875) | Update dependencies |
| 0.0.34 | 2025-09-05 | [65966](https://github.com/airbytehq/airbyte/pull/65966) | Update to CDK v7.0.0 |
| 0.0.33 | 2025-08-23 | [65174](https://github.com/airbytehq/airbyte/pull/65174) | Update dependencies |
| 0.0.32 | 2025-08-09 | [64746](https://github.com/airbytehq/airbyte/pull/64746) | Update dependencies |
| 0.0.31 | 2025-08-02 | [64246](https://github.com/airbytehq/airbyte/pull/64246) | Update dependencies |
| 0.0.30 | 2025-07-26 | [63841](https://github.com/airbytehq/airbyte/pull/63841) | Update dependencies |
| 0.0.29 | 2025-07-19 | [63425](https://github.com/airbytehq/airbyte/pull/63425) | Update dependencies |
| 0.0.28 | 2025-07-12 | [62661](https://github.com/airbytehq/airbyte/pull/62661) | Update dependencies |
| 0.0.27 | 2025-06-28 | [62336](https://github.com/airbytehq/airbyte/pull/62336) | Update dependencies |
| 0.0.26 | 2025-06-21 | [61871](https://github.com/airbytehq/airbyte/pull/61871) | Update dependencies |
| 0.0.25 | 2025-06-14 | [61074](https://github.com/airbytehq/airbyte/pull/61074) | Update dependencies |
| 0.0.24 | 2025-05-24 | [60510](https://github.com/airbytehq/airbyte/pull/60510) | Update dependencies |
| 0.0.23 | 2025-05-10 | [60097](https://github.com/airbytehq/airbyte/pull/60097) | Update dependencies |
| 0.0.22 | 2025-05-04 | [59505](https://github.com/airbytehq/airbyte/pull/59505) | Update dependencies |
| 0.0.21 | 2025-04-27 | [59065](https://github.com/airbytehq/airbyte/pull/59065) | Update dependencies |
| 0.0.20 | 2025-04-19 | [58500](https://github.com/airbytehq/airbyte/pull/58500) | Update dependencies |
| 0.0.19 | 2025-04-12 | [57908](https://github.com/airbytehq/airbyte/pull/57908) | Update dependencies |
| 0.0.18 | 2025-04-05 | [57354](https://github.com/airbytehq/airbyte/pull/57354) | Update dependencies |
| 0.0.17 | 2025-03-29 | [56728](https://github.com/airbytehq/airbyte/pull/56728) | Update dependencies |
| 0.0.16 | 2025-03-22 | [56166](https://github.com/airbytehq/airbyte/pull/56166) | Update dependencies |
| 0.0.15 | 2025-03-08 | [55541](https://github.com/airbytehq/airbyte/pull/55541) | Update dependencies |
| 0.0.14 | 2025-03-01 | [55043](https://github.com/airbytehq/airbyte/pull/55043) | Update dependencies |
| 0.0.13 | 2025-02-23 | [54616](https://github.com/airbytehq/airbyte/pull/54616) | Update dependencies |
| 0.0.12 | 2025-02-15 | [53986](https://github.com/airbytehq/airbyte/pull/53986) | Update dependencies |
| 0.0.11 | 2025-02-08 | [53497](https://github.com/airbytehq/airbyte/pull/53497) | Update dependencies |
| 0.0.10 | 2025-02-01 | [52984](https://github.com/airbytehq/airbyte/pull/52984) | Update dependencies |
| 0.0.9 | 2025-01-25 | [52500](https://github.com/airbytehq/airbyte/pull/52500) | Update dependencies |
| 0.0.8 | 2025-01-18 | [51883](https://github.com/airbytehq/airbyte/pull/51883) | Update dependencies |
| 0.0.7 | 2025-01-11 | [51338](https://github.com/airbytehq/airbyte/pull/51338) | Update dependencies |
| 0.0.6 | 2024-12-28 | [50706](https://github.com/airbytehq/airbyte/pull/50706) | Update dependencies |
| 0.0.5 | 2024-12-21 | [50284](https://github.com/airbytehq/airbyte/pull/50284) | Update dependencies |
| 0.0.4 | 2024-12-14 | [49720](https://github.com/airbytehq/airbyte/pull/49720) | Update dependencies |
| 0.0.3 | 2024-12-12 | [49357](https://github.com/airbytehq/airbyte/pull/49357) | Update dependencies |
| 0.0.2 | 2024-12-11 | [49073](https://github.com/airbytehq/airbyte/pull/49073) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.1   | 2024-11-09 | | Initial release by [@parthiv11](https://github.com/parthiv11) via Connector Builder |

</details>
