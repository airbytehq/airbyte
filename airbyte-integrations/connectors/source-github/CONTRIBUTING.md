# Contributing to source-github

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

This connector is manifest-only: `manifest.yaml` serves every stream (with every JSON schema inline) and runs on the `source-declarative-manifest` base image. `components.py` holds the custom components the manifest names by `class_name`; `unit_tests/` is a self-contained poetry project (`cd unit_tests && poetry install --no-root && poetry run pytest`). See `AGENTS.md` for the details a change needs to respect.

## Behavior that differs from the legacy Python connector

These are deliberate; `AGENTS.md` ("Manifest design notes") has the reasoning and the tests that pin them.

- A repository that keeps answering 502/504 fails the stream instead of being skipped silently.
- 404 and 409 skip the repository on the first response instead of after five retries.
- Skipped repositories are logged at INFO and the message cannot name the repository.
- Incremental streams re-emit the record whose cursor equals the stored state once per sync.
- State is checkpointed per partition, so an interrupted sync restarts the repository it was reading.

## Manifest comments

Keep comments in `manifest.yaml` to one to three lines that say what a definition must not lose. Put the reasoning, history and measurements in the matching `AGENTS.md` section and point to it.

## Incremental Stream Considerations

The GitHub REST and GraphQL APIs support `since` parameter on many list endpoints and `updated` sorting.

**Connector type:** manifest-only — every stream in `manifest.yaml`, plus `components.py` for the custom components

**Analysis status:** Every stream is in the manifest; the stream-by-stream table is in `AGENTS.md`.
