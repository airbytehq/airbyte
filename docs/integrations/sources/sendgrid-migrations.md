# Sendgrid Migration Guide

## Upgrading to 1.0.0

We're continuously striving to enhance the quality and reliability of our connectors at Airbyte.
As part of our commitment to delivering exceptional service, we are transitioning Source Sendgrid from the Python Connector Development Kit (CDK)
to our new low-code framework improving maintainability and reliability of the connector.
However, due to differences between the Python and low-code CDKs, this migration constitutes a breaking change.
  
* The configuration options have been renamed to `api_key` and `start_date`.
* The `unsubscribe_groups` stream has been removed. It was the same as `suppression_groups`. You can use that and get the same data.
* The `single_sends` stream has been renamed `singlesend_stats`. This is closer to the data and API.
* The `segments` stream has been upgraded to use the Sendgrid 2.0 API because the older one has been deprecated. The schema has changed as a result.

To ensure a smooth upgrade, please refresh your schemas and reset your data before resuming syncs.

## Connector Upgrade Guide

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


### Refresh all schemas and reset data

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


### Refresh affected schemas and reset data

1. Select **Connections** in the main navbar.
    1. Select the connection(s) affected by the update.
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

For more information on resetting your data in Airbyte, see [this page](https://docs.airbyte.com/operator-guides/reset).

