# Contributing to source-github

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

This connector is manifest-only: `manifest.yaml` serves every stream (with every JSON schema inline) and runs on the `source-declarative-manifest` base image. `components.py` holds the custom components the manifest names by `class_name`; `unit_tests/` is a self-contained poetry project (`cd unit_tests && poetry install --no-root && poetry run pytest`). See `AGENTS.md` for the details a change needs to respect.

## Behavior that differs from the legacy Python connector

These are deliberate. `AGENTS.md` has the reasoning: "Manifest design notes › Error handling" for the first three, "Migration to manifest-only" for the last two.

- A repository that keeps answering 502/504 fails the stream instead of being skipped silently (`test_repeated_502_fails_the_stream`).
- 404 and 409 skip the repository on the first response instead of after the retries run out (5, or 7 on `comments`; `test_inaccessible_repository_is_skipped`).
- Skipped repositories are logged at INFO, and the shared skip messages do not name the repository (the stargazers ones do, from `request_url`).
- Incremental streams re-emit the record whose cursor equals the stored state once per sync (`test_start_date_filters_older_records_and_keeps_the_boundary`).
- State is checkpointed per partition, so an interrupted sync restarts the repository it was reading.

## Manifest comments

Keep comments in `manifest.yaml` to one to three lines that say what a definition must not lose. Put the reasoning, history and measurements in the matching `AGENTS.md` section and point to it.

## Incremental Stream Considerations

The GitHub REST and GraphQL APIs support `since` parameter on many list endpoints and `updated` sorting.

`pull_request_commits` supports incremental sync using `pull_request_updated_at`, copied from the parent PR's `updated_at`. It resumes the parent per repository and emits every commit of each selected PR, regardless of commit author date. Commits removed by force-push or rebase are not deleted from the destination in incremental mode (primary key `sha`); Full Refresh | Overwrite removes them.

**Connector type:** manifest-only — every stream in `manifest.yaml`, plus `components.py` for the custom components

**Analysis status:** Every stream is in the manifest; the stream-by-stream table is in `AGENTS.md`.
