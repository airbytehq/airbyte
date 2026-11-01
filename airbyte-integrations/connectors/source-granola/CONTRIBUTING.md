# Contributing to source-granola

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Authentication

The Granola public API supports bearer API-key authentication only, so `manifest.yaml` uses a `BearerAuthenticator` with the user-supplied `api_key` (marked `airbyte_secret: true`). OAuth is not implemented because Granola exposes no OAuth application model for this API — there is no app registration, authorization endpoint, or client-credentials flow to build against.

Vendor evidence, re-verified 2026-08-12:

- Granola's published OpenAPI document ([`openapi.json`](https://docs.granola.ai/api-reference/openapi.json)) declares exactly one security scheme, `ApiKeyAuth` (`type: http`, `scheme: bearer`, `bearerFormat: apiKey`), and every operation on every path references only that scheme.
- The [Granola API help-center page](https://docs.granola.ai/help-center/sharing/integrations/granola-api) documents personal and workspace API keys created from the desktop app (Settings → Connectors → API keys) as the only way to get programmatic access, and contrasts it with MCP: "The Granola API gives you an API key for scripts, automations, and custom integrations. MCP uses browser-based OAuth and is designed for conversational AI tools like Claude and ChatGPT."
- Granola's only OAuth surface is its hosted [MCP server](https://docs.granola.ai/help-center/sharing/integrations/mcp) (`https://mcp.granola.ai/mcp`), which authenticates each end user through an interactive browser OAuth 2.0 flow with Dynamic Client Registration and states "There is no API key or service account access method for MCP." A per-user browser flow against a conversational tool endpoint is out of scope for a replication source, so it is not an alternative for this connector.

Revisit this if Granola publishes an OAuth application model for the public API.

## HTTP error handling

`base_error_handler` maps shared HTTP failures, and every stream's error handler lists the same shared filters by `$ref` plus its stream-specific one. A local `response_filters` list next to `$ref` replaces the referenced list wholesale (`evaluated_ref | evaluated_dict`), so putting the shared filters only on `base_error_handler` would silently drop them from `detailed_notes` and `note_transcripts`, which each define their own list.

- `401` and `403` → `FAIL` with `failure_type: config_error`, with separate messages: `401` means Granola rejected the key, `403` means the key lacks access.
- `429` → `RATE_LIMITED`; backoff honors `Retry-After` up to 60 seconds, then exponential backoff with factor 5, `max_retries: 5`.
- `500`/`502`/`503`/`504` → `RETRY`, failing as `transient_error` once retries run out. The CDK applies an `HttpResponseFilter`'s `failure_type` only when the action is `FAIL`. For `RETRY` it uses its default mapping (`HttpResponseFilter.matches` in `airbyte_cdk/sources/declarative/requesters/error_handlers/http_response_filter.py`), which covers only these four codes. Any other 5xx, such as `501` or `507`, still retries but fails as `system_error`, and adding it to the filter would not change that.
- `413` on `detailed_notes` and `404` on `note_transcripts` → `IGNORE` (see Oversized Transcripts).

## Deletions

The Granola API has no way to return deleted notes on the stream that lists them. `GET /v1/notes` has no parameter for deleted or trashed notes, note records carry no deletion field, and no webhook event fires on deletion (checked against the [OpenAPI spec](https://docs.granola.ai/api-reference/openapi.json) on 2026-09-25). Deletions only appear as `document.hard_deleted` events on the Enterprise-only `GET /v1/audit` endpoint, which needs a separate Audit API key that a workspace admin creates. The connector doesn't read `/v1/audit`: deletions belong on the stream that returns the records, not on a separate stream. If Granola adds an option to include deleted notes in `GET /v1/notes`, set it on the `notes` request.

## Oversized Transcripts

`GET /v1/notes/{note_id}?include=transcript` answers `413` with `code: TRANSCRIPT_TOO_LARGE` when a transcript exceeds the size Granola returns inline. `detailed_notes` maps 413 to `IGNORE` so the note is skipped instead of retried and failed. The CDK emits the filter's `error_message` at INFO, not WARN (`HttpClient._handle_error_resolution` in `airbyte_cdk/sources/streams/http/http_client.py`), so the skip is invisible to log filters set above INFO, and the whole note record is dropped from `detailed_notes` — not just its transcript. The `note_transcripts` stream replicates those transcripts from the paged `GET /v1/notes/{note_id}/transcript` endpoint (`page_size` max 100, `cursor`/`hasMore` pagination), and maps that endpoint's documented 404 to `IGNORE` so a note deleted or unshared mid-sync does not fail the stream. `note_transcripts` emits one record per transcript segment with the parent `note_id` added by an `AddFields` transformation, and has no primary key because segments carry no stable identifier.

## Incremental Stream Considerations

The Granola API connector has 3 streams: `notes` (incremental with `updated_at` cursor), `detailed_notes` and `note_transcripts` (children of notes via `SubstreamPartitionRouter`). No FR parent streams remain.

| Stream | Volume Tier | Relationship | Cursor Field | API Incremental Support | Current Status | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| notes | medium | top-level parent | updated_at | updated_at | incremental | |
| detailed_notes | medium | child | none | none | deferred_child | |
| note_transcripts | medium | child | none | none | deferred_child | |

The `notes` cursor is `updated_at` with a single slice: the API exposes `updated_after` but no `updated_before`, so there is no `step` or end bound. A note edited after a sync is re-emitted on the next incremental sync. The child streams have no `incremental_dependency`, so the parent is fully re-read from `start_date` on every sync; they already picked up edited notes before 1.0.0. The bound stays second-granular (`%Y-%m-%dT%H:%M:%SZ`) because Granola has treated date-only bounds as excluding the named day, and `cursor_datetime_formats` retains `%Y-%m-%d` so date-only state from earlier versions still parses. `lookback_window: PT1S` re-requests the stored cursor's second, because `updated_after` is exclusive and a whole-second value excludes that entire second.

### Future incremental stream candidates

- **Child streams (2 streams):** `detailed_notes`, `note_transcripts` — partitioned via `SubstreamPartitionRouter`. A follow-up session should evaluate incremental support.
