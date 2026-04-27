# source-jira: Unique Behaviors

## 1. Global Silent 400 Error Ignoring

The base error handler for source-jira silently ignores ALL HTTP 400 (Bad Request) responses across every stream. This means any malformed request, invalid JQL query, unsupported field, or missing parameter will produce zero records for that request rather than raising an error.

Many individual streams add additional IGNORE rules for 403 and 404, meaning permission errors and missing resources are also silently skipped.

**Why this matters:** If a Jira instance changes its configuration (e.g., disabling a feature or changing field availability), affected streams will silently return fewer or zero records instead of alerting the user. Debugging missing data requires checking API responses directly, as the connector intentionally suppresses these errors to handle the wide variation in Jira instance configurations.

## 2. `incremental_dependency: true` on `issues` Child Substreams (and the One Excluded Child)

Several `issues_stream` child substreams use `incremental_dependency: true` on the `ParentStreamConfig`. This is a partition-router optimization, not a sync-mode declaration:
- The children themselves declare `supported_sync_modes: [full_refresh]` in the discover catalog (they have no own cursor).
- On a warm sync, the parent partition router restricts iteration to `issues` whose `updated` cursor has advanced since the last sync.
- This is only safe if every mutation on the child resource bumps `issue.updated`. If it does not, the child mutation is silently skipped on warm syncs, and by the time the parent's cursor advances for unrelated reasons the missed mutation is unrecoverable. This is a source-side correctness bug, not just a destination-mode amplification.

### Empirical verification matrix (live, 2026-04-27 against `airbyteio.atlassian.net`, test issue `TESTKEY13-3`)

The verification pattern is: capture `issue.updated`, perform the child mutation against the live API, re-fetch the issue, check whether `updated` advanced. Each child action was retried with a "real change" payload to avoid idempotency-driven false negatives (e.g., re-adding an existing watcher is a no-op and does not bump; remove + re-add does).

Children currently using `incremental_dependency: true`:
| Child stream | Mutation tested | `issue.updated` bumps? |
|---|---|---|
| `issue_remote_links` | Add remote link via `POST /issue/{key}/remotelink` | YES |
| `issue_votes` | Cast vote via `POST /issue/{key}/votes` | YES |
| `issue_watchers` | Remove + re-add watcher via `/issue/{key}/watchers` | YES |
| `issue_transitions` | Perform transition via `POST /issue/{key}/transitions` | YES |

Children explicitly excluded:
| Child stream | Mutation tested | `issue.updated` bumps? |
|---|---|---|
| `issue_property_keys` | Add / update / delete issue property via `/issue/{key}/properties/{key}` | NO |

`issue_property_keys` therefore does NOT use `incremental_dependency: true`. The exclusion is documented inline in the manifest (`__issue_property_keys_substream`).

**Why this matters:** if the Jira REST API changes its behavior — e.g., starts (or stops) bumping `issue.updated` on a particular child mutation — the safety of `incremental_dependency: true` for that child changes accordingly. Re-run the verification pattern before adding new substreams to the `incremental_dependency: true` set, and re-verify the existing matrix periodically. The verification methodology and decision tree are documented in the [`add-incremental-stream-support` skill](https://github.com/airbytehq/ai-skills/blob/main/.agents/skills/add-incremental-stream-support/SKILL.md).
