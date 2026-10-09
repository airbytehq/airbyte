> NOTE: CLAUDE.md is a symlink to AGENTS.md; update AGENTS.md (not the symlink) when changing these instructions.

# Contributing to source-shopify

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Incremental Stream Considerations

The Shopify REST API supports `updated_at_min` filtering on most resource endpoints. The connector is a Python CDK connector with `IncrementalShopifyStream`, `IncrementalShopifySubstream`, and `IncrementalShopifyNestedStream` classes providing layered incremental patterns.

**Connector type:** Python CDK

**Analysis status:** Pure Python CDK connector with comprehensive incremental patterns. Full stream-by-stream analysis requires Python code review.

### Future incremental stream candidates

- **All streams deferred for Python code review:** This connector defines its streams in Python code rather than declarative manifest YAML. A full stream-by-stream incremental analysis table (per the standard CONTRIBUTING.md schema) should be added by a future agent after reviewing the Python stream definitions, their `cursor_field` properties, and the API endpoints they call.
