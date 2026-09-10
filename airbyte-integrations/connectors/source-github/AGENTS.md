> NOTE: CLAUDE.md is a symlink to AGENTS.md; update AGENTS.md (not the symlink) when changing these instructions.

# Contributing to source-github

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Migration to manifest-only (in progress)

This connector is being migrated from Python stream classes to a declarative manifest, one
group of streams at a time (tracking issue: airbytehq/airbyte-internal-issues#16492). It is
therefore a **hybrid** connector right now, and a change usually has to be made in exactly
one of the two halves:

- `source_github/manifest.yaml` — the migrated streams. Currently: `repositories`,
  `assignees`, `branches`, `collaborators`, `issue_labels`, `tags`, `organizations`, `teams`,
  `users`. Their schemas are inline (`InlineSchemaLoader`); there is no file under
  `source_github/schemas/` for them.
- `source_github/streams.py` — everything not yet migrated. These still extend
  `GithubStream`/`GithubStreamABC` and read their schema from `source_github/schemas/`.

Things worth knowing before touching either half:

- `SourceGithub.streams()` returns **only** the Python streams. `read()` and `discover()`
  merge them with the manifest streams, so migrating a stream means deleting it from
  `streams.py`, dropping it from the `streams()` list, and adding it to `manifest.yaml`.
- A few Python classes are _technical_ streams that are deliberately not in the catalog:
  `RepositoryStats`, `Branches` (how `Commits` discovers branches) and `Teams` (parent of
  `TeamMembers`, itself the parent of `TeamMemberships`). Do not delete `Branches` or `Teams`
  even though the user-facing `branches` and `teams` streams are declarative now. Neither has a
  file under `source_github/schemas/` any more, so both override `get_json_schema()` — returning
  only the fields their children actually read, rather than a second copy of the inline schema
  that could drift from it. A technical stream you keep behind after a migration needs the same
  treatment, and `Teams` additionally keeps `use_cache = True` so its parent read shares
  `teams.sqlite` with the declarative stream instead of paying for the listing twice.
- Repository/organization resolution lives in the manifest (`repositories_resolver` and
  `repository_stats`, unioned by `repository_partition_router` /
  `organization_resolution_partition_router`). The Python streams get their lists by enumerating
  those same routers, so both halves slice identically — which is only true as long as a
  migrated stream references the same router `SourceGithub` enumerates for its Python
  counterpart. See the organization-router section below; the two org routers are not
  interchangeable.
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
- Three known differences from the Python error contract apply to **every** stream migrated
  from here on. All are spelled out in the error-handling comment block in `manifest.yaml`; do
  not re-litigate them per stream.
  - **502/504 after retries fails the stream** instead of skipping the repository and finishing
    COMPLETE, because `DefaultErrorHandler` has no "retry N times, then ignore".
  - **404 and 409 are skipped on the first response.** Legacy mapped both to RETRY
    (`GITHUB_DEFAULT_ERROR_MAPPING`) and only skipped once the retries were spent, so a
    transient 404 recovered where a migrated stream now drops that repository from a COMPLETE
    sync. Same CDK limitation as above; accepted, not fixed.
  - **Skips are logged at INFO, and cannot name the repository.** Legacy logged
    `Skipping <stream> for repository <repo>` at WARNING. `stream_partition` is not reachable
    from `error_message` — referencing it raises rather than rendering blank. The stream name is
    reachable via `{{ parameters.… }}`, but only with a `$parameters` entry on each stream and a
    per-stream copy of every skip filter, since a `$ref`d filter sees `parameters == {}`; not
    worth losing the shared definitions for. The CDK follow-up (slice access in
    `HttpResponseFilter`) fixes both halves.
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
  `repos/{owner}/{repo}`. Every org-scoped stream must slice on this one: the declarative
  `organizations`/`teams`/`users` via `organization_scoped_retriever`, and the Python `Teams`
  and its substreams via `SourceGithub._resolve_repositories_and_organizations`, which
  enumerates it. Its wildcard branch reads its parents through `repositories_resolver`, whose
  `record_filter` is `wildcard_repository_filter`, so an organization whose wildcard matched no
  repository is not a partition either — that is why the declarative streams need no equivalent
  of the `repository_owners` filter `SourceGithub` applies by hand.

The asymmetric `parent_key`s are load-bearing, not an inconsistency to tidy: *list org repos*
returns `owner` but no `organization`, while *get a repository* returns both, so using
`owner/login` on the explicit-repo branch would hand user logins back to the org-scoped streams.

2.2.0 wired the org-scoped streams to the config-derived router, and every affected sync died on
the platform heartbeat (airbytehq/oncall#13422). Step 4 moved `organizations`/`teams`/`users` into
the manifest and they reference the resolution router;
`test_only_payload_confirmed_organizations_are_sliced` pins that, and reverting the `$ref` fails
it for all three. Any org-scoped stream migrated from here on needs the same `$ref`.

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

## Workflow run attempts: three traps, all silent

`workflow_run_attempts` is the first manifest stream whose parent carries state
(`incremental_dependency`, which appears nowhere else in the manifest), and so the first whose
incremental behaviour is decided by a stream other than itself. Parent/child wiring on its own is
not new — `repositories` slices on `organization_partition_router`, whose parent is the internal
`repository_stats` stream — and the difference between that router and
`organization_resolution_partition_router` is what broke 2.2.0, so read the manifest comment above
them before adding another one.

Each trap below cost a review round. They are enforced by
`unit_tests/test_workflow_run_attempts.py`; if a test there starts failing, read this before
"fixing" it.

**Never filter the child on the attempt's own cursor.** `GET /actions/runs` returns one record per
run — the latest attempt — so earlier attempts are only reachable through the per-attempt endpoint.
A sync landing between the first attempt finishing and the re-run starting leaves the cursor above
attempt 1's `updated_at`. If the child filters on its own records, attempt 1 is dropped and no later
sync revisits it, because the run's cursor has already moved past. Gating belongs on the parent run;
the child's cursor exists only so `incremental_dependency` persists parent state.

**Never put a filter parameter on the run listing.** GitHub caps `GET /actions/runs` at 1000 results
whenever `actor`, `branch`, `check_suite_id`, `created`, `event`, `head_sha` or `status` is present,
and it truncates invisibly: measured on a 23352-run repository, `created=>=1970-01-01` served pages
1-10 with `total_count: 23352` and then answered page 11 with an empty array, `total_count: 0` and no
`rel="next"`. The unfiltered listing returned 100 records on page 20 of the same repository. The
32-day re-run window is applied as a paginator `stop_condition` for this reason.

**A JSON-Schema `$ref` to a file does not work inside a manifest.** The manifest reference resolver
claims every `$ref` key, and for a non-`#/` target it returns the raw string and discards the sibling
keys — so a property copied from `schemas/*.json` as `{$ref: user.json, description: ...}` collapses
to the literal string `"user.json"` and the published schema stops being valid JSON Schema. Shared
sub-schemas belong in `definitions` and are referenced with `#/definitions/...`.

### Where the declarative run listing diverges from WorkflowRuns

`workflow_runs_for_attempts` is an internal parent reading the same endpoint as the Python
`WorkflowRuns`, and mirrors its incremental contract, but four behaviours could not be reproduced
exactly with declarative components:

- **The 32-day pagination break is anchored on `start_date`, not on the cursor**, because a
  `stop_condition` cannot see the cursor. An incremental sync therefore pages back to
  `start_date - 32 days` rather than `cursor - 32 days` — more pages than legacy spent
  incrementally, and exactly what legacy spent on its first sync, or on every sync of a config
  with no `start_date`.
- **The run listing is read a second time when `workflow_runs` is also selected.** A manifest
  stream and a Python stream cannot share a read; `use_cache` does not help, as the two build
  separate cache backends.
- **The cursor boundary is inclusive.** `ConcurrentCursor.should_be_synced` is
  `start <= value <= end` where `SemiIncrementalMixin` used a strict `>`, so the newest run of each
  repository is re-read once per sync. Deduplicating destinations absorb it.
- **A repository added after the first sync starts from the global cursor, not from
  `start_date`.** `ConcurrentPerPartitionCursor` seeds an unknown partition from the global cursor
  — its own docstring: "The history data added after the initial sync will be missing" — where
  legacy backfilled it. The `repositories` stream carries the same caveat for the same reason.

Two more things that bite when reading that stream's manifest. A paginator `stop_condition` is
evaluated with `config`, `response`, `headers`, `last_record` and `last_page_size` only — never the
cursor or the slice — and `last_record` is assigned *after* the record selector has run, so on a
client-side-incremental stream it is empty on exactly the pages a break needs to fire on. And
`JinjaInterpolation._eval` swallows a `TypeError` and returns the raw template, which
`InterpolatedBoolean` reads as **true**: an expression in a stop condition that can raise is an
expression that silently ends pagination.

## Incremental Stream Considerations

The GitHub REST and GraphQL APIs support `since` parameter on many list endpoints and `updated` sorting.

**Connector type:** hybrid — declarative manifest plus Python CDK stream classes

**Analysis status:** Full stream-by-stream analysis requires Python code review of the streams still in `streams.py`.

### Future incremental stream candidates

- **Streams still in `streams.py` deferred for Python code review:** a full stream-by-stream incremental analysis table (per the standard CONTRIBUTING.md schema) should be added by a future agent after reviewing the remaining Python stream definitions, their `cursor_field` properties, and the API endpoints they call.
- **The five streams migrated in Step 3** (`assignees`, `branches`, `collaborators`, `issue_labels`, `tags`) have no usable cursor: none of their endpoints returns an `updated_at`/`created_at` field or accepts `since`, so they stay full refresh.
