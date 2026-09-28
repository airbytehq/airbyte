> NOTE: CLAUDE.md is a symlink to AGENTS.md; update AGENTS.md (not the symlink) when changing these instructions.

# Contributing to source-twilio

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Incremental Stream Considerations

The Twilio REST API supports `DateCreated` filtering on many resource list endpoints. The connector uses Python custom components referenced from the manifest.

**Connector type:** Python custom components (hybrid manifest + Python)

**Analysis status:** Streams are Python-defined via custom components. Full stream-by-stream analysis requires Python code review.

### Future incremental stream candidates

- **All streams deferred for Python code review:** This connector defines its streams in Python code rather than declarative manifest YAML. A full stream-by-stream incremental analysis table (per the standard CONTRIBUTING.md schema) should be added by a future agent after reviewing the Python stream definitions, their `cursor_field` properties, and the API endpoints they call.

## Alerts request window splitting

The `alerts` stream uses `SPLIT_REQUEST_WINDOW` and `request_window_splitting` for Twilio 400 responses containing "Invalid page and pageSize combination"; the filter matches on message only because `HttpResponseFilter` conditions are OR'd. Windows split in half at `PT1S` granularity up to CDK's max depth of 10, and a 400 on a later page can cause earlier-page records to be replayed. Other 400 responses continue to fail.
