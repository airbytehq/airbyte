> NOTE: CLAUDE.md is a symlink to AGENTS.md; update AGENTS.md (not the symlink) when changing these instructions.

# Contributing to source-facebook-marketing

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Incremental Stream Considerations

The Facebook Marketing API supports date-based filtering via `time_range` and `filtering` parameters. The connector is a Python CDK connector with classes like `FBMarketingIncrementalStream` and `FBMarketingReversedIncrementalStream` providing incremental patterns.

**Connector type:** Python CDK

**Analysis status:** Pure Python CDK connector with sophisticated incremental patterns already in place. Full stream-by-stream analysis requires Python code review.

### Insights cursor and lookback window

Insights streams (`AdsInsights` and custom insights) keep a per-account `date_start` cursor plus a `slices` list of days completed out of order. Every sync that starts from state re-reads `insights_lookback_window` days before the cursor. The cursor only moves forward: completing a re-read day that is older than the saved cursor leaves the cursor where it was, so an interrupted sync resumes from the same lookback window instead of an earlier one.

### Future incremental stream candidates

- **All streams deferred for Python code review:** This connector defines its streams in Python code rather than declarative manifest YAML. A full stream-by-stream incremental analysis table (per the standard CONTRIBUTING.md schema) should be added by a future agent after reviewing the Python stream definitions, their `cursor_field` properties, and the API endpoints they call.
