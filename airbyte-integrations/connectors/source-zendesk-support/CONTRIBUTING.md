# Contributing to source-zendesk-support

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Incremental Stream Considerations

The Zendesk Support API supports incremental export endpoints (`/api/v2/incremental/...`) for tickets, users, organizations, and other high-volume resources. The connector uses Python custom components referenced from the manifest.

**Connector type:** Python custom components (hybrid manifest + Python)

**Analysis status:** Streams are Python-defined via custom components. The connector is mature with extensive incremental support already in place via Zendesk's incremental export API.

### Deferred streams

- **All streams deferred for Python code review:** This connector defines its streams in Python code rather than declarative manifest YAML. A full stream-by-stream incremental analysis table (per the standard CONTRIBUTING.md schema) should be added by a future agent after reviewing the Python stream definitions, their `cursor_field` properties, and the API endpoints they call.
