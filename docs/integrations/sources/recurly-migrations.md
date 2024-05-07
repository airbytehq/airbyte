# Recurly Migration Guide

## Upgrading to 1.0.0

We recently rolled out an update to the Recurly connector using a newer version of our CDK, as well as introducing several additions to the existing stream schemas. Our aim with these updates is always to enhance the connector's functionality and provide you with a richer set of data to support your integration needs.

While our intention was to make these updates as seamless as possible, we've observed that some users are experiencing issues during the "Discover" step of the sync process. This has led us to re-categorize the recent changes as breaking updates, despite not removing fields or altering property names within the schema.

Once you have migrated to the new version, we highly recommend all users refresh their schemas and reset their data before resuming syncs

### For Airbyte Open Source: Update the local connector image

Airbyte Open Source users with existing connections must manually update the connector image in their local registry before proceeding with the migration. To do so:

1. Select **Settings** in the main navbar.
   1. Select **Sources**.
2. Find Recurly in the list of connectors.

:::note
You will see two versions listed, the current in-use version and the latest version available.
:::

3. Select **Change** to update your OSS version to the latest available version.

### Update the connector version

1. Select **Sources** in the main navbar.
2. Select the instance of the connector you wish to upgrade.

:::note
Each instance of the connector must be updated separately. If you have created multiple instances of a connector, updating one will not affect the others.
:::

3. Select **Upgrade**
   1. Follow the prompt to confirm you are ready to upgrade to the new version.

### Refresh schemas and reset data

1. Select **Connections** in the main navbar.
2. Select the connection(s) affected by the update.
3. Select the **Replication** tab.
   1. Select **Refresh source schema**.
   2. Select **OK**.

:::note
Any detected schema changes will be listed for your review.
:::

4. Select **Save changes** at the bottom of the page.
   1. Ensure the **Reset all streams** option is checked.
5. Select **Save connection**.

:::note
This will reset the data in your destination and initiate a fresh sync.
:::

For more information on resetting your data in Airbyte, see [this page](https://docs.airbyte.com/operator-guides/reset).
