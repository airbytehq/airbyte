> NOTE: CLAUDE.md is a symlink to AGENTS.md; update AGENTS.md (not the symlink) when changing these instructions.

# Contributing to source-gong

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Incremental Stream Considerations

The Gong API exposes incremental filtering via `fromDateTime` on the calls and scorecards endpoints. The `users` endpoint does not support date-based filtering. Child streams (e.g. `answered_scorecards`) are partitioned via `SubstreamPartitionRouter`.

| Stream | Volume Tier | Relationship | Cursor Field | API Incremental Support | Current Status | Notes |
|---|---|---|---|---|---|---|
| answeredScorecards | medium | top-level parent | reviewTime | reviewTime | incremental |  |
| calls | medium | top-level parent | started | started | incremental |  |
| extensiveCalls | medium | top-level parent | startdatetime | startdatetime | incremental |  |
| scorecards | small | top-level parent | none | none | deferred_no_api_support | No date filter on list endpoint; config-style lookup |
| users | small | top-level parent | none | none | deferred_no_api_support | No date filter on list endpoint |
| callTranscripts | medium | child | started | started | incremental |  |

### Future incremental stream candidates

- **No API date filter (2 streams):** `scorecards`, `users` — these streams do not have a documented date-based filter on their list endpoints. A future agent should verify via live API probing whether undocumented filter parameters are accepted.

## Error handling

All requesters share the same response mappings, defined in `manifest.yaml` (`definitions.auth_error_filter`, `definitions.transient_error_filter`) and appended to each stream's error handler:

| Response | Action | Failure type | Rationale |
|---|---|---|---|
| 404 with "… found corresponding to the provided filters" | IGNORE (empty stream) | — | Gong signals an empty result set as a 404 with this message; only that 404 is treated as empty. Warning: a key whose user lacks call visibility gets a byte-identical 404, so a misconfigured key looks like an empty source; this is indistinguishable server-side. |
| Any other 404 | FAIL (terminal) | `system_error` | CDK default mapping ("Not found. The requested resource was not found on the server."). Catches bad paths and removed resources instead of silently emptying the stream. |
| 401, 403 | FAIL | `config_error` | Invalid, expired, or scope-limited credentials. Surfaced with an actionable message instead of a raw exception. |
| 429, 500, 502, 503, 504 | RETRY | `transient_error` | Backoff honors the `Retry-After` header (`WaitTimeFromHeader`). Retry-After can reach hours when the 10,000 requests/day quota is exhausted, which is why `maxSecondsBetweenMessages` is 86400. |
| Any other error response | FAIL (terminal) | `system_error` | CDK `DefaultErrorHandler` fallback. An explicit catch-all FAIL filter is deliberately omitted: `HttpResponseFilter` predicates are evaluated against every response, including HTTP 200s, so a match-anything rule would fail successful requests. |

## Competitor parity (Fivetran Gong schema)

The stream inventory is deliberately unchanged at 6 streams. Everything Fivetran normalizes into child tables ships here as nested fields, mostly on `extensiveCalls`:

| Fivetran table | Verdict | Our stream / field |
|---|---|---|
| CALL | covered | `calls`, `extensiveCalls` |
| USER | covered | `users` |
| SCORECARD | covered | `scorecards` |
| SCORECARD_QUESTION | covered-as-field | `scorecards.questions[]` |
| ANSWERED_SCORECARD | covered | `answeredScorecards` |
| ANSWERED_SCORECARD_ANSWER | covered-as-field | `answeredScorecards.answers[]` |
| CALL_TRANSCRIPT | covered | `callTranscripts.transcript[]` |
| CALL_PARTICIPANT | covered-as-field | `extensiveCalls.parties[]` |
| CALL_TRACKER / TRACKER | covered-as-field | `extensiveCalls.content.trackers[]` |
| CALL_TOPIC | covered-as-field | `extensiveCalls.content.topics[]` |
| CALL_OUTLINE / CALL_OUTLINE_ITEM | covered-as-field | `extensiveCalls.content.outline[]` / `.items[]` |
| CALL_HIGHLIGHT / CALL_HIGHLIGHT_ITEM | covered-as-field | `extensiveCalls.content.highlights[]` / `.items[]` |
| CALL_KEY_POINT | covered-as-field | `extensiveCalls.content.keyPoints[]` |
| CALL_VIDEO | covered-as-field | `extensiveCalls.interaction.video[]`, `media.videoUrl` / `audioUrl` |
| CALL_STRUCTURE | covered-as-field | `extensiveCalls.content.outline[].section` |
| CALL_CONTEXT_* | covered-as-field | `extensiveCalls.context[].objects[].fields[]` |
| Interaction stats / talk-time | covered-as-field | `extensiveCalls.interaction.speakers[]`, `interactionStats[]`, `questions` |

Five Fivetran tables are intentionally not replicated. Justifications:

| Fivetran table | Justification |
|---|---|
| TRACKER_LANGUAGE | Tracker *occurrences* ship on `extensiveCalls.content.trackers[]`; per-tracker language configuration is workspace settings metadata, not sales-activity data. Candidate future stream (`/v2/settings/trackers`) if requested. |
| LANGUAGE_KEYWORDS | Keyword/language configuration metadata, same category as above — settings, not activity data. |
| ENGAGE_FLOW | Gong Engage is a separate product with its own API surface; out of scope for this connector. |
| ENTITY_VALUE / *_ENTITY_SCHEMA | CRM-entity schema metadata describing Gong's CRM integration config; the CRM-context *values* per call ship on `extensiveCalls.context[]`. |
| PERMISSION_* | Permission-profile admin configuration; not sales-activity data, and results would vary with the API key user's own visibility. |
