> NOTE: CLAUDE.md is a symlink to AGENTS.md; update AGENTS.md (not the symlink) when changing these instructions.

# Contributing to source-github

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Migration to manifest-only (in progress)

This connector is being migrated from Python stream classes to a declarative manifest, one
group of streams at a time (tracking issue: airbytehq/airbyte-internal-issues#16492). It is
therefore a **hybrid** connector right now, and a change usually has to be made in exactly
one of the two halves:

- `source_github/manifest.yaml` — every REST stream. Their schemas are inline
  (`InlineSchemaLoader`); there is no file under `source_github/schemas/` for them, with one
  exception: `issue_timeline_events` keeps `schemas/issue_timeline_events.json` behind a
  `JsonFileSchemaLoader`, because its shared `base_event` definition is referenced 23 times and
  inlines to almost 7,000 lines. When a schema being inlined carries a `$ref` to
  `schemas/shared/*.json`, expand it verbatim and drop any sibling keys (`description` next to a
  `$ref`) — jsonref, which the legacy loader used, replaced the whole node, so the discovered
  schema never had them. A `$ref` inside an inline schema is not resolved, and `#/definitions/...`
  would be swallowed by the manifest's own `$ref` resolver. The safe recipe is to dump
  `<PythonClass>().get_json_schema()` and compare before deleting the class.
- `source_github/streams.py` — the six GraphQL streams (`releases`, `pull_request_stats`, `reviews`,
  `projects_v2`, `issue_reactions`, `pull_request_comment_reactions`), left for Step 9. They still
  extend `GithubStream`/`GithubStreamABC` and read their schema from `source_github/schemas/`.

Things worth knowing before touching either half:

- `SourceGithub.streams()` returns **only** the Python streams. `read()` and `discover()`
  merge them with the manifest streams, so migrating a stream means deleting it from
  `streams.py`, dropping it from the `streams()` list, and adding it to `manifest.yaml`.
- No Python _technical_ stream is left. `Branches` and `RepositoryStats` went with Step 8: the
  manifest's `repository_partition_router` now carries the repository's `default_branch` as an
  `extra_fields` entry on every repository partition, and `repository_branches_resolver` (an
  internal stream, not in the catalog) lists branches for `commits`.
- Parent-child streams (Step 7) are `SubstreamPartitionRouter`s over the manifest parent
  definition (`$ref: "#/definitions/<parent>_stream"`). Parent fields the child needs in its path
  or record come through `extra_fields` on the `ParentStreamConfig` and are read as
  `stream_slice.extra_fields['<field>']`; the partition value itself is `stream_partition.<field>`.
  The parent is read with a fresh state manager (no `incremental_dependency`), i.e. from
  `start_date`, which is what the Python parents did. Set `use_cache: true` on a parent's
  requester so the parent read is served from the pages the parent stream itself fetched.
- The Python parent-child streams nested their state under the repository and each parent id
  (`{repo: {project_id: {column_id: {updated_at}}}}`). `LegacyToPerPartitionStateMigration` only
  handles one level, so those four streams use
  `components.NestedLegacyToPerPartitionStateMigration`, which rebuilds the exact partition the
  router emits (`{"column_id": 50, "parent_slice": {"project_id": 5, "parent_slice": {"repository": ...}}}`,
  ids as integers). `issue_timeline_events` collapses a page of events into one record with
  `components.IssueTimelineEventsExtractor`; nothing declarative groups records per page.
- Step 8 patterns worth knowing before touching those four streams:
  - `workflow_runs` cannot use `is_data_feed`: runs are listed by `created_at` while the cursor is
    `updated_at`, and a re-run of an old run appears deep in the list. Legacy stopped at the first
    run created more than 32 days before the cursor; `components.WorkflowRunsPaginationStrategy`
    does the same from the raw page, reading the slice start from the `X-Airbyte-Window-Start`
    request header (the paginator only sees records that survived the client-side filter, and
    GitHub ignores the header). Do not replace this with GitHub's `created` filter: it caps the
    result set at 1,000 runs, so a busy repository would silently lose runs. `lookback_window`
    would not do either: it moves the request window but `ConcurrentCursor.should_be_synced` still
    compares against the un-shifted start.
  - `workflow_jobs` is a substream of `workflow_runs` with `incremental_dependency: true` and
    `global_substream_cursor: true`: one `completed_at` cursor for the stream, and the parent
    resumes per repository from `parent_state`, which is what the Python class did by handing its
    cursor to the parent. `components.WorkflowJobsLegacyStateMigration` turns the legacy
    `{repo: {completed_at}}` into that shape; the parent's own legacy migration then converts
    `parent_state`. A record filter needs `is not none`, not a bare value: Jinja renders `None`
    as "None", which the CDK's boolean does not treat as false.
  - `contributor_activity` retries 202 with a 90s constant backoff. `WaitUntilTimeFromHeader` must
    not sit in front of it in `backoff_strategies`, because it answers `min_wait` whenever its
    header is absent and would turn every 202 into a 60s wait.
  - `commits` slices per branch through `components.CommitsBranchPartitionRouter`, a
    `SubstreamPartitionRouter` over `repository_branches_resolver` that keeps the configured
    branches that exist and falls back to the default branch otherwise, exactly like
    `Commits._validate_branches_to_pull`. The nested legacy state is migrated with
    `integer_ids: false` so a digit-only branch name stays a string.
- Tests that need a plain repo-scoped Python `HttpStream` — the `GithubStreamABC.read_records`
  error-path tests and the authenticator quota tests — use `unit_tests/utils.py::ProbeStream`.
  They used `Deployments` until Step 5 migrated it, the org-scoped tests used `Teams` until
  Step 7, and the error-handler tests used `RepositoryStats` until Step 8; every remaining Python
  stream is GraphQL. Do not move them onto another real stream that the next step will migrate
  again.
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
- Semi-incremental streams (endpoint takes no cursor parameter; legacy `SemiIncrementalMixin`)
  get exactly one of two `DatetimeBasedCursor` switches, and the migration issue's "sorted"
  column is not a reliable guide — check `is_sorted` on the legacy class:
  - `is_data_feed: true` only when the request is `sort=updated&direction=desc` and legacy had
    `is_sorted = "desc"`. The CDK then stops paginating at the first record older than the
    cursor. On an endpoint GitHub serves ascending (commit comments, stargazers) or without an
    ordering guarantee, this stops after the first page and silently loses every newer record.
  - `is_client_side_incremental: true` otherwise: every page is read and the record selector
    drops records outside the cursor window, which is what legacy did.
  - Never both. With `is_data_feed` the CDK logs a warning and ignores the other flag.
  - The CDK filter is inclusive (`start <= cursor <= now`) where legacy kept `cursor > start`,
    so the boundary record is re-emitted once per sync. Accepted on every migrated incremental
    stream; pin it in a test rather than trying to reproduce the strict comparison.
  - `%z` on the cursor formats if the endpoint stamps records with an offset instead of `Z`
    (only the Actions API does: `workflows`, and `workflow_runs`/`workflow_jobs` when they
    move). State is written with `strftime`, which keeps the record's offset and never converts
    to UTC, so a `...%SZ` output format stamps `Z` onto a local wall-clock time and the stored
    state is off by the offset. Use `datetime_format: "%Y-%m-%dT%H:%M:%S%z"` for those streams;
    `test_workflows_offset_timestamps_keep_their_instant_across_syncs` shows the failure mode.
  - Every one of them needs `state_migrations: [LegacyToPerPartitionStateMigration]`; the legacy
    `{repository: {cursor_field: value}}` state is not recognised without it and an upgraded
    connection would silently re-read from `start_date`.
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
- Incremental streams migrated from here on share two more differences from the Python contract,
  both spelled out on `server_side_since_cursor` in `manifest.yaml`:
  - **The boundary record is re-emitted.** `SemiIncrementalMixin.read_records` kept records
    strictly newer than the cursor (`cursor_value > start_point`); the CDK's client-side filter
    compares `start <= cursor <= end` (`ConcurrentCursor.should_be_synced`), so it cannot
    reproduce that and turning `is_client_side_incremental` on buys nothing. One unchanged
    record per partition per sync, deduped by the destination on the primary key.
  - **`is_sorted = "asc"` has no declarative equivalent.** Its only effect was
    `state_checkpoint_interval = page_size`, i.e. a STATE message per page. Concurrent
    declarative cursors checkpoint per partition, so an interrupted sync restarts the partition.
- Every migrated incremental stream needs `state_migrations: [LegacyToPerPartitionStateMigration]`.
  The Python state shape was `{<partition>: {<cursor_field>: <value>}}`, which the CDK does not
  recognise; without the migration an upgraded connection silently re-reads from `start_date`.
  It works with `UnionPartitionRouter` (it reads `partition_field` off the router directly), so
  `repository_partition_router` and `organization_partition_router` are both fine.
- When migrating a stream, check `unit_tests/integration/test_<stream>.py` for tests that assert
  `SubstreamResumableFullRefreshCursor` state (`__ab_full_refresh_sync_complete`): declarative
  full-refresh streams emit a single terminal state message instead. Those tests also construct
  `SourceGithub()` with no arguments and pass state only to `read()`; a declarative stream reads
  its state at construction, so they have to build `SourceGithub(config=..., catalog=...,
  state=...)` or the state is silently ignored (`test_events.py` shows the adapted form). `test_assignees.py` also
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

## Incremental Stream Considerations

The GitHub REST and GraphQL APIs support `since` parameter on many list endpoints and `updated` sorting.

**Connector type:** hybrid — declarative manifest plus Python CDK stream classes

**Analysis status:** Full stream-by-stream analysis requires Python code review of the streams still in `streams.py`.

### Future incremental stream candidates

- **Streams still in `streams.py` deferred for Python code review:** a full stream-by-stream incremental analysis table (per the standard CONTRIBUTING.md schema) should be added by a future agent after reviewing the remaining Python stream definitions, their `cursor_field` properties, and the API endpoints they call.
- **The five streams migrated in Step 3** (`assignees`, `branches`, `collaborators`, `issue_labels`, `tags`) have no usable cursor: none of their endpoints returns an `updated_at`/`created_at` field or accepts `since`, so they stay full refresh.
- **The nine streams migrated in Step 5** (`events`, `pull_requests`, `commit_comments`, `issue_milestones`, `stargazers`, `projects`, `issue_events`, `deployments`, `workflows`) have a cursor field but no server-side filter, so they are client-side incremental; `pull_requests` and `issue_milestones` additionally sort newest-first and use the data-feed stop condition. See the semi-incremental bullet above before adding another.
- **The three streams migrated in Step 6** (`comments`, `issues`, `review_comments`) are the connector's only REST streams that filter server-side: their endpoints accept `since` and the declarative `DatetimeBasedCursor` injects it via `start_time_option`. Any further stream whose endpoint accepts `since` belongs in that group rather than the client-side-filtered one.
- **The eight streams migrated in Step 7** (`pull_request_commits`, `project_columns`, `project_cards`, `team_members`, `team_memberships`, `issue_timeline_events`, `commit_comment_reactions`, `issue_comment_reactions`) are substreams. `project_columns`, `project_cards` and the two reaction streams are client-side incremental with a cursor per parent record; the other four have no cursor and stay full refresh.
- **The four streams migrated in Step 8** (`commits`, `contributor_activity`, `workflow_runs`, `workflow_jobs`): `commits` filters server-side with `since` per branch, `workflow_runs` and `workflow_jobs` are client-side incremental with the 32-day `created` window described above, `contributor_activity` has no cursor and stays full refresh.
