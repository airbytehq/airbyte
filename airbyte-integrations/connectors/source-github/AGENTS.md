> NOTE: CLAUDE.md is a symlink to AGENTS.md; update AGENTS.md (not the symlink) when changing these instructions.

# Contributing to source-github

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Authentication: one shared authenticator, always

The connector is mid-migration: some streams come from `manifest.yaml`, the rest are Python
`HttpStream` classes. Both sides **must** use the same authenticator instance, because
`RateLimitedMultipleTokenAuthenticator` tracks each token's remaining REST/GraphQL quota in
local counters. Two instances over the same tokens each believe they own the full budget, so
the connector plans for twice the quota GitHub grants and overruns the rate limit.

`SourceGithub._get_authenticator()` gets that instance by asking the manifest's component
factory for `definitions.requester_base.authenticator`. This reads like it constructs a new
one but does not: `ModelToComponentFactory` caches these by resolved constructor arguments
specifically so every stream shares one set of counters. The cache key is value-based, so pass
the **transformed** config — a different `api_url`, token list or `max_waiting_time` produces a
different instance. `test_authenticator_instance_is_shared_with_manifest_streams` guards this;
do not add a second authenticator when migrating further streams.

Reactive token rotation is the CDK's job, not the connector's. Each `TokenQuota` pool in the
manifest declares `remaining_header`/`reset_header`/`limit_header`, so `HttpClient` feeds
every response back into the authenticator (`update_from_response`): a primary rate limit
arrives as `X-RateLimit-Remaining: 0`, the rejected token's pool goes to zero and the next
request rotates. `exhaustion_status_codes` is intentionally left empty — GitHub uses 403 for
secondary limits and missing scopes too, and listing it would park a token whose primary
quota is fine. Before sleeping on a rate limit, `HttpClient` also asks
`has_alternative_token` and retries in 0.1s on a spare token instead of waiting out the reset
window. Do not reintroduce connector-side rotation — a previous version poked the
authenticator's private `_tokens_iter`, which this replaced.

The authenticator's `max_wait_time` bounds only the manifest/authenticator path. Python
`HttpStream` streams carry their own `max_wait_time_seconds`, derived from
`max_waiting_time` (default 120 minutes), into `GithubStreamABCBackoffStrategy`. The strategy
returns a rate-limit-derived wait only when `is_rate_limited_response` detects a rate-limit
signal; other retryable statuses, such as 404, fall through to default backoff. Every GitHub
response carries `X-RateLimit-Reset`, so using that header alone would make plain 404s wait
until the reset window.

Not rotated, deliberately: a secondary rate limit, where the token's counters stay positive.
GitHub scopes secondary limits per account, so another token of the same account gets rejected
the same way; the reset wait is the correct response there.

## Organizations must be payload-confirmed, never taken from config text

`repositories` accepts wildcard entries (`owner/*`). The owner in such an entry is only a
*candidate* organization — GitHub has no way to tell an org from a personal account by name, so
`GET /orgs/{login}` 404s whenever the owner is a user. Two routers exist for this reason and are
not interchangeable:

- `organization_partition_router` derives orgs from the config string. Only the `repositories`
  stream may use it, because that stream has to *attempt* `orgs/{login}/repos` to discover
  whether the login is an organization at all.
- `organization_resolution_partition_router` derives orgs from response payloads —
  `owner/login` on the `orgs/{org}/repos` listing, `organization/login` on
  `repos/{owner}/{repo}`. Every org-scoped stream (`Organizations`, `Teams`, `Users`, and their
  substreams) must slice on this one, and `SourceGithub._resolve_repositories_and_organizations`
  enumerates it for the Python streams.

The asymmetric `parent_key`s are load-bearing, not an inconsistency to tidy: *list org repos*
returns `owner` but no `organization`, while *get a repository* returns both, so using
`owner/login` on the explicit-repo branch would hand user logins back to the org-scoped streams.

2.2.0 wired the org-scoped streams to the config-derived router, and every affected sync died on
the platform heartbeat (airbytehq/oncall#13422). When Step 3 migrates
`Organizations`/`Teams`/`Users` into the manifest, they must reference the resolution router.

## A swallowed error must close its resumable-full-refresh slice

`HttpStream._read_pages` closes an RFR slice only after the last page returns, so an error raised
mid-slice and then *swallowed* — logged and returned from, rather than re-raised — leaves the
partition's cursor state empty. `CursorBasedCheckpointReader._find_next_slice` reads empty as
"still in progress" and hands the same partition back, forever: no record, no STATE, and the
platform eventually kills the attempt on the source heartbeat rather than the stream skipping in
milliseconds.

Any new `read_records` path that logs a warning and returns instead of raising must call
`GithubStreamABC._close_slice_after_swallowed_error(stream_slice)`. It no-ops for incremental
streams and for slices that carry no `partition` key — several substreams read their parent by
calling `read_records` directly with a bare mapping, and those parents are shared instances whose
STATE would otherwise gain a meaningless `{"partition": {}}` entry.

## Incremental Stream Considerations

The GitHub REST and GraphQL APIs support `since` parameter on many list endpoints and `updated` sorting. The connector is a Python CDK connector with stream classes extending `GithubStream`.

**Connector type:** Python CDK

**Analysis status:** Pure Python CDK connector. Full stream-by-stream analysis requires Python code review.

### Future incremental stream candidates

- **All streams deferred for Python code review:** This connector defines its streams in Python code rather than declarative manifest YAML. A full stream-by-stream incremental analysis table (per the standard CONTRIBUTING.md schema) should be added by a future agent after reviewing the Python stream definitions, their `cursor_field` properties, and the API endpoints they call.
