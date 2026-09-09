> NOTE: CLAUDE.md is a symlink to AGENTS.md; update AGENTS.md (not the symlink) when changing these instructions.

# source-sendgrid: Unique Behaviors

## 1. Async Contacts Export with Gzipped CSV Download

The `contacts` stream uses `AsyncRetriever` with a three-phase workflow: POST to `/v3/marketing/contacts/exports` to create an export job, poll the job status until `ready`, then download the result. Unlike all other streams in this connector which use standard synchronous JSON retrieval, the contacts export produces a gzipped CSV file that is decoded via `GzipDecoder` wrapping a `CsvDecoder`.

**Why this matters:** The contacts stream behaves fundamentally differently from every other stream in the connector. It has no pagination, no incremental sync, and returns data in CSV format instead of JSON. Export jobs can take significant time to complete, and if the job fails or times out on SendGrid's side, no partial results are available.

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

### Future incremental stream candidates

- **No API date filter (9 streams):** `campaigns`, `contacts`, `lists`, `segments`, `singlesend_stats`, `singlesends`, `stats_automations`, `suppression_groups`, `templates` — these endpoints do not expose date-based filtering. A future agent should verify via live API probing whether undocumented filter parameters are accepted.
