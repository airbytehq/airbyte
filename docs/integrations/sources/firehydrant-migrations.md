# FireHydrant Migration Guide

## Upgrading to 1.0.0

This version fixes a typo in the `enviroments` stream name. The stream has been renamed to `environments`.

### Summary of changes

- The `enviroments` stream has been renamed to `environments`.

### Refresh affected schemas and reset data

1. Select **Connections** in the main navbar and select the connection(s) affected by the update.
1. Select the **Replication** tab, then select **Refresh source schema** and select **OK**. Any detected schema changes will be listed for your review.
1. Select **Save changes** at the bottom of the page. Ensure the **Reset affected streams** option is checked.
1. Select **Save connection**. This will reset the data in your destination and initiate a fresh sync.

For more information on resetting your data in Airbyte, see [this page](/platform/operator-guides/clear).
