> NOTE: CLAUDE.md is a symlink to AGENTS.md; update AGENTS.md (not the symlink) when changing these instructions.

# Contributing to source-github

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Migration to manifest-only (in progress)

This connector is being migrated from Python stream classes to a declarative manifest, one
group of streams at a time (tracking issue: airbytehq/airbyte-internal-issues#16492). It is
therefore a **hybrid** connector right now, and a change usually has to be made in exactly
one of the two halves:

- `source_github/manifest.yaml` — the migrated streams. Currently: `repositories`,
  `assignees`, `branches`, `collaborators`, `issue_labels`, `tags`. Their schemas are inline
  (`InlineSchemaLoader`); there is no file under `source_github/schemas/` for them.
- `source_github/streams.py` — everything not yet migrated. These still extend
  `GithubStream`/`GithubStreamABC` and read their schema from `source_github/schemas/`.

Things worth knowing before touching either half:

- `SourceGithub.streams()` returns **only** the Python streams. `read()` and `discover()`
  merge them with the manifest streams, so migrating a stream means deleting it from
  `streams.py`, dropping it from the `streams()` list, and adding it to `manifest.yaml`.
- A few Python classes are _technical_ streams that are deliberately not in the catalog:
  `RepositoryStats` and `Branches` (the latter is how `Commits` discovers branches). Do not
  delete `Branches` even though the user-facing `branches` stream is declarative now. It has no
  file under `source_github/schemas/` any more, so it overrides `get_json_schema()`; a technical
  stream you keep behind after a migration needs the same treatment.
- Repository/organization resolution lives in the manifest (`repositories_resolver` and
  `repository_stats`, unioned by `repository_partition_router` /
  `organization_partition_router`). The Python streams get their repo list by enumerating
  those same routers, so both halves always slice identically.
- Error contract differs per stream group and is expressed by two composed error handlers in
  the manifest: `strict_access_error_handler` (403 fails — repo listing and resolution, which
  is what makes `check` surface bad token scopes) and `skip_inaccessible_error_handler`
  (403/404/409 skip the repository — the repo-scoped child streams). Both fail an unexpected 410,
  mirroring `GITHUB_DEFAULT_ERROR_MAPPING`. When migrating a stream, pick the handler that
  matches what `GithubStreamABC.read_records` did for it, and remember that 410 is absent from
  the CDK default mapping — an endpoint GitHub answers 410 on needs a filter or it burns five
  retries behind the 60s backoff floor before failing.
- The 410 disabled-feature skip (`disabled_feature_skip_filter`, mirroring
  `errors_handlers.py::is_gone_with_feature_disabled`) lives on
  `skip_inaccessible_error_handler` only, and its predicate must name the feature:
  `(issues|projects|discussions) (are|is) disabled`. A declarative predicate cannot see the
  status code, so legacy's bare "is disabled"/"are disabled" match would also swallow a 401
  "Your account is disabled" and silently drop the repository from a sync that still reports
  COMPLETE. Migrating a stream whose GitHub feature can be disabled per repository means adding
  that word to the pattern; forget it and you get a loud failure from `gone_fail_filter`, not a
  silent skip. Escape the word boundaries as `\\b` — Jinja parses its own string literals, so a
  single `\b` reaches `re` as a backspace and the filter stops matching without erroring.
- Two known differences from the Python error contract apply to **every** stream migrated from
  here on. Both are spelled out in the error-handling comment block in `manifest.yaml`; do not
  re-litigate them per stream.
  - **502/504 after retries fails the stream** instead of skipping the repository and finishing
    COMPLETE, because `DefaultErrorHandler` has no "retry N times, then ignore".
  - **Skips are logged at INFO without slice context.** `HttpResponseFilter.error_message` can
    only interpolate `response`/`headers`, so a migrated stream cannot say _which_ repository it
    skipped. Legacy logged `Skipping <stream> for repository <repo>` at WARNING.
- When migrating a stream, check `unit_tests/integration/test_<stream>.py` for tests that assert
  `SubstreamResumableFullRefreshCursor` state (`__ab_full_refresh_sync_complete`): declarative
  full-refresh streams emit a single terminal state message instead. `test_assignees.py` also
  turned out to define the same test name twice, so only the second body ran — worth grepping
  for that in the other `integration/test_*.py` files before trusting their coverage.

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

## Incremental Stream Considerations

The GitHub REST and GraphQL APIs support `since` parameter on many list endpoints and `updated` sorting.

**Connector type:** hybrid — declarative manifest plus Python CDK stream classes

**Analysis status:** Full stream-by-stream analysis requires Python code review of the streams still in `streams.py`.

### Future incremental stream candidates

- **Streams still in `streams.py` deferred for Python code review:** a full stream-by-stream incremental analysis table (per the standard CONTRIBUTING.md schema) should be added by a future agent after reviewing the remaining Python stream definitions, their `cursor_field` properties, and the API endpoints they call.
- **The five streams migrated in Step 3** (`assignees`, `branches`, `collaborators`, `issue_labels`, `tags`) have no usable cursor: none of their endpoints returns an `updated_at`/`created_at` field or accepts `since`, so they stay full refresh.
