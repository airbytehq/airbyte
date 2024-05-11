# Instagram Migration Guide

## Upgrading to 3.0.0

The Instagram connector has been upgrade to API v18 (following the deprecation of v11). Connector will be upgraded to API v18. Affected Streams and their corresponding changes are listed below:

- `Media Insights`

  Old metric will be replaced with the new ones, refer to the [IG Media Insights](https://developers.facebook.com/docs/instagram-api/reference/ig-media/insights#metrics) for more info.

  | Old metric                 | New metric         |
  | -------------------------- | ------------------ |
  | carousel_album_engagement  | total_interactions |
  | carousel_album_impressions | impressions        |
  | carousel_album_reach       | reach              |
  | carousel_album_saved       | saved              |
  | carousel_album_video_views | video_views        |
  | engagement                 | total_interactions |

:::note

You may see different results: `engagement` count includes likes, comments, and saves while `total_interactions` count includes likes, comments, and saves, as well as shares.

:::

New metrics for Reels: `ig_reels_avg_watch_time`, `ig_reels_video_view_total_time`

- `User Lifetime Insights`

  - Metric `audience_locale` will become unavailable.
  - Metrics `audience_city`, `audience_country`, and `audience_gender_age` will be consolidated into a single metric named `follower_demographics`, featuring respective breakdowns for `city`, `country`, and `age,gender`.
  - Primary key will be changed to `["business_account_id", "breakdown"]`.

:::note

Due to Instagram limitations, the "Metric Type" will be set to `total_value` for `follower_demographics` metric. Refer to the [docs](https://developers.facebook.com/docs/instagram-api/reference/ig-user/insights#metric-type) for more info.

:::

- `Story Insights`

  Metrics: `exits`, `taps_back`, `taps_forward` will become unavailable.

Please follow the instructions below to migrate to version 3.0.0:

1. Select **Connections** in the main navbar.
   1.1 Select the connection(s) affected by the update.
2. Select the **Replication** tab.
   2.1 Select **Refresh source schema**.
   `note
        Any detected schema changes will be listed for your review.
        `
   2.2 Select **OK**.
3. Select **Save changes** at the bottom of the page.
   3.1 Ensure the **Reset affected streams** option is checked.
   `note
        Depending on destination type you may not be prompted to reset your data
        `
4. Select **Save connection**.
   `note
    This will reset the data in your destination and initiate a fresh sync.
    `

For more information on resetting your data in Airbyte, see [this page](https://docs.airbyte.com/operator-guides/reset).

## Upgrading to 2.0.0

This release adds a default primary key for the streams UserLifetimeInsights and UserInsights, and updates the format of timestamp fields in the UserLifetimeInsights, UserInsights, Media and Stories streams to include timezone information.

To ensure uninterrupted syncs, users should:

- Refresh the source schema
- Reset affected streams
