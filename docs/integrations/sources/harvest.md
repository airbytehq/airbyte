# Harvest

This page contains the setup guide and reference information for the Harvest source connector.

## Prerequisites

To set up the Harvest source connector, you'll need your [Harvest Account ID](https://help.getharvest.com/api-v2/authentication-api/authentication/authentication/#account-id) and a method for authentication, either a [Personal Access Token](https://help.getharvest.com/api-v2/authentication-api/authentication/authentication/#personal-access-tokens) or OAuth credentials.

## Setup guide

<!-- env:cloud -->
**For Airbyte Cloud:**

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces).
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select **Harvest** from the Source type dropdown.
4. Enter the name for the Harvest connector.
5. Enter your [Harvest Account ID](https://help.getharvest.com/api-v2/authentication-api/authentication/authentication/#account-id).
6. For **Start Date**, enter the date in YYYY-MM-DDTHH:mm:ssZ format. The data added on and after this date will be replicated.
7. Select the desired **Authentication mechanism**:
   - If using **Authenticate with Personal Access Token**:
     1. Log into Harvest and [create a new Personal Access Token](https://id.getharvest.com/developers) or locate an existing one.
     2. Enter the Personal Access Token in the **api_token** field.
   - If using **Authenticate via Harvest (OAuth)**:
     1. Obtain the Client ID and Client Secret from your [Harvest developer application](https://id.getharvest.com/oauth2?state=unique_state_string&response_type=code&client_id=your_client_id&redirect_uri=your_redirect_uri) ([Documentation](https://help.getharvest.com/api-v2/authentication-api/authentication/oauth-2-0/#step-1--create-the-application)).
     2. Follow the instructions in the Airbyte UI to authenticate and obtain a Refresh Token.
     3. Enter the Client ID, Client Secret, and Refresh Token in their respective fields.

8. Click **Set up source**.
<!-- /env:cloud -->

<!-- env:oss -->
**For Airbyte Open Source:**

1. Navigate to the Airbyte Open Source dashboard.
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select **Harvest** from the Source type dropdown.
4. Enter the name for the Harvest connector.
5. Enter your [Harvest Account ID](https://help.getharvest.com/api-v2/authentication-api/authentication/authentication/#account-id).
6. For **Start Date**, enter the date in YYYY-MM-DDTHH:mm:ssZ format. The data added on and after this date will be replicated.
7. Select the desired **Authentication mechanism**:
   - If using **Authenticate with Personal Access Token**:
     1. Log into Harvest and [create a new Personal Access Token](https://id.getharvest.com/developers) or locate an existing one.
     2. Enter the Personal Access Token in the **api_token** field.
   - If using **Authenticate via Harvest (OAuth)**:
     1. Obtain the Client ID and Client Secret from your [Harvest developer application](https://id.getharvest.com/oauth2?state=unique_state_string&response_type=code&client_id=your_client_id&redirect_uri=your_redirect_uri) ([Documentation](https://help.getharvest.com/api-v2/authentication-api/authentication/oauth-2-0/#step-1--create-the-application)).
     2. Follow the instructions in the Airbyte UI to authenticate and obtain a Refresh Token.
     3. Enter the Client ID, Client Secret, and Refresh Token in their respective fields.

8. Click **Set up source**.
<!-- /env:oss -->

## Supported sync modes

The Harvest source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

* [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
* [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
* [Incremental - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)
* [Incremental - Deduped History](https://docs.airbyte.com/understanding-airbyte/connections/incremental-deduped-history)

## Supported Streams

[Original documentation goes here]

## Performance considerations

The connector is restricted by the [Harvest rate limits](https://help.getharvest.com/api-v2/introduction/overview/general/#rate-limiting).

## Changelog

[Original documentation goes here]