import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

# Gong Migration Guide

## Upgrading to 1.0.0

:::note
This change is only breaking if you are syncing the `extensiveCalls` stream.
:::

This update fixes schema bugs in the `extensiveCalls` stream to match the actual data returned by the [Gong API](https://us-66463.app.gong.io/settings/api/documentation#post-/v2/calls/extensive):

- The `context` field type changed from `object` to `array`. The Gong API returns `context` as an array of CRM context objects, but the previous schema incorrectly defined it as a single object.
- The `value` field within `context.objects.fields` now accepts `string`, `number`, `boolean`, `object`, and `array` types instead of only `object`. The Gong API returns field values in various types depending on the CRM field.

These schema corrections change the data types in the destination table for the `extensiveCalls` stream. Users syncing this stream must refresh the source schema and reset the stream after upgrading.

Users should:

- Refresh the source schema for the `extensiveCalls` stream.
- Reset the stream after upgrading to ensure data is resynced with the corrected schema.

## Connector upgrade guide

<MigrationGuide />
