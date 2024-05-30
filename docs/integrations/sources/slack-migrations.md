# Slack Migration Guide

## Upgrading to 1.0.0

We're continuously striving to enhance the quality and reliability of our connectors at Airbyte. As part of our commitment to delivering exceptional service, we are transitioning source Slack from the Python Connector Development Kit (CDK) to our innovative low-code framework. This is part of a strategic move to streamline many processes across connectors, bolstering maintainability and freeing us to focus more of our efforts on improving the performance and features of our evolving platform and growing catalog. However, due to differences between the Python and low-code CDKs, this migration constitutes a breaking change.

We’ve evolved and standardized how state is managed for incremental streams that are nested within a parent stream. This change impacts how individual states are tracked and stored for each partition, using a more structured approach to ensure the most granular and flexible state management. This change will affect the `Channel Messages` stream.

## Migration Steps

Clearing your data is required in order to continue syncing `Channel Messages` successfully. To clear your data for the `Channel Messages` stream, follow the steps below:

1. Select **Connections** in the main nav bar.
   1. Select the connection(s) affected by the update.
2. Select the **Status** tab.
   1. In the **Enabled streams** list, click the three dots on the right side of the `Channel Messages` and select **Clear Data**.

After the clear succeeds, trigger a sync by clicking **Sync Now**. For more information on clearing your data in Airbyte, see [this page](https://docs.airbyte.com/operator-guides/reset).
