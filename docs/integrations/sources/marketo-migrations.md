# Marketo Migration Guide

## Upgrading to 2.0.0

This release migrates the Leads and Activities bulk export streams from Python to the low-code declarative framework. As part of this migration, six activity stream names change due to a standardized naming convention.

### Changed stream names

| Old name (v1.x) | New name (v2.0.0) |
|:---|:---|
| `activities_addto_list` | `activities_add_to_list` |
| `activities_push_leadto_marketo` | `activities_push_lead_to_marketo` |
| `activities_removefrom_list` | `activities_remove_from_list` |
| `activities_change_statusin_progression` | `activities_change_status_in_progression` |
| `activities_addto_opportunity` | `activities_add_to_opportunity` |
| `activities_removefrom_opportunity` | `activities_remove_from_opportunity` |

All other activity stream names remain unchanged.

### Migration steps

1. **Refresh your source schema** in the Airbyte UI after upgrading to pick up the renamed streams.
2. **Reset the affected streams** listed above. Because the stream names changed, existing state for the old names is no longer valid. Resetting ensures data is re-synced under the new stream names.
3. **Update any downstream references** (e.g., dbt models, dashboards, or orchestration scripts) that reference the old stream names.
