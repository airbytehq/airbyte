import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

# Square Migration Guide

## Upgrading to 2.0.0

Square retired the Labor API `Shift` endpoints (deprecated in Square API version `2025-05-21`, retired in `2026-05-21`). Once Square enforces the retirement, `POST /v2/labor/shifts/search` returns `410 GONE` for every caller, regardless of the `Square-Version` header. Version 2.0.0 moves the `shifts` stream to the replacement endpoint, `POST /v2/labor/timecards/search`, so the stream keeps working.

### Who is affected

Only connections that sync the `shifts` stream. All other streams are unchanged.

### What changed

- The `shifts` stream now reads `Timecard` objects from Square's Timecards API. Square keeps the same `id` for a timecard and the shift it replaces, so the stream's primary key and existing record identities are preserved. The stream name is unchanged.
- The `employee_id` field is removed. Square deprecated it in 2020 in favor of `team_member_id`, and the Timecards API doesn't return it. `team_member_id` carries the same value and is still present.
- The `wage` object is unchanged in shape (`title`, `hourly_rate.amount`, `hourly_rate.currency`). The optional `wage.job_id`, `wage.tip_eligible`, and `declared_cash_tip_money` fields are now declared in the schema.

### Migration steps

1. Upgrade the connector to 2.0.0.
2. Open each connection that syncs `shifts` and refresh the source schema so the `employee_id` column is dropped from the stream schema. No clear or full re-sync is required: records keep the same primary key, so existing rows in your destination stay valid.
3. Update downstream SQL, dbt models, dashboards, or exports that reference `shifts.employee_id` to use `shifts.team_member_id` instead. Existing rows already contain `team_member_id` with the same value.

## Connector upgrade guide

<MigrationGuide />
