# Zendesk Chat Migration Guide

## Upgrading to 1.0.0

Now, subdoimain is a required property in the spec, The base url is now being updated to use subdomain as per the [official update](https://developer.zendesk.com/api-reference/live-chat/introduction/) from zendesk chat documentation

### For Airbyte Open Source: Update the local connector image

Airbyte Open Source users must manually update the connector image in their local registry before proceeding with the migration. To do so:

1. Select **Settings** in the main navbar.
    - Select **Sources**.
2. Find Zendesk Chat in the list of connectors.

:::note
You will see two versions listed, the current in-use version and the latest version available.
:::

3. Select **Change** to update your OSS version to the latest available version.

### For Airbyte Cloud: Update the connector version

1. Select **Sources** in the main navbar.
2. Select the instance of the connector you wish to upgrade.

:::note
Each instance of the connector must be updated separately. If you have created multiple instances of a connector, updating one will not affect the others.
:::

3. Select **Upgrade**
    - Follow the prompt to confirm you are ready to upgrade to the new version.

### Refresh affected schemas and data

1. Select **Connections** in the main nav bar.
    - Select the connection(s) affected by the update.
2. Select the **Replication** tab.
    - Select **Refresh source schema**.
    - Select **OK**.

:::note
Any detected schema changes will be listed for your review.
:::

3. Select **Save changes** at the bottom of the page.
    - Ensure the **Refresh affected streams** option is checked.

:::note
Depending on destination type you may not be prompted to refresh your data. See below.
:::

4. Select **Save connection**.

:::note
This will refresh the data in your destination and initiate a fresh sync.
:::

For more information on refreshes your data in Airbyte, see [this page](https://docs.airbyte.com/operator-guides/refreshes).