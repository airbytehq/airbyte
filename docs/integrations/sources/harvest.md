# Harvest

This page contains the setup guide and reference information for the Harvest source connector.

## Prerequisites

To set up the Harvest source connector, you'll need the following:

- A [Harvest Account ID and API key](https://help.getharvest.com/api-v2/authentication-api/authentication/authentication/).

## Setup guide

<!-- env:cloud -->
**For Airbyte Cloud:**

1. Log into your [Harvest account](https://id.getharvest.com/external_sessions/new?redirect=&_ga=2.188922882.1670427647.1658452883-143018431.1658452883) and go to `Developers` (if you do not see Developers, contact your Harvest Account Administrator).
2. Click on `Create New Personal Access Token`.
3. Enter a name and click `Create Personal Access Token`.
4. Copy your Personal Access Token.
5. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces).
6. Click **Sources** and then click **+ New source**.
7. On the Set up the source page, select **Harvest** from the Source type dropdown.
8. Enter a name for the Harvest connector.
9. Enter your Harvest Account ID.
10. For **Start Date**, enter the date in YYYY-MM-DDTHH:mm:ssZ format. The data added on and after this date will be replicated.
11. For Authentication mechanism, select **Authenticate with Personal Access Token** from the dropdown. Paste the Personal Access Token from step 4.
12. Click **Set up source**.

<!-- /env:cloud -->

<!-- env:oss -->
**For Airbyte Open Source:**

1. Log into your [Harvest account](https://id.getharvest.com/external_sessions/new