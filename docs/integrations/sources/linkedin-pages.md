# LinkedIn Pages

This page contains the setup guide and reference information for the LinkedIn Pages source connector.

The connector syncs follower, share, and profile data for a single LinkedIn Page (organization) using the [LinkedIn Community Management API](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/community-management-overview?view=li-lms-2026-10). It sends requests with the `Linkedin-Version: 202610` header. LinkedIn supports each Marketing API version for at least one year, so the connector must be updated periodically to stay on a supported version.

## Prerequisites

- A LinkedIn member account with the **ADMINISTRATOR** role on the LinkedIn Page you want to sync. The API returns `403 Forbidden` for organizations the authenticated member doesn't administer.
- A LinkedIn developer app that has been approved for the **Community Management API** product.
- The `rw_organization_admin` OAuth scope. Every stream this connector syncs requires this scope.
- The numeric ID of your LinkedIn Page (organization).

## Setup guide

### Step 1: Create a LinkedIn developer app

1. Sign in to LinkedIn as a member who is an administrator of the Page you want to sync.
2. Go to [LinkedIn Developers](https://www.linkedin.com/developers/apps) and click **Create app**. Provide:
   - **App name**: for example, `airbyte-source`.
   - **LinkedIn Page**: search for and select your company's LinkedIn Page.
   - **Privacy policy URL**: a link to your company's privacy policy.
   - **App logo**: your company's logo.
3. Review and agree to the legal terms, then create the app.
4. On the **Settings** tab, click **Verify** and send the generated verification URL to an administrator of your LinkedIn Page so they can verify the app.
5. On the **Auth** tab, copy the **Client ID** and **Client Secret**. You need these if you use OAuth 2.0 authentication.

### Step 2: Request Community Management API access

1. On the **Products** tab of your app, request access to the **Community Management API**.
2. Complete the access request form. LinkedIn first grants the Development tier, which has limited API call volume. To get full access, apply for the Standard tier. For details, see [Community Management API access](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/community-management-overview?view=li-lms-2026-10).

:::note
If your app already has the Advertising API product, LinkedIn requires you to apply for Community Management API Development tier access from a new app linked to the same LinkedIn Page. After LinkedIn approves the Standard tier, you can request it on your existing app. For details, see the FAQ on the [Community Management API overview](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/community-management-overview?view=li-lms-2026-10).
:::

### Step 3: Generate a token

1. Go to the LinkedIn Developers [OAuth Token Tools](https://www.linkedin.com/developers/tools/oauth) and click **Create token**.
2. Select the app you created and select the `rw_organization_admin` scope.
3. Click **Request access token**. Save the **Access token**, and the **Refresh token** if one is shown.

Access tokens are valid for 60 days. Refresh tokens are valid for 365 days from when they were first issued, and using a refresh token to get a new access token doesn't extend that lifetime. When a token expires, the connector receives a `401` response and you need to generate a new token. For more information, see [Refresh tokens with OAuth 2.0](https://learn.microsoft.com/en-us/linkedin/shared/authentication/programmatic-refresh-tokens).

### Step 4: Find your organization ID

The connector needs the numeric organization ID that LinkedIn uses in organization URNs (`urn:li:organization:{id}`), such as `123456789`. This isn't the same as your Page's vanity name. If you only know the vanity name, you can look up the ID with the [Organization Lookup API](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/organizations/organization-lookup-api?view=li-lms-2026-10).

### Step 5: Set up the connector in Airbyte

1. In Airbyte, create a new source and select **LinkedIn Pages**.
2. For **Authentication**, choose one of the following:
   - **OAuth2.0**: Enter the **Client ID**, **Client secret**, and **Refresh token**. The connector uses the refresh token to request new access tokens, so it keeps working until the refresh token expires after 365 days.
   - **Access token**: Enter the **Access token**. The connector stops working when the token expires after 60 days.
3. For **Organization ID**, enter the ID from Step 4.
4. (Optional) For **Start Date**, enter the date in `YYYY-MM-DDTHH:MM:SSZ` format from which to sync the time-bound streams. See [Time-bound streams](#time-bound-streams) for how the connector applies this value.
5. (Optional) For **Time Granularity Type**, choose `DAY` or `MONTH`. This controls the granularity of the time-bound streams. The default is `DAY`.
6. Click **Set up source**.

## Supported sync modes

| Feature                                   | Supported? | Notes                                   |
| :---------------------------------------- | :--------- | :-------------------------------------- |
| Full Refresh Overwrite Sync               | Yes        |                                         |
| Full Refresh Append Sync                  | Yes        |                                         |
| Incremental - Append Sync                 | Yes        | Time-bound streams only                 |
| Incremental - Append + Deduplication Sync | No         | Streams don't define a primary key      |
| Namespaces                                | No         |                                         |

## Supported streams

| Stream | API endpoint | Incremental |
| :----- | :----------- | :---------- |
| `organization_lookup` | [Organization lookup](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/organizations/organization-lookup-api?view=li-lms-2026-10) (`/organizations/{id}`) | No |
| `follower_statistics` | [Lifetime follower statistics](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/organizations/follower-statistics?view=li-lms-2026-10) (`/organizationalEntityFollowerStatistics`) | No |
| `share_statistics` | [Lifetime share statistics](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/organizations/share-statistics?view=li-lms-2026-10) (`/organizationalEntityShareStatistics`) | No |
| `total_follower_count` | [Organization follower count](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/organizations/organization-lookup-api?view=li-lms-2026-10) (`/networkSizes`) | No |
| `follower_statistics_time_bound` | [Time-bound follower statistics](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/organizations/follower-statistics?view=li-lms-2026-10) (`/organizationalEntityFollowerStatistics`) | Yes |
| `share_statistics_time_bound` | [Time-bound share statistics](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/organizations/share-statistics?view=li-lms-2026-10) (`/organizationalEntityShareStatistics`) | Yes |

`follower_statistics` returns lifetime follower counts segmented by demographic facets such as function, seniority, industry, and location. LinkedIn limits each facet to the top 100 results. Share statistics include organic activity only. Sponsored activity isn't counted.

### Time-bound streams

The `follower_statistics_time_bound` and `share_statistics_time_bound` streams return statistics for each day or month, depending on **Time Granularity Type**. They use `timeRangeEnd`, in epoch milliseconds, as the incremental cursor.

LinkedIn only returns time-bound statistics from 12 months before the request date up to 2 days before the request date (UTC). The connector enforces this window:

- The sync starts at the later of **Start Date** and 365 days before the current date. If **Start Date** is older than 365 days, the connector ignores it and starts 365 days ago.
- The sync ends 2 days before the current date.

Time-bound follower statistics are aggregated counts. LinkedIn doesn't segment them by demographic facet.

## Data type mapping

| Integration Type | Airbyte Type | Notes                      |
| :--------------- | :----------- | :------------------------- |
| `number`         | `number`     | float number               |
| `integer`        | `integer`    | whole number               |
| `array`          | `array`      |                            |
| `boolean`        | `boolean`    | True/False                 |
| `string`         | `string`     |                            |

## Limitations and troubleshooting

### Rate limits

LinkedIn limits the number of API calls each application and member can make in a 24-hour period. These limits reset at midnight UTC. LinkedIn doesn't publish the limits; to see them, go to [LinkedIn Developers](https://www.linkedin.com/developers/apps), select your app, and open the **Analytics** tab. For more information, see [LinkedIn rate limits](https://learn.microsoft.com/en-us/linkedin/shared/api-guide/concepts/rate-limits).

The connector doesn't retry rate-limited requests. If LinkedIn returns a `429 Too Many Requests` response, the sync fails with a message that the LinkedIn API requests are rate limited. Wait for the limit to reset, then run the sync again.

### Invalid time intervals

If a time-bound stream fails with a message that the start date must be at most 12 months and at least 2 days before the request date, LinkedIn rejected the requested time range. Check that **Start Date** is at least 2 days in the past.

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
| :-------- | :----------- | :------------------------------------------------------- | :--------------------------------------------------- |
| 1.1.27 | 2026-10-21 | [89366](https://github.com/airbytehq/airbyte/pull/89366) | Update LinkedIn API version to 202610 |
| 1.1.26 | 2026-10-19 | [85905](https://github.com/airbytehq/airbyte/pull/85905) | Update LinkedIn Marketing API version from 202503 to 202608 |
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
