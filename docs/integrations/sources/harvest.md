# Harvest

This page contains the setup guide and reference information for the Harvest source connector.

## Prerequisites

To set up the Harvest source connector, you'll need the [Harvest Account ID and API key](https://help.getharvest.com/api-v2/authentication-api/authentication/authentication/).

## Setup guide

<!-- env:cloud -->
**For Airbyte Cloud:**

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces).
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select **Harvest** from the Source type dropdown.
4. Enter the name for the Harvest connector.
5. Enter your [Harvest Account ID](https://help.getharvest.com/api-v2/authentication-api/authentication/authentication/).
6. For **Start Date**, enter the date in YYYY-MM-DDTHH:mm:ssZ format. The data added on and after this date will be replicated.
7. For Authentication mechanism, select your preferred option:
    - If you choose **Authenticate via Harvest (OAuth)**, click **Authenticate your Harvest account**. Log in and authorize your Harvest account.
    - If you choose **Authenticate with Personal Access Token**, enter your [Personal Access Token](https://help.getharvest.com/api-v2/authentication-api/authentication/authentication/#personal-access-tokens).
8. Click **Set up source**.
<!-- /env:cloud -->

<!-- env:oss -->
**For Airbyte Open Source:**

1. Navigate to the Airbyte Open Source dashboard.
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select **Harvest** from the Source type dropdown.
4. Enter the name for the Harvest connector.
5. Enter your [Harvest Account ID](https://help.getharvest.com/api-v2/authentication-api/authentication/authentication/).
6. For **Start Date**, enter the date in YYYY-MM-DDTHH:mm:ssZ format. The data added on and after this date will be replicated.
7. For **Authentication mechanism**, select your preferred option:
    - If you choose **Authenticate via Harvest (OAuth)**, enter your **Client ID**, **Client Secret**, and **Refresh Token** for your Harvest developer application. (You can create an OAuth2 application in your Harvest account by going to [Developers](https://id.getharvest.com/developers))
    - If you choose **Authenticate with Personal Access Token**, enter your [Personal Access Token](https://help.getharvest.com/api-v2/authentication-api/authentication/authentication/#personal-access-tokens).
8. Click **Set up source**.
<!-- /env:oss -->

## Supported sync modes

The Harvest source connector supports the following [sync modes](https://docs.airbyte.com/cloud/the-core-concepts#connection-sync-modes):

* [Full Refresh - Overwrite](https://docs.airbyte.com/the-core-concepts/connections/full-refresh-overwrite/)
* [Full Refresh - Append](https://docs.airbyte.com/the-core-concepts/connections/full-refresh-append)
* [Incremental - Append](https://docs.airbyte.com/the-core-concepts/connections/incremental-append)
* [Incremental - Deduped History](https://docs.airbyte.com/the-core-concepts/connections/incremental-deduped-history)