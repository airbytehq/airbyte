# Gitlab Migration Guide

## Upgrading to 4.0.0

We're continuously striving to enhance the quality and reliability of our connectors at Airbyte.
As part of our commitment to delivering exceptional service, we are transitioning Source Gitlab from the Python Connector Development Kit (CDK)
to our new low-code framework improving maintainability and reliability of the connector.
However, due to differences between the Python and low-code CDKs, this migration constitutes a breaking change.

The primary key was changed for streams `group_members`, `group_labels`, `project_members`, `project_labels`, `branches`, and `tags`.
Users will need to reset the affected streams after upgrading.

## Connector Upgrade Guide

### For Airbyte Open Source: Update the local connector image

Airbyte Open Source users must manually update the connector image in their local registry before proceeding with the migration. To do so:

1. Select **Settings** in the main navbar.
   1. Select **Sources**.
2. Find Gitlab in the list of connectors.

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

## Upgrading to 3.0.0

In this release, `merge_request_commits` stream schema has been fixed so that it returns commits for each merge_request.
Users will need to refresh the source schema and reset `merge_request_commits` stream after upgrading.

## Connector Upgrade Guide

### For Airbyte Open Source: Update the local connector image

Airbyte Open Source users must manually update the connector image in their local registry before proceeding with the migration. To do so:

1. Select **Settings** in the main navbar.
   1. Select **Sources**.
2. Find Gitlab in the list of connectors.

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

In the 2.0.0 config change, several streams were updated to date-time field format, as declared in the Gitlab API.
These changes impact `pipeline.created_at` and` pipeline.updated_at` fields for stream Deployments and `expires_at` field for stream Group Members and stream Project Members.
You will need to refresh the source schema and reset affected streams after upgrading.
