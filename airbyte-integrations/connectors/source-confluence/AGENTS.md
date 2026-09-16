> NOTE: CLAUDE.md is a symlink to AGENTS.md; update AGENTS.md (not the symlink) when changing these instructions.

# Contributing to source-confluence

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Incremental Stream Considerations

The Confluence Cloud REST API uses cursor-based pagination. The `audit` endpoint supports `startDate`/`endDate` filtering but records are append-only (audit logs). The `blog_posts`, `pages`, `group`, and `space` endpoints do not support `updated_at`-style filtering via query parameters.

| Stream | Volume Tier | Relationship | Cursor Field | API Incremental Support | Current Status | Notes |
|---|---|---|---|---|---|---|
| audit | medium | top-level parent | none | created_at_only | deferred_no_api_support | Append-only audit log; supports startDate/endDate but records are immutable |
| blog_posts | medium | top-level parent | none | none | deferred_no_api_support | No date filter on list endpoint; has sort but no filter |
| group | small | top-level parent | none | none | deferred_no_api_support | Config-style lookup |
| pages | large | top-level parent | none | none | deferred_no_api_support | No date filter on list endpoint |
| space | small | top-level parent | none | none | deferred_no_api_support | Config-style lookup |

### Future incremental stream candidates

- **No API date filter (5 streams):** `audit`, `blog_posts`, `group`, `pages`, `space` — these streams do not have a documented date-based filter on their list endpoints. A future agent should verify via live API probing whether undocumented filter parameters are accepted.
