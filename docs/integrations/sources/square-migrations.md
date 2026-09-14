import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

# Square Migration Guide

## Upgrading to 2.0.0

Square retired the Labor API `Shift` endpoints in API version `2026-05-21` and replaced them with `Timecard` endpoints. The `shifts` stream now reads from `SearchTimecards` (Square-Version `2025-05-21`).

Changes to the `shifts` stream:

- The `employee_id` field is no longer emitted. Square removed it from the `Timecard` object; use `team_member_id`, which identifies the same person.
- Record IDs (`id`) are unchanged, so existing records keep their identity.

After upgrading, refresh the source schema and reset the `shifts` stream.

## Connector upgrade guide

<MigrationGuide />
