# Microsoft Dataverse Migration Guide

import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

## Upgrading to 1.0.0

This release corrects the schema type for Dataverse fields configured with `DateTimeBehavior=DateOnly`. Previously, all DateTime fields were mapped to `format: "date-time"` (timestamp with timezone), which caused DateOnly values like `"2024-03-15"` to fail RFC 3339 datetime validation, resulting in `DESTINATION_SERIALIZATION_ERROR` and nulled data.

Starting with version 1.0.0, DateOnly fields are correctly mapped to `format: "date"`. This is a schema type change that requires affected streams to be reset.

### Steps to upgrade

1. Upgrade the connector to version 1.0.0.
2. Refresh the source schema in your connection settings.
3. Reset and re-sync any streams that contain DateOnly fields.

After the reset, DateOnly fields that were previously being nulled will now sync correctly.

## Connector upgrade guide

<MigrationGuide />
