# Pylon Migration Guide

import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

## Upgrading to 1.0.0

:::danger Risk of permanent data loss
Clearing a stream deletes its data in your destination. Back up the affected tables before clearing. Before clearing `issues`, set **Start Date** (`start_date`) early enough to cover the history you need. By default, the connector only re-reads the last 30 days.
:::

### What changed

Version 1.0.0 corrects the declared field types to match the Pylon API. Typed destinations previously nulled the string tags because the schema declared objects. Eight timestamp fields now have a date-time format.

| Stream | Field | Old type | New type |
| --- | --- | --- | --- |
| `accounts` | `tags` | array of objects | array of strings |
| `issues` | `tags` | array of objects | array of strings |
| `accounts` | `created_at` | nullable string | nullable string, `format: date-time` |
| `issues` | `first_response_time` | nullable string | nullable string, `format: date-time` |
| `issues` | `resolution_time` | nullable string | nullable string, `format: date-time` |
| `issues` | `latest_message_time` | nullable string | nullable string, `format: date-time` |
| `issues` | `snoozed_until_time` | nullable string | nullable string, `format: date-time` |
| `issue_messages` | `timestamp` | nullable string | nullable string, `format: date-time` |
| `custom_fields` | `created_at` | nullable string | nullable string, `format: date-time` |
| `custom_fields` | `updated_at` | nullable string | nullable string, `format: date-time` |

### Who is affected

Connections syncing `accounts`, `issues`, `issue_messages` or `custom_fields` are affected. Connections syncing none of these streams need no action.

### Upgrade steps

1. Back up the affected destination tables.
2. Upgrade the connector to 1.0.0.
3. Refresh the source schema and accept the changes.
4. Destinations that can't change a column's type in place, such as S3 Data Lake and other Iceberg destinations, must clear the affected streams. Before clearing `issues`, set **Start Date** (`start_date`) early enough to cover the history you need. The default only re-reads the last 30 days.
5. Sync the connection.

`accounts`, `issue_messages` and `custom_fields` use full refresh and are rebuilt on the next sync. `issues` is incremental. Rows synced before the upgrade keep nulled tags until the stream is cleared and synced again. To replace those tags, back up the table, set **Start Date** before the history you need, then clear `issues` and sync again.

## Connector upgrade guide

<MigrationGuide />
