# Productive
This page contains the setup guide and reference information for the [Productive](https://app.productive.io/) source connector.

## Documentation reference:
Visit `https://developer.productive.io/index.html#top` for API documentation

## Authentication setup
`Source-productive` uses api key authentication,
Visit `https://app.productive.io/ORG_ID-UUID/settings/api-integrations` for getting your API Key and organization ID

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `organization_id` | `string` | Organization ID. The organization ID which could be seen from `https://app.productive.io/xxxx-xxxx/settings/api-integrations` page |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| activities | id | DefaultPaginator | ✅ |  ❌  |
| approval_policies |  | DefaultPaginator | ✅ |  ❌  |
| workflows | id | DefaultPaginator | ✅ |  ❌  |
| boards | id | DefaultPaginator | ✅ |  ❌  |
| attachments | id | DefaultPaginator | ✅ |  ❌  |
| bookings | id | DefaultPaginator | ✅ |  ❌  |
| comments | id | DefaultPaginator | ✅ |  ❌  |
| companies | id | DefaultPaginator | ✅ |  ❌  |
| contact_entries | id | DefaultPaginator | ✅ |  ❌  |
| custom_field_options | id | DefaultPaginator | ✅ |  ❌  |
| custom_fields | id | DefaultPaginator | ✅ |  ❌  |
| dashboards | id | DefaultPaginator | ✅ |  ❌  |
| deal_statuses | id | DefaultPaginator | ✅ |  ❌  |
| deals | id | DefaultPaginator | ✅ |  ❌  |
| document_types | id | DefaultPaginator | ✅ |  ❌  |
| entitlements | id | DefaultPaginator | ✅ |  ❌  |
| events | id | DefaultPaginator | ✅ |  ❌  |
| exchange_rates | id | DefaultPaginator | ✅ |  ❌  |
| expenses | id | DefaultPaginator | ✅ |  ❌  |
| filters | id | DefaultPaginator | ✅ |  ❌  |
| holiday_calendars | id | DefaultPaginator | ✅ |  ❌  |
| holidays | id | DefaultPaginator | ✅ |  ❌  |
| invoice_attributions | id | DefaultPaginator | ✅ |  ❌  |
| invoices | id | DefaultPaginator | ✅ |  ❌  |
| line_items | id | DefaultPaginator | ✅ |  ❌  |
| lost_reasons | id | DefaultPaginator | ✅ |  ❌  |
| memberships | id | DefaultPaginator | ✅ |  ❌  |
| organizations | id | DefaultPaginator | ✅ |  ❌  |
| organization_memberships | id | DefaultPaginator | ✅ |  ❌  |
| pages | id | DefaultPaginator | ✅ |  ❌  |
| page_versions | id | DefaultPaginator | ✅ |  ❌  |
| payment_reminder_sequences | id | DefaultPaginator | ✅ |  ❌  |
| payment_reminders | id | DefaultPaginator | ✅ |  ❌  |
| payments | id | DefaultPaginator | ✅ |  ❌  |
| pipelines | id | DefaultPaginator | ✅ |  ❌  |
| prices | id | DefaultPaginator | ✅ |  ❌  |
| project_assignments | id | DefaultPaginator | ✅ |  ❌  |
| projects | id | DefaultPaginator | ✅ |  ❌  |
| rate_cards | id | DefaultPaginator | ✅ |  ❌  |
| reports_booking-reports | id | DefaultPaginator | ✅ |  ❌  |
| salaries | id | DefaultPaginator | ✅ |  ❌  |
| sections | id | DefaultPaginator | ✅ |  ❌  |
| services | id | DefaultPaginator | ✅ |  ❌  |
| service_types | id | DefaultPaginator | ✅ |  ❌  |
| sessions | id | DefaultPaginator | ✅ |  ❌  |
| subsidiaries | id | DefaultPaginator | ✅ |  ❌  |
| tags | id | DefaultPaginator | ✅ |  ❌  |
| task_lists | id | DefaultPaginator | ✅ |  ❌  |
| tax_rates | id | DefaultPaginator | ✅ |  ❌  |
| tasks | id | DefaultPaginator | ✅ |  ❌  |
| time_entries | id | DefaultPaginator | ✅ |  ❌  |
| time_entry_versions | id | DefaultPaginator | ✅ |  ❌  |
| timers | id | DefaultPaginator | ✅ |  ❌  |
| reports_timesheet_reports | id | DefaultPaginator | ✅ |  ❌  |
| users | id | DefaultPaginator | ✅ |  ❌  |
| widgets | id | DefaultPaginator | ✅ |  ❌  |
| workflow_statuses | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
| ------------------ | ------------ | -- | ---------------- |
| 0.0.14 | 2025-02-23 | [54626](https://github.com/airbytehq/airbyte/pull/54626) | Update dependencies |
| 0.0.13 | 2025-02-15 | [54021](https://github.com/airbytehq/airbyte/pull/54021) | Update dependencies |
| 0.0.12 | 2025-02-08 | [53506](https://github.com/airbytehq/airbyte/pull/53506) | Update dependencies |
| 0.0.11 | 2025-02-01 | [53031](https://github.com/airbytehq/airbyte/pull/53031) | Update dependencies |
| 0.0.10 | 2025-01-25 | [52466](https://github.com/airbytehq/airbyte/pull/52466) | Update dependencies |
| 0.0.9 | 2025-01-18 | [51927](https://github.com/airbytehq/airbyte/pull/51927) | Update dependencies |
| 0.0.8 | 2025-01-11 | [51332](https://github.com/airbytehq/airbyte/pull/51332) | Update dependencies |
| 0.0.7 | 2024-12-28 | [50698](https://github.com/airbytehq/airbyte/pull/50698) | Update dependencies |
| 0.0.6 | 2024-12-21 | [50279](https://github.com/airbytehq/airbyte/pull/50279) | Update dependencies |
| 0.0.5 | 2024-12-14 | [49721](https://github.com/airbytehq/airbyte/pull/49721) | Update dependencies |
| 0.0.4 | 2024-12-12 | [49070](https://github.com/airbytehq/airbyte/pull/49070) | Update dependencies |
| 0.0.3 | 2024-11-04 | [48289](https://github.com/airbytehq/airbyte/pull/48289) | Update dependencies |
| 0.0.2 | 2024-10-28 | [47656](https://github.com/airbytehq/airbyte/pull/47656) | Update dependencies |
| 0.0.1 | 2024-09-11 | [45401](https://github.com/airbytehq/airbyte/pull/45401) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>
