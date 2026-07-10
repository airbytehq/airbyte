import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

# ClickHouse Migration Guide

## Upgrading to 0.4.0

Version 0.4.0 formally declares the temporal column typing introduced in version 0.3.1 as a breaking change. Before version 0.3.1, `Date`, `Date32`, `DateTime`, and `DateTime64` columns were emitted as unformatted strings. These columns now emit Airbyte date or timestamp types.

### Who is affected

This change affects connections that sync at least one stream containing a `Date`, `Date32`, `DateTime`, or `DateTime64` column. Typed destinations may reject the schema change because an existing string column can't always evolve to a date or timestamp column.

Connections whose selected streams don't contain these column types require no action.

### Steps to upgrade

For every affected connection, including connections already using version 0.3.1:

1. Upgrade the ClickHouse source to version 0.4.0.
2. Open the connection and select the **Schema** tab.
3. Select **Refresh source schema**, review the detected type changes, and select **OK**.
4. Select **Save changes** and ensure **Clear affected streams** is selected.
5. After the clear completes, run a new sync.

Clearing an affected stream removes its existing destination data and reads the stream again from the beginning. If you can't clear the data, keep or pin the connector to version 0.3.0 and contact Airbyte Support before upgrading.

## Connector upgrade guide

<MigrationGuide />
