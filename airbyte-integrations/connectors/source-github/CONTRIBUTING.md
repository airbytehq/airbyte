# Contributing to source-github

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Migration to manifest-only (complete)

This connector is manifest-driven: `source_github/manifest.yaml` serves every stream, with every JSON schema inline (`source_github/schemas/` no longer exists). The Python that is left is `source_github/source.py` (config validation, repository resolution, `check`, and the `read`/`discover` overrides) and `source_github/components.py` (the custom components the manifest names by `class_name`). See `AGENTS.md` for the details a change needs to respect.

## Incremental Stream Considerations

The GitHub REST and GraphQL APIs support `since` parameter on many list endpoints and `updated` sorting.

**Connector type:** manifest-driven — every stream in `manifest.yaml`, plus `components.py` for the custom components

**Analysis status:** Every stream is in the manifest; the per-step notes below cover them all.

### Future incremental stream candidates

- **The five streams migrated in Step 3** (`assignees`, `branches`, `collaborators`, `issue_labels`, `tags`) have no usable cursor: none of their endpoints returns an `updated_at`/`created_at` field or accepts `since`, so they stay full refresh.
- **The three streams migrated in Step 4** (`organizations`, `teams`, `users`) stay full refresh for the same reason, and they slice on organizations rather than repositories. `teams` and `users` carry an injected `organization` field; `organizations` does not, because the Python class it replaced never added one.
- **The six streams migrated in Step 9** (`releases`, `projects_v2`, `pull_request_stats`, `reviews`, `issue_reactions`, `pull_request_comment_reactions`) are the GraphQL streams. All six are client-side incremental: GraphQL exposes no `since` filter, so the cursor window is applied to the records the query returns. `pull_request_stats` and `reviews` read newest-first and stop at the first already-synced pull request.
