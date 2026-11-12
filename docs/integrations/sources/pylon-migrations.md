# Pylon Migration Guide

import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

## Upgrading to 1.0.0

:::danger Risk of permanent data loss
Clearing a stream deletes its data in your destination. Back up the affected tables before clearing. Before clearing `issues` or `issue_messages`, set **Start Date** (`start_date`) early enough to cover the history you need. By default, the connector only re-reads the last 30 days for these streams.
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

1. If your destination is ClickHouse, you can check your server before upgrading by running `SELECT CAST('2026-01-10T12:00:00Z' AS Nullable(DateTime64(3)))`. If it returns NULL, your server is affected, and you'll need the ClickHouse step below.
2. Upgrade the connector to 1.0.0.
3. Refresh the source schema and accept the changes.
4. Destinations that can't change a column's type in place, such as S3 Data Lake and other Iceberg destinations, must clear the affected streams. Back up the affected tables first, before clearing. Before clearing `issues` or `issue_messages`, set **Start Date** (`start_date`) early enough to cover the history you need. The default only re-reads the last 30 days.
5. If your destination is ClickHouse, existing values in the changed timestamp columns may be set to null during the upgrade, depending on your ClickHouse version. With **Full Refresh | Overwrite**, `accounts` and `custom_fields` are fully rewritten on the next sync. For `issues` and `issue_messages`, after upgrading: back up the tables, set **Start Date** (`start_date`) early enough to cover the history you need, then clear `issues` and `issue_messages` and sync again.
6. Sync the connection.

With **Full Refresh | Overwrite**, `accounts` and `custom_fields` are fully rewritten on the next sync. With **Full Refresh | Append**, rows synced before the upgrade stay next to the new ones until you clear the stream. `issue_messages` uses full refresh but only re-reads messages for issues updated since **Start Date**, so it is limited like `issues`. `issues` is incremental. Rows synced before the upgrade keep nulled tags until the stream is cleared and synced again. To replace those tags, back up the table, set **Start Date** before the history you need, then clear `issues` and sync again.

### Update downstream queries

- The 8 timestamp columns in the preceding table are now timestamp columns instead of text. Update SQL, `dbt` models and dashboards that treat them as text, for example string comparisons, `LIKE`, substrings or casts from strings.
- `tags` on `accounts` and `issues` is now an array of strings. Update anything that expects objects, such as `tags[0]:name`, or that worked around the old null values.

## Upgrading to 0.0.8

Connector version 0.0.8 switches the Issues stream from `GET /issues` (cursored on `created_at`) to `POST /issues/search` (cursored on `updated_at`) so that incremental syncs capture updates to existing issues, not just newly created ones. Connections upgrading from any earlier version automatically run a one-time state migration that rewinds the issues cursor and re-pulls history starting from:

- the **Start Date** you configured, if it is set, or
- **30 days before the first sync**, if Start Date is unset.

If you need a longer backfill, set Start Date to the desired date before the first sync on 0.0.8. Subsequent syncs use the new `updated_at` cursor incrementally and do not re-pull history.

## Connector upgrade guide

<MigrationGuide />
