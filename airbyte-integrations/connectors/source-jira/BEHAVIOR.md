# source-jira: Unique Behaviors

## 1. Global Silent 400 Error Ignoring

The base error handler for source-jira silently ignores ALL HTTP 400 (Bad Request) responses across every stream. This means any malformed request, invalid JQL query, unsupported field, or missing parameter will produce zero records for that request rather than raising an error.

Many individual streams add additional IGNORE rules for 403 and 404, meaning permission errors and missing resources are also silently skipped.

**Why this matters:** If a Jira instance changes its configuration (e.g., disabling a feature or changing field availability), affected streams will silently return fewer or zero records instead of alerting the user. Debugging missing data requires checking API responses directly, as the connector intentionally suppresses these errors to handle the wide variation in Jira instance configurations.
