# Jira Migration Guide

## Upgrading to 5.0.0

Atlassian is removing the `GET /rest/api/3/workflow/search` endpoint on June 1, 2026 (see Atlassian's [CHANGE-2569](https://developer.atlassian.com/cloud/jira/platform/changelog/#CHANGE-2569)). This version of the source-jira connector migrates the `workflows` stream to the replacement endpoint `GET /rest/api/3/workflows/search`, which returns a different response shape.

### What changed

- The primary key of the `workflows` stream changed from `[entityId, name]` to `[id]`.
- The replacement endpoint returns global and project workflows. The deprecated endpoint returned published classic workflows and didn't return next-gen workflows.
- Record-level field changes:
  - `id` is now a top-level UUID string (previously an object `{ entityId, name }`).
  - `name` is now a top-level string (previously nested inside `id`).
  - New fields: `isEditable`, `scope`, `taskId`, `version`, `loopedTransitionContainerLayout`, `startPointLayout`.
  - Removed fields: `isDefault`, `hasDraftWorkflow`, `operations`, `projects`, `schemes`.
  - `transitions[]` items now use `links`, `actions`, `conditions`, `validators`, `triggers`, `transitionScreen`, and `toStatusReference` instead of `from`, `to`, `rules.postFunctions`, and `screen`.
  - `statuses[]` items now include `statusReference`, `statusCategory`, and `layout` in addition to `id` and `name`.
  - `created` and `updated` are now nullable and are no longer guaranteed to be ISO date-time formatted strings.

### Who is affected

Users syncing the `workflows` stream. Users who do not sync this stream can upgrade without action.

### Steps to migrate

1. Select **Connections** in the main navbar, then select the affected connection(s).
2. Select the **Schema** tab and click **Refresh source schema**, then **OK**.
3. Select **Save changes** at the bottom of the page.
4. Select the **Status** tab, click the three-dot menu on the **Workflows** stream, and press **Clear data**.
5. Return to the **Schema** tab, re-enable the stream if needed, and select **Sync now**.

For more information on resetting your data in Airbyte, see [this page](/platform/operator-guides/clear).

If you have downstream models that depend on the previous shape of `workflows` records, update them to read the workflow identifier from `id` (string) instead of `id.entityId`, the workflow name from `name` (string) instead of `id.name`, and transition source/target references from `transitions[].links[].fromStatusReference` / `toStatusReference` instead of `transitions[].from` / `to`.

## Upgrading to 4.0.0

This is a breaking change for users syncing the **Pull Requests** stream, which will no longer be supported moving forward. This version removes all code pertaining to this stream, as well as the `enable_experimental_streams` config option.

Users who do not have this stream enabled will not be affected and can safely upgrade to version `4.0.0`. If you are syncing data from this stream, please:

1. Select **Connections** in the main navbar, then select the connection(s) affected by the update.
2. Select the **Schema** tab.
3. Disable the `pull_requests` stream
4. In the main navbar, navigate to the **Sources** tab and select the affected Jira source. Set the `enable_experimental_streams` field to false and save your changes.

If you're a self-managed user and can't upgrade to the new version yet, you can pin the connector to a specific version. [Help managing upgrades](/platform/managing-airbyte/connector-updates).

## Upgrading to 3.0.0

This is a breaking change for **Workflows** stream, which used `Id` field as pk.
This version introduces changing of pk from `Id`(type: object) to composite pk `[entityId, name]`(type: string, string), as it makes stream compatible with destinations that do not support complex primary keys(e.g. BigQuery).

To gracefully handle these changes for your existing connections, we highly recommend resetting your data before resuming your data syncs with the new version. The **Workflows** stream can be manually reset in the following way:

1. Select **Connections** in the main navbar.
   1. Select the connection(s) affected by the update.
2. Select the **Schema** tab.
3. Click **Refresh source schema**, then **Ok**.
4. Select **Save changes** at the bottom of the page.
5. Select the **Status** tab and click three dots on the right side of **Workflows**.
6. Press the **Clear data** button.
7. Return to the **Schema** tab.
8. Check all your streams.
9. Select **Sync now** to sync your data

For more information on resetting your data in Airbyte, see [this page](/platform/operator-guides/clear).

## Upgrading to 2.0.0

We're continuously striving to enhance the quality and reliability of our connectors at Airbyte. As part of our commitment to delivering exceptional service, we are transitioning source-jira from the Python Connector Development Kit (CDK) to our innovative low-code framework. This is part of a strategic move to streamline many processes across connectors, bolstering maintainability and freeing us to focus more of our efforts on improving the performance and features of our evolving platform and growing catalog. However, due to differences between the Python and low-code CDKs, this migration constitutes a breaking change.

To gracefully handle these changes for your existing connections, we highly recommend resetting your data before resuming your data syncs with the new version. The **Issues**, **Board Issues** and **Sprint Issues** streams can be manually reset in the following way:

1. Select **Connections** in the main navbar.
   1. Select the connection(s) affected by the update.
2. Select the **Schema** tab.
3. Uncheck all streams except the affected ones.
4. Select **Save changes** at the bottom of the page.
5. Select the **Settings** tab.
6. Press the **Clear your data** button.
7. Return to the **Schema** tab.
8. Check all your streams.
9. Select **Sync now** to sync your data

For more information on resetting your data in Airbyte, see [this page](/platform/operator-guides/clear).

## Upgrading to 1.0.0

Note: this change is only breaking if you are using the `Boards Issues` stream in Incremental Sync mode.

This is a breaking change because Stream State for `Boards Issues` will be changed, so please follow the instructions below to migrate to version 1.0.0:

1. Select **Connections** in the main navbar.
   1. Select the connection(s) affected by the update.
2. Select the **Replication** tab.
   1. Select **Refresh source schema**.
   :::note
     Any detected schema changes will be listed for your review.
   :::
   2. Select **OK**.
3. Select **Save changes** at the bottom of the page.
   1. Ensure the **Reset affected streams** option is checked.
   :::note
     Depending on destination type you may not be prompted to reset your data
   :::
4. Select **Save connection**.
   :::note
 This will reset the data in your destination and initiate a fresh sync.
   :::

For more information on resetting your data in Airbyte, see [this page](/platform/operator-guides/clear).
