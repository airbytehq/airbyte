import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

# Linear Migration Guide

## Upgrading to 1.0.0

This release adds `date` and `date-time` schema formats to Linear temporal fields so Airbyte destinations store them as typed date and timestamp columns instead of strings. It also removes fields Linear has deprecated — `users.inviteHash`, `users.calendarHash`, `teams.inviteHash`, `teams.private`, `teams.markedAsDuplicateWorkflowState` (and the derived `teams.markedAsDuplicateWorkflowStateId`), and `customer_statuses.type` — and adds `teams.visibility`, Linear's replacement for `teams.private`.

Users syncing any of these streams are affected by temporal column type changes: `attachments`, `comments`, `customer_needs`, `customer_statuses`, `customer_tiers`, `customers`, `cycles`, `issue_labels`, `issue_relations`, `issues`, `project_milestones`, `project_statuses`, `projects`, `teams`, `users`, and `workflow_states`. Users syncing `users`, `teams`, or `customer_statuses` are also affected by the deprecated-field removals.

After upgrading to 1.0.0, refresh the source schema and clear these affected streams before the first sync. Update downstream models and queries that cast the changed columns from strings to use the new date and timestamp column types.

### Replacing `teams.private` with `teams.visibility`

`teams.visibility` is a string with three possible values, so it is not a drop-in rename of the old boolean:

| Old `private` | New `visibility` |
| --- | --- |
| `true` | `private` |
| `false` | `public` or `restricted` |

`restricted` means a non-private team inside a private-team boundary, so it is explicitly not private. Rewrite downstream logic as `visibility = 'private'` rather than `visibility != 'public'`.

:::warning Preserve history before clearing incremental streams
If **Start Date** is unset, do not clear `attachments`, `comments`, `customer_needs`, `customers`, `cycles`, `issue_labels`, `issues`, `project_milestones`, `projects`, `teams`, `users`, or `workflow_states` yet. First set and save **Start Date** to a fixed UTC timestamp at or before the earliest `updatedAt` record that you need to retain. When **Start Date** is unset, a fresh sync recalculates it as two years before that sync, so records older than the new boundary are not reloaded after the clear.
:::

Clearing deletes the affected streams' data in the destination. Snapshot anything in those tables that your warehouse cannot reconstruct from a re-sync before you begin.

<MigrationGuide />
