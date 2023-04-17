# Criteo

This page contains the setup guide and reference information for the Criteo source connector.

## Setup guide​

### Step 1: Set up Criteo​

To get your credentials, you need to create a Criteo account and then create an [Organization](https://developers.criteo.com/marketing-solutions/docs/create-your-organization) and an [App](https://developers.criteo.com/marketing-solutions/docs/create-your-app) within the [Developer Dashboard](Developer Dashboard) page.

### Step 2: Set up the Criteo connector in Airbyte

<!-- env:cloud -->
**For Airbyte Cloud:**

1. Log in to your [Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select **Criteo** from the **Source type** dropdown.
4. Enter a name for your source.
5. Click **Authenticate your Criteo account**.
   * Log in and Authorize the Criteo account. Select the permissions you want to allow Airbyte.
6. Enter the **Start Date** in YYYY-MM-DD format. All data generated after this date will be replicated.
7. Enter the **Advertiser Ids** separated by comma.
8. Select the **Dimensions** from list.
9. Select the **Metrics** from List.
10. Select the **Currency**
11. Select the **Timezone**
12. Specify the **Lookback Window**
13. Click **Set up source**.
14. Click **Set up source**.
<!-- /env:cloud -->

<!-- env:oss -->
**For Airbyte Open Source:**

1. Log in to your Airbyte Open Source account.
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select **Criteo** from the **Source type** dropdown.
4. Enter a name for your source.
5. Paste the client ID and client secret from [Step 1](#step-1-set-up-Criteo​).
6. Enter the **Start Date** in YYYY-MM-DD format.
7. Enter the **Advertiser Ids** separated by comma.
8. Select the **Dimensions** from list.
9. Select the **Metrics** from List.
10. Select the **Currency**
11. Select the **Timezone**
12. Specify the **Lookback Window**
13. Click **Set up source**.
<!-- /env:oss -->

## Supported sync modes

The Criteo source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):
* [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
* [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
* [Incremental - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)

## Supported Streams

The Criteo source connector supports the following streams. For more information, see the [Criteo API](https://developers.Criteo.com/reference/intro).

* [Statistic Report](https://developers.criteo.com/marketing-solutions/reference/getadsetreport)


## Changelog

| Version | Date       | Pull Request                                             | Subject                                                         |
|:--------|:-----------|:---------------------------------------------------------|:----------------------------------------------------------------|
| 0.1.0   | 2023-04-17 | [7092](https://github.com/airbytehq/airbyte/pull/7092)   | Initial Release                                                 |
