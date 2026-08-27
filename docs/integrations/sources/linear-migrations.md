# Linear Migration Guide

## Upgrading to 1.0.0

This release adds `date` and `date-time` schema formats to Linear temporal fields so Airbyte destinations store them as typed date and timestamp columns instead of strings. It also removes Linear's deprecated `users.inviteHash`, `teams.inviteHash`, `teams.private`, and `customer_statuses.type` fields and replaces `teams.private` with `teams.visibility`.

Users syncing any of these streams are affected by temporal column type changes: `attachments`, `comments`, `customer_needs`, `customer_statuses`, `customer_tiers`, `customers`, `cycles`, `issue_labels`, `issue_relations`, `issues`, `project_milestones`, `project_statuses`, `projects`, `teams`, `users`, and `workflow_states`. Users syncing `users`, `teams`, or `customer_statuses` are also affected by the deprecated-field removals.

After upgrading to 1.0.0, refresh the source schema and clear these affected streams before the first sync. Update downstream models and queries that cast the changed columns from strings to use the new date and timestamp column types.

:::warning Preserve history before clearing incremental streams
If **Start Date** is unset, do not clear `attachments`, `comments`, `customer_needs`, `customers`, `cycles`, `issue_labels`, `issues`, `project_milestones`, `projects`, `teams`, `users`, or `workflow_states` yet. First set and save **Start Date** to a fixed UTC timestamp at or before the earliest `updatedAt` record that you need to retain. When **Start Date** is unset, a fresh sync recalculates it as two years before that sync, so records older than the new boundary are not reloaded after the clear.
:::

### Refresh affected schemas and clear data

1. Select **Connections** in the main nav bar.
   1. Select the connection affected by the update.
2. Select the **Schema** tab.
   1. Select **Refresh source schema**.
   2. Select **OK**.

:::note
Any detected schema changes will be listed for your review.
:::

3. Select **Save changes** at the top right of the page.
   1. Ensure the **Reset affected streams** option is checked.

:::note
Depending on destination type you may not be prompted to reset your data.
:::

4. Select **Save connection**.

:::note
This will clear data in the affected streams and initiate a fresh sync.
:::

For more information on clearing your data in Airbyte, see [this page](/platform/operator-guides/clear).
