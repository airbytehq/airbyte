# Facebook Pages

This page contains the setup guide and reference information for the Facebook Pages source connector.

## Prerequisites

- A [Facebook Developer](https://developers.facebook.com/async/registration/) account
- A [Facebook App](https://developers.facebook.com/apps/)
- A Facebook Page you manage
- A long-lived Page access token with the following permissions:
  - `pages_read_engagement`
  - `pages_read_user_content`
  - `pages_show_list`
  - `read_insights`

:::note
This connector uses the Facebook Graph API v24.0.
:::

## Setup guide

### Set up Facebook Pages

1. Create a [Facebook Developer Account](https://developers.facebook.com/async/registration/).
2. Create a [Facebook App](https://developers.facebook.com/apps/). Choose **Business** as the app type. Fill out the remaining fields to create your app.
3. Open the [Graph API Explorer](https://developers.facebook.com/tools/explorer/). Select your app in the **Meta App** field and your Page in the **User or Page** field. Add the following permissions:
   - `pages_read_engagement`
   - `pages_read_user_content`
   - `pages_show_list`
   - `read_insights`
4. Click **Generate Access Token** and follow the instructions.

After completing these steps, the Graph API Explorer should look something like this:

![Facebook Pages Graph API Explorer](/.gitbook/assets/facebook-pages-1.png)

5. [Generate a long-lived User access token](https://developers.facebook.com/docs/facebook-login/guides/access-tokens/get-long-lived#get-a-long-lived-user-access-token).
6. [Generate a long-lived Page token](https://developers.facebook.com/docs/facebook-login/guides/access-tokens/get-long-lived#long-lived-page-token) from the long-lived User access token.

:::caution
Long-lived Page tokens do not expire as long as the User access token used to generate them remains valid. However, if you change your Facebook password, revoke app permissions, or the app loses its `pages_show_list` permission, the token becomes invalid and you must generate a new one.
:::

### Set up the connector in Airbyte

1. In Airbyte, navigate to **Sources** and click **+ New source**.
2. Select **Facebook Pages** from the source type dropdown.
3. Enter a name for the source.
4. Authenticate using one of the following methods:
   - **OAuth** (Airbyte Cloud only): Click **Authenticate your Facebook Pages account** and follow the prompts.
   - **Page Access Token**: Paste the long-lived Page token you generated in the previous section.
5. Enter your **Page ID**. If your page URL is `https://www.facebook.com/YourPageName`, the Page ID is `YourPageName`. You can also find your numeric Page ID in your Page's **About** section or by using the [Graph API Explorer](https://developers.facebook.com/tools/explorer/).
6. Optionally, set **Page Size** to control the number of records per page for the `post` and `post_insights` streams. The default is 100. Decrease this value if you encounter "Please reduce the amount of data you're asking for" errors.

#### Creating your own OAuth app

If you need to use your own OAuth app instead of the Airbyte-managed one, follow [Meta's guide to creating an app](https://developers.facebook.com/docs/development/create-an-app/).

Your OAuth app requires the following permissions:

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

| Stream | Description |
| :--- | :--- |
| [Page](https://developers.facebook.com/docs/graph-api/reference/v24.0/page/#overview) | Metadata about your Facebook Page, including name, category, description, follower count, and contact information. |
| [Post](https://developers.facebook.com/docs/graph-api/reference/v24.0/page/feed) | Posts published on your Page's feed, including message content, attachments, creation time, and privacy settings. |
| [Page Insights](https://developers.facebook.com/docs/graph-api/reference/v24.0/page/insights) | Aggregated analytics for your Page, such as total actions, post engagements, fan additions, impressions, and media views. |
| [Post Insights](https://developers.facebook.com/docs/graph-api/reference/v24.0/insights) | Per-post analytics, including unique impressions, clicks, click breakdowns by type, reactions by type, and media views. |

## Limitations and troubleshooting

### Access token errors

If syncs fail with authentication errors, your access token may be invalid. Common causes include:

- **Password change**: Changing your Facebook password invalidates all active tokens.
- **Revoked permissions**: If you or another Page admin revokes the app's permissions, the token stops working.
- **App restrictions**: If Meta restricts your app for policy violations, tokens issued by that app become invalid.

To resolve this, generate a new long-lived Page token by following the [setup guide](#set-up-facebook-pages).

### "Bad request" errors (HTTP 400)

If syncs fail with `HTTP Status Code: 400. Error: Bad request. Please check your request parameters`, this typically indicates one of the following:

- **Expired or invalid access token**: The token used to authenticate has expired or been revoked. Generate a new long-lived Page token.
- **Insufficient permissions**: The token lacks one or more required permissions. Verify that your token includes all [required permissions](#prerequisites).
- **Invalid Page ID**: The configured Page ID does not match a Page accessible with the provided token. Verify the Page ID in your connector configuration.

The connector retries 400 errors automatically, so you may see this error reported as a backoff exception after retries are exhausted.

### "Please reduce the amount of data you're asking for" error

This error occurs when the Facebook Graph API considers the response data too large. There are two ways to resolve it:

- **Remove fields from the request**: Go to your connection's **Schema** tab and deselect fields you don't need for the affected stream. This reduces the number of fields included in API requests. Supported streams: `page`, `post`.
- **Reduce page size**: Set the **Page Size** configuration parameter to a lower value, such as 25 or 50. This reduces the number of records fetched per API request. Supported streams: `post`, `post_insights`.

### Product catalogs field not available

Starting from version 2.0.4, the `product_catalogs` field is no longer synced in the Page stream and always returns `null`. The Facebook Graph API only returns product catalogs owned directly by the Page, not catalogs owned by a Business. Because most product catalogs are now Business-owned, this field does not return meaningful data for most users.

### Rate limiting

Facebook applies [rate limits](https://developers.facebook.com/docs/graph-api/overview/rate-limiting) to all API requests. Requests made with Page access tokens are subject to Business Use Case rate limits. If syncs are slow or encounter rate limit errors, you can [request a rate limit increase](https://developers.facebook.com/docs/graph-api/overview/rate-limiting) from Meta.

Using a long-lived Page token rather than a short-lived app token significantly reduces rate limiting issues.

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
| 0.1.5   | 2021-11-26 | [8267](https://github.com/airbytehq/airbyte/pull/8267)         | updated all empty objects in schemas for Page and Post streams                                                                                                         |
| 0.1.4   | 2021-11-26 | [](https://github.com/airbytehq/airbyte/pull/)                 | Remove unsupported insights_export field from Pages request                                                                                                            |
| 0.1.3   | 2021-10-28 | [7440](https://github.com/airbytehq/airbyte/pull/7440)         | Generate Page token from config access token                                                                                                                           |
| 0.1.2   | 2021-10-18 | [7128](https://github.com/airbytehq/airbyte/pull/7128)         | Upgrade Facebook API to v.12                                                                                                                                           |
| 0.1.1   | 2021-09-30 | [6438](https://github.com/airbytehq/airbyte/pull/6438)         | Annotate Oauth2 flow initialization parameters in connector specification                                                                                              |
| 0.1.0   | 2021-09-01 | [5158](https://github.com/airbytehq/airbyte/pull/5158)         | Initial Release                                                                                                                                                        |

</details>
