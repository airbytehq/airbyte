# Contributing to source-github

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Migration to manifest-only (in progress)

This connector is being migrated from Python stream classes to a declarative manifest, a few streams at a time, so it is currently a hybrid: `source_github/manifest.yaml` serves the migrated streams (`repositories`, `assignees`, `branches`, `collaborators`, `issue_labels`, `tags`) and `source_github/streams.py` serves the rest. When you change a stream, check which half owns it first. Migrated streams keep their JSON schema inline in the manifest instead of under `source_github/schemas/`. See `AGENTS.md` for the details a change to either half needs to respect.

## Incremental Stream Considerations

The GitHub REST and GraphQL APIs support `since` parameter on many list endpoints and `updated` sorting.

**Connector type:** hybrid — declarative manifest plus Python CDK stream classes

**Analysis status:** Full stream-by-stream analysis requires Python code review of the streams still in `streams.py`.

### Future incremental stream candidates

- **Streams still in `streams.py` deferred for Python code review:** a full stream-by-stream incremental analysis table (per the standard CONTRIBUTING.md schema) should be added after reviewing the remaining Python stream definitions, their `cursor_field` properties, and the API endpoints they call.
- **The five streams migrated in Step 3** (`assignees`, `branches`, `collaborators`, `issue_labels`, `tags`) have no usable cursor: none of their endpoints returns an `updated_at`/`created_at` field or accepts `since`, so they stay full refresh.
