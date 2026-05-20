# Contributing to source-google-analytics-data-api

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Incremental Stream Considerations

The Google Analytics Data API v1 uses `runReport` and `runRealtimeReport` methods that accept date ranges. The connector dynamically generates report streams based on user configuration. The `google_analytics_stream_template` in the manifest defines the base template for these report streams. Report generation inherently uses date ranges and the connector handles incremental via date windowing.

| Stream | Volume Tier | Relationship | Cursor Field | API Incremental Support | Current Status | Notes |
|---|---|---|---|---|---|---|
| google_analytics_stream_template | medium | top-level parent | none | none | deferred_no_api_support | Template definition for dynamic report streams; not a standalone data endpoint |

### Deferred streams

- **No API date filter (1 streams):** `google_analytics_stream_template` — these endpoints do not expose date-based filtering. A future agent should verify via live API probing whether undocumented filter parameters are accepted.
