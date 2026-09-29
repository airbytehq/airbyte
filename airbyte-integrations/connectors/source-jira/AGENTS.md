> NOTE: CLAUDE.md is a symlink to AGENTS.md; update AGENTS.md (not the symlink) when changing these instructions.

# source-jira: Unique Behaviors

## 1. Global Silent 400 Error Ignoring

The base error handler for source-jira silently ignores ALL HTTP 400 (Bad Request) responses across every stream. This means any malformed request, invalid JQL query, unsupported field, or missing parameter will produce zero records for that request rather than raising an error.

Many individual streams add additional IGNORE rules for 403 and 404, meaning permission errors and missing resources are also silently skipped.

**Why this matters:** If a Jira instance changes its configuration (e.g., disabling a feature or changing field availability), affected streams will silently return fewer or zero records instead of alerting the user. Debugging missing data requires checking API responses directly, as the connector intentionally suppresses these errors to handle the wide variation in Jira instance configurations.

## Incremental Stream Considerations

The Jira REST API supports `updatedDate` JQL filtering for issues and related entities. The connector uses Python custom components referenced from the manifest. PR airbytehq/airbyte#76840 (in flight) addresses inert-flag cleanup. The four child streams (`issue_remote_links`, `issue_transitions`, `issue_votes`, `issue_watchers`) lack record-level `updated` fields.

**Connector type:** Python custom components (hybrid manifest + Python)

**Analysis status:** Streams are Python-defined via custom components. PR airbytehq/airbyte#76840 is in flight for inert-flag cleanup. Full stream-by-stream analysis requires Python code review.

### Future incremental stream candidates

- **All streams deferred for Python code review:** This connector defines its streams in Python code rather than declarative manifest YAML. A full stream-by-stream incremental analysis table (per the standard CONTRIBUTING.md schema) should be added by a future agent after reviewing the Python stream definitions, their `cursor_field` properties, and the API endpoints they call.
