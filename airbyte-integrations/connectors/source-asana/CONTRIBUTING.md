# Contributing to source-asana

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Incremental Stream Considerations

The Asana API supports `modified_since` filtering on tasks and other endpoints. The connector is a Python CDK connector. PR airbytehq/airbyte#76838 (in flight) adds incremental sync for the `tasks` stream and performs inert-flag cleanup.

**Connector type:** Python CDK

**Analysis status:** Pure Python CDK connector. PR airbytehq/airbyte#76838 is in flight for `tasks` stream incremental. Full stream-by-stream analysis requires Python code review.

### Future incremental stream candidates

- **All streams deferred for Python code review:** This connector defines its streams in Python code rather than declarative manifest YAML. A full stream-by-stream incremental analysis table (per the standard CONTRIBUTING.md schema) should be added by a future agent after reviewing the Python stream definitions, their `cursor_field` properties, and the API endpoints they call.
