import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

# Hibob Migration Guide

## Upgrading to 1.0.0

This version replaces the previous HiBob source connector implementation with a manifest-only connector built against the current HiBob public API documentation.

The new connector fixes the previously unusable implementation by switching to the documented HiBob API hosts, updating authentication to HiBob service user credentials, and rebuilding the stream set around commonly used HR data resources.

This change affects all users of the existing HiBob connector. The `payroll` stream is removed, and the `employees` and `profiles` stream schemas are rebuilt. Version 1.0.0 also adds new streams for employee field metadata, company named lists, work history, lifecycle history, employment history, time off request changes, and job roles.

Before running the upgraded connector:

1. Confirm your HiBob service user has permissions for each stream you plan to sync.
2. Refresh the source schema in Airbyte.
3. Review the selected streams and destination sync modes.
4. Reset any affected streams before resuming syncs.

## Connector upgrade guide

<MigrationGuide />
