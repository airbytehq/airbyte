# Contributing to source-amplitude

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Incremental Stream Considerations

The Amplitude API supports incremental data export via the Export API with date-based windowing. The connector uses Python custom components referenced from the manifest via `custom_components_mapping`. All streams are defined in Python code. The connector already supports incremental sync for its primary data export streams (events, active_users, average_sessions, annotations, cohorts).

**Connector type:** Python custom components (hybrid manifest + Python)

**Analysis status:** Streams are Python-defined via custom components. Full stream-by-stream analysis requires Python code review. The connector's primary high-volume streams appear to already support incremental sync.

### Deferred streams

- **All streams deferred for Python code review:** This connector defines its streams in Python code rather than declarative manifest YAML. A full stream-by-stream incremental analysis table (per the standard CONTRIBUTING.md schema) should be added by a future agent after reviewing the Python stream definitions, their `cursor_field` properties, and the API endpoints they call.
