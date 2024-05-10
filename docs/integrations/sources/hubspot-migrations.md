# HubSpot Migration Guide

## Upgrading to 4.0.0

:::note
This change is only breaking if you are syncing streams `Deals Property History` or `Companies Peoperty History`.
:::

This update brings extended schema with data type changes for the Marketing Emails stream.

Users should:

- Refresh the source schema for the Marketing Emails stream.
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

## Upgrading to 3.0.0

:::note
This change is only breaking if you are syncing the Marketing Emails stream.
:::

This update brings extended schema with data type changes for the Marketing Emails stream.

Users should:

- Refresh the source schema for the Marketing Emails stream.
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

## Upgrading to 2.0.0

:::note
This change is only breaking if you are syncing the Property History stream.
:::

With this update, you can now access historical property changes for Deals and Companies, in addition to Contacts. To facilitate this change, the Property History stream has been renamed to Contacts Property History (since it contained historical property changes from Contacts) and two new streams have been added: Deals Property History and Companies Property History.

This constitutes a breaking change as the Property History stream has been deprecated and replaced with the Contacts Property History. Please follow the instructions below to migrate to version 2.0.0:

1. Select **Connections** in the main navbar.
   1. Select the connection(s) affected by the update.
2. Select the **Replication** tab.
   1. Select **Refresh source schema**.

:::note
Any detected schema changes will be listed for your review. Select **OK** to proceed.
:::

3. Select **Save changes** at the bottom of the page.
   1. Ensure the **Reset affected streams** option is checked.

:::note
Depending on destination type you may not be prompted to reset your data
:::

4. Select **Save connection**.

:::note
This will reset the data in your destination and initiate a fresh sync.
:::

For more information on resetting your data in Airbyte, see [this page](https://docs.airbyte.com/operator-guides/reset).
