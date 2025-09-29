import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

# Metabase Migration Guide

## Upgrading to 2.0.0

Source Metabase has updated the `dashboards` stream's endpoint due to the previous endpoint being deprecated by the service. The new version no longer returns the `creator` field for the `dashboards` stream.

## Connector upgrade guide

<MigrationGuide />
