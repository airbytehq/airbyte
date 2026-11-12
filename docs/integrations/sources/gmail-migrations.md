import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

# Gmail Migration Guide

## Upgrading to 1.0.0

:::danger Risk of permanent data loss
Only run **Refresh stream and remove records** if step 3 below tells you to. It deletes the existing destination rows before re-syncing, and Gmail can only return messages that still exist in the mailbox and are allowed by the connection's start date and spam/trash settings. Messages that were deleted, trashed or marked as spam since the original sync don't come back. Back up the affected tables before removing records if you need that data.
:::

Version 1.0.0 declares the count and size fields of four streams as integers, and gives the `profile` stream a primary key. The values themselves don't change: Gmail documents these fields as int32 integers, and the connector already emitted whole numbers. Only the declared type changes, so typed destinations change the matching columns from a decimal or float type to an integer type.

### What changes

The `profile` stream now uses `emailAddress` as its primary key. The following fields change from `number` to `integer`; they stay nullable:

- `profile`: `messagesTotal`, `threadsTotal`
- `labels_details`: `messagesTotal`, `messagesUnread`, `threadsTotal`, `threadsUnread`
- `messages_details`: `sizeEstimate`, `payload.body.size`, `payload.parts[].body.size`, `payload.parts[].parts[].body.size`, and `payload.parts[].parts[].parts[].body.size`
- `threads_details`: `messages[].sizeEstimate`, `messages[].payload.body.size`, `messages[].payload.parts[].body.size`, `messages[].payload.parts[].parts[].body.size`, and `messages[].payload.parts[].parts[].parts[].body.size`

### Why

The Gmail API documents these fields as int32 integers in its [`users.getProfile`](https://developers.google.com/workspace/gmail/api/reference/rest/v1/users/getProfile), [`users.labels`](https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.labels) and [`users.messages`](https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.messages) references. The profile endpoint returns one record for the authenticated mailbox, and `emailAddress` identifies that record, so you can now select a deduplicated sync mode for `profile`.

### Who is affected

Connections that sync at least one of `profile`, `labels_details`, `messages_details` or `threads_details`. Connections that sync only `drafts`, `labels`, `messages` or `threads` aren't affected and need no action.

Among affected connections:

- **Destinations that type their columns** (BigQuery, Snowflake, Postgres, Redshift, MSSQL, ClickHouse and similar) change `messagesTotal`, `messagesUnread`, `threadsTotal`, `threadsUnread` and `sizeEstimate` from a decimal or float column to an integer column. The nested `payload` and `messages` objects are stored as JSON, so their `size` fields don't change a column type. Most of these destinations convert the existing column in place on the next sync.
- **S3 Data Lake (Iceberg)** types nested fields too, and can't convert a double column to a long column in place. All four streams in an Append or Append + Deduped mode fail with `Schema evolution for column "..." between double and long is not allowed` until you refresh them; see step 3. **Refresh stream and remove records** recreates the table with the new column types.
- **Object storage and file destinations** that write JSON or CSV aren't affected: the values are written the same way as before.
- **`profile` in Full Refresh | Append** keeps one row per sync, as before. Connections that set their own primary key for `profile` now use `emailAddress`.

### Upgrade steps

1. Upgrade the Gmail source to version 1.0.0.
2. Refresh the source schema for each affected connection and review the detected changes before saving.
3. Run a sync. Most destinations convert the columns automatically and no further action is needed. If the sync fails with a schema-evolution error, for example on S3 Data Lake in an Append or Append + Deduped mode, refresh only that stream with **Refresh stream** → **Refresh stream and remove records**. Read the warning at the top of this guide first: a `messages_details` re-sync reads every message from your start date again, one `messages.get` call per message, so large mailboxes take a long time and messages deleted from the mailbox don't come back. Streams in **Full Refresh | Overwrite** are rebuilt by every sync and never need a separate refresh.
4. Update downstream queries, models and exports that depend on the changed columns or on the `profile` key.

### Update downstream queries

On destinations that type their columns, these seven columns become integer columns (for example `INT64` in BigQuery, `NUMBER(38,0)` in Snowflake, `BIGINT` in Postgres): `profile.messagesTotal`, `profile.threadsTotal`, `labels_details.messagesTotal`, `labels_details.messagesUnread`, `labels_details.threadsTotal`, `labels_details.threadsUnread` and `messages_details.sizeEstimate`. Check:

- Divisions between two of these columns. In Postgres, `messagesUnread / messagesTotal` on integer columns truncates to `0`; cast one side to a decimal type first.
- Casts and type checks that expected a decimal or float column, such as `CAST(messagesTotal AS INTEGER)`, which are no longer needed.
- Models or dashboards that deduplicate `profile` on a key of their own; the stream's key is now `emailAddress`.

For more information about refresh options, see [Refresh data](/platform/operator-guides/refreshes).

## Connector upgrade guide

<MigrationGuide />
