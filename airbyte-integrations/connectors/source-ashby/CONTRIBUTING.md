# Contributing to source-ashby

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Incremental Stream Considerations

The Ashby API uses `.list` endpoints with cursor-based pagination. The `applications` and `interview_schedules` endpoints support `createdAfter` filtering, but since these resources are mutable (status changes, updates), `created_at`-only filtering is insufficient for true incremental sync. The Ashby API may support `updatedAfter` on some endpoints — this needs live API verification. All other `.list` endpoints (candidates, jobs, offers, etc.) do not document date-based filtering.

| Stream | Volume Tier | Relationship | Cursor Field | API Incremental Support | Current Status | Notes |
|---|---|---|---|---|---|---|
| applications | large | top-level parent | none | created_at_only | deferred_no_api_support | Has `createdAfter` in body; mutable resource (status changes). Verify if `updatedAfter` is supported. |
| archive_reasons | small | top-level parent | none | none | deferred_no_api_support | Config-style lookup |
| candidate_tags | small | top-level parent | none | none | deferred_no_api_support | Config-style lookup |
| candidates | large | top-level parent | none | none | deferred_no_api_support | No documented date filter on `.list`. High volume. |
| custom_fields | small | top-level parent | none | none | deferred_no_api_support | Config-style lookup |
| departments | small | top-level parent | none | none | deferred_no_api_support | Config-style lookup |
| feedback_form_definitions | small | top-level parent | none | none | deferred_no_api_support | Config-style lookup |
| interview_schedules | medium | top-level parent | none | created_at_only | deferred_no_api_support | Has `createdAfter` in body; mutable resource. Verify if `updatedAfter` is supported. |
| job_postings | medium | top-level parent | none | none | deferred_no_api_support | No documented date filter |
| jobs | medium | top-level parent | none | none | deferred_no_api_support | No documented date filter |
| locations | small | top-level parent | none | none | deferred_no_api_support | Config-style lookup |
| offers | medium | top-level parent | none | none | deferred_no_api_support | No documented date filter |
| sources | small | top-level parent | none | none | deferred_no_api_support | Config-style lookup |
| users | small | top-level parent | none | none | deferred_no_api_support | Config-style lookup; Ashby workspace users |

### Future incremental stream candidates

- **No API date filter (12 streams):** `archive_reasons`, `candidate_tags`, `candidates`, `custom_fields`, `departments`, `feedback_form_definitions`, `job_postings`, `jobs`, `locations`, `offers`, `sources`, `users` — these endpoints do not expose date-based filtering. A future agent should verify via live API probing whether undocumented filter parameters are accepted.
- **Created-at only (2 streams):** `applications`, `interview_schedules` — these endpoints support `created` filtering but the resources are mutable, making `created_at`-only filtering insufficient for true incremental sync. Verify whether `updatedAfter` is supported.

## Authentication, Rate Limits, and Sync Tokens

- **Authentication:** Ashby's public API authenticates only with API keys (HTTP Basic, key as username, blank password) and offers no OAuth flow — see the [Ashby authentication reference](https://developers.ashbyhq.com/reference/authentication).
- **Rate limits:** Ashby publishes no numeric rate limit for its `.list` endpoints, so `api_budget` only throttles the per-application partitioned endpoints (`application.listHistory` and `application.listCriteriaEvaluations`, 100 requests/minute each). All other streams rely on the shared error handler's backoff on HTTP 429 (`Retry-After` header first, then exponential).
- **Error envelope:** Ashby returns most errors as HTTP 200 responses with `success: false` and an `errorInfo` object; these are surfaced by the shared `definitions.error_handler`, which every requester references. `application_history` and `application_criteria_evaluations` override its `response_filters` with the shared `definitions.response_filters` entries plus an `application_not_found` IGNORE ahead of the generic FAIL, because a sibling `response_filters` key replaces the referenced list rather than extending it.
- **Sync tokens:** `syncToken`-based incremental sync is deferred until the CDK sync-token cursor ships (airbytehq/airbyte-internal-issues#17213, adoption tracked in airbytehq/airbyte-internal-issues#17372). `createdAfter` alone is not a viable cursor because these resources mutate after creation.
