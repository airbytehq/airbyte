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

### Streams not changed

- `expenses`: Zoho Books documents `last_modified_time` only as a response attribute, not as a
  List query parameter, and the response example shows it blank, so it is unsafe as a cursor.
- `customer_payments`: The Zoho Books customer-payments documentation does not mention
  `last_modified_time` as either a query parameter or response attribute.
- `journals` and `transactions`: Their manifest schemas do not define a `last_modified_time` property.

## Connector upgrade guide

<MigrationGuide />
