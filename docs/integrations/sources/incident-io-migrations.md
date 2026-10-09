import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

# incident.io Migration Guide

## Upgrading to 1.0.0

:::danger Risk of permanent data loss
Clearing a stream truncates its destination data. Snapshot or back up affected tables first. A re-sync is bounded by `start_date` and the history incident.io still serves, so records before your configured start date or no longer available from incident.io will not be restored.
:::

### What changed

Version 1.0.0 declares 49 existing fields as nullable date-time strings with Airbyte type `timestamp_with_timezone`. Their JSON Schema type remains `["string", "null"]`.

| Stream | Field | Previous type | New type |
| --- | --- | --- | --- |
| actions | `completed_at` | nullable `string` | nullable `string`, `format: date-time`, `timestamp_with_timezone` |
| actions | `created_at` | nullable `string` | nullable `string`, `format: date-time`, `timestamp_with_timezone` |
| actions | `updated_at` | nullable `string` | nullable `string`, `format: date-time`, `timestamp_with_timezone` |
| alerts | `created_at` | nullable `string` | nullable `string`, `format: date-time`, `timestamp_with_timezone` |
| alerts | `resolved_at` | nullable `string` | nullable `string`, `format: date-time`, `timestamp_with_timezone` |
| alerts | `updated_at` | nullable `string` | nullable `string`, `format: date-time`, `timestamp_with_timezone` |
| catalog_types | `created_at` | nullable `string` | nullable `string`, `format: date-time`, `timestamp_with_timezone` |
| catalog_types | `last_synced_at` | nullable `string` | nullable `string`, `format: date-time`, `timestamp_with_timezone` |
| catalog_types | `updated_at` | nullable `string` | nullable `string`, `format: date-time`, `timestamp_with_timezone` |
| custom_fields | `created_at` | nullable `string` | nullable `string`, `format: date-time`, `timestamp_with_timezone` |
| custom_fields | `updated_at` | nullable `string` | nullable `string`, `format: date-time`, `timestamp_with_timezone` |
| escalations | `created_at` | nullable `string` | nullable `string`, `format: date-time`, `timestamp_with_timezone` |
| escalations | `updated_at` | nullable `string` | nullable `string`, `format: date-time`, `timestamp_with_timezone` |
| escalations | `events[].occurred_at` | nullable `string` | nullable `string`, `format: date-time`, `timestamp_with_timezone` |
| escalations | `related_alerts[].created_at` | nullable `string` | nullable `string`, `format: date-time`, `timestamp_with_timezone` |
| escalations | `related_alerts[].resolved_at` | nullable `string` | nullable `string`, `format: date-time`, `timestamp_with_timezone` |
| escalations | `related_alerts[].updated_at` | nullable `string` | nullable `string`, `format: date-time`, `timestamp_with_timezone` |
| follow-ups | `completed_at` | nullable `string` | nullable `string`, `format: date-time`, `timestamp_with_timezone` |
| follow-ups | `created_at` | nullable `string` | nullable `string`, `format: date-time`, `timestamp_with_timezone` |
| follow-ups | `updated_at` | nullable `string` | nullable `string`, `format: date-time`, `timestamp_with_timezone` |
| incident_roles | `created_at` | nullable `string` | nullable `string`, `format: date-time`, `timestamp_with_timezone` |
| incident_roles | `updated_at` | nullable `string` | nullable `string`, `format: date-time`, `timestamp_with_timezone` |
| incident_statuses | `created_at` | nullable `string` | nullable `string`, `format: date-time`, `timestamp_with_timezone` |
| incident_statuses | `updated_at` | nullable `string` | nullable `string`, `format: date-time`, `timestamp_with_timezone` |
| severities | `created_at` | nullable `string` | nullable `string`, `format: date-time`, `timestamp_with_timezone` |
| severities | `updated_at` | nullable `string` | nullable `string`, `format: date-time`, `timestamp_with_timezone` |
| incident_updates | `created_at` | nullable `string` | nullable `string`, `format: date-time`, `timestamp_with_timezone` |
| incident_updates | `new_incident_status.created_at` | nullable `string` | nullable `string`, `format: date-time`, `timestamp_with_timezone` |
| incident_updates | `new_incident_status.updated_at` | nullable `string` | nullable `string`, `format: date-time`, `timestamp_with_timezone` |
| incident_updates | `new_severity.created_at` | nullable `string` | nullable `string`, `format: date-time`, `timestamp_with_timezone` |
| incident_updates | `new_severity.updated_at` | nullable `string` | nullable `string`, `format: date-time`, `timestamp_with_timezone` |
| incidents | `created_at` | nullable `string` | nullable `string`, `format: date-time`, `timestamp_with_timezone` |
| incidents | `updated_at` | nullable `string` | nullable `string`, `format: date-time`, `timestamp_with_timezone` |
| incidents | `last_activity_at` | nullable `string` | nullable `string`, `format: date-time`, `timestamp_with_timezone` |
| incidents | `incident_status.created_at` | nullable `string` | nullable `string`, `format: date-time`, `timestamp_with_timezone` |
| incidents | `incident_status.updated_at` | nullable `string` | nullable `string`, `format: date-time`, `timestamp_with_timezone` |
| incidents | `incident_type.created_at` | nullable `string` | nullable `string`, `format: date-time`, `timestamp_with_timezone` |
| incidents | `incident_type.updated_at` | nullable `string` | nullable `string`, `format: date-time`, `timestamp_with_timezone` |
| incidents | `severity.created_at` | nullable `string` | nullable `string`, `format: date-time`, `timestamp_with_timezone` |
| incidents | `severity.updated_at` | nullable `string` | nullable `string`, `format: date-time`, `timestamp_with_timezone` |
| incidents | `incident_role_assignments[].role.created_at` | nullable `string` | nullable `string`, `format: date-time`, `timestamp_with_timezone` |
| incidents | `incident_role_assignments[].role.updated_at` | nullable `string` | nullable `string`, `format: date-time`, `timestamp_with_timezone` |
| incidents | `incident_timestamp_values[].value.value` | nullable `string` | nullable `string`, `format: date-time`, `timestamp_with_timezone` |
| schedules | `created_at` | nullable `string` | nullable `string`, `format: date-time`, `timestamp_with_timezone` |
| schedules | `updated_at` | nullable `string` | nullable `string`, `format: date-time`, `timestamp_with_timezone` |
| schedules | `config.rotations[].handover_start_at` | nullable `string` | nullable `string`, `format: date-time`, `timestamp_with_timezone` |
| schedules | `current_shifts[].start_at` | nullable `string` | nullable `string`, `format: date-time`, `timestamp_with_timezone` |
| schedules | `current_shifts[].end_at` | nullable `string` | nullable `string`, `format: date-time`, `timestamp_with_timezone` |
| workflows | `runs_from` | nullable `string` | nullable `string`, `format: date-time`, `timestamp_with_timezone` |

The `catalog_types` stream now reads `/v3/catalog_types`. The v3 response no longer has `semantic_type`. The five new top-level fields are `engine_resource_type`, `estimated_count`, `is_team_type`, `owning_team_ids`, and `use_name_as_identifier`. The nested v3 additions are `schema.attributes[].backlink_attribute`, `schema.attributes[].path`, `schema.attributes[].path[].attribute_id`, and `schema.attributes[].path[].attribute_name`. These nine additions are nullable and intentionally do not constrain values with enums or required properties.

The `incidents` stream now requests all five modes: `standard`, `retrospective`, `test`, `tutorial`, and `stream`. Its child stream `incident_attachments` follows the expanded parent scope and may also return more records. The manifest has no other child stream whose parent is `incidents`. In the sandbox precheck, the response contained 20 standard, 2 retrospective, 1 test, 2 tutorial, and 0 stream incidents.

### Why

Destinations currently load these timestamp values as text. The timestamp annotations let destinations treat them as time-zone-aware timestamps. incident.io has deprecated `/v2/catalog_types`; the v3 endpoint removes `semantic_type` and exposes the v3 catalog fields.

### Who is affected

Connections that sync any of `actions`, `alerts`, `catalog_types`, `custom_fields`, `escalations`, `follow-ups`, `incident_roles`, `incident_statuses`, `incident_updates`, `incidents`, `schedules`, `severities`, or `workflows` need to refresh their source schema. Connections syncing `incident_attachments` may receive additional records because the parent incidents stream now includes all five modes. Connections that sync none of these streams do not need to change their schema or clear data for this release.

### Steps

1. Upgrade to version 1.0.0.
2. Refresh the source schema and accept the changes.
3. For full-refresh streams using **Overwrite**, the next sync rebuilds the affected table, so no clear is needed. For full-refresh streams using **Append**, existing rows remain and new rows are appended; old timestamp values remain text unless the destination can evolve the column.
4. For incremental streams (`actions`, `follow-ups`, `incidents`, `alerts`, and `escalations`), if your destination cannot change an existing column's type, clear only those incremental streams whose type change it cannot apply, then sync them again. A clear is destructive and truncates the destination data for that stream. If no clear is done on an append-mode stream, old rows keep the text values.
5. A clear re-syncs from `start_date`. The default `2020-01-01T00:00:00Z` predates incident.io data. If you use a later `start_date`, records last updated before it will not be re-synced; snapshot or back up the destination first. Records no longer available from incident.io will not be restored by a clear. The incidents endpoint is limited to 60 requests per minute, so a full backfill can take time.

### Downstream changes

Update SQL and dbt models, dashboards, and exports that cast or compare the 49 timestamp fields as text. Queries that read `catalog_types.semantic_type` will fail because that field is removed; use the remaining catalog fields or the new v3 fields as appropriate. The `incidents` stream may contain more rows now that test, tutorial, and stream modes are requested; filter on the `mode` field if you need the previous standard-and-retrospective scope. The `incident_attachments` stream may also contain attachments for those additional incidents.

## Connector upgrade guide

<MigrationGuide />
