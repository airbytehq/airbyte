# Uptick Migration Guide

## Upgrading to 0.4.0

This release introduces breaking changes removing unused fields from the connector schema.

### What changed

- The `assets` stream removes the `floorplan_location_id` field as it is not useful.
- The `tasksessions` stream removes `hours`, `sell_hours`, `appointment_attendance`, `is_suspicious_started`, and `is_suspicious_finished` to reduce server load from computed fields.

### Required actions

After upgrading to version 0.4.0:

1. **Refresh your source schema** in the Airbyte UI to see the updated field schema.
2. **Reset affected streams** (`assets` and `tasksessions`) to re-sync data with the new schema (recommended if you need to ensure data consistency)
3. **Update downstream queries and dashboards** that reference removed fields:
   - For `assets`: Remove references to `floorplan_location_id`
   - For `tasksessions`:
     - Replace `hours` with `duration_hours` if you were using it
     - Remove references to `sell_hours`, `appointment_attendance`, `is_suspicious_started`, and `is_suspicious_finished`
