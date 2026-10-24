import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

# Redshift Migration Guide

## Upgrading to 1.0.0

Version 1.0.0 changes how the Redshift source types temporal columns. Before version 1.0.0, all Redshift temporal columns were emitted as unformatted strings, so typed destinations created text columns for them. Version 1.0.0 emits these columns as Airbyte temporal types:

| Redshift type | Before 1.0.0 | 1.0.0 and later              |
| :------------ | :----------- | :--------------------------- |
| `date`        | `string`     | `date`                       |
| `timestamp`   | `string`     | `timestamp_without_timezone` |
| `timestamptz` | `string`     | `timestamp_with_timezone`    |

The emitted values don't change. `time` and `timetz` columns are still emitted as strings.

### Who is affected

This change affects connections that sync at least one stream containing a `date`, `timestamp`, or `timestamptz` column. Connections whose selected streams don't contain these column types require no migration action.

After you refresh the source schema, destinations create or change the affected columns as native date or timestamp columns. Typed destinations may reject this change because an existing string column can't always evolve to a date or timestamp column. Downstream queries, dbt models, or dashboards that treat these columns as text may also need updates.

### Migration steps

1. Upgrade the Redshift source to version 1.0.0.
2. Open the connection and select the **Schema** tab.
3. Select **Refresh source schema**, then select **OK**.
4. Select **Save changes**. If your destination can't change existing string columns to date or timestamp columns, ensure **Clear affected streams** is selected for streams that contain `date`, `timestamp`, or `timestamptz` columns.
5. Run a new sync.

Clearing a stream removes its existing destination data and reads the stream again from the beginning. Back up the affected destination tables first if you need to keep them.

Don't downgrade a connection that has successfully synced on version 1.0.0 or later. Its destination already contains temporal columns, so downgrading can cause a timestamp-to-string schema evolution failure.

## Connector upgrade guide

<MigrationGuide />
