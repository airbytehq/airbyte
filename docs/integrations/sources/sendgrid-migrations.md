# Sendgrid Migration Guide

## Upgrading to 1.0.0

We're continuously striving to enhance the quality and reliability of our connectors at Airbyte.

As part of our commitment to delivering exceptional service, we are transitioning Source Sendgrid from the Python Connector Development Kit (CDK)
to our new low-code framework improving maintainability and reliability of the connector. Due to differences between the Python and low-code CDKs, this migration constitutes a breaking change.

- The configuration options have been renamed to `api_key` and `start_date`.
- The `unsubscribe_groups` stream has been removed as it was a duplicate of `suppression_groups`. You can use `suppression_groups` and get the same data you were previously receiving in `unsubscribe_groups`.
- The `single_sends` stream has been renamed to `singlesend_stats`. This was done to more closely match the data from the Sendgrid API.
- The `segments` stream has been upgraded to use the Sendgrid 2.0 API as the previous version of the API has been deprecated. As a result, fields within the stream have changed to reflect the new API.

To ensure a smooth upgrade, please clear your streams and trigger a sync to bring in historical data.

## Migration Steps

### For Airbyte Open Source: Update the local connector image

Airbyte Open Source users must manually update the connector image in their local registry before proceeding with the migration. To do so:

1. Select **Settings** in the main navbar.
   1. Select **Sources**.
2. Find Sendgrid in the list of connectors.

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

### For Airbyte Cloud and Open Source: Steps to Update Schema and Clear Streams

To clear your data for the affected streams, follow the steps below:

1. Select **Connections** in the main navbar and select the connection(s) affected by the update.
2. Select the **Schema** tab.
   1. Select **Refresh source schema** to bring in any schema changes. Any detected schema changes will be listed for your review.
   2. Select **OK** to approve changes.
3. Select **Save changes** at the bottom of the page.
   1. Ensure the **Clear affected streams** option is checked to ensure your streams continue syncing successfully with the new schema.
4. Select **Save connection**.

This will clear the data in your destination for the subset of streams with schema changes. After the clear succeeds, trigger a sync by clicking **Sync Now**. For more information on clearing your data in Airbyte, see [this page](/operator-guides/clear).
