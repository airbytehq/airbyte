import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

# Gong Migration Guide

## Upgrading to 2.0.0

:::note
This change only affects you if you sync the `extensiveCalls` stream. No other streams are impacted.
:::

Version 2.0.0 corrects two declared field types in the `extensiveCalls` stream schema so they match the data the [Gong API](https://us-66463.app.gong.io/settings/api/documentation#post-/v2/calls/extensive) actually returns:

- `parties[].context` is now declared as an `array` (or `null`). It was previously declared as an `object`. Gong returns this field as an array, and the mismatch caused schema-validation warnings.
- `media` is now explicitly declared as an `object` (or `null`). It previously had no declared type.

This release also declares fields that Gong returns but the schema previously omitted: `users.conferencingProviders`, `scorecards.reviewMethod`, and `answeredScorecards.reviewMethod`. These are additive and non-breaking.

### What this means for your destination

The connector already emitted these values in the corrected shape, so the records written to your destination don't change. Nested field types don't appear in any destination's schema: in databases and warehouses `parties` and `media` are JSON columns, and in object storage (JSONL, CSV, Avro, Parquet) and Iceberg `parties[].context` is written as a JSON string both before and after this change. No column types, file schemas, primary keys, or cursors change, so downstream SQL, dbt models, and dashboards need no updates. Refresh the source schema only. Do not clear the stream.

### Migration steps

1. Select **Connections** in the main nav bar, then select the connection affected by the update.
1. Select the **Schema** tab.
1. Select **Refresh source schema**, then select **OK**.
1. Select **Save changes** at the top right of the page. Make sure the **Reset affected streams** option is **not** checked.
1. Select **Save connection**.

:::danger Clearing the stream is destructive and unnecessary
Clearing the `extensiveCalls` stream deletes its data in your destination and re-syncs it from your configured **Start date** (connections without one sync from `1970-01-01`). Calls outside your start date, or that Gong no longer returns, can't be recovered. This upgrade doesn't require a clear for any destination.
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
