# Zendesk Chat Migration Guide

## Upgrading to 1.0.0

The Live Chat API [changed its URL structure](https://developer.zendesk.com/api-reference/live-chat/introduction/) to use the Zendesk subdomain.
The `subdomain` field of the connector configuration is now required. 
You can find your Zendesk subdomain by following instructions [here](https://support.zendesk.com/hc/en-us/articles/4409381383578-Where-can-I-find-my-Zendesk-subdomain).

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
