import MigrationGuide from '@site/static/\_migration_guides_upgrade_guide.md';

# OpenAI Ads Migration Guide

## Upgrading to 1.0.0

:::note
This change is only breaking if you are syncing the `spend_limit_windows` stream.
:::

The `start_date` and `end_date` fields of the `spend_limit_windows` stream are now declared with `format: date`, because the [OpenAI Ads API](https://developers.openai.com/ads/api-reference/ad-account) returns them as `YYYY-MM-DD` dates. Destinations that support a date type now store these columns as dates instead of strings.

### Migration Steps

### Refresh affected schemas and reset data

1. Select **Connections** in the main nav bar.
   1. Select the connection affected by the update.
1. Select the **Schema** tab.
   1. Select **Refresh source schema**.
   1. Select **OK**.

:::note
Any detected schema changes will be listed for your review.
:::

1. Select **Save changes** at the top right of the page.
   1. Ensure the **Reset affected streams** option is checked.

:::note
Depending on destination type you may not be prompted to reset your data.
:::

1. Select **Save connection**.

:::note
This will reset the data in your destination and initiate a fresh sync.
:::

For more information on resetting your data in Airbyte, see [this page](/platform/operator-guides/clear)

## Connector upgrade guide

<MigrationGuide />
