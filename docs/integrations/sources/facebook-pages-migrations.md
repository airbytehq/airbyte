# Facebook Pages Migration Guide

## Upgrading to 1.0.0

:::note
This change is only breaking if you are syncing stream `Page`.
:::

This version brings an updated schema for the `v19.0` API version of the `Page` stream.
The `messenger_ads_default_page_welcome_message` field has been deleted, and `call_to_actions`, `posts`, `published_posts`, `ratings`, `tabs` and `tagged` fields have been added.

Users should:

- Refresh the source schema for the `Page` stream.
- Reset the stream after upgrading to ensure uninterrupted syncs.

### Refresh affected schemas and reset data

1. Select **Connections** in the main nav bar.
   1. Select the connection affected by the update.
2. Select the **Replication** tab.
   1. Select **Refresh source schema**.
   2. Select **OK**.

:::note
Any detected schema changes will be listed for your review.
:::

3. Select **Save changes** at the bottom of the page.
   1. Ensure the **Reset affected streams** option is checked.

:::note
Depending on destination type you may not be prompted to reset your data.
:::

4. Select **Save connection**.

:::note
This will reset the data in your destination and initiate a fresh sync.
:::

For more information on resetting your data in Airbyte, see [this page](https://docs.airbyte.com/operator-guides/reset)
