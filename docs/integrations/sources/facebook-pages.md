# Facebook Pages

This page contains the setup guide and reference information for the Facebook Pages source connector.

## Prerequisites

To set up the Facebook Pages source connector with Airbyte, you'll need to create your Facebook Application and use both long-lived Page access token and Facebook Page ID.

:::note
The Facebook Pages souce connector is currently only compatible with v15 of the Facebook Graph API.
:::

## Setup Guide
The following steps will guide you through setting up the Facebook Pages Source connector with the required authentication details and proper access.

### Step 1: Set up Facebook Pages
1. Create a Facebook Developer Account: To create a facebook developer account, follow the [instructions](https://developers.facebook.com/async/registration/).

2. Create a Facebook App: To create a new facebook app, visit the [Facebook App dashboard](https://developers.facebook.com/apps/) and click on the "Create App" button. Choose "Company" as the purpose of the app. Provide the requested details and submit the form.

3. Connect a Page: To connect a user page, go to the [Facebook Graph API explorer](https://developers.facebook.com/tools/explorer/). In the "Meta App" field, select the app you just created. In the "User or Page" field, select the page you want to connect to. Add the following permissions to the app:
   * pages_read_engagement
   * pages_read_user_content
   * pages_show_list
   * read_insights

   Click "Generate Access Token" and follow the instructions.

4. Generate Long-Lived User Access Token: To get a long-lived user access token, follow the [instructions](https://developers.facebook.com/docs/facebook-login/guides/access-tokens/get-long-lived#get-a-long-lived-user-access-token).

5. Generate Long-Lived Page Token: To get a long-lived page token, follow the [instructions](https://developers.facebook.com/docs/facebook-login/guides/access-tokens/get-long-lived#long-lived-page-token).

### Step 2: Set up the Facebook Pages connector in Airbyte
1. In the Airbyte UI, access the "Set up the source" page.

2. Enter a name for the Facebook Pages connector and select "Facebook Pages" as the Source type in the dropdown list.

3. Input the "Page Access Token" and "Page ID" as follows:

   * Page Access Token: Paste the Long-Lived Page Token you generated in step 5 of the "Set up Facebook Pages" section.

   * Page ID: This is the ID of the Facebook page you want to connect. If you have a page URL such as `https://www.facebook.com/Test-1111111111`, the ID would be `Test-1111111111`.

4. Complete the setup process by clicking on "Save & Continue".

## Supported sync modes

The Facebook Pages source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):
* [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
* [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)


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

Facebook heavily throttles API tokens generated from Facebook Apps by default, making it infeasible to use such a token for syncs with Airbyte. To be able to use this connector without your syncs taking days due to rate limiting follow the instructions in the Setup Guide below to access better rate limits.

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
