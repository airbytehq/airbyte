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
| 0.0.1 | 2024-09-11 | [45401](https://github.com/airbytehq/airbyte/pull/45401) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>