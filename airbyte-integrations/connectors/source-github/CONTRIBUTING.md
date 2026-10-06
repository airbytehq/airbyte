# Contributing to source-github

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

This connector is manifest-only: `manifest.yaml` serves every stream (with every JSON schema inline) and runs on the `source-declarative-manifest` base image. `components.py` holds the custom components the manifest names by `class_name`; `unit_tests/` is a self-contained poetry project (`cd unit_tests && poetry install --no-root && poetry run pytest`). See `AGENTS.md` for the details a change needs to respect.

## Incremental Stream Considerations

The GitHub REST and GraphQL APIs support `since` parameter on many list endpoints and `updated` sorting.

**Connector type:** manifest-only — every stream in `manifest.yaml`, plus `components.py` for the custom components

**Analysis status:** Every stream is in the manifest; the stream-by-stream table is in `AGENTS.md`.
