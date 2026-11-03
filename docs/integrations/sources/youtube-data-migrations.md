import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

# Youtube Data Migration Guide

## Upgrading to 1.0.0

:::note
This change affects all streams. The primary-key and result-set changes are limited to `comments`, `videos`, and `channel_comments`; the timestamp typing affects every stream.
:::

Version 1.0.0 makes three changes that alter what lands in your destination:

- **Primary keys declared.** `videos` is now keyed by `videoId`, and `comments` / `channel_comments` by composite keys (`[videoId, id]` / `[channelId, id]`), where `id` is a new top-level field carrying the comment-thread id. Declaring primary keys does not change existing syncs by itself; it lets you select a deduplicating sync mode for these streams if your destination supports one.
- **Timestamp fields typed.** Nine fields (`publishedAt`, `updatedAt`, `publishAt`, `timeLinked`, `datetime`, and their nested occurrences) now declare `format: date-time`, so destinations that map JSON-schema formats will change these columns from plain strings to timestamp types. The connector-synthesized `video.datetime` field also changed from Python's space-separated form to ISO-8601.
- **`videos` returns only videos.** The stream's search request now pins `type=video`; channel and playlist id records that previously appeared (with a null `videoId`) are no longer returned.

:::danger
If any stream uses **Full Refresh | Append**, clearing it permanently deletes history the source cannot re-supply: the per-sync `video.statistics` snapshots, videos beyond YouTube's 500-result search limit for a channel, and comments since deleted on YouTube. Snapshot or rename those tables before clearing, or skip the reset and accept mixed `datetime` formats in existing rows.
:::

### Migration Steps

### Refresh affected schemas and reset data where needed

1. Select **Connections** in the main nav bar.
   1. Select the connection affected by the update.
1. Select the **Schema** tab.
   1. Select **Refresh source schema**.
   1. Select **OK**.

:::note
Any detected schema changes will be listed for your review.
:::

1. Select **Save changes** at the top right of the page.
   1. If your streams use **Full Refresh | Overwrite**, or your destination fails to alter the timestamp columns in place, check **Reset affected streams**. Otherwise leave it unchecked.

:::note
Depending on destination type you may not be prompted to reset your data.
:::

1. Select **Save connection**.

:::note
If you checked **Reset affected streams**, this clears the data in your destination and initiates a fresh sync. Otherwise the next sync continues with the updated schema.
:::

Data-lake destinations (for example Iceberg-based ones) do not recreate the physical table on a stream reset. If a sync fails after upgrading with a schema-evolution error on a timestamp column, drop or recreate the affected destination tables, then run a fresh sync. For **Full Refresh | Append** streams this permanently deletes the accumulated history, so snapshot those tables first.

For more information on resetting your data in Airbyte, see [this page](/platform/operator-guides/clear)

## Connector upgrade guide

<MigrationGuide />
