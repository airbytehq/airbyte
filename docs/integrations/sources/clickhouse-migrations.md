import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

# ClickHouse Migration Guide

## Upgrading to 0.4.0

This release upgrades the ClickHouse JDBC driver from 0.3.2-patch10 to 0.9.8. The 0.9.7+ driver decodes Date and Date32 columns as `LocalDate` without timezone adjustment. Users syncing Date or Date32 columns may see changed values if their data relied on the previous timezone-adjusted behavior. A full refresh of affected streams is recommended after upgrading.

## Connector upgrade guide

<MigrationGuide />
