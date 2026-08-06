# Zoho Books Migration Guide

import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

## Upgrading to 0.1.0

Version 0.1.0 changes the incremental cursor for the following streams from the document `date` to `last_modified_time`:

- `invoices`
- `creditnotes`
- `purchase_orders`
- `sales_orders`

This ensures that edits to existing documents, such as status changes, payments, and
voiding, are synchronized even when the document date is older than the previous cursor.

### Migration steps

1. Select **Connections** in the main navbar, then select the affected connection(s).
2. Select the **Schema** tab and click **Refresh source schema**, then **OK**.
3. Select **Save changes** at the bottom of the page.
4. For each affected stream, open the stream menu and select **Clear data** or reset the stream.
5. Return to the **Schema** tab and select **Sync now**.

The first sync after clearing these streams re-reads their full history from `start_date`, so a
large one-time sync is expected and is not a runaway sync.

### Streams not changed

The other document streams continue to use the document date because Zoho Books does not
support filtering them by modification time or reliably return a modification timestamp for them.

## Connector upgrade guide

<MigrationGuide />
