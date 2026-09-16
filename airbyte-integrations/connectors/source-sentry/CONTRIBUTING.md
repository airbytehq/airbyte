# Contributing to source-sentry

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Incremental Stream Considerations

The Sentry API supports date-based filtering on events and issues endpoints, which the connector already uses for incremental streams. The remaining FR parent stream `project_detail` is a singleton config endpoint that returns a single project object — not suitable for incremental sync.

| Stream | Volume Tier | Relationship | Cursor Field | API Incremental Support | Current Status | Notes |
|---|---|---|---|---|---|---|
| events | medium | top-level parent | dateCreated | dateCreated | incremental |  |
| issues | medium | top-level parent | lastSeen | lastSeen | incremental |  |
| project_detail | small | top-level parent | none | none | deferred_no_api_support | Singleton project config endpoint |
| projects | medium | top-level parent | dateCreated | dateCreated | incremental |  |
| releases | medium | top-level parent | dateCreated | dateCreated | incremental |  |

### Future incremental stream candidates

- **No API date filter (1 streams):** `project_detail` — these streams do not have a documented date-based filter on their list endpoints. A future agent should verify via live API probing whether undocumented filter parameters are accepted.
