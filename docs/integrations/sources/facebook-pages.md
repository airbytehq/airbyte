# Facebook Pages

:::danger
The Facebook Pages API utilized by this connector has been deprecated. You will not be able to make a successful connection. If you would like to make a community contribution or track API upgrade status, visit: https://github.com/airbytehq/airbyte/issues/25515.
:::

This page contains the setup guide and reference information for the Facebook Pages source connector.

## Prerequisites

To set up the Facebook Pages source connector with Airbyte, you'll need to create your Facebook Application and use both long-lived Page access token and Facebook Page ID.

:::note
The Facebook Pages souce connector is currently only compatible with v15 of the Facebook Graph API.
:::

## Setup guide

### Step 1: Set up Facebook Pages

1. Create Facebook Developer Account. Follow [instruction](https://developers.facebook.com/async/registration/) to create one.
2. Create [Facebook App](https://developers.facebook.com/apps/). Choose "Company" as the purpose of the app. Fill out the remaining fields to create your app, then follow along the "Connect a User Page" section.
3. Connect a User [Page](https://developers.facebook.com/tools/explorer/). Choose your app at `Meta App` field. Choose your Page at `User or Page` field. Add next permission:
   - pages_read_engagement
   - pages_read_user_content
   - pages_show_list
   - read_insights
4. Click Generate Access Token and follow instructions.

After all the steps, it should look something like this

![](../../.gitbook/assets/facebook-pages-1.png)

5. [Generate](https://developers.facebook.com/docs/facebook-login/guides/access-tokens/get-long-lived#get-a-long-lived-user-access-token) Long-Lived User Access Token.
6. [Generate](https://developers.facebook.com/docs/facebook-login/guides/access-tokens/get-long-lived#long-lived-page-token) Long-Lived Page Token.

### Step 2: Set up the Facebook Pages connector in Airbyte

### For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ New source**.
3. On the Set up the source page, enter the name for the Facebook Pages connector and select **Facebook Pages** from the Source type dropdown.
4. Fill in Page Access Token with Long-Lived Page Token
5. Fill in Page ID (if you have a page URL such as `https://www.facebook.com/Test-1111111111`, the ID would be`Test-1111111111`)

### For Airbyte OSS:

1. Navigate to the Airbyte Open Source dashboard.
2. Set the name for your source.
3. On the Set up the source page, enter the name for the Facebook Pages connector and select **Facebook Pages** from the Source type dropdown.
4. Fill in Page Access Token with Long-Lived Page Token
5. Fill in Page ID (if you have a page URL such as `https://www.facebook.com/Test-1111111111`, the ID would be`Test-1111111111`)

## Supported sync modes

The Facebook Pages source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
- [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)

## Supported Streams

- [Page](https://developers.facebook.com/docs/graph-api/reference/v19.0/page/#overview)
- [Post](https://developers.facebook.com/docs/graph-api/reference/v19.0/page/feed)
- [Page Insights](https://developers.facebook.com/docs/graph-api/reference/v19.0/page/insights)
- [Post Insights](https://developers.facebook.com/docs/graph-api/reference/v19.0/insights)

## Data type map

| Integration Type | Airbyte Type | Notes |
| :--------------- | :----------- | :---- |
| `string`         | `string`     |       |
| `number`         | `number`     |       |
| `array`          | `array`      |       |
| `object`         | `object`     |       |

## Performance considerations

Facebook heavily throttles API tokens generated from Facebook Apps by default, making it infeasible to use such a token for syncs with Airbyte. To be able to use this connector without your syncs taking days due to rate limiting follow the instructions in the Setup Guide below to access better rate limits.

See Facebook's [documentation on rate limiting](https://developers.facebook.com/docs/graph-api/overview/rate-limiting) for more information on requesting a quota upgrade.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                                                                                                                |
|:--------|:-----------| :------------------------------------------------------- |:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 1.0.30  | 2025-01-23 | [52122](https://github.com/airbytehq/airbyte/pull/52122/files) | Upgrade Facebook API to v21.0                                                                                                                                          |
| 1.0.29  | 2025-01-18 | [51637](https://github.com/airbytehq/airbyte/pull/51637) | Update dependencies                                                                                                                                                    |
| 1.0.28  | 2025-01-11 | [51056](https://github.com/airbytehq/airbyte/pull/51056) | Update dependencies                                                                                                                                                    |
| 1.0.27  | 2025-01-04 | [50923](https://github.com/airbytehq/airbyte/pull/50923) | Update dependencies                                                                                                                                                    |
| 1.0.26  | 2024-12-28 | [50530](https://github.com/airbytehq/airbyte/pull/50530) | Update dependencies                                                                                                                                                    |
| 1.0.25  | 2024-12-21 | [49997](https://github.com/airbytehq/airbyte/pull/49997) | Update dependencies                                                                                                                                                    |
| 1.0.24  | 2024-12-14 | [49154](https://github.com/airbytehq/airbyte/pull/49154) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 1.0.23  | 2024-10-29 | [47737](https://github.com/airbytehq/airbyte/pull/47737) | Update dependencies                                                                                                                                                    |
| 1.0.22  | 2024-10-21 | [47025](https://github.com/airbytehq/airbyte/pull/47025) | Update dependencies                                                                                                                                                    |
| 1.0.21  | 2024-10-12 | [46807](https://github.com/airbytehq/airbyte/pull/46807) | Update dependencies                                                                                                                                                    |
| 1.0.20  | 2024-10-05 | [46461](https://github.com/airbytehq/airbyte/pull/46461) | Update dependencies                                                                                                                                                    |
| 1.0.19  | 2024-09-28 | [46133](https://github.com/airbytehq/airbyte/pull/46133) | Update dependencies                                                                                                                                                    |
| 1.0.18  | 2024-09-21 | [45734](https://github.com/airbytehq/airbyte/pull/45734) | Update dependencies                                                                                                                                                    |
| 1.0.17  | 2024-09-14 | [45563](https://github.com/airbytehq/airbyte/pull/45563) | Update dependencies                                                                                                                                                    |
| 1.0.16  | 2024-09-07 | [45311](https://github.com/airbytehq/airbyte/pull/45311) | Update dependencies                                                                                                                                                    |
| 1.0.15  | 2024-08-31 | [45052](https://github.com/airbytehq/airbyte/pull/45052) | Update dependencies                                                                                                                                                    |
| 1.0.14  | 2024-08-24 | [44664](https://github.com/airbytehq/airbyte/pull/44664) | Update dependencies                                                                                                                                                    |
| 1.0.13  | 2024-08-17 | [44234](https://github.com/airbytehq/airbyte/pull/44234) | Update dependencies                                                                                                                                                    |
| 1.0.12  | 2024-08-12 | [43729](https://github.com/airbytehq/airbyte/pull/43729) | Update dependencies                                                                                                                                                    |
| 1.0.11  | 2024-08-10 | [43477](https://github.com/airbytehq/airbyte/pull/43477) | Update dependencies                                                                                                                                                    |
| 1.0.10  | 2024-08-03 | [43224](https://github.com/airbytehq/airbyte/pull/43224) | Update dependencies                                                                                                                                                    |
| 1.0.9   | 2024-07-27 | [42787](https://github.com/airbytehq/airbyte/pull/42787) | Update dependencies                                                                                                                                                    |
| 1.0.8   | 2024-07-20 | [42255](https://github.com/airbytehq/airbyte/pull/42255) | Update dependencies                                                                                                                                                    |
| 1.0.7   | 2024-07-13 | [41685](https://github.com/airbytehq/airbyte/pull/41685) | Update dependencies                                                                                                                                                    |
| 1.0.6   | 2024-07-10 | [41543](https://github.com/airbytehq/airbyte/pull/41543) | Update dependencies                                                                                                                                                    |
| 1.0.5   | 2024-07-09 | [41126](https://github.com/airbytehq/airbyte/pull/41126) | Update dependencies                                                                                                                                                    |
| 1.0.4   | 2024-07-06 | [40812](https://github.com/airbytehq/airbyte/pull/40812) | Update dependencies                                                                                                                                                    |
| 1.0.3   | 2024-06-25 | [40500](https://github.com/airbytehq/airbyte/pull/40500) | Update dependencies                                                                                                                                                    |
| 1.0.2   | 2024-06-22 | [40058](https://github.com/airbytehq/airbyte/pull/40058) | Update dependencies                                                                                                                                                    |
| 1.0.1   | 2024-06-06 | [39243](https://github.com/airbytehq/airbyte/pull/39243) | [autopull] Upgrade base image to v1.2.2                                                                                                                                |
| 1.0.0   | 2024-03-14 | [36015](https://github.com/airbytehq/airbyte/pull/36015) | Upgrade Facebook API to v19.0                                                                                                                                          |
| 0.3.0   | 2023-06-26 | [27728](https://github.com/airbytehq/airbyte/pull/27728) | License Update: Elv2                                                                                                                                                   |
| 0.2.5   | 2023-04-13 | [26939](https://github.com/airbytehq/airbyte/pull/26939) | Add advancedAuth to the connector spec                                                                                                                                 |
| 0.2.4   | 2023-04-13 | [25143](https://github.com/airbytehq/airbyte/pull/25143) | Update insight metrics request params                                                                                                                                  |
| 0.2.3   | 2023-02-23 | [23395](https://github.com/airbytehq/airbyte/pull/23395) | Parse datetime to rfc3339                                                                                                                                              |
| 0.2.2   | 2023-02-10 | [22804](https://github.com/airbytehq/airbyte/pull/22804) | Retry 500 errors                                                                                                                                                       |
| 0.2.1   | 2022-12-29 | [20925](https://github.com/airbytehq/airbyte/pull/20925) | Fix tests; modify expected records                                                                                                                                     |
| 0.2.0   | 2022-11-24 | [19788](https://github.com/airbytehq/airbyte/pull/19788) | Migrate lo low-code; Beta certification; Upgrade Facebook API to v.15                                                                                                  |
| 0.1.6   | 2021-12-22 | [9032](https://github.com/airbytehq/airbyte/pull/9032) | Remove deprecated field `live_encoders` from Page stream                                                                                                               |
| 0.1.5   | 2021-11-26 | [8267](https://github.com/airbytehq/airbyte/pull/8267) | updated all empty objects in schemas for Page and Post streams                                                                                                         |
| 0.1.4   | 2021-11-26 | [](https://github.com/airbytehq/airbyte/pull/)           | Remove unsupported insights_export field from Pages request                                                                                                            |
| 0.1.3   | 2021-10-28 | [7440](https://github.com/airbytehq/airbyte/pull/7440)   | Generate Page token from config access token                                                                                                                           |
| 0.1.2   | 2021-10-18 | [7128](https://github.com/airbytehq/airbyte/pull/7128)   | Upgrade Facebook API to v.12                                                                                                                                           |
| 0.1.1   | 2021-09-30 | [6438](https://github.com/airbytehq/airbyte/pull/6438)   | Annotate Oauth2 flow initialization parameters in connector specification                                                                                              |
| 0.1.0   | 2021-09-01 | [5158](https://github.com/airbytehq/airbyte/pull/5158)   | Initial Release                                                                                                                                                        |

</details>
