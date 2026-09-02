import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

# Gong Migration Guide

## Upgrading to 1.0.0

:::note
This change only affects users syncing the `extensiveCalls` stream.
:::

This update fixes schema bugs in the `extensiveCalls` stream to match the actual data returned by the [Gong API](https://gong.app.gong.io/settings/api/documentation#post-/v2/calls/extensive):

- **`context` field type changed from `object` to `array`.** The Gong API returns `context` as an array of CRM context objects, but the previous schema incorrectly defined it as a single object.
- **`value` field type widened.** The `value` field within `context.objects.fields` now accepts `string`, `number`, `boolean`, `object`, and `array` types instead of only `object`. The Gong API returns field values in various types depending on the CRM field.

These schema corrections change the data types in the destination table for the `extensiveCalls` stream. After upgrading, you must refresh the source schema and reset the `extensiveCalls` stream.

## Connector upgrade guide

<MigrationGuide />
