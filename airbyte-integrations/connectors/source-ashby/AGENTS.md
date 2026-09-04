> NOTE: CLAUDE.md is a symlink to AGENTS.md; update AGENTS.md (not the symlink) when changing these instructions.

# Contributing to source-ashby

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## `interviews` Returns Interview Definitions, Not Scheduled Interviews

`/interview.list` returns the reusable interview *templates* configured on a job — its `Interview` component declares exactly twelve properties: `id`, `title`, `externalTitle`, `type`, `isArchived`, `isDebrief`, `isFeedbackRequired`, `isFeedbackRequested`, `instructionsHtml`, `instructionsPlain`, `jobId`, `feedbackFormDefinitionId`. Nothing about a *scheduled* interview (`applicationId`, `interviewStageId`, `status`, `startTime`, `endTime`, `meetingLink`, `feedbackLink`, `interviewerUserIds`, `createdAt`, `updatedAt`, `cancelledAt`, `interviewScheduleId`) comes back from it. Those fields were declared on the stream anyway and emitted as null on every record; 2.0.0 removed them ([oncall#13405](https://github.com/airbytehq/oncall/issues/13405), after [#85183](https://github.com/airbytehq/airbyte/pull/85183) declared the real fields but kept the null ones to stay non-breaking).

Scheduling data lives in `interview_schedules`: `applicationId`, `interviewStageId`, `status`, `createdAt`, and `updatedAt` are top-level, and `startTime`, `endTime`, `feedbackLink`, `interviewerUserIds`, `meetingLink`, and `interviewScheduleId` are on the objects in its `interviewEvents` array. Cancellation is represented by the schedule's `status`, not by a `cancelledAt` timestamp.

**Why this matters:** a request for interview scheduling data must be answered from `interview_schedules`, not by adding fields to `interviews`. Ashby returns 200 with the fields simply absent, so a wrongly declared property looks like a healthy always-null column rather than an error. `unit_tests/test_interviews_schema.py` pins the `interviews` schema to the twelve real properties in both directions.

## Incremental Stream Considerations

The Ashby API uses `.list` endpoints with cursor-based pagination. The `applications` and `interview_schedules` endpoints support `createdAfter` filtering, but since these resources are mutable (status changes, updates), `created_at`-only filtering is insufficient for true incremental sync. The Ashby API may support `updatedAfter` on some endpoints — this needs live API verification. All other `.list` endpoints (candidates, jobs, offers, etc.) do not document date-based filtering.

| Stream | Volume Tier | Relationship | Cursor Field | API Incremental Support | Current Status | Notes |
|---|---|---|---|---|---|---|
| applications | large | top-level parent | none | created_at_only | deferred_no_api_support | Has `createdAfter` in body; mutable resource (status changes). Verify if `updatedAfter` is supported. |
| application_history | large | substream of applications | none | none | full_refresh_only | No date filter or `syncToken`; one request per application; ~23 hours for ~108,100 applications at ~1.31 req/s. |
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
