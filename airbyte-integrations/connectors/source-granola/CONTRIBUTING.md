# Contributing to source-granola

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Authentication

The Granola public API supports bearer API-key authentication only, so `manifest.yaml` uses a `BearerAuthenticator` with the user-supplied `api_key` (marked `airbyte_secret: true`). OAuth is not implemented because Granola exposes no OAuth application model for this API — there is no app registration, authorization endpoint, or client-credentials flow to build against.

Vendor evidence, re-verified 2026-08-12:

- Granola's published OpenAPI document ([`openapi.json`](https://docs.granola.ai/api-reference/openapi.json)) declares exactly one security scheme, `ApiKeyAuth` (`type: http`, `scheme: bearer`, `bearerFormat: apiKey`), and every operation on every path references only that scheme.
- The [Granola API help-center page](https://docs.granola.ai/help-center/sharing/integrations/granola-api) documents personal and workspace API keys created from the desktop app (Settings → Connectors → API keys) as the only way to get programmatic access, and contrasts it with MCP: "The Granola API gives you an API key for scripts, automations, and custom integrations. MCP uses browser-based OAuth and is designed for conversational AI tools like Claude and ChatGPT."
- Granola's only OAuth surface is its hosted [MCP server](https://docs.granola.ai/help-center/sharing/integrations/mcp) (`https://mcp.granola.ai/mcp`), which authenticates each end user through an interactive browser OAuth 2.0 flow with Dynamic Client Registration and states "There is no API key or service account access method for MCP." A per-user browser flow against a conversational tool endpoint is out of scope for a replication source, so it is not an alternative for this connector.

Revisit this if Granola publishes an OAuth application model for the public API.

## Oversized Transcripts

`GET /v1/notes/{note_id}?include=transcript` answers `413` with `code: TRANSCRIPT_TOO_LARGE` when a transcript exceeds the size Granola returns inline. `detailed_notes` maps 413 to `IGNORE` so the note is skipped instead of retried and failed. The CDK emits the filter's `error_message` at INFO, not WARN (`HttpClient._handle_error_resolution` in `airbyte_cdk/sources/streams/http/http_client.py`), so the skip is invisible to log filters set above INFO, and the whole note record is dropped from `detailed_notes` — not just its transcript. The `note_transcripts` stream replicates those transcripts from the paged `GET /v1/notes/{note_id}/transcript` endpoint (`page_size` max 100, `cursor`/`hasMore` pagination), and maps that endpoint's documented 404 to `IGNORE` so a note deleted or unshared mid-sync does not fail the stream. `note_transcripts` emits one record per transcript segment with the parent `note_id` added by an `AddFields` transformation, and has no primary key because segments carry no stable identifier.

## Incremental Stream Considerations

The Granola API connector has 3 streams: `notes` (incremental with `created_at` cursor), `detailed_notes` and `note_transcripts` (children of notes via `SubstreamPartitionRouter`). No FR parent streams remain.

| Stream | Volume Tier | Relationship | Cursor Field | API Incremental Support | Current Status | Notes |
|---|---|---|---|---|---|---|
| notes | medium | top-level parent | created_at | created_at | incremental |  |
| detailed_notes | medium | child | none | none | deferred_child |  |
| note_transcripts | medium | child | none | none | deferred_child |  |

The `notes` cursor slices on second-granular date-times (`%Y-%m-%dT%H:%M:%SZ` with `cursor_granularity: PT1S`) because the API's `created_before=<date>` excludes that whole day, which used to drop notes created on a slice boundary date. `cursor_datetime_formats` retains `%Y-%m-%d` so date-only state from earlier versions still parses.

### Future incremental stream candidates

- **Child streams (2 streams):** `detailed_notes`, `note_transcripts` — partitioned via `SubstreamPartitionRouter`. A follow-up session should evaluate incremental support.
