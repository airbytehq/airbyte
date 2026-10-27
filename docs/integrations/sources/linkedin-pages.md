# LinkedIn Pages

<HideInUI>

This page contains the setup guide and reference information for the [LinkedIn Pages](https://docs.airbyte.com/integrations/sources/linkedin-pages) source connector.

</HideInUI>

This source syncs one LinkedIn Page through LinkedIn's [Community Management API](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/community-management-overview?view=li-lms-2026-10): the page's profile, its follower, share and page statistics, and its posts with their comments and reactions.

## Prerequisites

- A LinkedIn member who is a **super admin** of the page. The API calls this role `ADMINISTRATOR`, and LinkedIn only returns statistics for pages where the member who authorized the token has it.
- A LinkedIn developer app with access to the Community Management API. LinkedIn reviews every access request and only grants this API to registered legal organizations, so have your organization's legal name and address and a business email address ready ([app review](https://learn.microsoft.com/en-us/linkedin/marketing/community-management-app-review?view=li-lms-2026-10)).
- The app's **Client ID** and **Client Secret**, and a refresh token or an access token that the super admin authorized with the scopes listed in [Set up LinkedIn Pages](#set-up-linkedin-pages).
- The page's **Organization ID**: the number in the page's admin URL, for example `123456789` in `linkedin.com/company/123456789/admin`.

## Setup guide

### Set up LinkedIn Pages

Airbyte Cloud and Airbyte Open Source both use credentials from your own LinkedIn developer app.

1. Sign in to LinkedIn as a super admin of the page.
2. Open [LinkedIn Developers](https://www.linkedin.com/developers/apps) and select **Create app**. Enter an app name that doesn't contain "LinkedIn", select your page under **LinkedIn Page**, add a privacy policy URL and a logo, accept the legal agreement, and create the app.
3. In the app's **Settings** tab, select **Verify**, generate the verification URL and send it to a super admin of the page. They have 30 days to approve it. If you're the super admin, open the URL yourself.
4. In the **Products** tab, request access to the **Community Management API** and fill in LinkedIn's access request form. LinkedIn only accepts this request from a new app that has no other API products, and a rejected request can't be repeated with the same app ([LinkedIn FAQ](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/community-management-overview?view=li-lms-2026-10#frequently-asked-questions)).
5. LinkedIn starts approved apps on the Development tier: 500 requests per app and 100 per member per day, meant for building and testing, which LinkedIn expects you to finish within 12 months. The Standard tier is LinkedIn's production tier. Apply for it early from the **Products** tab: LinkedIn asks for a screen recording of the app and test credentials ([access tiers](https://learn.microsoft.com/en-us/linkedin/marketing/increasing-access?view=li-lms-2026-10)).
6. In the **Auth** tab, copy the **Client ID** and the **Primary Client Secret**.
7. Open the [OAuth Token Tools](https://www.linkedin.com/developers/tools/oauth), select **Create token**, and select your app. Select the `rw_organization_admin` and `r_organization_social` scopes. For `post_comments`, also select `r_organization_social_feed`, which LinkedIn grants with the Community Management API: without it, that stream fails with a `403` error while the other streams keep working. Request the token, sign in as the super admin, and allow access.
8. Copy the refresh token and the access token. An access token lasts 60 days. A refresh token lasts 365 days from when you create it, refreshing doesn't extend it, and the connector exchanges it for a new access token on each sync. Create a new token before the year is up. LinkedIn only returns refresh tokens to [apps approved for them](https://learn.microsoft.com/en-us/linkedin/shared/authentication/programmatic-refresh-tokens). If you don't get one, use the **Access token** method and replace the token every 60 days.

### Set up the LinkedIn Pages connector in Airbyte

1. In Airbyte, go to **Sources** and select **New source**, then select **LinkedIn Pages**.
2. For **Authentication**, select **OAuth2.0** and enter the **Client ID**, **Client secret** and **Refresh token** from the steps above. Or select **Access token** and enter the access token.
3. For **Organization ID**, enter the number from the page's admin URL.
4. Optional: for **Start Date**, enter a UTC date and time in the format `YYYY-MM-DDT00:00:00Z`. LinkedIn serves time-bound statistics for the last 12 months only, so an earlier date is clamped to 12 months ago for those streams. Posts, comments, reactions and post statistics cover posts last modified since this date, or all posts if you leave it blank. The three per-post streams send requests for every post in that range on each sync, so a later date saves daily quota.
5. For **Time Granularity Type**, select `DAY` (the default) or `MONTH`. It applies to the three time-bound statistics streams.
6. Optional: for **Number of concurrent workers**, enter a value from 1 to 10. The default is 3, and values below 2 run as 2.
7. Select **Set up source**.

## Supported sync modes

The LinkedIn Pages source connector supports the following [sync modes](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes):

- Full Refresh - Overwrite
- Full Refresh - Append
- Incremental - Append, for the time-bound statistics streams and `posts`
- Incremental - Append + Deduped, for the time-bound statistics streams and `posts`

Every stream declares a primary key, so **Full Refresh - Overwrite + Deduped** is also available where your destination supports it.

## Supported Streams

| Stream | Sync modes | Primary key | Cursor |
| :-- | :-- | :-- | :-- |
| [`organization_lookup`](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/organizations/organization-lookup-api?view=li-lms-2026-10#retrieve-organizations) | Full Refresh | `id` | |
| [`total_follower_count`](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/organizations/organization-lookup-api?view=li-lms-2026-10#retrieve-organization-follower-count) | Full Refresh | `organizationalEntity` | |
| [`follower_statistics`](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/organizations/follower-statistics?view=li-lms-2026-10#retrieve-lifetime-follower-statistics) | Full Refresh | `organizationalEntity` | |
| [`share_statistics`](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/organizations/share-statistics?view=li-lms-2026-10#retrieve-lifetime-share-statistics) | Full Refresh | `organizationalEntity` | |
| [`page_statistics`](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/organizations/page-statistics?view=li-lms-2026-10#retrieve-lifetime-organization-page-statistics) | Full Refresh | `organization` | |
| [`follower_statistics_time_bound`](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/organizations/follower-statistics?view=li-lms-2026-10#retrieve-time-bound-follower-statistics) | Full Refresh, Incremental | `organizationalEntity`, `timeRangeStart`, `timeRangeEnd` | `timeRangeEnd` |
| [`share_statistics_time_bound`](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/organizations/share-statistics?view=li-lms-2026-10#retrieve-time-bound-share-statistics) | Full Refresh, Incremental | `organizationalEntity`, `timeRangeStart`, `timeRangeEnd` | `timeRangeEnd` |
| [`page_statistics_time_bound`](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/organizations/page-statistics?view=li-lms-2026-10#retrieve-time-bound-organization-page-statistics) | Full Refresh, Incremental | `organization`, `timeRangeStart`, `timeRangeEnd` | `timeRangeEnd` |
| [`posts`](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/posts-api?view=li-lms-2026-10#find-posts-by-authors) | Full Refresh, Incremental | `id` | `lastModifiedAt` |
| [`post_comments`](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/comments-api?view=li-lms-2026-10#get-comments-on-shares) | Full Refresh | `object`, `id` | |
| [`post_reactions`](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/reactions-api?view=li-lms-2026-10#get-reactions-on-a-share) | Full Refresh | `id` | |
| [`post_statistics`](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/organizations/share-statistics?view=li-lms-2026-10#retrieve-statistics-for-specific-shares) | Full Refresh | `post_urn` | |

### Lifetime statistics

`total_follower_count`, `follower_statistics`, `share_statistics` and `page_statistics` return one row per sync with the page's current totals. In **Overwrite** or **Deduped** modes you keep the latest row. In **Append** modes each sync adds a snapshot.

### Time-bound statistics

:::warning
LinkedIn only serves the last 12 months of time-bound statistics. Sync the three time-bound streams in an **Incremental** mode to keep older rows. **Full Refresh - Overwrite**, clearing a stream and refreshing it with **Remove records** keep only the last 12 months, so back up the tables before you do any of them.
:::

LinkedIn serves time-bound statistics from 12 months before the request date up to 2 days before it, in UTC. Every window the connector requests starts and ends at midnight UTC:

- With `DAY`, a sync reads whole days up to 3 days back: a sync on October 27 reads through October 24.
- With `MONTH`, a sync reads complete months only, so a month arrives 2 days after it ends. When 12 months ago or the **Start Date** falls inside a month, the first sync, and the first sync after a clear or refresh, includes that partial month.

`date` on the three time-bound streams is the UTC date of `timeRangeStart`. If you change **Time Granularity Type**, the rows you already synced stay: day and month rows have different keys, so filter on `timeRangeEnd - timeRangeStart` before you aggregate.

### Posts, comments and reactions

`posts` syncs posts the page authored and last modified since **Start Date**, or all of them when it is blank. LinkedIn's posts endpoint has no date filter, so each sync pages through every post the page ever authored, 100 per request, and keeps those inside the window. Incremental syncs add new and edited posts. LinkedIn doesn't return deleted posts, so they stay in your destination until you refresh the stream. If a newer post is deleted while a sync pages through the list, one older post can be skipped until you refresh `posts`. Before you refresh it, check that **Start Date** covers every post you want to keep.

`post_comments`, `post_reactions` and `post_statistics` request every post from the window on each sync. `post_comments` syncs first-level comments only, not replies. `post_statistics` holds lifetime clicks, comments, engagement, impressions, likes and shares per post; LinkedIn leaves out posts without impressions or actions, so those have no row. When a post is deleted during a sync, the connector logs the 404 for that post and continues.

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

### Performance considerations

- LinkedIn limits the number of requests per app and per member each day, and the limits reset at midnight UTC. The Development tier allows 500 requests per app and 100 per member. LinkedIn doesn't publish Standard tier limits: see your app's **Analytics** tab in [LinkedIn Developers](https://www.linkedin.com/developers/apps) ([rate limits](https://learn.microsoft.com/en-us/linkedin/shared/api-guide/concepts/rate-limits)). The same tab shows the daily quota for exchanging refresh tokens.
- The connector retries `429` and `5xx` responses with exponential backoff, up to 5 times. If the daily quota is used up, the sync fails after its retries. Run it again after midnight UTC.
- `post_comments`, `post_reactions` and `post_statistics` send at least one request per post in the window on every sync, so request volume grows with the number of posts. On the Development tier, a window with more than about 100 posts uses up the daily quota for these streams. Set a later **Start Date**, turn off these streams, or move to the Standard tier.
- More concurrent workers finish syncs with many posts faster, but they use the daily quota faster too.
- The connector sends `Linkedin-Version: 202610`. LinkedIn supports each monthly API version for at least one year ([versioning](https://learn.microsoft.com/en-us/linkedin/marketing/versioning)). When LinkedIn retires the version a connector release sends, syncs fail with a `426` error until you upgrade the connector.

## Limitations & Troubleshooting

- **`Refresh token was rejected by the OAuth provider`**: the refresh token expired (365 days after you created it) or was revoked. Create a new token as in [Set up LinkedIn Pages](#set-up-linkedin-pages) and update the source.
- **`LinkedIn rejected the credentials (401)`**: the access token expired or was revoked. Create a new token and update the source.
- **`LinkedIn denied the request (403)`**: the token is missing a scope from the setup steps (`post_comments` needs `r_organization_social_feed`), or the member who authorized it isn't a super admin of the page in **Organization ID**.
- **`LinkedIn returned 404 for organization ...`**: check the **Organization ID**. The page may also be deactivated, or the app may not have access to the Community Management API.
- **`LinkedIn no longer accepts the API version this connector version sends (426)`**: upgrade the source to the latest version.
- **`API rate limit exceeded.`** or **`LinkedIn rate limit reached (429)`**: the daily quota is used up. See [Performance considerations](#performance-considerations).

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
| :-------- | :----------- | :------------------------------------------------------- | :--------------------------------------------------- |
| 2.0.0 | 2026-10-27 | [89708](https://github.com/airbytehq/airbyte/pull/89708) | Declare primary keys, type epoch-millisecond fields as integers and add a date field to time-bound statistics |
| 1.3.0 | 2026-10-26 | [89713](https://github.com/airbytehq/airbyte/pull/89713) | Add posts, comments, reactions, post statistics and page statistics streams |
| 1.2.0 | 2026-10-26 | [89710](https://github.com/airbytehq/airbyte/pull/89710) | Retry rate limits and server errors, explain auth and API version errors, and request whole statistics windows |
| 1.1.27 | 2026-10-20 | [89366](https://github.com/airbytehq/airbyte/pull/89366) | Update LinkedIn API version to 202610 |
| 1.1.26 | 2026-09-14 | [85905](https://github.com/airbytehq/airbyte/pull/85905) | Update LinkedIn Marketing API version from 202503 to 202608 |
| 1.1.25 | 2025-05-24 | [60685](https://github.com/airbytehq/airbyte/pull/60685) | Update dependencies |
| 1.1.24 | 2025-05-10 | [59786](https://github.com/airbytehq/airbyte/pull/59786) | Update dependencies |
| 1.1.23 | 2025-05-03 | [58801](https://github.com/airbytehq/airbyte/pull/58801) | Update dependencies |
| 1.1.22 | 2025-04-19 | [58174](https://github.com/airbytehq/airbyte/pull/58174) | Update dependencies |
| 1.1.21 | 2025-04-12 | [57721](https://github.com/airbytehq/airbyte/pull/57721) | Update dependencies |
| 1.1.20 | 2025-04-05 | [56679](https://github.com/airbytehq/airbyte/pull/56679) | Update dependencies |
| 1.1.19 | 2025-03-22 | [56029](https://github.com/airbytehq/airbyte/pull/56029) | Update dependencies |
| 1.1.18 | 2025-03-18 | [55816](https://github.com/airbytehq/airbyte/pull/55816) | Bump LinkedIn API to 202503 |
| 1.1.17 | 2025-03-08 | [55441](https://github.com/airbytehq/airbyte/pull/55441) | Update dependencies |
| 1.1.16 | 2025-03-01 | [54775](https://github.com/airbytehq/airbyte/pull/54775) | Update dependencies |
| 1.1.15 | 2025-02-22 | [54339](https://github.com/airbytehq/airbyte/pull/54339) | Update dependencies |
| 1.1.14 | 2025-02-15 | [53859](https://github.com/airbytehq/airbyte/pull/53859) | Update dependencies |
| 1.1.13 | 2025-02-08 | [53256](https://github.com/airbytehq/airbyte/pull/53256) | Update dependencies |
| 1.1.12 | 2025-02-01 | [52767](https://github.com/airbytehq/airbyte/pull/52767) | Update dependencies |
| 1.1.11 | 2025-01-25 | [52246](https://github.com/airbytehq/airbyte/pull/52246) | Update dependencies |
| 1.1.10 | 2025-01-18 | [51798](https://github.com/airbytehq/airbyte/pull/51798) | Update dependencies |
| 1.1.9 | 2025-01-11 | [51149](https://github.com/airbytehq/airbyte/pull/51149) | Update dependencies |
| 1.1.8 | 2024-12-28 | [50645](https://github.com/airbytehq/airbyte/pull/50645) | Update dependencies |
| 1.1.7 | 2024-12-21 | [50114](https://github.com/airbytehq/airbyte/pull/50114) | Update dependencies |
| 1.1.6 | 2024-12-14 | [49593](https://github.com/airbytehq/airbyte/pull/49593) | Update dependencies |
| 1.1.5 | 2024-12-12 | [49272](https://github.com/airbytehq/airbyte/pull/49272) | Update dependencies |
| 1.1.4 | 2024-12-11 | [48924](https://github.com/airbytehq/airbyte/pull/48924) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 1.1.3 | 2024-10-29 | [47749](https://github.com/airbytehq/airbyte/pull/47749) | Update dependencies |
| 1.1.2 | 2024-10-28 | [47455](https://github.com/airbytehq/airbyte/pull/47455) | Update dependencies |
| 1.1.1 | 2024-08-16 | [44196](https://github.com/airbytehq/airbyte/pull/44196) | Bump source-declarative-manifest version |
| 1.1.0 | 2024-08-15 | [44132](https://github.com/airbytehq/airbyte/pull/44132) | Refactor connector to manifest-only format |
| 1.0.17 | 2024-08-10 | [43560](https://github.com/airbytehq/airbyte/pull/43560) | Update dependencies |
| 1.0.16 | 2024-08-03 | [43281](https://github.com/airbytehq/airbyte/pull/43281) | Update dependencies |
| 1.0.15 | 2024-07-27 | [42782](https://github.com/airbytehq/airbyte/pull/42782) | Update dependencies |
| 1.0.14 | 2024-07-20 | [42218](https://github.com/airbytehq/airbyte/pull/42218) | Update dependencies |
| 1.0.13 | 2024-07-13 | [41833](https://github.com/airbytehq/airbyte/pull/41833) | Update dependencies |
| 1.0.12 | 2024-07-10 | [41407](https://github.com/airbytehq/airbyte/pull/41407) | Update dependencies |
| 1.0.11 | 2024-07-09 | [41274](https://github.com/airbytehq/airbyte/pull/41274) | Update dependencies |
| 1.0.10 | 2024-07-06 | [40828](https://github.com/airbytehq/airbyte/pull/40828) | Update dependencies |
| 1.0.9 | 2024-06-25 | [40422](https://github.com/airbytehq/airbyte/pull/40422) | Update dependencies |
| 1.0.8 | 2024-06-22 | [39975](https://github.com/airbytehq/airbyte/pull/39975) | Update dependencies |
| 1.0.7 | 2024-06-13 | [36744](https://github.com/airbytehq/airbyte/pull/36744) | Add time bound incremental streams for follower & share statistics. Migrate to Low Code |
| 1.0.6 | 2024-06-06 | [39171](https://github.com/airbytehq/airbyte/pull/39171) | [autopull] Upgrade base image to v1.2.2 |
| 1.0.5 | 2024-06-03 | [38918](https://github.com/airbytehq/airbyte/pull/38918) | Replace AirbyteLogger with logging.Logger |
| 1.0.4 | 2024-06-03 | [38918](https://github.com/airbytehq/airbyte/pull/38918) | Replace AirbyteLogger with logging.Logger |
| 1.0.3 | 2024-05-21 | [38526](https://github.com/airbytehq/airbyte/pull/38526) | [autopull] base image + poetry + up_to_date |
| 1.0.2 | 2023-05-30 | [24352](https://github.com/airbytehq/airbyte/pull/24352) | Remove duplicate streams |
| 1.0.1 | 2023-03-22 | [24352](https://github.com/airbytehq/airbyte/pull/24352) | Remove `authSpecification` as it's not yet supported |
| 1.0.0 | 2023-03-16 | [18967](https://github.com/airbytehq/airbyte/pull/18967) | Fixed failing connection checks |
| 0.1.0 | 2022-08-11 | [13098](https://github.com/airbytehq/airbyte/pull/13098) | Initial Release |

</details>
