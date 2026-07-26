import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

# Productboard Migration Guide

## Upgrading to 1.0.0

Productboard has retired the v1 REST API, so Source Productboard has been migrated to the Productboard v2 API. This is a breaking change: the endpoints, the record shape, and the set of available streams all change.

### What changed

| Aspect | Before (v1) | After (v2) |
|--------|-------------|------------|
| Endpoints | `/products`, `/features`, `/notes`, … with the `X-Version: 1` header | Unified `/v2/entities` (one entity type per stream) and `/v2/notes`; no version header |
| Record shape | Flat fields (`name`, `status`, `owner`, …) | Business fields nested under `fields`; related entities under `relationships`; workspace custom fields as UUID-keyed entries inside `fields` |
| Pagination | `pageCursor` | `links.next` cursor |

### Removed streams

The following streams have no v2 equivalent and were removed. Their data is now inline on the entity or note records:

- `feedback-form-configurations`
- `custom-fields`
- `company-custom-fields`
- `tags` (now inline on notes/entities)
- `feature-statuses` (now `fields.status`)
- `links` (now under `relationships`)
- `feature-release-assignments` (now under `relationships`)
- `custom-fields-values` (values now inline under `fields`)

### Refresh affected schemas and reset data

After upgrading, refresh the source schema and reset all streams. Resetting is required so the `notes` stream re-initializes its incremental cursor under the v2 API and so downstream tables pick up the new nested `fields` record shape.

<MigrationGuide />
