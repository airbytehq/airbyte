# source-asana: Unique Behaviors

## 1. `tasks` is incremental; its child substreams remain full-refresh

This connector recently gained incremental sync on the `tasks` stream (using the Asana API's `modified_since` filter against `task.modified_at`). The four substreams that partition off `tasks` — `stories`, `stories_compact`, `attachments`, `attachments_compact` — remain full-refresh and have no cursor of their own. On every sync, those children re-iterate every parent partition the partition router yields.

`incremental_dependency: true` is intentionally NOT set on the partition routers for these children. The flag is a partition-router optimization that only takes effect when the child has its own cursor (an `incremental_sync` block, or `is_client_side_incremental: true`); on full-refresh children it is inert because there is no child-state mechanism to persist `parent_state` into. See the platform docs at [Incremental Dependency](https://docs.airbyte.com/platform/connector-development/config-based/understanding-the-yaml-file/incremental-syncs#incremental-dependency) for the mechanism, and in particular [When `incremental_dependency` has no effect](https://docs.airbyte.com/platform/connector-development/config-based/understanding-the-yaml-file/incremental-syncs#when-incremental_dependency-has-no-effect).

### Empirical verification matrix (live, 2026-04-27 against the Asana API, `Airbyte, Inc` workspace, `Illustrations` project, test task `1214303992681244`)

This matrix is retained as forward-compatible record. It documents whether each child mutation advances `task.modified_at` — the parent-cursor-bump assumption — so that if a future change gives any of these children their own cursor and activates `incremental_dependency: true` on its router, the safety question is already answered for the Asana API as observed on this date.

The verification pattern is: capture `task.modified_at`, perform the child mutation against the live API, re-fetch the task, check whether `modified_at` advanced.

| Child stream(s) | Mutation tested | `task.modified_at` bumps? |
|---|---|---|
| `stories`, `stories_compact` | Add story (comment) via `POST /tasks/{task_gid}/stories` | YES |
| `attachments`, `attachments_compact` | Add URL-attachment via `POST /attachments?parent={task_gid}` | YES |
| (sanity baseline) | Rename task via `PUT /tasks/{task_gid}` | YES |

All four children would be empirically safe under `incremental_dependency: true` on the Asana API as observed on the verification date — but the flag is not currently enabled because the children lack a cursor of their own.

**Why this matters:** if the Asana API changes its behavior — e.g., stops bumping `task.modified_at` on a particular child mutation — the verification result changes accordingly. Re-run the verification pattern before activating `incremental_dependency: true` on any of these children in the future, and re-verify the existing matrix periodically. The verification methodology and decision tree are documented in the [`add-incremental-stream-support` skill](https://github.com/airbytehq/ai-skills/blob/main/.agents/skills/add-incremental-stream-support/SKILL.md).

**Cross-reference:** the source-jira matrix (in `airbyte-integrations/connectors/source-jira/CONTRIBUTING.md`) shows that Atlassian's API behaves differently per child resource type — issue properties do NOT bump `issue.updated`. The result is API-specific: every connector's children must be verified independently before activating `incremental_dependency: true`, even when using the same partition-router mechanism.
