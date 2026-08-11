import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

# Sample Data Migration Guide

## Upgrading to 8.0.0

The `always_updated` configuration field has been removed from the connection spec. Connections that previously set `always_updated: false` will now always refresh `updated_at` values on every sync. If you relied on that field to stop emitting records after `count` records, update your connection configuration accordingly after upgrading.

## Upgrading to 7.0.0

This is a test breaking change to validate breaking change infrastructure. No actual schema or functionality changes were made. No user action is required.

## Upgrading to 6.0.0

All streams (`users`, `products`, and `purchases`) now properly declare `id` as their respective primary keys. Existing sync jobs should still work as expected but you may need to reset your sync and/or update write mode after upgrading to the latest connector version.

## Upgrading to 5.0.0

Some columns are narrowing from `number` to `integer`. You may need to force normalization to rebuild your destination tables by manually dropping the SCD and final tables, refreshing the connection schema (skipping the reset), and running a sync. Alternatively, you can just run a reset.

## Upgrading to 4.0.0

Nothing to do here - this was a test breaking change.

## Connector upgrade guide

<MigrationGuide />
