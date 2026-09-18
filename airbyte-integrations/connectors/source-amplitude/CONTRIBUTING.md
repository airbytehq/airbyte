# Contributing to source-amplitude

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Incremental Stream Considerations

**Connector type:** Hybrid (manifest.yaml + Python custom components for record extraction/transformation)

**Analysis status:** Complete. All 6 streams analyzed. 3 use incremental sync with `DatetimeBasedCursor`; 3 are full-refresh due to API limitations.

### Incremental Streams

| Stream | Cursor Field | API Filter | Notes |
|--------|-------------|------------|-------|
| active_users | `date` | `start`/`end` date params | Amplitude Active Users API with date range |
| average_session_length | `date` | `start`/`end` date params | Amplitude Average Session Length API |
| events | `server_upload_time` | `start`/`end` date params | Amplitude Export API with date-based windowing |

### Full-Refresh Streams (Not Actionable)

| Stream | Reason | Evidence |
|--------|--------|----------|
| annotations | No date filtering support | Amplitude Annotations API; no `incremental_sync` in manifest |
| cohorts | No date filtering support | Amplitude Cohorts API returns all cohorts; no `modified_since` or date param |
| events_list | No date filtering support | Amplitude Events List API returns all event types; no date param |
