# source-asana: Unique Behaviors

## 1. `incremental_dependency: true` on `tasks` Child Substreams

The `stories`, `stories_compact`, `attachments`, and `attachments_compact` streams partition off the `tasks` parent stream and use `incremental_dependency: true` on the `ParentStreamConfig`. This is a partition-router optimization, not a sync-mode declaration:
- The children themselves declare `supported_sync_modes: [full_refresh]` in the discover catalog (they have no own cursor).
- On a warm sync, the parent partition router restricts iteration to `tasks` whose `modified_at` cursor has advanced since the last sync.
- This is only safe if every mutation on the child resource bumps `task.modified_at`. If it does not, the child mutation is silently skipped on warm syncs, and by the time the parent's cursor advances for unrelated reasons the missed mutation is unrecoverable. This is a source-side correctness bug, not just a destination-mode amplification.

### Empirical verification matrix (live, 2026-04-27 against the Asana API, `Airbyte, Inc` workspace, `Illustrations` project, test task `1214303992681244`)

The verification pattern is: capture `task.modified_at`, perform the child mutation against the live API, re-fetch the task, check whether `modified_at` advanced.

| Child stream(s) | Mutation tested | `task.modified_at` bumps? |
|---|---|---|
| `stories`, `stories_compact` | Add story (comment) via `POST /tasks/{task_gid}/stories` | YES |
| `attachments`, `attachments_compact` | Add URL-attachment via `POST /attachments?parent={task_gid}` | YES |
| (sanity baseline) | Rename task via `PUT /tasks/{task_gid}` | YES |

All 4 children using `incremental_dependency: true` are empirically safe on the Asana API.

**Why this matters:** if the Asana API changes its behavior — e.g., stops bumping `task.modified_at` on a particular child mutation — the safety of `incremental_dependency: true` for that child changes accordingly. Re-run the verification pattern before adding new substreams to the `incremental_dependency: true` set, and re-verify the existing matrix periodically. The verification methodology and decision tree are documented in the [`add-incremental-stream-support` skill](https://github.com/airbytehq/ai-skills/blob/main/.agents/skills/add-incremental-stream-support/SKILL.md).

**Cross-reference:** the source-jira matrix (in `airbyte-integrations/connectors/source-jira/CONTRIBUTING.md`) shows that Atlassian's API behaves differently per child resource type — issue properties do NOT bump `issue.updated`. The result is API-specific: every connector's children must be verified independently, even when using the same `incremental_dependency` mechanism.
