# Contributing to source-incident-io

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Incremental Stream Considerations

The incident.io API v2 supports date-based filtering on a limited set of endpoints. The `/v2/incidents` endpoint supports `updated_at[gte]` and `updated_at[lte]` query parameters ([API reference](https://docs.incident.io/api-reference/incidents-v2/list)). The `/v2/alerts` endpoint only supports `created_at` filtering, not `updated_at`. Most other list endpoints (actions, follow-ups, custom_fields, etc.) do not expose any date-based filtering.

All streams in this connector are top-level (no parent/child SubstreamPartitionRouter relationships). The connector uses cursor-based pagination via the `pagination_meta.after` field.

| Stream | Volume Tier | Relationship | Cursor Field | API Incremental Support | Current Status | Notes |
|---|---|---|---|---|---|---|
| incidents | xlarge | top-level parent | updated_at | updated_at | in_scope_this_pr | [API ref](https://docs.incident.io/api-reference/incidents-v2/list) — supports `updated_at[gte]` |
| alerts | large | top-level parent | updated_at | created_at_only | deferred_no_api_support | Only `created_at` filter, not `updated_at` — insufficient for mutable resource |
| escalations | large | top-level parent | updated_at | none | deferred_no_api_support | No date-based filter on list endpoint |
| actions | medium | top-level parent | updated_at | none | deferred_no_api_support | No date-based filter on list endpoint |
| follow-ups | medium | top-level parent | updated_at | none | deferred_no_api_support | No date-based filter on list endpoint |
| incident_updates | medium | top-level parent | none | none | deferred_no_api_support | No updated_at field; append-only log |
| catalog_types | small | top-level parent | updated_at | none | deferred_no_api_support | Config-style stream, low volume |
| custom_fields | small | top-level parent | updated_at | none | deferred_no_api_support | Config-style stream, low volume |
| incident_roles | small | top-level parent | updated_at | none | deferred_no_api_support | Config-style stream, low volume |
| incident_timestamps | small | top-level parent | none | none | not_applicable | Config-style stream, no updated_at |
| incident_statuses | small | top-level parent | updated_at | none | deferred_no_api_support | Config-style stream, low volume |
| workflows | small | top-level parent | none | none | deferred_no_api_support | No updated_at field |
| users | small | top-level parent | none | none | deferred_no_api_support | No updated_at field or date filter |
| severities | small | top-level parent | updated_at | none | deferred_no_api_support | Config-style stream, low volume |
| schedules | small | top-level parent | updated_at | none | deferred_no_api_support | Config-style stream, low volume |

### Deferred streams

- **No API date filter (10 streams):** `alerts`, `escalations`, `actions`, `follow-ups`, `catalog_types`, `custom_fields`, `incident_roles`, `incident_statuses`, `severities`, `schedules` — these streams have `updated_at` on the record but the incident.io API does not expose an `updated_at`-based filter on their list endpoints. The `alerts` endpoint supports `created_at` filtering only, which is insufficient for a mutable resource. A future agent should verify via live API probing whether undocumented `updated_at` filter parameters are accepted.
- **No cursor field (3 streams):** `incident_timestamps`, `workflows`, `users` — no `updated_at` field on the record schema.
- **Append-only (1 stream):** `incident_updates` — log-style entries without `updated_at`; could potentially use `created_at` for append-only incremental in the future.
