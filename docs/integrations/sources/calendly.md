# Calendly
Calendly source syncs your organization members, groups, available event types, and scheduled events from Calendly!

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. Go to Integrations → API &amp; Webhooks to obtain your bearer token. https://calendly.com/integrations/api_webhooks |  |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| event_types | uri | DefaultPaginator | ✅ |  ✅  |
| api_user | uri | No pagination | ✅ |  ❌  |
| groups | uri | DefaultPaginator | ✅ |  ❌  |
| organization_memberships | uri | DefaultPaginator | ✅ |  ❌  |
| scheduled_events | uri | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date       | Subject        |
|------------------|------------|----------------|
| 0.0.1 | 2024-09-01 | Initial release by [@natikgadzhi](https://github.com/natikgadzhi) via Connector Builder|

</details>