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
budget (see the comment on the `check` component in `manifest.yaml`).

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
  retries behind the 60s backoff floor before failing.
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

2.2.0 wired the org-scoped streams to the config-derived router, and every affected sync died on
the platform heartbeat (airbytehq/oncall#13422). Step 4 moved `organizations`/`teams`/`users` into
the manifest and they reference the resolution router;
`test_only_payload_confirmed_organizations_are_sliced` pins that, and reverting the `$ref` fails
it for all three. Any org-scoped stream migrated from here on needs the same `$ref`.

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
| `pull_request_commits` | full refresh | — | — | substream of `pull_requests` |
| `project_columns` | incremental | `updated_at` | client-side | substream of `projects` |
| `project_cards` | incremental | `updated_at` | client-side | substream of `project_columns` |
| `team_members` | full refresh | — | — | substream of `teams` |
| `team_memberships` | full refresh | — | — | substream of `team_members` |
| `issue_timeline_events` | full refresh | — | — | substream of `issues` |
| `commit_comment_reactions` | incremental | `created_at` | client-side | substream of `commit_comments` |
| `issue_comment_reactions` | incremental | `created_at` | client-side | substream of `comments` |
| `commits` | incremental | `created_at` | server-side `since` | slices per branch via `CommitsBranchPartitionRouter` |
| `contributor_activity` | full refresh | — | — | retries 202 with a 90s constant backoff |
| `workflow_runs` | incremental | `updated_at` | client-side, 32-day window | `WorkflowRunsPaginationStrategy` |
| `workflow_jobs` | incremental | `completed_at` | client-side, 32-day window | substream of `workflow_runs` |
| `releases` | incremental | `created_at` | client-side | GraphQL |
| `projects_v2` | incremental | `updated_at` | client-side | GraphQL |
| `pull_request_stats` | incremental | `updated_at` | data feed (newest-first stop) | GraphQL |
| `reviews` | incremental | `updated_at` | client-side | GraphQL |
| `issue_reactions` | incremental | `created_at` | client-side | GraphQL |
| `pull_request_comment_reactions` | incremental | `created_at` | client-side | GraphQL |

- **The five streams migrated in Step 3** (`assignees`, `branches`, `collaborators`, `issue_labels`, `tags`) have no usable cursor: none of their endpoints returns an `updated_at`/`created_at` field or accepts `since`, so they stay full refresh.
- **The nine streams migrated in Step 5** (`events`, `pull_requests`, `commit_comments`, `issue_milestones`, `stargazers`, `projects`, `issue_events`, `deployments`, `workflows`) have a cursor field but no server-side filter, so they are client-side incremental; `pull_requests` and `issue_milestones` additionally sort newest-first and use the data-feed stop condition. See the semi-incremental bullet above before adding another.
- **The three streams migrated in Step 6** (`comments`, `issues`, `review_comments`) are the connector's only REST streams that filter server-side: their endpoints accept `since` and the declarative `DatetimeBasedCursor` injects it via `start_time_option`. Any further stream whose endpoint accepts `since` belongs in that group rather than the client-side-filtered one.
- **The eight streams migrated in Step 7** (`pull_request_commits`, `project_columns`, `project_cards`, `team_members`, `team_memberships`, `issue_timeline_events`, `commit_comment_reactions`, `issue_comment_reactions`) are substreams. `project_columns`, `project_cards` and the two reaction streams are client-side incremental with a cursor per parent record; the other four have no cursor and stay full refresh.
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

- **The six streams migrated in Step 9** (`releases`, `projects_v2`, `pull_request_stats`, `reviews`, `issue_reactions`, `pull_request_comment_reactions`) are the GraphQL streams. GraphQL exposes no `since` filter, so the cursor window is applied to the records the query returns. Five of them are client-side incremental; `pull_request_stats` alone reads `pullRequests(orderBy: {field: UPDATED_AT, direction: DESC})` with `is_data_feed: true` and stops at the first already-synced pull request. `reviews` reads the same connection `ASC` and is client-side incremental, because its traversal order is not its cursor order, so it has no early exit to take.
