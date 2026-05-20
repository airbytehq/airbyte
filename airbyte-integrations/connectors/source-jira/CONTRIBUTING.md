# Contributing to source-jira

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Incremental Stream Considerations

The Jira REST API supports `updatedDate` JQL filtering for issues and related entities. The connector uses Python custom components referenced from the manifest. PR airbytehq/airbyte#76840 (in flight) addresses inert-flag cleanup. The four child streams (`issue_remote_links`, `issue_transitions`, `issue_votes`, `issue_watchers`) lack record-level `updated` fields.

**Connector type:** Python custom components (hybrid manifest + Python)

**Analysis status:** Streams are Python-defined via custom components. PR airbytehq/airbyte#76840 is in flight for inert-flag cleanup. Full stream-by-stream analysis requires Python code review.

### Deferred streams

- **All streams deferred for Python code review:** This connector defines its streams in Python code rather than declarative manifest YAML. A full stream-by-stream incremental analysis table (per the standard CONTRIBUTING.md schema) should be added by a future agent after reviewing the Python stream definitions, their `cursor_field` properties, and the API endpoints they call.
