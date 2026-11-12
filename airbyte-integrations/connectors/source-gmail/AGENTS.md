> NOTE: CLAUDE.md is a symlink to AGENTS.md; update AGENTS.md (not the symlink) when changing these instructions.

# Contributing to source-gmail

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Incremental Stream Considerations

The Gmail API uses a query-based filtering system (`q` parameter) that supports date ranges via `after:` and `before:` operators. However, these filter by internal date (similar to created_at), not by modification time. Messages and threads are mutable (labels change, read status), making `created_at`-style filtering insufficient. The `profile`, `drafts`, and `labels` streams are small config-style endpoints.

| Stream | Volume Tier | Relationship | Cursor Field | API Incremental Support | Current Status | Notes |
|---|---|---|---|---|---|---|
| drafts | small | top-level parent | none | none | deferred_no_api_support | No date filter; relatively small set per user |
| labels | small | top-level parent | none | none | deferred_no_api_support | Config-style lookup, typically <100 labels |
| messages | xlarge | top-level parent | none | created_at_only | deferred_no_api_support | Gmail q parameter supports after:/before: but filters by internalDate (received), not modification time |
| profile | small | top-level parent | none | none | deferred_no_api_support | Singleton user profile endpoint |
| threads | xlarge | top-level parent | none | created_at_only | deferred_no_api_support | Same limitation as messages — q parameter filters by date received |
| labels_details | medium | child | none | none | deferred_child |  |
| messages_details | medium | child | internalDate (ms) | created_at_only | incremental_lookback | Private `messages_for_details` parent uses 30-day slices with a one-hour lookback |
| threads_details | medium | child | none | none | deferred_child |  |

`messages_details` uses an internal `messages_for_details` parent, which is not exposed as a top-level stream. The parent cursor stores each 30-day slice's `_listed_until` in Unix seconds and bounds Gmail's list request to the previous sync end minus one hour; the child `internalDate` cursor is stored in milliseconds using `%ms`. Gmail's `after:` filter is based on receipt date, not modification time, so label or read-state changes on older messages require a full refresh.

### Future incremental stream candidates

- **No API date filter (5 streams):** `drafts`, `labels`, `messages`, `profile`, `threads` — these streams do not have a documented date-based filter on their list endpoints. A future agent should verify via live API probing whether undocumented filter parameters are accepted.
- **Child streams (2 streams):** `labels_details`, `threads_details` — partitioned via `SubstreamPartitionRouter`. A follow-up session should evaluate whether these can be made incremental independently or via `incremental_dependency`.

## Rate-limit backoff

Gmail quota responses sometimes include the required wait only in the body as a `Retry after` timestamp, without a `Retry-After` header. The connector honors the header first, then the body timestamp, read by the CDK's `WaitTimeFromResponse` strategy, and falls back to exponential backoff when neither is present. Body waits are capped at 1,800 seconds, below `maxSecondsBetweenMessages: 3600`, leaving headroom under the connector's maximum inter-message interval.

## API budget

The `api_budget` paces requests to Gmail's per-user quota, not the per-project one, because the project quota is shared with every other user of the OAuth client. Both the limit and the `get` weights depend on `credentials.auth_type`. OAuth (`Client`, and legacy top-level configs) uses the quota of Airbyte Cloud's OAuth app, whose project kept the pre-May-2026 quota (confirmed in its Google Cloud console): 15,000 units per user per minute, `messages.get` 5, `threads.get` 10. Self-managed OAuth clients on newer projects are not modelled and fall back to Gmail's rate-limit backoff. `Service` gets the newer quota, since a service account belongs to the customer's own project: 6,000 units, and because the connector sends no `format` param (Gmail defaults to `full`), `messages.get` costs 60 and `threads.get` 120. Adding a `format` param changes these costs.
