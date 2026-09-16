import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

# ClickHouse Migration Guide

## Upgrading to 0.4.0

Version 0.4.0 formally declares the temporal column typing introduced in version 0.3.1 as a breaking change. Before version 0.3.1, `Date`, `Date32`, `DateTime`, and `DateTime64` columns were emitted as unformatted strings. These columns now emit Airbyte date or timestamp types.

### Who is affected

This change affects connections that sync at least one stream containing a `Date`, `Date32`, `DateTime`, or `DateTime64` column. Typed destinations may reject the schema change because an existing string column can't always evolve to a date or timestamp column.

Connections whose selected streams don't contain these column types require no migration action.

Use your connection's current status to choose a migration path:

- If the connection syncs successfully on version 0.3.1, upgrade to version 0.4.0. Don't refresh the schema or clear data. The destination already uses the new temporal types.
- If the connection fails with a `Schema evolution ... between string and timestamp is not allowed` error, follow the steps below.
- If the connection is still on version 0.3.0 or earlier, follow the steps below when you're ready to upgrade.

### Resolve a schema evolution failure

For connections that fail with the string-to-timestamp schema evolution error:

1. Upgrade the ClickHouse source to version 0.4.0.
2. Open the connection and select the **Schema** tab.
3. Select **Refresh source schema**, then select **OK**. If no new changes appear because the connection already uses version 0.3.1, continue to the next step.
4. Select **Save changes** and ensure **Clear affected streams** is selected for the failing streams.
5. After the clear completes, run a new sync.

Clearing an affected stream removes its existing destination data and reads the stream again from the beginning.

If you can't clear the data:

- A connection that has never successfully synced on version 0.3.1 or later can remain temporarily on version 0.3.0. Contact Airbyte Support before upgrading.
- Don't downgrade a connection that has successfully synced on version 0.3.1 or later. Its destination already contains temporal columns, so downgrading can cause a timestamp-to-string schema evolution failure.

## Connector upgrade guide

<MigrationGuide />
