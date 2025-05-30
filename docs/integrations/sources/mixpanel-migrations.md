# Mixpanel Migration Guide

## Upgrading to 3.0.0

In this release, we introduce breaking change for `CohortMembers` stream:

- State is changed to per-partition format.
- Key is changed to a unique key (based on `distinct_id` and `cohort_id` fields). The previous key was not unique and didn't support the possibility for user be in multiple cohorts.

To gracefully handle these changes for your existing connections, we highly recommend resetting your data before resuming your data syncs with the new version.

:::note
To add start date filtering for the `Cohorts`, `CohortMembers`, and `Engage` streams, the default retrieval range has been updated from all existing records to only include records created within the past year if start date not provided.
:::

## Migration Steps

### For Airbyte Open Source: Update the local connector image

Airbyte Open Source users must manually update the connector image in their local registry before proceeding with the migration. To do so:

1. Select **Settings** in the main navbar.
   1. Select **Sources**.
2. Find `Mixpanel` in the list of connectors.

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

For more information on resetting your data in Airbyte, see [this page](/operator-guides/clear).

## Upgrading to 2.0.0

In this release, the default primary key for stream Export has been deleted, allowing users to select the key that best fits their data. Refreshing the source schema and resetting affected streams is necessary only if new primary keys are to be applied following the upgrade.

## Upgrading to 1.0.0

In this release, the datetime field of stream engage has had its type changed from date-time to string due to inconsistent data from Mixpanel. Additionally, the primary key for stream export has been fixed to uniquely identify records. Users will need to refresh the source schema and reset affected streams after upgrading.
