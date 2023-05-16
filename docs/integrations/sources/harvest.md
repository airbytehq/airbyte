# Harvest

This page contains the setup guide and reference information for the Harvest source connector.

## Prerequisites

To set up the Harvest source connector, you'll need the following:

- A Harvest account with administrative access.
- Your Harvest **Account ID** and **API key**. To obtain these, follow the [authentication API documentation](https://help.getharvest.com/api-v2/authentication-api/authentication/authentication/).

## Setup guide

Ensure that you follow these instructions in the order listed.

**For Airbyte Cloud:**

1. Log into your [Airbyte Cloud workspace](https://cloud.airbyte.com/workspaces).
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select **Harvest** from the Source type dropdown.
4. Enter the name for the Harvest connector.
5. Enter your Harvest **Account ID**.
6. For **Start Date**, enter the date in `YYYY-MM-DDTHH:mm:ssZ` format. The data added on and after this date will be replicated.
   - Example: `2022-12-01T00:00:00Z`
7. For Authentication mechanism, select **Authenticate via Harvest (OAuth)** from the dropdown and click **Authenticate your Harvest account**.
8. Log in to Harvest and authorize your Harvest account.
9. Click **Set up source**.

**For Airbyte Open Source:**

1. Navigate to the Airbyte Open Source dashboard.
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select **Harvest** from the Source type dropdown.
4. Enter the name for the Harvest connector.
5. Enter your Harvest **Account ID**.
6. For **Start Date**, enter the date in `YYYY-MM-DDTHH:mm:ssZ