> NOTE: CLAUDE.md is a symlink to AGENTS.md; update AGENTS.md (not the symlink) when changing these instructions.

# Contributing to source-sentry

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Multiple projects

`project` is a list of project slugs. `events`, `issues`, and `project_detail` read each slug as its own partition (`project_partition_router`, which also removes duplicate slugs), so the `events` and `issues` state holds one cursor per project under `states[].partition.project`. A state saved before 1.1.0 (`{"dateCreated": ...}` or `{"lastSeen": ...}`) is applied to every project on the first sync after the upgrade.

A slug added to an existing connection has no cursor of its own, so it starts from the connection's newest bookmark (the CDK's `ConcurrentPerPartitionCursor` falls back to the global cursor), not from `start_date`. Its older events and issues aren't synced; the docs tell users to refresh `events` and `issues` after adding a project. The manifest has no setting to change this, so a fix needs a custom state migration or a CDK option.

Setup (`CheckStream` on `project_detail`) reads only the first slug, so a misspelled slug later in the list fails the first sync instead. The 404 message tells users to check every slug, and the stream failure that follows includes the failing request URL. Don't put `{{ request_url }}` in the message: the 7.37.1 runtime supports it, but the unit tests' CDK 7.5.1 rejects it as an undeclared variable and turns the 404 into a system error.

Configs saved before 1.1.0 hold one slug as text. The `config_normalization_rules` migration wraps it in a list before the spec check, and the platform saves the migrated config. A connection pinned back to 1.0.16 or earlier then fails the spec check until **Projects** is edited back to a single slug, and its first sync re-reads `events` and `issues` in full.

## Start date

The optional `start_date` setting (**Events start date** in the form) is the first-sync lower bound for `events` only, sent as Sentry's `start` query parameter. `issues`, `projects`, and `releases` keep master's fixed `1900-01-01T00:00:00.0Z` start, so a recent events date doesn't cut their history and `all_projects_detail` can keep `projects` as its parent. When `start_date` is empty, `events` falls back to `1900-01-01T00:00:00Z`, meaning no lower bound. Keep that fallback: a recent date would make connections saved without a start date sync fewer events than before, which is a breaking change.

It's entered without fractional seconds; the events `start_datetime` parses it with its own `datetime_format`, so the cursor and request formats are unchanged. Later syncs start from saved state.

## Incremental Stream Considerations

The Sentry API supports date-based filtering on events and issues endpoints, which the connector already uses for incremental streams. The remaining FR parent stream `project_detail` is a singleton config endpoint that returns a single project object — not suitable for incremental sync.

| Stream | Volume Tier | Relationship | Cursor Field | API Incremental Support | Current Status | Notes |
|---|---|---|---|---|---|---|
| events | medium | top-level parent | dateCreated | dateCreated | incremental |  |
| issues | medium | top-level parent | lastSeen | lastSeen | incremental |  |
| project_detail | small | top-level parent | none | none | deferred_no_api_support | Singleton project config endpoint |
| projects | medium | top-level parent | dateCreated | dateCreated | incremental |  |
| releases | medium | top-level parent | dateCreated | dateCreated | incremental |  |

### Future incremental stream candidates

- **No API date filter (1 streams):** `project_detail` — these streams do not have a documented date-based filter on their list endpoints. A future agent should verify via live API probing whether undocumented filter parameters are accepted.
