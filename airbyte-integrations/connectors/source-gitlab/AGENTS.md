> NOTE: CLAUDE.md is a symlink to AGENTS.md; update AGENTS.md (not the symlink) when changing these instructions.

# source-gitlab: Unique Behaviors

## 1. Single-Use Rotating Refresh Tokens

GitLab's OAuth implementation issues single-use refresh tokens. Every time an access token is refreshed, the old refresh token is invalidated and a new one is returned. The connector uses `refresh_token_updater` to persist the new refresh token back to the connection configuration after each token exchange.

**Why this matters:** If a token refresh succeeds but the new refresh token fails to persist (e.g., due to a crash or network issue between the exchange and the config update), the connection becomes permanently broken and requires re-authentication. Standard OAuth connectors can retry with the same refresh token, but GitLab cannot.

## Incremental Stream Considerations

The GitLab API supports `updated_after` filtering on many endpoints. The connector uses Python custom components (`GroupStreamsPartitionRouter`, `ProjectStreamsPartitionRouter`) referenced from the manifest to partition its declarative streams by group/project.

`pipelines_extended`, `jobs`, and `pipeline_trigger_jobs` are incremental via `incremental_dependency: true` on the `pipelines` parent with `global_substream_cursor: true`. Their shared cursor, `pipeline_updated_at` (the parent pipeline's `updated_at` taken from `extra_fields`), only holds state: it is never sent to GitLab, and its far-future `end_datetime` stops it from skipping a pipeline the parent returned when the stored value is later than the worker clock. Keep the cursor key different from the parent's `updated_at`: when the child state has no `parent_state`, the CDK applies the child's global `state` to the parent. Job-level changes that don't bump the parent pipeline's `updated_at` (erased jobs, expired artifacts, `downstream_pipeline` status in `pipeline_trigger_jobs`) are not re-read in incremental mode. These streams also honor incoming state in Full Refresh mode (the platform clears it at the start of each Full Refresh sync), so callers outside the platform must not pass a previous sync's state for them.

**Connector type:** Manifest-only connector with Python custom partition routers.

**Analysis status:** Streams are defined in the manifest and use Python custom partition routers. Full stream-by-stream analysis requires reviewing the manifest and custom router behavior.

`deployments`, `project_milestones`, and `group_milestones` use a one-window `updated_at` cursor starting at 1970-01-01, not `start_date`, so Full Refresh and the first Incremental sync retain their full-history scope. `merge_request_commits` uses an incremental dependency on `merge_requests` and stores the parent `updated_at` as `merge_request_updated_at`; this cursor differs from the parent's `updated_at` and is never sent to GitLab. Consequently, only commits for merge requests returned by the incremental parent query are read, and commit changes that do not update the parent merge request's `updated_at` are not picked up.

### Future incremental stream candidates

- Further stream-by-stream incremental analysis should review the declarative manifest, custom partition routers, cursor fields, and API endpoints.
