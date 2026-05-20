# Contributing to source-klaviyo

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Incremental Stream Considerations

The Klaviyo API supports cursor-based pagination and `filter` parameters with `greater-than` on `datetime` and `updated` fields for high-volume endpoints (profiles, events, campaigns, flows, lists, segments, etc.), which the connector already uses for 13 incremental streams. The single remaining FR parent stream (`metrics_for_reporting`) is a config-style lookup that lists available metric definitions without date-based filtering.

| Stream | Volume Tier | Relationship | Cursor Field | API Incremental Support | Current Status | Notes |
|---|---|---|---|---|---|---|
| campaigns | medium | top-level parent | updated_at | updated_at | incremental |  |
| campaigns_detailed | medium | top-level parent | updated_at | updated_at | incremental |  |
| email_templates | medium | top-level parent | updated | updated | incremental |  |
| events | medium | top-level parent | datetime | datetime | incremental |  |
| events_detailed | medium | top-level parent | datetime | datetime | incremental |  |
| flows | medium | top-level parent | updated | updated | incremental |  |
| global_exclusions | medium | top-level parent | updated | updated | incremental |  |
| lists | medium | top-level parent | updated | updated | incremental |  |
| metrics | medium | top-level parent | updated | updated | incremental |  |
| metrics_for_reporting | small | top-level parent | none | none | deferred_no_api_support | Lists metric definitions; config-style lookup, no date filter |
| profiles | medium | top-level parent | updated | updated | incremental |  |
| campaign_values_reports | medium | child | date | date | incremental |  |
| flow_series_reports | medium | child | date | date | incremental |  |
| lists_detailed | medium | child | updated | updated | incremental |  |

### Deferred streams

- **No API date filter (1 streams):** `metrics_for_reporting` — these endpoints do not expose date-based filtering. A future agent should verify via live API probing whether undocumented filter parameters are accepted.
