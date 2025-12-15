# Zendesk Sunshine Migration Guide

import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

## Upgrading to 1.0.0

This release migrates the connector from the deprecated Zendesk Legacy Custom Objects API (`/api/sunshine/`) to the new Custom Objects API (`/api/v2/custom_objects/`).

### Breaking Changes

**Stream Removals:**
The following legacy streams have been removed and replaced with new streams that use the updated API:

| Removed Stream | Replacement Stream | Notes |
|----------------|-------------------|-------|
| `limits` | - | No direct equivalent in new API |
| `object_types` | `custom_objects` | Lists all custom objects |
| `object_records` | `custom_object_records` | Records for each custom object |
| `object_type_policies` | - | Permissions now handled differently |
| `relationship_types` | - | Now handled via lookup fields |
| `relationship_records` | - | Now handled via lookup fields |

**New Streams Added:**
- `custom_objects` - Lists all custom objects in your Zendesk account
- `custom_object_fields` - Lists fields for each custom object
- `custom_object_records` - Lists records for each custom object (supports incremental sync)

### Prerequisites

Before upgrading to this version, you **must** migrate your legacy custom objects in Zendesk to the new custom objects experience. See the [Zendesk migration guide](https://developer.zendesk.com/documentation/custom-data/custom-objects/migrating-legacy-custom-objects-to-the-new-custom-objects-experience/) for instructions.

### Connector upgrade guide

<MigrationGuide />

### Migration Steps

1. **Migrate your data in Zendesk first**: Follow Zendesk's migration guide to convert your legacy custom objects to the new custom objects experience
2. **Clear existing data**: After upgrading the connector, you will need to clear your existing synced data as the schema has changed
3. **Update stream selection**: Select the new streams (`custom_objects`, `custom_object_fields`, `custom_object_records`) in your connection configuration
4. **Run a full refresh sync**: Perform a full refresh to sync data using the new API

### Why This Change?

Zendesk is deprecating the Legacy Custom Objects API with the following timeline:
- **January 15, 2026**: No new legacy custom objects can be created
- **June 2026**: Full removal of legacy API

This migration ensures continued functionality of the connector after the legacy API is removed.
