# Metabase Migration Guide

## Upgrading to 2.0.0

Source Metabase has updated the `dashboards` stream's endpoint due to the previous endpoint being deprecated by the service. The new version no longer returns the `creator` field for the `dashboards` stream.

## Connector upgrade guide

[Help with upgrades](/platform/managing-airbyte/connector-updates).

### Refresh affected schemas and reset data

1. Select **Connections** in the main navbar.
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
