# Greenhouse Migration Guide

## Upgrading to 1.0.0

This update fixes a bug in the `applications` stream to retrieve updated records accurately. It requires clearing the state and syncing the stream again.

## Steps to Clear Streams

To clear your data for the impacted streams, follow the steps below:

1. Select **Connections** in the main nav bar.
   1. Select the connection(s) affected by the update.
2. Select the **Status** tab.
   1. In the **Enabled streams** list, click the three dots on the right side of the stream and select **Clear Data**.

After the clear succeeds, trigger a sync by clicking **Sync Now**. For more information on clearing your data in Airbyte, see [this page](https://docs.airbyte.com/operator-guides/reset).
