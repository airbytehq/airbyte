# source-gitlab: Unique Behaviors

## 1. Single-Use Rotating Refresh Tokens

GitLab's OAuth implementation issues single-use refresh tokens. Every time an access token is refreshed, the old refresh token is invalidated and a new one is returned. The connector uses `refresh_token_updater` to persist the new refresh token back to the connection configuration after each token exchange.

**Why this matters:** If a token refresh succeeds but the new refresh token fails to persist (e.g., due to a crash or network issue between the exchange and the config update), the connection becomes permanently broken and requires re-authentication. Standard OAuth connectors can retry with the same refresh token, but GitLab cannot.

## Incremental Stream Considerations

The GitLab API supports `updated_after` filtering on many endpoints. The connector uses Python custom components (`GroupStreamsPartitionRouter`, `ProjectStreamsPartitionRouter`) referenced from the manifest. Streams are defined in Python code and partitioned by group/project.

**Connector type:** Python custom components (hybrid manifest + Python)

**Analysis status:** Streams are Python-defined via custom components with custom partition routers. Full stream-by-stream analysis requires Python code review.

### Future incremental stream candidates

- **All streams deferred for Python code review:** This connector defines its streams in Python code rather than declarative manifest YAML. A full stream-by-stream incremental analysis table (per the standard CONTRIBUTING.md schema) should be added by a future agent after reviewing the Python stream definitions, their `cursor_field` properties, and the API endpoints they call.
