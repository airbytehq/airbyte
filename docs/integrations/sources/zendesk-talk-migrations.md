# Zendesk Talk Migration Guide

## Upgrading to 1.0.0

We're continuously striving to enhance the quality and reliability of our connectors at Airbyte. As part of our commitment to delivering exceptional service, we are transitioning source zendesk-talk from the Python Connector Development Kit (CDK) to our innovative low-code framework. This is part of a strategic move to streamline many processes across connectors, bolstering maintainability and freeing us to focus more of our efforts on improving the performance and features of our evolving platform and growing catalog. However, due to differences between the Python and low-code CDKs, this migration constitutes a breaking change.

We’ve evolved and standardized how state is managed for incremental streams that are nested within a parent stream. This change impacts how individual states are tracked and stored for each partition, using a more structured approach to ensure the most granular and flexible state management. This change will affect the `calls` and `call_legs` streams.

To gracefully handle these changes for your existing connections, we highly recommend resetting your data before resuming your data syncs with the new version.

## Migration Steps

### Connector upgrade guide

[Help with upgrades](/platform/managing-airbyte/connector-updates).

### Refresh affected schemas and reset data

1. Select **Connections** in the main nav bar.
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

For more information on resetting your data in Airbyte, see [this page](/platform/operator-guides/clear).
