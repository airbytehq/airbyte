# Facebook Marketing Migration Guide

## Upgrading to 2.0.0

Streams Ads-Insights-\* streams now have updated schemas.

:::danger
Please note that data older than 37 months will become unavailable due to Facebook limitations.
It is recommended to create a backup at the destination before proceeding with migration.
:::

### Update Custom Insights Reports (this step can be skipped if you did not define any)

1. Select **Sources** in the main navbar.
   1. Select the Facebook Marketing Connector.
2. Select the **Retest saved source**.
3. Remove unsupported fields from the list in Custom Insights section.
4. Select **Test and Save**.

### Refresh affected schemas and reset data

1. Select **Connections** in the main navbar.
   1. Select the connection(s) affected by the update.
2. Select the **Replication** tab.
   1. Select **Refresh source schema**.
   2. Select **OK**.

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

For more information on resetting your data in Airbyte, see [this page](https://docs.airbyte.com/operator-guides/reset).
