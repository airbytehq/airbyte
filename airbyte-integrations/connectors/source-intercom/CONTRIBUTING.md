# Contributing to source-intercom

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Incremental Stream Considerations

The Intercom API supports cursor-based pagination and `updated_at`-style filtering on some high-volume endpoints (companies, contacts, conversations). The connector already uses `DatetimeBasedCursor` for these. The remaining FR parent streams (admins, tags, teams, company_attributes, contact_attributes) are small config-style endpoints without date filtering.

| Stream | Volume Tier | Relationship | Cursor Field | API Incremental Support | Current Status | Notes |
|---|---|---|---|---|---|---|
| activity_logs | medium | top-level parent | created_at | created_at | incremental |  |
| admins | small | top-level parent | none | none | deferred_no_api_support | Config-style lookup, no date filter |
| companies | medium | top-level parent | updated_at | updated_at | incremental |  |
| company_attributes | small | top-level parent | none | none | deferred_no_api_support | Schema attributes endpoint, no date filter |
| contact_attributes | small | top-level parent | none | none | deferred_no_api_support | Schema attributes endpoint, no date filter |
| contacts | medium | top-level parent | updated_at | updated_at | incremental |  |
| conversations | medium | top-level parent | updated_at | updated_at | incremental |  |
| segments | medium | top-level parent | updated_at | updated_at | incremental |  |
| tags | small | top-level parent | none | none | deferred_no_api_support | Config-style lookup, no date filter |
| teams | small | top-level parent | none | none | deferred_no_api_support | Config-style lookup, no date filter |
| tickets | medium | top-level parent | updated_at | updated_at | incremental |  |
| company_segments | medium | child | updated_at | updated_at | incremental |  |
| conversation_parts | medium | child | updated_at | updated_at | incremental |  |

### Deferred streams

- **No API date filter (5 streams):** `admins`, `company_attributes`, `contact_attributes`, `tags`, `teams` — these streams do not have a documented date-based filter on their list endpoints. A future agent should verify via live API probing whether undocumented filter parameters are accepted.
