# Asana Migration Guide

## Upgrading to 1.0.0

We're continuously striving to enhance the quality and reliability of our connectors at Airbyte.
As part of our commitment to delivering exceptional service, we are transitioning source Asana from the Python Connector Development Kit (CDK) to our innovative low-code framework.
This is part of a strategic move to streamline many processes across connectors, bolstering maintainability and freeing us to focus more of our efforts on improving the performance and features of our evolving platform and growing catalog.
However, due to differences between the Python and low-code CDKs, this migration constitutes a breaking change. 

This release introduces an updated data type of the `name` field in the `events` stream. Users will need to reset this stream after upgrading.

## Connector upgrade guide

[Help with upgrades](/platform/managing-airbyte/connector-updates).

### Refresh affected schemas and reset data

1. Select **Connections** in the main nav bar.
   1. Select the connection(s) affected by the update.
2. Select the **Replication** tab. 1. Select **Refresh source schema**. 2. Select **OK**.
   :::note
   Any detected schema changes will be listed for your review.
   :::
3. Select **Save changes** at the bottom of the page. 1. Ensure the **Reset affected streams** option is checked.
   :::note
   Depending on destination type you may not be prompted to reset your data.
   :::
4. Select **Save connection**.
   :::note
   This will reset the data in your destination and initiate a fresh sync.
   :::

For more information on resetting your data in Airbyte, see [this page](/platform/operator-guides/clear).

