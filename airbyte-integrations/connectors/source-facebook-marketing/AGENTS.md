> NOTE: CLAUDE.md is a symlink to AGENTS.md; update AGENTS.md (not the symlink) when changing these instructions.

# Contributing to source-facebook-marketing

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Incremental Stream Considerations

The Facebook Marketing API supports date-based filtering via `time_range` and `filtering` parameters. The connector is a Python CDK connector with classes like `FBMarketingIncrementalStream` and `FBMarketingReversedIncrementalStream` providing incremental patterns.

**Connector type:** Python CDK

**Analysis status:** Pure Python CDK connector with sophisticated incremental patterns already in place. Full stream-by-stream analysis requires Python code review.

### Future incremental stream candidates

- **All streams deferred for Python code review:** This connector defines its streams in Python code rather than declarative manifest YAML. A full stream-by-stream incremental analysis table (per the standard CONTRIBUTING.md schema) should be added by a future agent after reviewing the Python stream definitions, their `cursor_field` properties, and the API endpoints they call.

### Insights streams cursor (`AdsInsights`)

- Each sync starts `insights_lookback_window` days before the saved `date_start` cursor to refresh recent data, and state is checkpointed after every day slice.
- The saved `date_start` must never move backwards while those lookback slices are re-read (`_advance_cursor`). Otherwise an interrupted attempt persists the lower value and the next attempt subtracts the lookback window again, widening the read window after each interruption.
- `slices` in state only holds completed slices ahead of the cursor; entries at or before the cursor are dropped.
