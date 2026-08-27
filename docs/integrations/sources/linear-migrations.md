# Linear Migration Guide

## Upgrading to 1.0.0

This update changes date and timestamp fields from strings to date and timestamp
columns. It also removes the deprecated `users.inviteHash`, `teams.inviteHash`,
`teams.private`, and `customer_statuses.type` fields. The `teams.visibility`
field replaces `teams.private`.

Refresh the source schema and clear the affected streams after upgrading. If
your downstream models or queries cast these columns from strings, update them
to use the new date and timestamp column types.

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
