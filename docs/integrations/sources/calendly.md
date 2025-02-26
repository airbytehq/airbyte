# Calendly

Calendly source syncs your organization members, groups, available event types, and scheduled events from Calendly!

## Configuration

| Input        | Type     | Description                                                                                                                  | Default Value |
| ------------ | -------- | ---------------------------------------------------------------------------------------------------------------------------- | ------------- |
| `api_key`    | `string` | API Key. Go to Integrations → API &amp; Webhooks to obtain your bearer token. https://calendly.com/integrations/api_webhooks |               |
| `start_date` | `string` | Start date to sync scheduled events from.                                                                                    |               |

## Streams

:::note

Incremental sync in `scheduled_events` uses `start_time` as a cursor. This may lead to situations where data gets stale if the event changes after it got synced. If you are running into this, periodic full refresh would resync all data.

:::

| Stream Name              | Primary Key | Pagination       | Supports Full Sync | Supports Incremental |
| ------------------------ | ----------- | ---------------- | ------------------ | -------------------- |
| event_types              | uri         | DefaultPaginator | ✅                 | ✅                   |
| api_user                 | uri         | No pagination    | ✅                 | ❌                   |
| groups                   | uri         | DefaultPaginator | ✅                 | ❌                   |
| organization_memberships | uri         | DefaultPaginator | ✅                 | ❌                   |
| scheduled_events         | uri         | DefaultPaginator | ✅                 | ✅                   |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                                                                                                                |
| ------- | ---------- | -------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 0.1.2 | 2025-02-22 | [54274](https://github.com/airbytehq/airbyte/pull/54274) | Update dependencies |
| 0.1.1 | 2025-02-15 | [51240](https://github.com/airbytehq/airbyte/pull/51240) | Update dependencies |
| 0.1.0 | 2025-02-12 | [52566](https://github.com/airbytehq/airbyte/pull/52566) | Add stream organization members, groups, available event types, and scheduled events. |
| 0.0.8 | 2024-12-28 | [50462](https://github.com/airbytehq/airbyte/pull/50462) | Update dependencies |
| 0.0.7 | 2024-12-21 | [50152](https://github.com/airbytehq/airbyte/pull/50152) | Update dependencies |
| 0.0.6 | 2024-12-14 | [49551](https://github.com/airbytehq/airbyte/pull/49551) | Update dependencies |
| 0.0.5 | 2024-12-12 | [49275](https://github.com/airbytehq/airbyte/pull/49275) | Update dependencies |
| 0.0.4 | 2024-12-11 | [49022](https://github.com/airbytehq/airbyte/pull/49022) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.3 | 2024-11-04 | [48279](https://github.com/airbytehq/airbyte/pull/48279) | Update dependencies |
| 0.0.2 | 2024-10-28 | [47568](https://github.com/airbytehq/airbyte/pull/47568) | Update dependencies |
| 0.0.1   | 2024-09-01 |                                                          | Initial release by [@natikgadzhi](https://github.com/natikgadzhi) via Connector Builder                                                                                |

</details>
