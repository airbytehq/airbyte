# Contributing to source-gong

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Incremental Stream Considerations

The Gong API exposes incremental filtering via `fromDateTime` on the calls and scorecards endpoints. The `users` endpoint does not support date-based filtering. Child streams (e.g. `answered_scorecards`) are partitioned via `SubstreamPartitionRouter`.

| Stream | Volume Tier | Relationship | Cursor Field | API Incremental Support | Current Status | Notes |
|---|---|---|---|---|---|---|
| answeredScorecards | medium | top-level parent | reviewTime | reviewTime | incremental |  |
| calls | medium | top-level parent | started | started | incremental |  |
| extensiveCalls | medium | top-level parent | startdatetime | startdatetime | incremental |  |
| scorecards | small | top-level parent | none | none | deferred_no_api_support | No date filter on list endpoint; config-style lookup |
| users | small | top-level parent | none | none | deferred_no_api_support | No date filter on list endpoint |
| callTranscripts | medium | child | started | started | incremental |  |

### Future incremental stream candidates

- **No API date filter (2 streams):** `scorecards`, `users` — these streams do not have a documented date-based filter on their list endpoints. A future agent should verify via live API probing whether undocumented filter parameters are accepted.
