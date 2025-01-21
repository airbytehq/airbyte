# Calendly

Calendly source syncs your organization members, groups, available event types, and scheduled events from Calendly!

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. Go to Integrations → API &amp; Webhooks to obtain your bearer token. https://calendly.com/integrations/api_webhooks |  |
| `start_date` | `string` | Start date to sync scheduled events from.  |  |

## Streams

:::note

Incremental sync in `scheduled_events` uses `start_time` as a cursor. This may lead to situations where data gets stale if the event changes after it got synced. If you are running into this, periodic full refresh would resync all data.

:::

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

| Version | Date | Pull Request | Subject |
|---------|------|--------------|---------|
| 0.0.1 | 2024-09-01 | | Initial release by [@natikgadzhi](https://github.com/natikgadzhi) via Connector Builder |

</details>
