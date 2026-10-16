# Instatus Migration Guide

## Upgrading to 1.0.0

The Instatus API returns some `name` fields as translation objects keyed by language, for example `{"default": "Response time"}`. The connector's schema declared these fields as strings, so the declared type did not match the data. Version 1.0.0 declares them as objects with a `default` key and one string key per translation.

The `name` column of the `metrics` stream changes type from string to object. This is the only change that requires action, and only for connections that sync the `metrics` stream.

The same fix applies to `components[].name` in the `subscribers` stream. That field sits inside the `components` array, so the `components` column keeps its type and the `subscribers` stream needs no action.

### Refresh the schema and clear the `metrics` stream

If your connection syncs the `metrics` stream, refresh the source schema and clear the `metrics` stream after upgrading. The next sync then writes the `name` column with its new type.

The `metrics` stream supports only full refresh, so the next sync re-reads every metric that the Instatus API currently returns.

:::caution
Clearing a stream deletes its data in the destination. If you sync `metrics` in append mode and want to keep rows from earlier syncs, back up the `metrics` table before you clear it.
:::

### Update downstream queries

Queries, models, and dashboards that read `metrics.name` as text need to read the `default` key of the object instead.

import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

## Connector upgrade guide

<MigrationGuide />
