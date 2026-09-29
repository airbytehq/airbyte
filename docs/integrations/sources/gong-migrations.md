import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

# Gong Migration Guide

## Upgrading to 2.0.0

:::note
This change only affects you if you sync the `extensiveCalls` stream. No other streams are impacted.
:::

Version 2.0.0 corrects two declared field types in the `extensiveCalls` stream schema so they match the data the [Gong API](https://us-66463.app.gong.io/settings/api/documentation#post-/v2/calls/extensive) actually returns:

- `parties[].context` is now declared as an `array` (or `null`). It was previously declared as an `object`. Gong has always returned this field as an array, and the mismatch caused schema-validation warnings on every record.
- `media` is now explicitly declared as an `object` (or `null`). It previously had no declared type.

This release also declares fields that Gong returns but the schema previously omitted: `users.conferencingProviders`, `scorecards.reviewMethod`, and `answeredScorecards.reviewMethod`. These are additive and non-breaking.

### What this means for your destination

The connector already emitted these values in the corrected shape, so the records written to your destination don't change. What happens next depends on how your destination stores nested fields:

- **Databases and data warehouses** (Snowflake, BigQuery, Redshift, Postgres, MySQL, and similar) and **object storage in JSONL or CSV format** store `parties` and `media` as a single JSON column. Nested field types don't appear in the destination schema, so no column types, primary keys, or cursors change. Refresh the source schema only. Do not clear the stream.
- **Object storage in Avro or Parquet format** (S3, GCS, Azure Blob Storage) and **Iceberg** derive a typed nested schema from the stream schema. For these destinations `parties[].context` changes from a record to an array, so files written after the upgrade have a different embedded schema than existing files, and Iceberg cannot evolve the `parties` column in place. Refresh the source schema and clear the `extensiveCalls` stream so it is rewritten with a consistent schema.

### Migration steps

1. Select **Connections** in the main nav bar, then select the connection affected by the update.
1. Select the **Schema** tab.
1. Select **Refresh source schema**, then select **OK**.
1. Select **Save changes** at the top right of the page.
   - For database, data warehouse, JSONL, and CSV destinations, make sure the **Reset affected streams** option is **not** checked.
   - For Avro, Parquet, and Iceberg destinations, make sure the **Reset affected streams** option is checked.
1. Select **Save connection**.

:::danger Clearing the stream is destructive
Clearing the `extensiveCalls` stream deletes its data in your destination and re-syncs it from your configured **Start date** (the last two years if you left it unset). Calls that Gong no longer serves can't be recovered. Only clear the stream if your destination requires it, as described above.
:::

For more information on clearing your data in Airbyte, see [this page](/platform/operator-guides/clear).

## Upgrading to 1.0.0

:::note
This change is only breaking if you are syncing the `extensiveCalls` stream.
:::

This update fixes schema bugs in the `extensiveCalls` stream to match the actual data returned by the [Gong API](https://us-66463.app.gong.io/settings/api/documentation#post-/v2/calls/extensive):

- The `context` field type changed from `object` to `array`. The Gong API returns `context` as an array of CRM context objects, but the previous schema incorrectly defined it as a single object.
- The `value` field within `context.objects.fields` now accepts `string`, `number`, `boolean`, `object`, and `array` types instead of only `object`. The Gong API returns field values in various types depending on the CRM field.

These schema corrections change the data types in the destination table for the `extensiveCalls` stream. Users syncing this stream must refresh the source schema and reset the stream after upgrading.

### Migration Steps

### Refresh affected schemas and reset data

1. Select **Connections** in the main nav bar.
   1. Select the connection affected by the update.
1. Select the **Schema** tab.
   1. Select **Refresh source schema**.
   1. Select **OK**.

:::note
Any detected schema changes will be listed for your review.
:::

1. Select **Save changes** at the top right of the page.
   1. Ensure the **Reset affected streams** option is checked.

:::note
Depending on destination type you may not be prompted to reset your data.
:::

1. Select **Save connection**.

:::note
This will reset the data in your destination and initiate a fresh sync.
:::

For more information on resetting your data in Airbyte, see [this page](/platform/operator-guides/clear)

## Connector upgrade guide

<MigrationGuide />
