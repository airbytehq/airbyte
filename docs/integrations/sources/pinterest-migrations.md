# Pinterest Migration Guide

## Upgrading to 2.0.0

We're continuously striving to enhance the quality and reliability of our connectors at Airbyte.
As part of our commitment to delivering exceptional service, we are transitioning source Pinterest from the Python Connector Development Kit (CDK) to our innovative low-code framework.
This is part of a strategic move to streamline many processes across connectors, bolstering maintainability and freeing us to focus more of our efforts on improving the performance and features of our evolving platform and growing catalog.
However, due to differences between the Python and low-code CDKs, this migration constitutes a breaking change.

We’ve evolved and standardized how state is managed for incremental streams that are nested within a parent stream.
This change impacts how individual states are tracked and stored for each partition, using a more structured approach to ensure the most granular and flexible state management.
This change will affect the following streams:

- `ad_account_analytics`
- `ad_analytics`
- `ad_group_analytics`
- `ad_groups`
- `ads`
- `campaign_analytics`
- `campaigns`

To gracefully handle these changes for your existing connections, we highly recommend resetting your data before resuming your data syncs with the new version.

## Migration Steps

### For Airbyte Open Source: Update the local connector image

Airbyte Open Source users must manually update the connector image in their local registry before proceeding with the migration. To do so:

1. Select **Settings** in the main navbar.
   1. Select **Sources**.
2. Find Pinterest in the list of connectors.

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

### Refresh affected schemas and reset data

1. Select **Connections** in the main nav bar.
   1. Select the connection(s) affected by the update.
2. Select the **Schema** tab.
3. Uncheck all streams except the affected ones.
4. Select **Save changes** at the bottom of the page.
5. Select the **Settings** tab.
6. Press the **Clear your data** button.
7. Return to the **Schema** tab.
8. Check all your streams.
9. Select **Sync now** to sync your data

For more information on resetting your data in Airbyte, see [this page](/operator-guides/clear).

## Upgrading to 1.0.0

This release updates date-time fields with airbyte_type: timestamp_without_timezone for streams BoardPins, BoardSectionPins, Boards, Catalogs, CatalogFeeds. Additionally, the stream names AdvertizerReport and AdvertizerTargetingReport have been renamed to AdvertiserReport and AdvertiserTargetingReport, respectively.

To ensure uninterrupted syncs, users should:

- Refresh the source schema
- Reset affected streams
