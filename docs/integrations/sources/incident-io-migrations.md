import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

# Incident.io Migration Guide

## Upgrading to 1.0.0

:::danger Risk of permanent data loss
Clearing a stream truncates its destination data. Snapshot or back up affected tables first. A re-sync is bounded by `start_date` and the history incident.io still serves, so records before your configured start date or no longer available from incident.io will not be restored.
:::

### What changed

Each field was a nullable string; it is now a nullable string with `format: date-time` and Airbyte type `timestamp_with_timezone`, so destinations that support it load a timestamp with time zone instead of text.

| Stream | Fields |
| --- | --- |
| actions | `completed_at`, `created_at`, `updated_at` |
| alerts | `created_at`, `resolved_at`, `updated_at` |
| catalog_types | `created_at`, `last_synced_at`, `updated_at` |
| custom_fields | `created_at`, `updated_at` |
| escalations | `created_at`, `updated_at`, `events[].occurred_at`, `related_alerts[].created_at`, `related_alerts[].resolved_at`, `related_alerts[].updated_at` |
| follow-ups | `completed_at`, `created_at`, `updated_at` |
| incident_roles | `created_at`, `updated_at` |
| incident_statuses | `created_at`, `updated_at` |
| incident_updates | `created_at`, `new_incident_status.created_at`, `new_incident_status.updated_at`, `new_severity.created_at`, `new_severity.updated_at` |
| incidents | `created_at`, `updated_at`, `last_activity_at`, `incident_status.created_at`, `incident_status.updated_at`, `incident_type.created_at`, `incident_type.updated_at`, `severity.created_at`, `severity.updated_at`, `incident_role_assignments[].role.created_at`, `incident_role_assignments[].role.updated_at`, `incident_timestamp_values[].value.value` |
| schedules | `created_at`, `updated_at`, `config.rotations[].handover_start_at`, `current_shifts[].start_at`, `current_shifts[].end_at` |
| severities | `created_at`, `updated_at` |
| workflows | `runs_from` |

The `catalog_types` stream now reads `/v3/catalog_types`. The v3 response no longer has `semantic_type`; incident.io documents that field on v2 as deprecated and always empty, so no populated data is lost. Four top-level fields are new in v3: `engine_resource_type`, `is_team_type`, `owning_team_ids`, and `use_name_as_identifier`. The stream also now declares fields that v2 already documented: `estimated_count`, `schema.attributes[].backlink_attribute`, `schema.attributes[].path`, `schema.attributes[].path[].attribute_id`, and `schema.attributes[].path[].attribute_name`. All nine are nullable. In v3, `schema.attributes[].mode` no longer uses `manual`; those attributes now report `api` or `dashboard`.

The `incidents` stream now requests all five modes: `standard`, `retrospective`, `test`, `tutorial`, and `stream`. Its child stream `incident_attachments` follows the expanded parent scope and may also return more records.

On an existing connection, `incidents` continues from its saved cursor, so test, tutorial, and stream incidents last updated before the upgrade are not synced. To include them, clear `incidents` after upgrading, then sync it again. `incident_attachments` is a full-refresh stream that re-reads every parent incident on each sync, so it picks up attachments of those incidents on its next sync without a clear.

### Why

Destinations currently load these timestamp values as text. The timestamp annotations let destinations treat them as time-zone-aware timestamps. incident.io has deprecated `/v2/catalog_types`; the v3 endpoint removes `semantic_type` and exposes the v3 catalog fields. incident.io has also deprecated `/v2/alert_routes`, so the `alert_routes` stream moves to `/v3/alert_routes`.

### Who is affected

Connections that sync any of `actions`, `alerts`, `catalog_types`, `custom_fields`, `escalations`, `follow-ups`, `incident_roles`, `incident_statuses`, `incident_updates`, `incidents`, `schedules`, `severities`, or `workflows` need to refresh their source schema. Connections syncing `incident_attachments` may receive additional records because the parent incidents stream now includes all five modes. Connections that sync none of these streams do not need to change their schema or clear data for this release. Connections that sync `alert_routes` need no action; see the `alert_routes` section below.

### Steps

1. Upgrade to version 1.0.0.
2. Refresh the source schema and accept the changes.
3. For full-refresh streams using **Overwrite**, the next sync rebuilds the affected table, so no clear is needed.
4. For any stream that keeps existing rows, meaning full-refresh streams using **Append** and the incremental streams (`actions`, `follow-ups`, `incidents`, `alerts`, and `escalations`), check whether your destination can change an existing column's type from text to timestamp. If it can, no clear is needed; the destination converts the values already in that column. If it cannot (for example, S3 Data Lake and other Iceberg destinations reject a string-to-timestamp change), clear only the streams whose type change it cannot apply, then sync them again. A clear is destructive and truncates the destination data for that stream.
5. A clear re-syncs from `start_date`. If you use a later `start_date`, records last updated before it will not be re-synced; snapshot or back up the destination first. Records no longer available from incident.io will not be restored by a clear. The incidents endpoint is limited to 60 requests per minute, so a full backfill can take time.

### Downstream changes

Update SQL and dbt models, dashboards, and exports that cast or compare the 49 timestamp fields as text. Remove `catalog_types.semantic_type` from queries; it was always empty and has no replacement. Filters on `schema.attributes[].mode = 'manual'` must match `api` or `dashboard` instead. The `incidents` stream may contain more rows now that test, tutorial, and stream modes are requested; filter on the `mode` field if you need the previous standard-and-retrospective scope. The `incident_attachments` stream may also contain attachments for those additional incidents.

### `alert_routes` moves to v3

The `alert_routes` stream now reads `/v3/alert_routes`, because incident.io has deprecated `/v2/alert_routes`. This is a path change only: the v2 and v3 list endpoints return the same fields (`id`, `name`, and `enabled`), and the primary key and pagination are unchanged. No action is needed.

## Connector upgrade guide

<MigrationGuide />
