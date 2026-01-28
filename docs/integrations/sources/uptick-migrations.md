import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

# Uptick Migration Guide

## Upgrading to 0.4.0

This release introduces breaking changes that remove unused fields from the connector schema.

### What changed

- The `assets` stream no longer includes the `floorplan_location_id` field.
- The `tasksessions` stream no longer includes `hours`, `sell_hours`, `appointment_attendance`, `is_suspicious_started`, and `is_suspicious_finished`. These computed fields were removed to reduce server load.

### Who is affected

This change affects users who sync the `assets` or `tasksessions` streams and have downstream queries, dashboards, or transformations that reference the removed fields.

### Required actions

After upgrading to version 0.4.0:

1. **Update downstream queries and dashboards** that reference removed fields:
   - For `assets`: Remove references to `floorplan_location_id`.
   - For `tasksessions`: Replace `hours` with `duration_hours` if you were using it. Remove references to `sell_hours`, `appointment_attendance`, `is_suspicious_started`, and `is_suspicious_finished`.

## Connector upgrade guide

<MigrationGuide />
