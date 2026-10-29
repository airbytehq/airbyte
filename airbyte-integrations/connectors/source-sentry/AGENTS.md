> NOTE: CLAUDE.md is a symlink to AGENTS.md; update AGENTS.md (not the symlink) when changing these instructions.

# Contributing to source-sentry

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Multiple projects

`project` is a list of project slugs. `events`, `issues`, and `project_detail` read each slug as its own partition (`project_partition_router`, which also removes duplicate slugs), so the `events` and `issues` state holds one cursor per project under `states[].partition.project`. A state saved before 1.1.0 (`{"dateCreated": ...}` or `{"lastSeen": ...}`) is applied to every project on the first sync after the upgrade.

Configs saved before 1.1.0 hold one slug as text. The `config_normalization_rules` migration wraps it in a list before the spec check, and the platform saves the migrated config. A connection pinned back to 1.0.16 or earlier then fails the spec check until **Projects** is edited back to a single slug, and its first sync re-reads `events` and `issues` from their start dates.

## Start dates

- `event_start_date` (default `1900-01-01T00:00:00Z`) is the first-sync lower bound for `events` only, sent as Sentry's `start` query parameter. A config that still has the older `start_date` key and no `event_start_date` uses `start_date` for events.
- `sync_start_date` (optional, `1900-01-01T00:00:00Z` when omitted) is the first-sync lower bound for `issues`, `projects`, and `releases`. It doesn't apply to `events`.

Both are entered without fractional seconds; each stream's `start_datetime` parses them with its own `datetime_format`, so the cursor and request formats are unchanged. Later syncs start from saved state. Because `projects` drops records created before the start of the sync window, `all_projects_detail` takes its project list from `projects_all`, which has no date filter.

## Incremental Stream Considerations

The Sentry API supports date-based filtering on events and issues endpoints, which the connector already uses for incremental streams. The remaining FR parent stream `project_detail` is a singleton config endpoint that returns a single project object — not suitable for incremental sync.

| Stream | Volume Tier | Relationship | Cursor Field | API Incremental Support | Current Status | Notes |
|---|---|---|---|---|---|---|
| events | medium | top-level parent | dateCreated | dateCreated | incremental |  |
| issues | medium | top-level parent | lastSeen | lastSeen | incremental |  |
| project_detail | small | top-level parent | none | none | deferred_no_api_support | Singleton project config endpoint |
| projects | medium | top-level parent | dateCreated | dateCreated | incremental |  |
| all_projects_detail | medium | child of `projects_all` | none | none | full refresh | Parent is a full org project list (no `start_date` record filter) so overwrite/deduped destinations keep every project detail row each sync. |
| releases | medium | top-level parent | dateCreated | dateCreated | incremental |  |

### Future incremental stream candidates

- **No API date filter (1 streams):** `project_detail` — these streams do not have a documented date-based filter on their list endpoints. A future agent should verify via live API probing whether undocumented filter parameters are accepted.
