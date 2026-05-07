# Marketo Migration Guide

import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

## Upgrading to 2.0.0

:::note
This change is only breaking if you are syncing the `leads` stream in
**Incremental** mode. Full refresh syncs of `leads` are not affected, since
they re-fetch the entire stream on every sync and never relied on the
cursor/filter relationship.
:::

This update changes the `leads` stream to filter Marketo's [Bulk Lead Extract](https://developers.marketo.com/rest-api/bulk-extract/bulk-lead-extract/)
API on `updatedAt` instead of `createdAt`. The cursor field is unchanged
(`updatedAt`).

Marketo's Bulk Lead Extract honors only one date-range filter per export job.
Earlier versions filtered on `createdAt` while using `updatedAt` as the cursor,
so any lead whose `createdAt` predated the cursor was silently excluded from
incremental syncs even when its `updatedAt` advanced into the sync window —
updates to pre-existing leads were therefore never written to the destination.
With this change, the filter matches the cursor and lead updates are captured
on every incremental sync.

### Full refresh users

If you sync the `leads` stream in **Full Refresh** mode, you can simply upgrade
to `2.0.0` — no migration steps are required. Full refresh syncs re-fetch the
entire stream on every run, so they were never affected by the cursor/filter
mismatch.

### Incremental users: refresh affected schemas and reset data

Users syncing the `leads` stream in **Incremental** mode should refresh the
source schema and clear data for the `leads` stream after upgrading. Without a
clear and resync, historical updates that were silently dropped by earlier
versions will not appear in the destination — the fix only prevents future
silent drops.

1. Select **Connections** in the main nav bar.
   1. Select the connection affected by the update.
2. Select the **Schema** tab.
   1. Select **Refresh source schema**.
   2. Select **OK**.

:::note
Any detected schema changes will be listed for your review.
:::

3. Select **Save changes** at the top right of the page.
   1. Ensure the **Reset affected streams** option is checked.

:::note
Depending on destination type you may not be prompted to reset your data.
:::

4. Select **Save connection**.

:::note
This will reset the data in your destination and initiate a fresh sync.
:::

For more information on resetting your data in Airbyte, see [this page](/platform/operator-guides/clear).

## Connector upgrade guide

<MigrationGuide />
