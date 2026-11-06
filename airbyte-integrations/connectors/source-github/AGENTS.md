> NOTE: CLAUDE.md is a symlink to AGENTS.md; update AGENTS.md (not the symlink) when changing these instructions.

# Contributing to source-github

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Migration to manifest-only (complete)

The connector is now fully manifest-only (tracking issue:
airbytehq/airbyte-internal-issues#16492): `manifest.yaml` and `components.py` at the connector
root, `language:manifest-only` in `metadata.yaml`, and no Python package — Step 9 moved the
last six (the GraphQL) streams into the manifest, and Step 10 deleted `source_github/`,
`main.py` and the root `pyproject.toml`. The connector runs on the `source-declarative-manifest`
base image, where `components.py` is loaded as `source_declarative_manifest.components` — every
`class_name:` in the manifest uses that module path, and `unit_tests/conftest.py` puts the
connector root on `sys.path` so the same imports work under `components` locally.

`unit_tests/` is a self-contained poetry project (`unit_tests/pyproject.toml`,
`package-mode = false`); run the suite exactly as CI does: `cd unit_tests && poetry install
--no-root && poetry run pytest`. Helpers live in `unit_tests/utils.py`: `make_source` builds
the `YamlDeclarativeSource` on `manifest.yaml`, and `resolve_repositories_and_organizations` /
`get_authenticator` are test-side ports of the connector's former resolution/authenticator
methods.

`check` is declarative too: `CheckStream` on `branches` with
`config_overrides.max_waiting_time: 1`. `branches` slices on `repository_partition_router`,
so `check` runs the same repository resolution the streams do — a config whose repos resolve
to nothing fails with "no stream slices were found" — and then reads one page of
`repos/{repo}/branches`. The `max_waiting_time` override is the interactive check's fail-fast
budget (see "Manifest design notes › `check`").

Config normalization, validation and the legacy config migrations live in the manifest
`spec.config_normalization_rules`: `config_migrations` runs
`components.MigrateRepository`/`MigrateBranch` (1.4.6 space-separated strings → lists, emitting
CONNECTOR_CONFIG), `transformations` runs `components.ConfigNormalization` (default/normalize
`api_url`, convert the legacy strings when the list keys are absent), and `validations` runs
`components.ApiUrlValidationStrategy` on `api_url`. The CDK runs migrations+transformations at
construction on `self._config` and the validations in `streams()`, so `read`/`discover`/`check`
get a config error.

- `manifest.yaml` — every stream, with every schema inline
  (`InlineSchemaLoader`). There is no `schemas/` directory; there is no `JsonFileSchemaLoader`
  left, including for `issue_timeline_events`, whose shared `base_event` definition is expanded
  at all 23 uses (~6,900 lines) because a manifest schema cannot express the reference.
  **No `$ref` may appear inside an inline schema.** A relative one (`user.json`) is left as a
  literal string and the platform gets `"user.json"` where an object belongs — DISCOVER then
  fails — and `#/definitions/...` is swallowed by the manifest's own `$ref` resolver. Expand the
  target verbatim and drop any sibling keys (`description` next to a `$ref`): jsonref, which the
  legacy loader used, replaced the whole node, so the discovered schema never had them.
  `test_every_discovered_schema_is_fully_expanded` in `unit_tests/test_source.py` enforces this.
  When changing a schema, dump the discovered catalog before and after and diff it.

Things worth knowing before touching either half:

- No Python _technical_ stream is left. `Branches` and `RepositoryStats` went with Step 8: the
  manifest's `repository_partition_router` now carries the repository's `default_branch` as an
  `extra_fields` entry on every repository partition, and `repository_branches_resolver` (an
  internal stream, not in the catalog) lists branches for `commits`.
- Parent-child streams (Step 7) are `SubstreamPartitionRouter`s over the manifest parent
  definition (`$ref: "#/definitions/<parent>_stream"`). Parent fields the child needs in its path
  or record come through `extra_fields` on the `ParentStreamConfig` and are read as
  `stream_slice.extra_fields['<field>']`; the partition value itself is `stream_partition.<field>`.
  Most parents are read with a fresh state manager (no `incremental_dependency`), i.e. from
  `start_date`, which is what the Python parents did. `pull_request_commits` instead resumes
  `pull_requests` per repository through `parent_state` (`incremental_dependency: true`),
  with a global `pull_request_updated_at` cursor copied from the parent. Do not enable
  client-side filtering on the child: every commit of an emitted PR must be emitted,
  even if its author date predates the window. Set `use_cache: true` on a parent's
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
    run created more than 32 days before the cursor; the `CursorPagination` `stop_condition` does
    the same from the raw page (`response`, not `last_record`, which only holds what survived the
    client-side filter), comparing it with `stream_interval['start_time']`. The paginator has had
    the slice in its interpolation context since airbytehq/airbyte-python-cdk#1166; before that a
    custom strategy read the slice start back from a request header. Keep every operand of the
    condition a comparison: a bare `None` reads as true to `InterpolatedBoolean` and would stop
    pagination on a malformed page. Do not replace this with GitHub's `created` filter: it caps the
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
    header is absent and would turn every 202 into a 60s wait. Its `Retry-After` strategy is
    wrapped in `RateLimitedResponseBackoffStrategy` like `rate_limit_backoff_strategies`.
  - `commits` slices per branch through `components.CommitsBranchPartitionRouter`, a
    `SubstreamPartitionRouter` over `repository_branches_resolver` that keeps the configured
    branches that exist and falls back to the default branch otherwise, exactly like
    `Commits._validate_branches_to_pull`. The nested legacy state is migrated with
    `integer_ids: false` so a digit-only branch name stays a string.
- The authenticator quota tests need real HTTP traffic through a `Stream`, and no connector
  stream is left to borrow. `unit_tests/utils.py::ProbeStream` is a minimal `HttpStream`
  (`GET repos/{repository}/probe_stream`) that exists only for them. It deliberately has no
  error handling or backoff of its own — assert manifest error behavior through a manifest
  stream, not through it.
- Repository/organization resolution lives in the manifest (`repositories_resolver` and
  `repository_stats`, unioned by `repository_partition_router` /
  `organization_resolution_partition_router`). `check` (`CheckStream` on `branches`) drives
  those same routers to decide whether a config resolves to anything at all, and
  `unit_tests/utils.py::resolve_repositories_and_organizations` enumerates them for the tests.
  See the organization-router section below; the two org routers are not interchangeable.
- Error contract differs per stream group and is expressed by two composed error handlers in
  the manifest: `strict_access_error_handler` (403 fails — repo listing and resolution, which
  is what makes `check` surface bad token scopes) and `skip_inaccessible_error_handler`
  (403/404/409 skip the repository — the repo-scoped child streams). Both fail an unexpected 410,
  mirroring `GITHUB_DEFAULT_ERROR_MAPPING`. When migrating a stream, pick the handler that
  matches what the legacy `GithubStreamABC.read_records` did for it, and remember that 410 is absent from
  the CDK default mapping — an endpoint GitHub answers 410 on needs a filter or it burns five
  retries with exponential backoff before failing.
- `rate_limit_backoff_strategies` is wrapped in `RateLimitedResponseBackoffStrategy`, so header
  waits only apply to rate-limited responses; 5xx/timeouts get the CDK default exponential backoff.
- `stargazers` uses `stargazers_error_handler` — `skip_inaccessible_error_handler` with 404/403
  filters naming GitHub's admin/collaborator restriction on the stargazers listing; keep its
  filter list in step when changing `skip_inaccessible_error_handler`. Each skip message starts
  with the repository, taken from `request_url` with `regex_search`: a filter's `error_message`
  never sees the partition.
- The 410 disabled-feature skip (`disabled_feature_skip_filter`, mirroring
  the legacy `is_gone_with_feature_disabled`) lives on
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
  from here on. Details are in "Manifest design notes › Error handling"; do
  not re-litigate them per stream.
  - **502/504 after retries fails the stream** instead of skipping the repository and finishing
    COMPLETE, because `DefaultErrorHandler` has no "retry N times, then ignore".
  - **404 and 409 are skipped on the first response.** Legacy mapped both to RETRY
    (`GITHUB_DEFAULT_ERROR_MAPPING`) and only skipped once the retries were spent, so a
    transient 404 recovered where a migrated stream now drops that repository from a COMPLETE
    sync. Same CDK limitation as above; accepted, not fixed.
  - **Skips are logged at INFO, and the shared skip messages do not name the repository.**
    Legacy logged `Skipping <stream> for repository <repo>` at WARNING. `stream_partition` is not
    reachable from `error_message` — referencing it raises rather than rendering blank; the
    repository can still be parsed out of `request_url`, as the stargazers filters do. The
    stream name is reachable via `{{ parameters.… }}`, but only with a `$parameters` entry on each stream and a
    per-stream copy of every skip filter, since a `$ref`d filter sees `parameters == {}`; not
    worth losing the shared definitions for. The CDK follow-up (slice access in
    `HttpResponseFilter`) fixes both halves.
- Incremental streams migrated from here on share two more differences from the Python contract:
  - **The boundary record is re-emitted.** `SemiIncrementalMixin.read_records` kept records
    strictly newer than the cursor (`cursor_value > start_point`); the CDK's client-side filter
    compares `start <= cursor <= end` (`ConcurrentCursor.should_be_synced`), so it cannot
    reproduce that and turning `is_client_side_incremental` on buys nothing. One unchanged
    record per partition per sync, deduped by the destination on the primary key.
  - **`is_sorted = "asc"` has no declarative equivalent.** Its only effect was
    `state_checkpoint_interval = page_size`, i.e. a STATE message per page. Concurrent
    declarative cursors checkpoint per partition, so an interrupted sync restarts the partition.
    Step 4 made the same trade for the organization-scoped streams.
- Every migrated incremental stream needs `state_migrations: [LegacyToPerPartitionStateMigration]`.
  The Python state shape was `{<partition>: {<cursor_field>: <value>}}`, which the CDK does not
  recognise; without the migration an upgraded connection silently re-reads from `start_date`.
  It works with `UnionPartitionRouter` (it reads `partition_field` off the router directly), so
  `repository_partition_router` and `organization_partition_router` are both fine.
- When migrating a stream, check `unit_tests/integration/test_<stream>.py` for tests that assert
  `SubstreamResumableFullRefreshCursor` state (`__ab_full_refresh_sync_complete`): declarative
  full-refresh streams emit a single terminal state message instead. Those tests also construct
  `make_source()` with no arguments and pass state only to `read()`; a declarative stream reads
  its state at construction, so they have to build `make_source(config=..., catalog=...,
  state=...)` or the state is silently ignored (`test_events.py` shows the adapted form). `test_assignees.py` also
  turned out to define the same test name twice, so only the second body ran — worth grepping
  for that in the other `integration/test_*.py` files before trusting their coverage.

## Authentication: one shared authenticator, always

Every stream now comes from `manifest.yaml`, and the repository/organization resolution the
routers perform issues HTTP too — all of it through the same authenticator
instance the streams use. `RateLimitedMultipleTokenAuthenticator` tracks each token's remaining
REST/GraphQL quota in local counters; two instances over the same tokens each believe they own
the full budget, so the connector plans for twice the quota GitHub grants and overruns the rate
limit.

`unit_tests/utils.py::get_authenticator` gets that instance by asking the manifest's component
factory for `definitions.requester_base.authenticator`. This reads like it constructs a new
one but does not: `ModelToComponentFactory` caches these by resolved constructor arguments
specifically so every stream shares one set of counters. The cache key is value-based, so pass
the **transformed** config — a different `api_url`, token list or `max_waiting_time` produces a
different instance. Do not add a second authenticator.

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

`max_waiting_time` (default 120 minutes) reaches three interpolations — the authenticator's
`max_wait_time` and the two backoff caps — and the CDK resolves the caps when the strategy is
constructed, so a value one of them cannot render fails every command rather than one retry.
`test_every_max_waiting_time_the_spec_allows_builds` covers every value the spec allows,
including null and zero.

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
  `organizations`/`teams`/`users` via `organization_scoped_retriever`; `check` and the tests'
  `resolve_repositories_and_organizations` enumerate the same router. Its wildcard branch reads its parents through `repositories_resolver`, whose
  `record_filter` is `wildcard_repository_filter`, so an organization whose wildcard matched no
  repository is not a partition either — that is why the declarative streams need no equivalent
  of the `repository_owners` filter the test helper applies by hand.

The asymmetric `parent_key`s are load-bearing, not an inconsistency to tidy: _list org repos_
returns `owner` but no `organization`, while _get a repository_ returns both, so using
`owner/login` on the explicit-repo branch would hand user logins back to the org-scoped streams.
`repository_partition_router` yields the deduplicated union of wildcard-expanded repos and
validated explicit repos; a user-owned explicit repo has no `organization` object, so it
contributes a repository but not an organization.

2.2.0 wired the org-scoped streams to the config-derived router, and every affected sync died on
the platform heartbeat (airbytehq/oncall#13422). Step 4 moved `organizations`/`teams`/`users` into
the manifest and they reference the resolution router;
`test_only_payload_confirmed_organizations_are_sliced` pins that, and reverting the `$ref` fails
it for all three. Any org-scoped stream migrated from here on needs the same `$ref`.

## Workflow run attempts: two silent traps

`workflow_run_attempts` is a substream of `workflow_runs`, wired like `workflow_jobs`
(`incremental_dependency: true`, `global_substream_cursor: true`). The listing returns only the
latest attempt of each run, so the child requests `/attempts/{run_attempt}` and follows
`previous_attempt_url` back to attempt 1. A run that was never re-run costs no request:
`components.WorkflowRunAttemptsRetriever` (a `CustomRetriever`) emits its only attempt from the
parent record, which reaches it whole through `extra_fields: [[]]` (dpath resolves the empty path
to the record; the router keys it by the empty string). Compared live, that record differs from
`GET .../attempts/1` only in the attempt-scoped `jobs_url`/`logs_url`, which the retriever
rebuilds, and in `created_at`/`updated_at`, which the attempt endpoint rounds up a second for
about a quarter of runs. Being a `CustomRetriever`, the factory hands it no client-side
incremental filter and no transformations, and its paginator needs `$parameters.url_base`.

Both traps below are pinned by `unit_tests/test_workflow_run_attempts.py`; if a test there starts
failing, read this before "fixing" it.

**Never filter the child on the attempt's own cursor.** A sync landing between the first attempt
finishing and the re-run starting leaves the cursor above attempt 1's `updated_at`. If the child
filters its own records, attempt 1 is dropped and no later sync revisits it, because the run's
cursor has already moved past. The parent decides which runs are new; the child's cursor has no
`is_client_side_incremental` and exists only so `incremental_dependency` persists parent state.

**A JSON-Schema `$ref` to a file does not work inside a manifest.** The manifest reference resolver
claims every `$ref` key, and for a non-`#/` target it returns the raw string and discards the
sibling keys, so a property copied from a schema file as `{$ref: user.json, description: ...}`
collapses to the literal string `"user.json"`. Shared sub-schemas belong in `definitions`
(`github_user_schema`) and are referenced with `#/definitions/...`.

## Manifest design notes

`manifest.yaml` keeps its comments to one to three lines. The reasoning behind them lives here,
grouped by the definition the comment sits on. Read the matching section before changing one.

### Config fragments and null-safe defaults

- The wildcard fragments (`wildcard_organizations` and `wildcard_repository_filter`) are
  hoisted into `definitions` so the two routers that expand wildcards and the two record filters
  that match against them cannot drift. `$ref` in value
  position resolves to the scalar before component construction, so they behave exactly like
  the literal strings.
- `wildcard_organizations` matches the star wherever it sits in the repo part (`org/*`,
  `org/prefix*`, `org/pre*fix`), which makes it the exact complement of the explicit-repo list
  (`^([^*]+)$`, "contains no star"). An earlier `[*]$` anchor let an interior-star entry match
  neither list, so it was dropped with no request and no warning, where the legacy resolver
  expanded it.
- `wildcard_repository_filter` passes everything when the config has no wildcard (legacy
  `Repositories(pattern=None)`). That clause is inert for the resolver stream: with no wildcards
  it has no partitions.
- A `.get(key, default)` default only applies when the key is _absent_. A present-but-null value
  (reachable through the API, Terraform or embedded use) renders as the literal `"None"`:
  - `max_waiting_time` became `"PTNoneM"` and every command failed at startup with
    `ISO8601Error: Unrecognised ISO 8601 date format: ''` (isodate splits on the `T` and reports
    the empty date half). It uses `is not none` rather than `or 120` so a user-set 0 is not read
    as absent and replaced by 120. The backoff caps use the same guard; a null would otherwise
    reach the multiplication as `None`.
  - `num_workers` raised `ValueError: default_concurrency did not evaluate to an integer` while
    the source was being constructed, failing every command.
  - `start_date` reached `MinMaxDatetime` as `"None"` and aborted the stream, so it uses `or`:
    any falsy value means "replicate everything". Client-side streams fall back to the epoch.
    The server-side `since` streams fall back to `2008-01-01T00:00:00Z`, which predates every
    GitHub repository: GitHub answers `since=1970-01-01T00:00:00Z` on the issues endpoint with an
    empty list. Legacy sent no `since` at all when `start_date` was unset.

### Page sizes

- `large_stream_page_size` (10) is `constants.DEFAULT_PAGE_SIZE_FOR_LARGE_STREAM`, the per-page
  size of the REST streams legacy marked `large_stream = True`: `pull_requests`, `comments`,
  `issues` and `review_comments` (which now overrides it with 100; see `review_comments_stream`).
  It is written out because `page_size_for_large_streams` was removed from the spec in 1.0.1 and
  cannot be set from the UI since; a config that still carries the key through the API or
  Terraform no longer steers these streams. 10 costs roughly 10x the requests and several times
  the wall clock of `per_page=100`. It was introduced to stop a 502 storm on `pull_requests`
  against a very large organization, which later secondary-rate-limit handling may have
  addressed on its own. Raising it is a deliberate, measurable change, not part of the migration.
- `graphql_large_stream_page_size` (10) applies to `releases` and `pull_request_stats` only, the
  two GraphQL streams legacy marked `large_stream`; every other GraphQL stream keeps
  `constants.DEFAULT_PAGE_SIZE` (100). `REDUCE_PAGE_SIZE` is the safety net, not a licence to raise
  the default. The GraphQL side has the stronger claim to the number: `releases` materializes
  `description` and `descriptionHTML` per node, and `first=100` reproduced a 502 in about 11
  seconds against nodejs/node.

### Authenticator quota pools

- `unavailable_status_codes: [404]`: GitHub Enterprise Server ships with HTTP API rate limiting
  disabled, and such an instance answers `GET /rate_limit` with 404 `{"message": "Rate limiting
  is not enabled."}`. Seeding runs before the first stream request, so without this the whole
  connection died on a generic "Resource not found", every command and not just sync. A listed
  status seeds that token's pools as untracked: no exhaustion waits, no proactive throttling, no
  rotation on exhaustion, while requests are still signed and tokens still rotate. An untracked
  token stays untracked for the whole sync, so a status the endpoint can also return
  transiently would cost quota tracking for the entire run; hence 404 only. 401/403 must never be
  listed, or a revoked credential reads as "quota tracking unavailable" instead of an auth
  failure. GitHub documents 404 for this endpoint without saying it means rate limiting is off;
  that mapping comes from GHES responses in the wild, which is why the CDK leaves it to the
  connector.
- The `*_header` fields reconcile each pool against every response, not only the initial
  `/rate_limit` seeding. GitHub returns these headers on every authenticated REST response, and
  local counters drift when the token is shared with another client, when requests overlap
  under `concurrency_level`, or when a sync outlives its seeding.
- No `exhaustion_status_codes`: GitHub's 403 is also a secondary limit (403 + `Retry-After`,
  primary quota untouched) and a missing-scope denial, and neither carries
  `X-RateLimit-Remaining: 0`. Listing 403 would zero the pool for those, which on a single-token
  config leaves nothing to rotate to and turns a retryable wait into "Rate limit is exceeded for
  all provided tokens."

### Error handling

The handlers replicate the legacy `GithubStreamABC` error contract. Rate limits are waited out
instead of failing the sync. GitHub signals them three ways, and the legacy handler (the Python
`GithubStreamABCErrorHandler`, removed in 2.7.0) retried on all of them, so all three are matched
ahead of the 404/403/409 filters:

1. a `Retry-After` header (sent on most, but per the docs not all, secondary-limit responses);
2. an "API rate limit exceeded" message (primary) or "exceeded a secondary rate limit" message
   (secondary without `Retry-After`; secondary limits are tracked apart from the primary quota,
   so `X-RateLimit-Remaining` may still be non-zero);
3. `X-RateLimit-Remaining: 0` on an error response, the fallback the docs prescribe when
   `Retry-After` is absent. A predicate cannot see the status code, so "is an error response" is
   approximated by GitHub's error envelope (a JSON object with a `message`). Successful payloads
   are arrays or objects without a top-level `message` and must not match: the request that
   spends the last quota point returns 200 with `X-RateLimit-Remaining: 0` and its records have
   to be kept. `response.get('message') is not none` is required because InterpolatedBoolean
   compares the rendered string against a false-values list that does not include `"None"`.

Every REST handler fails 401 as a config error through `unauthorized_fail_filter`; only
`graphql_error_handler` leaves 401 to the CDK default mapping. Other unmatched responses (429,
5xx, ...) fall back to that mapping on every handler. The terminal 403/404/409/410 handling differs
per requester (fail or skip, stargazers and attempt-chain messages, which handlers carry the 410
skip), so the filters are separate definitions composed into the handlers.

`success_filter` comes first in every handler. `DefaultErrorHandler.interpret_response`
evaluates `response_filters` before it checks `response.ok` and returns on the first match, so
without it a 200 that merely carries `Retry-After` (GHE, a proxy or a CDN throttling on its own
account) is classified RATE_LIMITED: its records are discarded and the request is retried until
`max_retries` runs out. It has to be its own filter rather than a conjunct in the predicates
below, because `http_codes` is OR'd with `predicate` inside a filter
(`http_response_filter.py::_matches_filter`) and the predicate context has no status code. It
matches 200 only: GitHub answers 202 on `/stats/contributors` to mean "still computing, retry
later".

Deliberate divergences from legacy (they point opposite ways; both are deliberate):

- **502/504 after retries fails the stream.** Legacy retried too, but `read_records` caught the
  exhausted-retries `AirbyteTracedException` for 502/504 (its `BAD_GATEWAY`/`GATEWAY_TIMEOUT`
  branches), logged a warning and moved on, reporting COMPLETE with that repository's records
  missing. Failing is the better contract (INCOMPLETE rather than COMPLETE-with-gaps), and parity
  is not declarative anyway: `DefaultErrorHandler` has no "retry N times, then ignore", and a
  `502/504 -> IGNORE` filter would drop the repository on the first blip. Pinned by
  `test_repeated_502_fails_the_stream`.
- **404 and 409 are skipped on the first response.** Legacy mapped both to RETRY (the Python
  `GITHUB_DEFAULT_ERROR_MAPPING`, removed in 2.7.0), so it only skipped after `max_retries = 5`.
  For a persistent 404/409 the outcome is the same and faster. For a transient one (GitHub is
  eventually consistent and does answer 404 for a repository that exists) the repository is now
  dropped from a sync that still reports COMPLETE. Parity is not declarative for the same reason
  as 502/504: `DefaultErrorHandler` has no "retry N times, then ignore". Accepted because the blips are rare and the
  alternative is retrying every deleted repository five times; revisit with the CDK follow-up.
- **Skip logging.** The `IGNORE` path logs the filter's `error_message` at INFO
  (`http_client.py`); legacy logged `Skipping <stream> for repository <repo>` at WARNING, so a
  scope-starved token can produce a zero-record COMPLETE sync whose only trace is unattributed
  INFO lines. The shared skip messages do not name the repository. `stream_partition` is not
  reachable: `HttpResponseFilter._create_error_message` passes only `config`, `response` and
  `headers`, and referencing the slice raises `undeclared variables` instead of rendering blank.
  The repository can be parsed out of `request_url` (the stargazers filters do; see below), which
  is the cheap way to name it in the shared filters too. The stream name is reachable through
  `{{ parameters.get(...) }}`, but a `$ref`d filter carries `parameters == {}`, so recovering it
  costs a `$parameters` entry per stream plus a per-stream copy of every skip filter. That trades
  the shared definitions (and the filter order they encode) for one word in a log line, so it is
  not done. Follow-up: give `HttpResponseFilter` access to the stream slice in the CDK, which
  fixes both halves (same bucket as the token rotation follow-up).

Per-filter notes:

- `disabled_feature_skip_filter`: GitHub answers 410 when the feature backing an endpoint is off
  for the repository ("Issues are disabled for this repo."), and legacy skipped exactly those
  (`is_gone_with_feature_disabled`). 410 is absent from the CDK default mapping, so without the
  filter it would be retried five times with exponential backoff and fail. It is a predicate, not
  `http_codes: [410]` + `error_message_contains`, because `HttpResponseFilter` ORs its conditions
  and that would skip every 410. The predicate keys off the error envelope (`response is
  mapping`); `| string` keeps a non-string `message` from raising. See the 410 bullet above for
  why the pattern must name the feature. Two silent traps: use `!= ''`, not `is not none`
  (`regex_search` returns an empty string on no match, so `is not none` renders "True" and skips
  everything); and `\\b`, not `\b` (Jinja parses its own string literals, so `\b` reaches `re`
  as a backspace and the filter quietly stops matching).
- `strict_access_error_handler` has no `disabled_feature_skip_filter`: its endpoint
  (`/orgs/{org}/repos`) never sends that 410 (nor does `/repos/{owner}/{repo}`, whose
  `resolve_explicit_repository_error_handler` has no 410 skip either), and including it would let
  an envelope mentioning a disabled feature match before `forbidden_fail_filter` and turn the
  403 `check` relies on into a silent skip.
- `forbidden_fail_filter`: legacy re-raised 403 for the org listing (the `Organizations` branch
  of `read_records`), so `repositories_resolver` and `repositories` fail with an actionable
  scopes/SSO message, which is what lets `check` catch a bad token. Not on `repository_stats`:
  legacy resolved explicit entries with `RepositoryStats`, a plain `GithubStream`, which skipped a
  403 with a warning.
- `resolve_explicit_repository_error_handler`: `repository_stats` gives the canonical `full_name`
  and `organization.login` for each explicit entry, and an entry that answers 404 or 403 is
  skipped. A 403 on an explicit `org/repo` (a SAML-protected
  org is the common case) raised while partitions are being generated kills the partition
  generator, so the stream would read nothing at all. Skipping keeps legacy's warn-and-continue.
  `check` still catches a bad token: with every entry skipped the resolved list is empty and
  `CheckStream` fails with "no stream slices were found".
- `forbidden_skip_filter`: one repository the token cannot read must not fail the other
  partitions. It runs after the rate-limit filters, so a secondary-limit 403 is still retried.
  The message covers repository and organization partitions (`organizations`/`teams`/`users`
  share the handler) and lists `read:org` first, the scope legacy named for the org streams
  (legacy: 404 "isn't available for organization", 403 "may be missing the `read:org` scope").
- `empty_repository_skip_filter`: 409 "Git Repository is empty." for a repository with no commits
  (`branches`, `tags`). Legacy IGNOREd that exact message and retried other 409s until it
  skipped, so skipping every 409 gives the same outcome without spending the retry budget.
- `comments_error_handler`: `comments` raised its budget to 7 in Python (`Comments.max_retries`).
  It is the highest-volume REST stream and meets transient 5xx most often.
- Stargazers filters: since July 2026 GitHub lists a repository's stargazers only to its admins
  and collaborators and answers everyone else with 404 (or 403 for some token types). The generic
  messages blame a deleted repository or missing scopes, so `stargazers` names the actual
  restriction. The repository comes from `request_url`
  (`.../repos/{owner}/{repo}/stargazers`, which also covers a GHES `/api/v3` prefix).
- `attempt_not_found_skip_filter`: a 404 partway through one run's attempt chain loses the rest
  of that run's history, and the run's cursor still advances, so no later sync retries it. Still
  IGNORE: GitHub deletes runs, and a run deleted between the listing and the attempt read would
  otherwise wedge the stream. The message names what was lost so it is greppable.

### Backoff floor

`rate_limit_backoff_strategies` are capped by Max Waiting Time, so that setting bounds every
rate-limit wait, not only the ones the authenticator decides before sending. `check` runs with
`max_waiting_time: 1`, a 61s cap, so it fails fast on an exhausted quota instead of sleeping until
the reset. The `+ 1` keeps the budget inclusive: the CDK compares with `>=`, so a 1-minute budget
would otherwise equal the `min_wait: 60` floor and a rate-limited response without a reset header
(a 429 or a secondary-limit 403 with no headers) would fail instead of retrying. `check` uses 1 rather than 0 for the same reason. Requires CDK >= 7.28.1
(airbytehq/airbyte-python-cdk#1126): before it, `HttpClient` asked for a spare token only after a
strategy returned a wait, and a cap raises instead, so a budget shorter than the reset distance
ended the stream rather than rotating (measured on 7.28.0: a 30-minute budget against a 60-minute
reset failed with a second token idle). `test_short_wait_budget_does_not_cost_token_rotation`
proves the fixed order end to end. 7.28.1 also resolves the cap at construction, so a bad
expression fails at startup.

`min_wait: 60` is the floor the legacy backoff enforced, so a reset already in the past or
seconds away does not become a tight retry loop. It does not land on the same responses legacy
floored:

| Response | here | legacy |
| :--- | :--- | :--- |
| 403 + `Retry-After: 30` | 30s (floor missing) | 60s |
| 403 + `X-RateLimit-Reset` now+10 | 60s | 60s |
| 403 + reset already past | 60s | 60s |
| 500 + `X-RateLimit-Reset` now+3000 | expo | expo |
| 500 / timeout, no such headers | expo | expo |

`WaitTimeFromHeader` has no `min_wait`, so `Retry-After` is used raw; `WaitUntilTimeFromHeader`
returns `min_wait` outright when its header is absent instead of flooring a computed wait; and
the strategies are shared by every retryable response on the requesters that inherit them.
`components.RateLimitedResponseBackoffStrategy` contains both effects by gating the two strategies
on a rate-limit response: headerless ordinary retries no longer inherit `min_wait`, and a reset
header on a 5xx is ignored (GitHub sends one on 500s; waiting for it spent the 600s `max_time`
retry budget in one sleep, airbytehq/oncall#13837). The `Retry-After` floor is still missing.
Alternatives measured and rejected: a `CompositeErrorHandler` with `min_wait` on a rate-limit-only
branch changes nothing (`CompositeErrorHandler.backoff_strategies` flattens every child's
strategies, and `HttpClient` takes the first truthy one, which is why the component gate is
needed); dropping `min_wait` fixes the leak but a
stale reset then falls to `backoff.expo` and spends the retries at 1, 2, 4, 8, 16s against a limit
that has not refilled. A CDK fix would still be right for other connectors: `WaitUntilTimeFromHeader` should return `None`
when its header is missing and `WaitTimeFromHeader` should gain `min_wait`; four other connectors
combine these strategies. Headerless 5xx and timeouts use the CDK default exponential backoff
(1/2/4/8/16s), as legacy did.

The wait is only paid when rotating cannot help: CDK 7.26.0 reconciles the authenticator's
counters against every response, so a primary rate limit spends the rejected token's pool and
`HttpClient` retries in 0.1s on a spare token (see "Authentication" above). This covers the
reactive rotation legacy's backoff strategy did at the 10-minute mark. A secondary limit is still
waited out: GitHub scopes it per account, so another token of the same account is rejected too.

### Pagination

`page_link_paginator` follows GitHub's documented end-of-data signal, the absence of a
`rel="next"` link, as legacy `GithubStreamABC.next_page_token` did. A short page is not
guaranteed to be the last one; inferring the end from `last_page_size < 100` would silently
truncate the org repo list that drives every partition. The full `next` URL becomes the request
path (`DefaultPaginator.path()` returns the token for a `RequestPath` option and `HttpRequester`
accepts an absolute URL). Extracting only `page=N` is not enough: past GitHub's large-dataset
threshold the link carries an opaque `after` cursor and page-only requests get 422. The
requester's `request_parameters`/`since` are still appended, duplicating identical values in the
URL, which GitHub accepts. `CursorPaginationStrategy` replaces `headers["link"]` with
`response.links`; chained `.get(...)` with defaults is required, because `headers.link.next.url`
raises `UndefinedError` on the last page and `InterpolatedString`'s default is the template
itself, so the error escapes. On the last page the cursor renders `""`, which becomes `None` and
ends pagination.

### Incremental REST streams

- `repositories` is listed `sort=updated&direction=desc`, so the data-feed stop ends pagination
  at the first page whose last record is at or below the partition cursor (legacy
  `Repositories.is_sorted = "desc"`); without it every sync walked the org's whole listing (`ceil(repos/100)` requests per org per
  sync instead of about 1). The
  CDK drops that boundary page's older records. `ConcurrentPerPartitionCursor` seeds a partition
  with no state from the _global_ cursor, so repos of an org added to `repositories` after the
  first sync are emitted only if updated after that cursor.
- `server_side_since_cursor` (`comments`, `issues`, `review_comments`, and `commits` with
  `cursor_field: created_at`): GitHub's `since` returns `updated_at >= since`; legacy added it from `SemiIncrementalMixin.get_starting_point`
  (`max(start_date, per-repository state)`). No `is_client_side_incremental`: see the boundary
  record bullet above. No `end_time_option`, `step` or `cursor_granularity`, so each partition
  (a repository, or a branch for `commits`) is one open-ended window paginated by `rel="next"`, as
  legacy did.
- `issues` restates `per_page` because `request_parameters` replaces the shared dict instead of
  merging. `state`/`sort`/`direction` are `Issues.stream_base_params`; without `state=all` GitHub
  returns open issues only. The `asc` ordering is kept so the request shape and record order are
  unchanged (see the `is_sorted = "asc"` bullet above).
- `comments` keeps `use_cache` so `issue_comment_reactions` reads its parent from pages this
  stream already fetched. They only share entries while the URLs match (the parent read sends
  `since=start_date`, this stream `since=<cursor>`), exactly as legacy `ReactionStream` did.
  `issues` keeps `use_cache` for the same reason: it is the parent of `issue_timeline_events`
  (legacy `Issues.use_cache = True`). Both stay while those substreams read these listings.
- `organization_scoped_requester.use_cache` lets one read of `orgs/{org}/teams` serve both
  `teams` and the `team_members` parent read; harmless for `organizations` and `users`.
- `add_organization_transformation` replaces legacy `Organizations.transform`. It is applied to
  `teams` and `users` only: `Organizations.parse_response` yielded the payload untouched, and the
  `organizations` schema has no `organization` property.

### Workflow runs and attempts

- `workflow_runs` `stop_condition`: runs are listed newest-created first and can be re-run for
  32 days, so once the page's oldest run was created more than 32 days before the slice start,
  nothing further can have been updated since (legacy `WorkflowRuns.read_records`). It reads the
  raw page, not `last_record`.
- `WorkflowRunAttemptsRetriever` path: `run_url` is the parent's absolute `url`, and
  `HttpRequester._join_url` lets it win, so GHES is followed too. A re-run starts at the latest
  attempt and walks back, costing `run_attempt` requests. `or 1` because `run_attempt` is optional
  in GitHub's schema and a missing extra field renders `"None"`, which would 404 the whole run.
- Record filter: `field_path: []` emits the body as-is, so a 200 carrying `{"message": ...}`
  (GitHub sends that on some redirect and deprecation paths) would land as a row with a null key.
  Nothing invents a missing `run_attempt`: the number is only knowable from the request path, so
  a default would mislabel a mid-chain attempt and overwrite a good row. Skipping loses one
  attempt; the walk continues.
- Paginator `stop_condition`: `DefaultPaginator` has no page cap, so a link pointing at the
  current attempt, or oscillating between two, would page until the sync is killed. The guard
  stops only on proof the chain failed to descend; anything unrecognised keeps walking, because an
  expression that raises renders the raw template, which reads as true and would silently end the
  walk. It is not end-anchored, so `.../attempts/1/` and `.../attempts/1?x=1` still descend. One
  shape stays unbounded (no usable `run_attempt` plus a same-run link with a numeric segment);
  bounding it would mean stopping on a payload the connector cannot reason about.

### GraphQL error handling

- The GraphQL streams post a parameterized document and the paginator injects
  `variables.first`/`variables.after`. Injecting into `variables` (rather than inlining values
  into the query text, as the legacy sgqlc builders did) is what makes `REDUCE_PAGE_SIZE` work: the
  CDK rebuilds the body on the retry. `combine_mappings` merges nested `body_json` paths when they
  do not collide, so the requester's `variables.owner`/`name` and the paginator's
  `variables.first`/`after` compose.
- `graphql_reduce_page_size_filter`: GitHub answers 502/504 when a query is too expensive for its
  internal deadline, so retrying the identical query only times out again. Legacy
  `GitHubGraphQLErrorHandler` halved `stream.page_size` and returned RETRY, but `HttpClient`
  replays the same prepared request with the oversized `first` already serialized, so only a
  later page saw the smaller size, and any non-502/504 response reset it.
- `graphql_body_rate_limited_filter` / `graphql_body_error_filter`: GitHub reports most GraphQL
  failures as 200 with an `errors` array (`RATE_LIMITED`, "Something went wrong while executing
  your query", node-limit breaches). Without them a 200 with `errors` is consumed as an empty page,
  the partition ends early and the sync reports success with data missing and nothing logged. The
  legacy handler had both branches (`check_graphql_rate_limited`, `_safe_json_get_errors`).
  `errors` is not always a list of objects (legacy tested `{"errors": "not found"}`); `selectattr`
  over a string iterates characters with no `type`, so the rate-limit predicate matches nothing and
  the generic filter picks it up.
- `graphql_body_not_found_skip_filter`: a repository the token cannot read is answered with 200,
  `data.repository: null` and an `errors` entry of type NOT_FOUND (missing, renamed, or hidden by
  scopes/SSO) or FORBIDDEN. The status-only skip filters never see it, so without this the generic
  body filter would retry it until the attempts run out and fail the stream.
- `graphql_error_handler.response_filters` order is the contract, because `DefaultErrorHandler`
  stops at the first match and a query timeout arrives as `errors` on a 200 _and_ on a 502/504:
  1. body predicates: rate limit first (a page-size reduction is the wrong answer to a spent
     quota), then page-size reduction (above the generic body filter, or a timed-out page is
     retried at the same size), then not-found skip, then the generic body error;
  2. `success_filter`, which would stop the chain on every 200 but still has to run for a 200 with
     no `errors` to keep `Retry-After` on a 200 from reading as a rate limit;
  3. status-only filters, last because a 502/504 reaching one first would be retried unchanged or
     skipped.
  Given up: a 502/504 that also carries rate-limit headers is reduced rather than waited out.
  GitHub answers rate limits with 403/429, so it does not send that shape.
- `graphql_page_size_reduction` halves per rejected page, floored at 1. From 10 the sequence is
  10, 5, 2, 1, then `retries_at_minimum_page_size` takes over: three more attempts at 1 with
  `backoff_seconds` multiplied by the attempt number, about seven requests over two minutes. From
  100 (`reviews`, `issue_reactions`, `pull_request_comment_reactions`, `projects_v2`) it is 100,
  50, 25, 12, 6, 3 and the sixth reduction is one past `max_attempts`, so those streams fail at 3
  and never reach the floor; no message may assume it was reached. Raising `max_attempts` to 6
  would let them reach it, but changes how long a stuck partition holds a sync open. `REDUCE_PAGE_SIZE` bypasses the error handler's retry
  budget and backoff, so these settings are the whole GraphQL 502/504 contract, kept comparable
  to other streams' (a 502/504 looks the same whether the query was too slow or GitHub had a
  passing problem). `reset_policy: NEVER` keeps the reduced size for the partition, since
  restoring it re-triggers the timeout on the next page; the size is local to one `_read_pages`
  call, so other repositories are unaffected.
- `failure_message` is appended to the CDK's terminal message. There is no page-size setting to
  point at, and the smallest size tried differs per stream (the CDK's sentence states it). A more
  recent start date is deliberately not suggested: these streams filter client-side, so it would
  not make the query cheaper.

### GraphQL streams

- `releases` (`CREATED_AT DESC`) and `pull_request_stats` (`UPDATED_AT DESC`) use `is_data_feed`.
  The CDK drops the boundary page's records outside the window, leaving the same records the
  legacy client-side filter emitted. For `releases`, ASC bought nothing, since the declarative cursor checkpoints once per partition,
  and without the stop every sync walked the full release history at 10 per page. For
  `pull_request_stats` it is the declarative form of legacy's `is_sorted = "desc"` exit, which
  existed because walking every pull request exhausted the GraphQL point budget and tripped
  heartbeat timeouts on large organizations. Legacy used ASC on the first read only for
  mid-partition checkpointing.
- `pull_request_comment_reactions` `owner`/`name` variables: only the repository listing
  document declares them; the drill-down documents root at `node(id:)`, and GraphQL rejects an
  undeclared variable. The test is which document the token carries, not whether there is a
  token: the listing paginates too (`typename: PullRequest` re-roots at the listing with no node
  id), and dropping the variables on its second page made GitHub answer `data: null`, so only the
  first page (100) of pull requests was ever scanned.

### `check`

`CheckStream` on `branches` runs the same repository resolution the streams do, then reads one
page of `repos/{repo}/branches`. `config_overrides.max_waiting_time: 1` makes the authenticator
raise "Rate limit is exceeded for all provided tokens." on an exhausted quota instead of sleeping
up to 120 minutes. 1 rather than 0 because the caps resolve to `max_waiting_time * 60 + 1` and the
floor is 60s: a 1s cap would fail the first rate-limited response without a reset header (429 or
secondary-limit 403) with the rate-limit message, while 61s retries a blip. Headerless 5xx use
exponential backoff and never consult that cap.

## Incremental Stream Considerations

The GitHub REST and GraphQL APIs support `since` parameter on many list endpoints and `updated` sorting.

**Connector type:** manifest-driven — every stream in `manifest.yaml`, plus `components.py` for the custom components

**Analysis status:** Every stream is in the manifest; the per-step notes below cover them all.

### Stream-by-stream incremental analysis

| Stream | Sync mode | Cursor field | Filtering | Notes |
| :----- | :-------- | :----------- | :-------- | :---- |
| `repositories` | incremental | `updated_at` | data feed (newest-first stop) | |
| `assignees` | full refresh | — | — | |
| `branches` | full refresh | — | — | |
| `collaborators` | full refresh | — | — | |
| `issue_labels` | full refresh | — | — | |
| `tags` | full refresh | — | — | |
| `organizations` | full refresh | — | — | |
| `teams` | full refresh | — | — | |
| `users` | full refresh | — | — | |
| `events` | incremental | `created_at` | client-side | |
| `pull_requests` | incremental | `updated_at` | data feed (newest-first stop) | |
| `commit_comments` | incremental | `updated_at` | client-side | |
| `issue_milestones` | incremental | `updated_at` | data feed (newest-first stop) | |
| `stargazers` | incremental | `starred_at` | client-side | |
| `projects` | incremental | `updated_at` | client-side | |
| `issue_events` | incremental | `created_at` | client-side | |
| `deployments` | incremental | `updated_at` | client-side | |
| `workflows` | incremental | `updated_at` | client-side | `%z` offset timestamps |
| `comments` | incremental | `updated_at` | server-side `since` | |
| `issues` | incremental | `updated_at` | server-side `since` | |
| `review_comments` | incremental | `updated_at` | server-side `since` | |
| `pull_request_commits` | incremental | `pull_request_updated_at` | parent per-repository cursor | substream of `pull_requests`; global child cursor |
| `project_columns` | incremental | `updated_at` | client-side | substream of `projects` |
| `project_cards` | incremental | `updated_at` | client-side | substream of `project_columns` |
| `team_members` | full refresh | — | — | substream of `teams` |
| `team_memberships` | full refresh | — | — | substream of `team_members` |
| `issue_timeline_events` | full refresh | — | — | substream of `issues` |
| `commit_comment_reactions` | incremental | `created_at` | client-side | substream of `commit_comments` |
| `issue_comment_reactions` | incremental | `created_at` | client-side | substream of `comments` |
| `commits` | incremental | `created_at` | server-side `since` | slices per branch via `CommitsBranchPartitionRouter` |
| `contributor_activity` | full refresh | — | — | retries 202 with a 90s constant backoff |
| `workflow_runs` | incremental | `updated_at` | client-side, 32-day window | `CursorPagination` `stop_condition` on `stream_interval` |
| `workflow_jobs` | incremental | `completed_at` | client-side, 32-day window | substream of `workflow_runs` |
| `workflow_run_attempts` | incremental | `updated_at` | parent `workflow_runs` decides; child never filters | substream of `workflow_runs`, walks `previous_attempt_url` |
| `releases` | incremental | `created_at` | data feed (newest-first stop) | GraphQL |
| `projects_v2` | incremental | `updated_at` | client-side | GraphQL |
| `pull_request_stats` | incremental | `updated_at` | data feed (newest-first stop) | GraphQL |
| `reviews` | incremental | `updated_at` | client-side | GraphQL |
| `issue_reactions` | incremental | `created_at` | client-side | GraphQL |
| `pull_request_comment_reactions` | incremental | `created_at` | client-side | GraphQL |

- **The five streams migrated in Step 3** (`assignees`, `branches`, `collaborators`, `issue_labels`, `tags`) have no usable cursor: none of their endpoints returns an `updated_at`/`created_at` field or accepts `since`, so they stay full refresh.
- **The nine streams migrated in Step 5** (`events`, `pull_requests`, `commit_comments`, `issue_milestones`, `stargazers`, `projects`, `issue_events`, `deployments`, `workflows`) have a cursor field but no server-side filter, so they are client-side incremental; `pull_requests` and `issue_milestones` additionally sort newest-first and use the data-feed stop condition. See the semi-incremental bullet above before adding another.
- **The three streams migrated in Step 6** (`comments`, `issues`, `review_comments`) are the connector's only REST streams that filter server-side: their endpoints accept `since` and the declarative `DatetimeBasedCursor` injects it via `start_time_option`. Any further stream whose endpoint accepts `since` belongs in that group rather than the client-side-filtered one.
- **The eight streams migrated in Step 7** (`pull_request_commits`, `project_columns`, `project_cards`, `team_members`, `team_memberships`, `issue_timeline_events`, `commit_comment_reactions`, `issue_comment_reactions`) are substreams. `project_columns`, `project_cards` and the two reaction streams are client-side incremental with a cursor per parent record. `pull_request_commits` is incremental using the parent PR's `updated_at` as `pull_request_updated_at`, with parent state per repository; the other three have no cursor and stay full refresh. Commits removed by force-push or rebase are not deleted in incremental mode (primary key `sha`); Full Refresh | Overwrite removes them.
- **The four streams migrated in Step 8** (`commits`, `contributor_activity`, `workflow_runs`, `workflow_jobs`): `commits` filters server-side with `since` per branch, `workflow_runs` and `workflow_jobs` are client-side incremental with the 32-day `created` window described above, `contributor_activity` has no cursor and stays full refresh.
- The GraphQL error contract is carried by the _order_ of `graphql_error_handler.response_filters`,
  not by the filters alone. GitHub reports GraphQL failures in the body — on a 200 and on a
  502/504 alike — so the body predicates and the status matchers compete for the same responses
  and `DefaultErrorHandler` stops at the first one that matches. Three rules hold:
  `graphql_reduce_page_size_filter` (502/504) must sit **above** `graphql_body_error_filter`, or a
  query timeout reported with an `errors` body is retried at the same page size and the reduction
  never happens; `graphql_body_not_found_skip_filter` must sit above it too, or an unreadable
  repository is retried until the attempts run out instead of being skipped like a REST 404; and
  all of the body filters must precede `success_filter`, which classifies every 200 as a success.
  Assert a new GraphQL error behavior with both body shapes — `{"message": ...}` and
  `{"errors": [...]}` — on the status you care about; a fixture with an empty body passes whatever
  the order is.

- **The six streams migrated in Step 9** (`releases`, `projects_v2`, `pull_request_stats`, `reviews`, `issue_reactions`, `pull_request_comment_reactions`) are the GraphQL streams. GraphQL exposes no `since` filter, so the cursor window is applied to the records the query returns. Four of them are client-side incremental; `releases` (`releases(orderBy: {field: CREATED_AT, direction: DESC})`) and `pull_request_stats` (`pullRequests(orderBy: {field: UPDATED_AT, direction: DESC})`) use `is_data_feed: true` and stop at the first already-synced record. `reviews` reads the same connection `ASC` and is client-side incremental, because its traversal order is not its cursor order, so it has no early exit to take. `reviews`, `issue_reactions` and `pull_request_comment_reactions` read every drilldown root with a CDK `CombinedExtractor` in `union` mode (one `DpathExtractor` per response shape, each with a `RecordExpander` that copies the one parent field the record needs with `parent_fields`). Both need an `airbyte-cdk` release containing airbyte-python-cdk#1162 and #1165.
