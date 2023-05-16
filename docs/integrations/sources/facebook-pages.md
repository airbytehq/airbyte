# Facebook Pages

This page contains the setup guide and reference information for the Facebook Pages source connector.

## Prerequisites

To set up the Facebook Pages source connector with Airbyte, you'll need to create your Facebook Application and use both a long-lived User access token and Facebook Page ID.

:::note
The Facebook Pages souce connector is currently only compatible with v15 of the Facebook Graph API.
:::

## Setup guide
### Step 1: Set up Facebook Pages

1. Create a Facebook Developer Account. Follow [these instructions](https://developers.facebook.com/docs/development/create-an-app/) to create one.
2. Create a Facebook App. Choose "Company" as the purpose of the app. Fill out the remaining fields to create your app.
3. Navigate to the "Facebook Login" tab in the sidebar. Add "https://localhost:8000" as the **Valid OAuth Redirect URIs**.
4. Navigate to the **Settings** > **Basic** section. Add the **Contact Email** and **Privacy Policy URL**.
5. Navigate to the **App Review** sidebar, select **Permissions and Features**. Add the following permissions:
   * pages_read_engagement
   * pages_read_user_content 
   * pages_show_list
   * read_insights
6. In the same section, toggle on **Data Access** for the Facebook Pages connector.
7. Select **Live** in the sidebar and enter the **Production Live Broadcasting** settings. Then save the changes.

After all the steps, it should look something like this:

![](../../.gitbook/assets/facebook-pages-1.png)

8. [Generate](https://developers.facebook.com/docs/facebook-login/access-tokens/) Long-Lived User Access Token.
9. [Generate](https://developers.facebook.com/docs/pages/access-tokens#page-token-generation) Long-Lived Page Token by selecting the page that you want to sync.

### Step 2: Set up the Facebook Pages connector in Airbyte

1. Log into your Airbyte account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ New source**.
3. On the Set up the source page, enter the name for the Facebook Pages connector and select **Facebook Pages** from the Source type dropdown.
4. Fill in Page Access Token with Long-Lived Page Token
5. Fill in Page ID (if you have a page URL such as `https://www.facebook.com/Test-1111111111`, the ID would be `Test-1111111111`)

## Supported sync modes

The Facebook Pages source connector supports the following [sync modes](https://docs.airbyte.io/cloud/core-concepts#connection-sync-modes):
* [Full Refresh - Overwrite](https://docs.airbyte.io/understanding-airbyte/connections/full-refresh-overwrite/)
* [Full Refresh - Append](https://docs.airbyte.io/understanding-airbyte/connections/full-refresh-append)


## Supported Streams

* [Page](https://developers.facebook.com/docs/graph-api/reference/v15.0/page/#overview)
* [Post](https://developers.facebook.com/docs/graph-api/reference/v15.0/page/feed)
* [Page Insights](https://developers.facebook.com/docs/graph-api/reference/v15.0/page/insights)
* [Post Insights](https://developers.facebook.com/docs/graph-api/reference/v15.0/insights)

## Data type map

| Integration Type | Airbyte Type | Notes |
|:-----------------|:-------------|:------|
| `string`         | `string`     |       |
| `number`         | `number`     |       |
| `array`          | `array`      |       |
| `object`         | `object`     |       |



## Performance considerations

Facebook heavily throttles API tokens generated from Facebook Apps by default, making it infeasible to use such a token for syncs with Airbyte. To be able to use this connector without your syncs taking days due to rate limiting follow the instructions in the Setup Guide above to access better rate limits.

See Facebook's [documentation on rate limiting](https://developers.facebook.com/docs/graph-api/overview/rate-limiting) for more information on requesting a quota upgrade.


## Changelog

| Version | Date       | Pull Request                                             | Subject                                                                   |
|:--------|:-----------|:---------------------------------------------------------|:--------------------------------------------------------------------------|
| 0.2.4   | 2023-04-13 | [25143](https://github.com/airbytehq/airbyte/pull/25143) | Update insight metrics request params                                                 |
| 0.2.3   | 2023-02-23 | [23395](https://github.com/airbytehq/airbyte/pull/23395) | Parse datetime to rfc3339                                                 |
| 0.2.2   | 2023-02-10 | [22804](https://github.com/airbytehq/airbyte/pull/22804) | Retry 500 errors                                                          |
| 0.2.1   | 2022-12-29 | [20925](https://github.com/airbytehq/airbyte/pull/20925) | Fix tests; modify expected records                                        |
| 0.2.0   | 2022-11-24 | [19788](https://github.com/airbytehq/airbyte/pull/19788) | Migrate lo low-code; Beta certification; Upgrade Facebook API to v.15     |
| 0.1.6   | 2021-12-22 | [9032](https://github.com/airbytehq/airbyte/pull/9032)   | Remove deprecated field `live_encoders` from Page stream                  |
| 0.1.5   | 2021-11-26 | [8267](https://github.com/airbytehq/airbyte/pull/8267)   | updated all empty objects in schemas for Page and Post streams            |
| 0.1.4   | 2021-11-26 | [](https://github.com/airbytehq/airbyte/pull/)           | Remove unsupported insights_export field from Pages request               |
| 0.1.3   | 2021-10-28 | [7440](https://github.com/airbytehq/airbyte/pull/7440)   | Generate Page token from config access token                              |
| 0.1.2   | 2021-10-18 | [7128](https://github.com/airbytehq/airbyte/pull/7128)   | Upgrade Facebook API to v.12                                              |
| 0.1.1   | 2021-09-30 | [6438](https://github.com/airbytehq/airbyte/pull/6438)   | Annotate Oauth2 flow initialization parameters in connector specification |
| 0.1.0   | 2021-09-01 | [5158](https://github.com/airbytehq/airbyte/pull/5158)   | Initial Release                                                           |


Please refer to the [Facebook Pages documentation](https://docs.airbyte.io/integrations/sources/facebook-pages) for more information on setting up and using this connector.