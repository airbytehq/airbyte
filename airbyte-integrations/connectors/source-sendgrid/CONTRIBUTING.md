# Contributing to source-sendgrid

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Incremental Stream Considerations

The SendGrid API supports `start_time`/`end_time` filtering on suppression endpoints (blocks, bounces, invalid_emails, spam_reports, global_suppressions), which the connector already uses for incremental streams. The remaining FR parent streams are marketing API endpoints (campaigns, contacts, lists, segments, singlesends, templates) and configuration endpoints (suppression_groups) that do not support date-based filtering on their list endpoints.

| Stream | Volume Tier | Relationship | Cursor Field | API Incremental Support | Current Status | Notes |
|---|---|---|---|---|---|---|
| blocks | medium | top-level parent | created | created | incremental |  |
| bounces | medium | top-level parent | created | created | incremental |  |
| campaigns | medium | top-level parent | none | none | deferred_no_api_support | Marketing campaigns list; no date filter |
| contacts | large | top-level parent | none | none | deferred_no_api_support | Marketing contacts; export API exists but list endpoint lacks date filter |
| global_suppressions | medium | top-level parent | created | created | incremental |  |
| invalid_emails | medium | top-level parent | created | created | incremental |  |
| lists | small | top-level parent | none | none | deferred_no_api_support | Marketing lists; config-style |
| segments | small | top-level parent | none | none | deferred_no_api_support | Marketing segments; config-style |
| singlesend_stats | medium | top-level parent | none | none | deferred_no_api_support | Stats for single sends; no date filter on list |
| singlesends | medium | top-level parent | none | none | deferred_no_api_support | Single sends list; no date filter |
| spam_reports | medium | top-level parent | created | created | incremental |  |
| stats_automations | medium | top-level parent | none | none | deferred_no_api_support | Automation stats; no date filter on list |
| suppression_group_members | medium | top-level parent | created_at | created_at | incremental |  |
| suppression_groups | small | top-level parent | none | none | deferred_no_api_support | ASM groups; config-style lookup |
| templates | small | top-level parent | none | none | deferred_no_api_support | Email templates; config-style lookup |

### Deferred streams

- **No API date filter (9 streams):** `campaigns`, `contacts`, `lists`, `segments`, `singlesend_stats`, `singlesends`, `stats_automations`, `suppression_groups`, `templates` — these endpoints do not expose date-based filtering. A future agent should verify via live API probing whether undocumented filter parameters are accepted.
