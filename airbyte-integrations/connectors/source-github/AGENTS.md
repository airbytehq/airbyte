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
  (403/404/409 skip the repository — the repo-scoped child streams). When migrating a stream,
  pick the handler that matches what `GithubStreamABC.read_records` did for it.
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

## Incremental Stream Considerations

The GitHub REST and GraphQL APIs support `since` parameter on many list endpoints and `updated` sorting.

**Connector type:** hybrid — declarative manifest plus Python CDK stream classes

**Analysis status:** Full stream-by-stream analysis requires Python code review of the streams still in `streams.py`.

### Future incremental stream candidates

- **Streams still in `streams.py` deferred for Python code review:** a full stream-by-stream incremental analysis table (per the standard CONTRIBUTING.md schema) should be added by a future agent after reviewing the remaining Python stream definitions, their `cursor_field` properties, and the API endpoints they call.
- **The five streams migrated in Step 3** (`assignees`, `branches`, `collaborators`, `issue_labels`, `tags`) have no usable cursor: none of their endpoints returns an `updated_at`/`created_at` field or accepts `since`, so they stay full refresh.
