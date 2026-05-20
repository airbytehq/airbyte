# Contributing to source-gitlab

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Incremental Stream Considerations

The GitLab API supports `updated_after` filtering on many endpoints. The connector uses Python custom components (`GroupStreamsPartitionRouter`, `ProjectStreamsPartitionRouter`) referenced from the manifest. Streams are defined in Python code and partitioned by group/project.

**Connector type:** Python custom components (hybrid manifest + Python)

**Analysis status:** Streams are Python-defined via custom components with custom partition routers. Full stream-by-stream analysis requires Python code review.

### Deferred streams

- **All streams deferred for Python code review:** This connector defines its streams in Python code rather than declarative manifest YAML. A full stream-by-stream incremental analysis table (per the standard CONTRIBUTING.md schema) should be added by a future agent after reviewing the Python stream definitions, their `cursor_field` properties, and the API endpoints they call.
