# Marketo Migration Guide

## Upgrading to 2.0.0

:::note
This change only affects users syncing the `leads` stream. Other streams
(`activities_*`, `campaigns`, `lists`, `programs`, `emails`, `program_tokens`,
`segmentations`, `activity_types`) are not impacted.
:::

### What changed

The `leads` stream now filters Marketo's [Bulk Lead Extract](https://developers.marketo.com/rest-api/bulk-extract/bulk-lead-extract/)
API on `updatedAt` instead of `createdAt`. The cursor field is still `updatedAt`
(unchanged).

### Why

Marketo's Bulk Lead Extract API honors only one date-range filter per export
job. In earlier versions, the `leads` stream used `updatedAt` as its cursor but
filtered exports on `createdAt`, so any lead whose `createdAt` fell before the
cursor position was silently excluded from incremental syncs — even when its
`updatedAt` advanced into the sync window. Updates to pre-existing leads were
therefore never written to the destination.

With this change, the filter matches the cursor, so updates to pre-existing
leads are included in every incremental sync.

### Who is affected

Users syncing the `leads` stream in incremental mode. Full-refresh syncs of
`leads` are not affected. Other streams are not affected.

### Migration steps

After upgrading to 2.0.0:

1. **Refresh the source schema** for the `leads` stream so any dynamic-schema
   field changes (such as custom Marketo fields) are picked up.
2. **Clear data for the `leads` stream** and re-sync. This backfills historical
   updates to pre-existing leads that were silently dropped by earlier
   versions. Without a clear-and-resync, those missed updates will not appear
   in the destination — the fix only prevents future silent drops.

#### Refresh schema and clear data

1. In the Airbyte UI, select **Connections** in the main nav.
2. Select the connection syncing Marketo leads.
3. On the **Schema** tab, select **Refresh source schema** and save.
4. Clear data for the `leads` stream so it is re-synced from scratch. Depending
   on your destination, this may be prompted automatically as part of the
   schema refresh; otherwise, use the **Clear data** action on the stream.
5. Start a sync.

:::note
Customers syncing a very large `leads` volume may want to coordinate the
clear-and-resync with their Marketo daily extract quota. The new behavior
consumes roughly the same quota as before for a given time window.
:::

## Connector upgrade guide

import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

<MigrationGuide />
