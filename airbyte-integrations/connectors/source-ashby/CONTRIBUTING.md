# Contributing to source-ashby

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Incremental Stream Considerations

Only `applications` and `application_history` sync incrementally; every other stream is full refresh. Ashby's `.list` endpoints page with a `cursor`, and most of them also accept a `syncToken` that returns only records changed since the previous sync. `syncToken` incremental is deferred for every stream (see [Sync tokens](#authentication-rate-limits-and-sync-tokens)). Some endpoints also accept `createdAfter`, but these resources mutate after creation, so `createdAfter` alone is not a viable cursor. No endpoint documents `updatedAfter`, and a live probe (2026-09-30) showed `application.list` silently ignores it: a request with `updatedAfter` set to the current time still returned applications last updated in 2022, while `createdAfter` filtered as documented. The connector sends `createdAfter` from the `start_date` config only on `application.list`, `applicationFeedback.list`, and `interviewSchedule.list`.

API support below is each endpoint's request-body schema on its [reference page](https://developers.ashbyhq.com/llms.txt), checked 2026-10-23.

| Stream | Volume Tier | Relationship | Cursor Field | API Incremental Support | Current Status | Notes |
|---|---|---|---|---|---|---|
| applications | large | top-level parent | updatedAt | created_at_and_sync_token | incremental | Client-side `updatedAt` filter with a 1-day lookback, because `application.list` has no `updatedAt` filter and is ordered by `createdAt`; every sync pages the full list. `syncToken` would be the complete cursor once supported. |
| application_history | large | substream of applications | application_updated_at | via parent | incremental | No date filter or `syncToken` on `application.listHistory`; the parent is read with its `updatedAt` state and 1-day lookback (`incremental_dependency`), so incremental syncs request history only for changed applications. A full sync is still ~23 hours for ~108,100 applications at ~1.31 req/s. |
| application_criteria_evaluations | medium | substream of applications | none | none | deferred_no_api_support | No date filter or `syncToken` on `application.listCriteriaEvaluations`. Partitioned only over applications in a `PreInterviewScreen` stage that are not `Archived` or `Hired`; PK `[application_id, id]`. |
| application_feedback | medium | top-level parent | none | created_at_and_sync_token | deferred_sync_token | `applicationFeedback.list` (added in Ashby API 2026-01-01). |
| approvals | medium | top-level parent | none | sync_token | deferred_sync_token | Not filtered by `entityType`, so offer, job, and opening approvals all sync. |
| archive_reasons | small | top-level parent | none | none | deferred_no_api_support | Config-style lookup; `includeArchived: true`. |
| candidate_tags | small | top-level parent | none | sync_token | deferred_sync_token | Config-style lookup; `includeArchived: true`. |
| candidates | large | top-level parent | none | created_at_and_sync_token | deferred_sync_token | High volume. |
| custom_fields | small | top-level parent | none | sync_token | deferred_sync_token | Config-style lookup; `includeArchived: true`. |
| departments | small | top-level parent | none | sync_token | deferred_sync_token | Config-style lookup; `includeArchived: true`. |
| feedback_form_definitions | small | top-level parent | none | sync_token | deferred_sync_token | Config-style lookup; `includeArchived: true`. |
| interview_plans | small | top-level parent | none | sync_token | deferred_sync_token | `includeArchived: true`; also the parent of `interview_stages`. |
| interview_schedules | medium | top-level parent | none | created_at_and_sync_token | deferred_sync_token | Sends `createdAfter` from `start_date`; mutable resource. |
| interview_stage_groups | small | top-level parent | none | none | deferred_no_api_support | Config-style lookup; no request parameters. |
| interview_stages | small | substream of interview_plans | none | none | deferred_no_api_support | `interviewStage.list` requires `interviewPlanId`; records carry `interviewPlanId` and `interview_plan_is_archived`. |
| interviewer_pools | small | top-level parent | none | sync_token | deferred_sync_token | `includeArchivedPools` and `includeArchivedTrainingStages` are `true`. |
| interviews | small | top-level parent | none | sync_token | deferred_sync_token | Interview definitions, not scheduled interviews; `includeArchived` and `includeNonSharedInterviews` are `true`. |
| job_boards | small | top-level parent | none | none | deferred_no_api_support | `jobBoard.list` returns only enabled boards and takes no request parameters. |
| job_postings | medium | top-level parent | none | none | deferred_no_api_support | No date filter or `syncToken`. |
| job_templates | small | top-level parent | none | sync_token | deferred_sync_token | Returns active and inactive templates. |
| jobs | medium | top-level parent | none | created_at_and_sync_token | deferred_sync_token | |
| locations | small | top-level parent | none | sync_token | deferred_sync_token | Config-style lookup; `includeArchived: true`. |
| offers | medium | top-level parent | none | created_at_and_sync_token | deferred_sync_token | |
| openings | medium | top-level parent | none | created_at_and_sync_token | deferred_sync_token | |
| projects | small | top-level parent | none | created_at_and_sync_token | deferred_sync_token | Requires `projectsRead` or `candidatesRead`. |
| source_tracking_links | small | top-level parent | none | sync_token | deferred_sync_token | `includeDisabled: true`. Declared as an empty stream in acceptance tests because the sandbox has no links. |
| sources | small | top-level parent | none | none | deferred_no_api_support | Config-style lookup; `includeArchived: true`. |
| survey_form_definitions | small | top-level parent | none | sync_token | deferred_sync_token | Config-style lookup. |
| users | small | top-level parent | none | sync_token | deferred_sync_token | Ashby workspace users; `includeDeactivated: true`. Also the connection-check stream. |

### Future incremental stream candidates

- **`syncToken` available (20 streams):** every `deferred_sync_token` stream above. `syncToken` would be the complete cursor for these endpoints, and for `applications`, once the CDK sync-token cursor ships.
- **No API support (7 streams):** `application_criteria_evaluations`, `archive_reasons`, `interview_stage_groups`, `interview_stages`, `job_boards`, `job_postings`, `sources`. These stay full refresh unless Ashby adds a filter; `application_criteria_evaluations` could follow `application_history` and use `incremental_dependency` on the parent.

## Authentication, Rate Limits, and Sync Tokens

- **Authentication:** Ashby's public API authenticates only with API keys (HTTP Basic, key as username, blank password) and offers no OAuth flow — see the [Ashby authentication reference](https://developers.ashbyhq.com/reference/authentication).
- **Rate limits:** Ashby documents 1,000 requests per minute per API key ([source](https://docs.ashbyhq.com/how-do-i-generate-an-api-key)). `concurrency_level` reads up to two streams at a time (`default_concurrency: 2`), and `api_budget` throttles only the per-application partitioned endpoints (`application.listHistory` and `application.listCriteriaEvaluations`, 100 requests/minute each). All other streams rely on the shared error handler's backoff on HTTP 429 (`Retry-After` header first, then exponential).
- **Error envelope:** Ashby returns most errors as HTTP 200 responses with `success: false` and an `errorInfo` object; these are surfaced by the shared `definitions.error_handler`, which every requester references. `application_history` and `application_criteria_evaluations` override its `response_filters` with the shared `definitions.response_filters` entries plus an `application_not_found` IGNORE ahead of the generic FAIL, because a sibling `response_filters` key replaces the referenced list rather than extending it.
- **Sync tokens:** `syncToken`-based incremental sync is deferred until the CDK sync-token cursor ships (airbytehq/airbyte-internal-issues#17213, adoption tracked in airbytehq/airbyte-internal-issues#17372). `createdAfter` alone is not a viable cursor because these resources mutate after creation.
