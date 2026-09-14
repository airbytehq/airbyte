import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

# Uptick Migration Guide

## Upgrading to 1.0.0

Version 1.0.0 upgrades the connector from Uptick API v2.14 to v2.15. Uptick API v2.15 no longer exposes several fields that were present in earlier API responses, so this release removes those fields from the connector schema.

### What changed

The following fields have been removed:

- `branches.fax`
- `defectquotelineitems.product_type`
- `servicetasks.due`
- `servicetasks.is_majorservice`
- `tasksessions.submitted`
- `tasksessions.is_approved`
- `tasksessions.is_submitted`

For the `tasksessions` stream, use `submitted_at` instead of `submitted`. To replace the removed boolean fields, treat a non-null `submitted_at` value as submitted and a non-null `approved_at` value as approved. The other removed fields do not have direct replacements in the connector.

### Who is affected

This change affects users who sync the `branches`, `defectquotelineitems`, `servicetasks`, or `tasksessions` streams and have downstream queries, dashboards, transformations, or destination schemas that reference the removed fields.

### Required actions

Before upgrading to version 1.0.0:

1. Update downstream queries, dashboards, and transformations to remove references to the deleted fields or use the `tasksessions` replacements described above.

After upgrading:

1. Refresh the source schema for each affected connection.
2. Review and save the affected connection schemas so the removed fields are no longer selected.
3. Run a sync and verify downstream models against the updated schemas.

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
