# Instagram

This page contains the setup guide and reference information for the Instagram source connector.

## Prerequisites

* [Meta for Developers account](https://developers.facebook.com)
* [Instagram business account](https://www.facebook.com/business/help/898752960195806) connected to your Facebook Page
* [Instagram Graph API](https://developers.facebook.com/docs/instagram-api/) added to your Facebook app
* [Facebook OAuth Reference](https://developers.facebook.com/docs/instagram-basic-display-api/reference)
* [Facebook ad account ID number](https://www.facebook.com/business/help/1492627900875762) (you'll use this to configure Instagram as a source in Airbyte)

## Setup Guide

### Generate Access Token

To generate the Access Token, follow these steps:

1. Go to your [Facebook Developer Dashboard](https://developers.facebook.com/apps) and select the app you want to use for the Instagram connector.
2. In the left sidebar, click on "Products" and then "+Add Product".
3. Find "Instagram Basic Display" and click "Set Up".
4. Navigate to the "Basic Display" tab under the Instagram section in the sidebar.
5. Scroll down to "User Token Generator" and click on "Generate Token".
6. Grant the necessary permissions (instagram_basic, instagram_manage_insights, pages_show_list, pages_read_engagement, Instagram Public Content Access) to the app.
7. Once the permissions are granted, the access token will be generated. Copy the token and save it securely.

### Set up the Instagram connector in Airbyte

1. Enter the **Start Date** in the YYYY-MM-DDTHH:mm:ssZ format. All data generated after this date will be replicated. If this field is blank, Airbyte will replicate all data.
2. Enter the **Access Token** that you generated in the previous section.
3. Click **Set up source**.

## Supported sync modes
The Instagram source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):
* [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
* [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
* [Incremental - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)
* [Incremental - Deduped History](https://docs.airbyte.com/understanding-airbyte/connections/incremental-deduped-history)

:::note

Incremental sync modes are only available for the [User Insights](https://developers.facebook.com/docs/instagram-api/reference/ig-user/insights) stream.

:::