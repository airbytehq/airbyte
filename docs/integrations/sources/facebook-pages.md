# Facebook Pages

This page contains the setup guide and reference information for the [Facebook Pages](https://developers.facebook.com/docs/pages/) source connector.

## Prerequisites

- A [Facebook Developer](https://developers.facebook.com/async/registration/) account
- A [Facebook App](https://developers.facebook.com/apps/)
- A Facebook Page that you manage
- A Long-Lived Page Access Token with the following permissions:
  - `pages_read_engagement`
  - `pages_read_user_content`
  - `pages_show_list`
  - `read_insights`

:::note
This connector uses the Facebook Graph API v24.0. Some fields and metrics available in earlier API versions have been removed. See the [v2.0.0 migration guide](facebook-pages-migrations.md#upgrading-to-200) for details.
:::

## Setup guide

### Set up Facebook Pages

1. If you don't already have one, [create a Facebook Developer account](https://developers.facebook.com/async/registration/).

2. [Create a Facebook App](https://developers.facebook.com/docs/development/create-an-app/). Fill out the required fields to create your app.

3. Go to the [Graph API Explorer](https://developers.facebook.com/tools/explorer/). Select your app in the **Meta App** field. Select your Page in the **User or Page** field. Add the following permissions:
   - `pages_read_engagement`
   - `pages_read_user_content`
   - `pages_show_list`
   - `read_insights`

4. Click **Generate Access Token** and follow the authorization prompts.

   After completing these steps, the Graph API Explorer should look something like this:

   ![Graph API Explorer with permissions configured](/.gitbook/assets/facebook-pages-1.png)

5. [Generate a Long-Lived User Access Token](https://developers.facebook.com/docs/facebook-login/guides/access-tokens/get-long-lived#get-a-long-lived-user-access-token). This requires your App ID and App Secret, available from your app's dashboard.

6. [Generate a Long-Lived Page Access Token](https://developers.facebook.com/docs/facebook-login/guides/access-tokens/get-long-lived#long-lived-page-token) from the Long-Lived User Access Token.

:::tip
Long-Lived Page Access Tokens do not expire, unlike Long-Lived User Access Tokens which expire after approximately 60 days. Use a Long-Lived Page Access Token to avoid re-authentication.
:::

### Set up the connector in Airbyte

1. In Airbyte, navigate to **Sources** and select **+ New source**.
2. Select **Facebook Pages** from the source type dropdown.
3. Enter a name for your source.
4. Enter the **Page Access Token** from the previous steps.
5. Enter the **Page ID**. If your page URL is `https://www.facebook.com/MyPageName`, the Page ID is `MyPageName`. You can also find the numeric Page ID in your Page's **About** section.
6. Optionally, set **Page Size** to control the number of records per page for the `post` and `post_insights` streams. The default and maximum is 100. Decrease this value if you encounter "Please reduce the amount of data you're asking for" errors.

### Creating your own OAuth App

If you use Airbyte Cloud with OAuth, you can also [create your own Facebook App](https://developers.facebook.com/docs/development/create-an-app/) for authentication. Your app requires these permissions:

- `pages_read_engagement`
- `pages_read_user_content`
- `pages_show_list`
- `read_insights`

If you encounter permission errors for specific Page fields, see [Meta's Permissions Reference](https://developers.facebook.com/docs/permissions) for additional permissions you might need.

## Supported sync modes

The Facebook Pages source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
- [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)

## Supported streams

- [Page](https://developers.facebook.com/docs/graph-api/reference/v24.0/page/#overview) - Returns metadata and details about your Facebook Page.
- [Post](https://developers.facebook.com/docs/graph-api/reference/v24.0/page/feed) - Returns posts from your Page's feed. You can deselect individual fields in the connection's **Schema** tab.
- [Page Insights](https://developers.facebook.com/docs/graph-api/reference/v24.0/page/insights) - Returns Page-level engagement metrics such as impressions, post engagements, and reactions.
- [Post Insights](https://developers.facebook.com/docs/graph-api/reference/v24.0/insights) - Returns post-level engagement metrics for each post, including impressions and reactions.

## Limitations and troubleshooting

### Rate limiting

The Facebook Graph API applies [rate limits](https://developers.facebook.com/docs/graph-api/overview/rate-limiting) to all requests. Pages API requests made with Page access tokens are subject to Business Use Case rate limits. When rate limited, the API returns error code `32`.

Facebook heavily throttles API tokens generated from Facebook Apps by default. To use this connector without syncs being delayed by rate limiting, use a Long-Lived Page Access Token as described in the setup guide.

### Page Insights requirements

The Page Insights stream has the following Facebook API requirements:

- The Page must have at least **100 likes** for insights data to be available.
- Insights data is only available for the **last two years**.
- Most Page Insights metrics update once every 24 hours.
- Demographic metrics such as age, gender, and location require data from 100 or more people to return results.

### Post stream limits

The Facebook API returns approximately 600 ranked, published posts per year. The maximum number of posts per page request is 100, controlled by the **Page Size** setting.

### "Please reduce the amount of data you're asking for" error

This error occurs when the Facebook Graph API considers the total response data too large. To resolve it:

- **Remove fields from the request.** Go to your connection's **Schema** tab and deselect fields you don't need for the affected stream. This reduces the number of fields included in API requests. Supported streams: `page`, `post`.
- **Reduce page size.** Set the **Page Size** configuration parameter to a lower value, such as 25 or 50. This reduces the number of records fetched per API request. Supported streams: `post`, `post_insights`.

### HTTP 400 "Bad request" errors

The connector automatically retries HTTP 400 errors returned by the Facebook API. These errors can occur when the API temporarily rejects a request due to server-side issues or when requesting fields that are not available for a specific Page type. If 400 errors persist, verify that your Page Access Token is valid and has the required permissions.

### Product catalogs field not available

Starting from version 2.0.4, the `product_catalogs` field is no longer synced in the Page stream and is always `null`. The Facebook Graph API only returns product catalogs owned directly by the Page, not catalogs owned by a Business. Since most product catalogs are now Business-owned catalogs, this field does not return meaningful data for most users.

### Access token issues

The connector converts your provided access token into a Page Access Token at runtime. This works with both User Access Tokens and Page Access Tokens. If you provide a User Access Token, the connector exchanges it for a Page Access Token using the Page ID you configured. If the exchange fails, verify that:

- The token has not expired. Long-Lived User Access Tokens expire after approximately 60 days.
- The token has the required permissions.
- The Page ID is correct and corresponds to a Page you have access to.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                                   | Subject                                                                                                                                                                |
|:--------|:-----------|:---------------------------------------------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 2.1.0 | 2026-02-09 | [72949](https://github.com/airbytehq/airbyte/pull/72949) | Use QueryProperties with JsonSchemaPropertySelector to limit API field requests to user-selected fields; add configurable page_size for post and post_insights streams |
| 2.0.4 | 2026-01-29 | [72253](https://github.com/airbytehq/airbyte/pull/72253) | Remove product_catalogs from fields request parameter |
| 2.0.3 | 2025-12-01 | [70248](https://github.com/airbytehq/airbyte/pull/70248) | Use correct pagination parameter name (`limit` instead of `page_size`) |
| 2.0.2 | 2025-12-01 | [70258](https://github.com/airbytehq/airbyte/pull/70258) | Use Post stream for check, handle 400 error in Page stream |
| 2.0.1 | 2025-11-27 | [70242](https://github.com/airbytehq/airbyte/pull/70242) | Refresh in-app documentation to reflect v24 API version |
| 2.0.0 | 2025-11-19 | [69714](https://github.com/airbytehq/airbyte/pull/69714) | Upgrade Facebook API to v24.0 |
| 1.1.4 | 2025-08-14 | [64141](https://github.com/airbytehq/airbyte/pull/64141) | Upgrade Facebook API to v23.0 |
| 1.1.3 | 2025-07-12 | [60391](https://github.com/airbytehq/airbyte/pull/60391) | Update dependencies |
| 1.1.2 | 2025-05-10 | [60043](https://github.com/airbytehq/airbyte/pull/60043) | Update dependencies |
| 1.1.1 | 2025-05-03 | [53787](https://github.com/airbytehq/airbyte/pull/53787) | Update dependencies |
| 1.1.0 | 2025-04-30 | [59126](https://github.com/airbytehq/airbyte/pull/59126) | Re-enable in cloud and update versions |
| 1.0.32 | 2025-02-01 | [52793](https://github.com/airbytehq/airbyte/pull/52793) | Update dependencies |
| 1.0.31  | 2025-01-27 | [52122](https://github.com/airbytehq/airbyte/pull/52122/files) | Upgrade Facebook API to v21.0                                                                                                                                          |
| 1.0.30  | 2025-01-25 | [52373](https://github.com/airbytehq/airbyte/pull/52373)       | Update dependencies                                                                                                                                                    |
| 1.0.29  | 2025-01-18 | [51637](https://github.com/airbytehq/airbyte/pull/51637)       | Update dependencies                                                                                                                                                    |
| 1.0.28  | 2025-01-11 | [51056](https://github.com/airbytehq/airbyte/pull/51056)       | Update dependencies                                                                                                                                                    |
| 1.0.27  | 2025-01-04 | [50923](https://github.com/airbytehq/airbyte/pull/50923)       | Update dependencies                                                                                                                                                    |
| 1.0.26  | 2024-12-28 | [50530](https://github.com/airbytehq/airbyte/pull/50530)       | Update dependencies                                                                                                                                                    |
| 1.0.25  | 2024-12-21 | [49997](https://github.com/airbytehq/airbyte/pull/49997)       | Update dependencies                                                                                                                                                    |
| 1.0.24  | 2024-12-14 | [49154](https://github.com/airbytehq/airbyte/pull/49154)       | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 1.0.23  | 2024-10-29 | [47737](https://github.com/airbytehq/airbyte/pull/47737)       | Update dependencies                                                                                                                                                    |
| 1.0.22  | 2024-10-21 | [47025](https://github.com/airbytehq/airbyte/pull/47025)       | Update dependencies                                                                                                                                                    |
| 1.0.21  | 2024-10-12 | [46807](https://github.com/airbytehq/airbyte/pull/46807)       | Update dependencies                                                                                                                                                    |
| 1.0.20  | 2024-10-05 | [46461](https://github.com/airbytehq/airbyte/pull/46461)       | Update dependencies                                                                                                                                                    |
| 1.0.19  | 2024-09-28 | [46133](https://github.com/airbytehq/airbyte/pull/46133)       | Update dependencies                                                                                                                                                    |
| 1.0.18  | 2024-09-21 | [45734](https://github.com/airbytehq/airbyte/pull/45734)       | Update dependencies                                                                                                                                                    |
| 1.0.17  | 2024-09-14 | [45563](https://github.com/airbytehq/airbyte/pull/45563)       | Update dependencies                                                                                                                                                    |
| 1.0.16  | 2024-09-07 | [45311](https://github.com/airbytehq/airbyte/pull/45311)       | Update dependencies                                                                                                                                                    |
| 1.0.15  | 2024-08-31 | [45052](https://github.com/airbytehq/airbyte/pull/45052)       | Update dependencies                                                                                                                                                    |
| 1.0.14  | 2024-08-24 | [44664](https://github.com/airbytehq/airbyte/pull/44664)       | Update dependencies                                                                                                                                                    |
| 1.0.13  | 2024-08-17 | [44234](https://github.com/airbytehq/airbyte/pull/44234)       | Update dependencies                                                                                                                                                    |
| 1.0.12  | 2024-08-12 | [43729](https://github.com/airbytehq/airbyte/pull/43729)       | Update dependencies                                                                                                                                                    |
| 1.0.11  | 2024-08-10 | [43477](https://github.com/airbytehq/airbyte/pull/43477)       | Update dependencies                                                                                                                                                    |
| 1.0.10  | 2024-08-03 | [43224](https://github.com/airbytehq/airbyte/pull/43224)       | Update dependencies                                                                                                                                                    |
| 1.0.9   | 2024-07-27 | [42787](https://github.com/airbytehq/airbyte/pull/42787)       | Update dependencies                                                                                                                                                    |
| 1.0.8   | 2024-07-20 | [42255](https://github.com/airbytehq/airbyte/pull/42255)       | Update dependencies                                                                                                                                                    |
| 1.0.7   | 2024-07-13 | [41685](https://github.com/airbytehq/airbyte/pull/41685)       | Update dependencies                                                                                                                                                    |
| 1.0.6   | 2024-07-10 | [41543](https://github.com/airbytehq/airbyte/pull/41543)       | Update dependencies                                                                                                                                                    |
| 1.0.5   | 2024-07-09 | [41126](https://github.com/airbytehq/airbyte/pull/41126)       | Update dependencies                                                                                                                                                    |
| 1.0.4   | 2024-07-06 | [40812](https://github.com/airbytehq/airbyte/pull/40812)       | Update dependencies                                                                                                                                                    |
| 1.0.3   | 2024-06-25 | [40500](https://github.com/airbytehq/airbyte/pull/40500)       | Update dependencies                                                                                                                                                    |
| 1.0.2   | 2024-06-22 | [40058](https://github.com/airbytehq/airbyte/pull/40058)       | Update dependencies                                                                                                                                                    |
| 1.0.1   | 2024-06-06 | [39243](https://github.com/airbytehq/airbyte/pull/39243)       | [autopull] Upgrade base image to v1.2.2                                                                                                                                |
| 1.0.0   | 2024-03-14 | [36015](https://github.com/airbytehq/airbyte/pull/36015)       | Upgrade Facebook API to v19.0                                                                                                                                          |
| 0.3.0   | 2023-06-26 | [27728](https://github.com/airbytehq/airbyte/pull/27728)       | License Update: Elv2                                                                                                                                                   |
| 0.2.5   | 2023-04-13 | [26939](https://github.com/airbytehq/airbyte/pull/26939)       | Add advancedAuth to the connector spec                                                                                                                                 |
| 0.2.4   | 2023-04-13 | [25143](https://github.com/airbytehq/airbyte/pull/25143)       | Update insight metrics request params                                                                                                                                  |
| 0.2.3   | 2023-02-23 | [23395](https://github.com/airbytehq/airbyte/pull/23395)       | Parse datetime to rfc3339                                                                                                                                              |
| 0.2.2   | 2023-02-10 | [22804](https://github.com/airbytehq/airbyte/pull/22804)       | Retry 500 errors                                                                                                                                                       |
| 0.2.1   | 2022-12-29 | [20925](https://github.com/airbytehq/airbyte/pull/20925)       | Fix tests; modify expected records                                                                                                                                     |
| 0.2.0   | 2022-11-24 | [19788](https://github.com/airbytehq/airbyte/pull/19788)       | Migrate lo low-code; Beta certification; Upgrade Facebook API to v.15                                                                                                  |
| 0.1.6   | 2021-12-22 | [9032](https://github.com/airbytehq/airbyte/pull/9032)         | Remove deprecated field `live_encoders` from Page stream                                                                                                               |
| 0.1.5   | 2021-11-26 | [8267](https://github.com/airbytehq/airbyte/pull/8267)         | Updated all empty objects in schemas for Page and Post streams                                                                                                         |
| 0.1.4   | 2021-11-26 |                                                                 | Remove unsupported insights_export field from Pages request                                                                                                            |
| 0.1.3   | 2021-10-28 | [7440](https://github.com/airbytehq/airbyte/pull/7440)         | Generate Page token from config access token                                                                                                                           |
| 0.1.2   | 2021-10-18 | [7128](https://github.com/airbytehq/airbyte/pull/7128)         | Upgrade Facebook API to v.12                                                                                                                                           |
| 0.1.1   | 2021-09-30 | [6438](https://github.com/airbytehq/airbyte/pull/6438)         | Annotate Oauth2 flow initialization parameters in connector specification                                                                                              |
| 0.1.0   | 2021-09-01 | [5158](https://github.com/airbytehq/airbyte/pull/5158)         | Initial Release                                                                                                                                                        |

</details>
