# Instagram

This page contains the setup guide and reference information for Instagram.

## Features

| Feature | Supported? |
| --- | --- |
| Full Refresh - Overwrite | Yes |
| Full Refresh - Append | Yes |
| Incremental - Append | Yes |
| Incremental - Append + Deduped | Yes |

  > Note: Incremental sync modes are only available for the [User Insights](https://developers.facebook.com/docs/instagram-api/reference/ig-user/insights) stream.

## Prerequisites

* [Instagram business account](https://www.facebook.com/business/help/898752960195806) linked to your Facebook page
* [Meta for Developers account](https://developers.facebook.com/)
* [Facebook ad account ID number](https://www.facebook.com/business/help/1492627900875762)
* Access Token generated using [Graph API Explorer](https://developers.facebook.com/tools/explorer/) or by using [an app you created on Facebook](https://developers.facebook.com/docs/instagram-api/getting-started)

## Setup guide

### Step 1: Connect you Instagram account to your Facebook Page

1. On yuor Facebook Page, click **Professional dashboard**.

2. Inside your dashboard, scroll down and find **Linked accounts** on the left sidebar.

3. Choose **Instagram** and click **Connect account**. You will be asked to login to your Instagram account. Once done, your Instagram account will be connected to your Facebook page.

### Step 2: Obtain credentials to set up Instagram

1. Use [Graph API Explorer](https://developers.facebook.com/tools/explorer/) or by using an app you can create on Facebook with the required permissions:
  > * instagram_basic
  > * instagram_manage_insights
  > * pages_show_list
  > * pages_read_engagement

2. Follow the guide [here](https://www.facebook.com/business/help/1492627900875762) to obtain your **Facebook ad account ID number**.

3. You're ready to set up Instagram in Daspire!

### Step 3: Set up Instagram in Daspire

1. Select **Instagram** from the Source list.

2. Enter a **Source Name**.

3. Enter **Access Token** you obtained in Step 2.

4. (Optional) Enter the **Start Date** in `YYYY-MM-DDTHH:mm:ssZ` format. All data generated after this date will be replicated. If left blank, the start date will be set to 2 years before the present date.

5. Click **Save & Test**.

## Output schema

This Source is capable of syncing the following core Streams:

* [Users](https://developers.facebook.com/docs/instagram-api/reference/ig-user)
* [User Insights](https://developers.facebook.com/docs/instagram-api/reference/ig-user/insights)
* [Media](https://developers.facebook.com/docs/instagram-api/reference/ig-user/media)
* [Media Insights](https://developers.facebook.com/docs/instagram-api/reference/ig-media/insights)
* [Stories](https://developers.facebook.com/docs/instagram-api/reference/ig-user/stories/)
* [Story Insights](https://developers.facebook.com/docs/instagram-api/reference/ig-media/insights)

## Data type mapping

| Integration Type | Daspire Type |
| --- | --- |
| `string` | `string` |
| `number` | `number` |
| `array` | `array` |
| `object` | `object` |

## Performance considerations

Instagram limits the number of requests that can be made at a time, but the Instagram integration gracefully handles rate limiting. See [Facebook's documentation on rate limiting](https://developers.facebook.com/docs/graph-api/overview/rate-limiting/#instagram-graph-api) for more information.

## Troubleshooting

Max number of tables that can be synced at a time is 6,000. We advise you to adjust your settings if it fails to fetch schema due to max number of tables reached.
