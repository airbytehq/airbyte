import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

# MySQL Migration Guide

## Upgrading to 4.0.0

This version changes the type mapping for `TINYINT(1)` and `BOOLEAN` columns in CDC (Change Data Capture) mode from `boolean` to `integer`.

### Who is affected

Users who meet **all** of the following conditions:

- Use **CDC replication mode** (binlog-based)
- Have streams containing `TINYINT(1)` or `BOOLEAN` columns
- Rely on those columns being synced as boolean values (`true`/`false`)

Users on **cursor-based (non-CDC) replication** are not affected. This mode already correctly maps `TINYINT` to integer.

### What changed

Previously, the CDC pipeline converted all `TINYINT(1)` values to boolean: any non-zero value became `true`, and zero became `false`. This caused **silent data loss** for columns that stored integer values beyond 0 and 1 (for example, status codes or flags using values like 2, 3, or 127).

After this change, `TINYINT(1)` columns are synced as integers, preserving their full value range (-128 to 127 signed, 0 to 255 unsigned). This aligns CDC mode with cursor-based replication, which already treated `TINYINT` as integer.

Because MySQL `BOOLEAN` is an alias for `TINYINT(1)`, columns declared as `BOOLEAN` are also affected. They will now sync as integers (0 or 1) instead of booleans (`false` or `true`).

### Migration steps

After upgrading to version 4.0.0:

1. Go to the **Schema** tab of each affected connection.
2. Click **Refresh source schema** to detect the updated column types.
3. Click **OK** to accept the schema changes.
4. **Clear data** for the affected streams so they re-sync with the corrected types.

## Connector upgrade guide

<MigrationGuide />

## Upgrading to 3.0.0

CDC syncs now has default cursor field called `_ab_cdc_cursor`. You will need to force normalization to rebuild your destination tables by manually dropping the SCD tables, refreshing the connection schema (skipping the reset), and running a sync. Alternatively, you can just run a reset.
