# Contributing to source-amplitude

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Incremental Stream Considerations

**Connector type:** Hybrid (manifest.yaml + Python custom components for record extraction/transformation)

**Analysis status:** Complete. All 6 streams analyzed. 3 use incremental sync with `DatetimeBasedCursor`; 3 are full-refresh due to API limitations.

### Incremental Streams

| Stream | Cursor Field | API Filter | Notes |
|--------|-------------|------------|-------|
| active_users | date | `start`/`end` date params | Amplitude Active Users API with date range |
| annotations | date | `start`/`end` date params | Amplitude Annotations/Labels API |
| average_session_length | date | `start`/`end` date params | Amplitude Average Session Length API |

### Full-Refresh Streams (Not Actionable)

| Stream | Reason | Evidence |
|--------|--------|----------|
| cohorts | No date filtering support | Amplitude Cohorts API returns all cohorts; no `modified_since` or date param |
| events | Handled via Amplitude Export API (separate bulk export) | Export API uses date-based file downloads, not cursor-based incremental |
| average_session_length | Already incremental (listed above) | Uses date-based cursor |

Note: The `events` stream uses Amplitude's Export API which downloads zipped event data files. This is a fundamentally different access pattern from cursor-based incremental sync.
