# Contributing to source-orb

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Incremental Stream Considerations

The Orb API supports cursor-based pagination. The connector uses Python custom components (`SubscriptionUsagePartitionRouter`) referenced from the manifest.

**Connector type:** Python custom components (hybrid manifest + Python)

**Analysis status:** Streams are Python-defined via custom components with a custom partition router for subscription usage. Full stream-by-stream analysis requires Python code review.

### Future incremental stream candidates

- **All streams deferred for Python code review:** This connector defines its streams in Python code rather than declarative manifest YAML. A full stream-by-stream incremental analysis table (per the standard CONTRIBUTING.md schema) should be added by a future agent after reviewing the Python stream definitions, their `cursor_field` properties, and the API endpoints they call.
