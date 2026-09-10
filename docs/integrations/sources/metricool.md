# Metricool

The Metricool source connector pulls social media analytics from the [Metricool REST API](https://app.metricool.com/resources/apidocs/index.html). For each brand you configure, it reads post-level and story-level statistics and daily metric timelines for Facebook, Instagram, TikTok, LinkedIn, Twitter (X), and YouTube, plus competitor benchmarks for Facebook and Instagram.

## Prerequisites

- A Metricool account on the **Advanced** or **Custom** plan. Metricool only exposes its API on these plans; Free and Starter accounts have no API token.
- Your Metricool API token, user ID, and the brand ID of each brand you want to sync. See [Get your credentials](#get-your-credentials).

## Setup guide

### Get your credentials

The connector authenticates every request with your API token (sent in the `X-Mc-Auth` header) and scopes requests with your user ID and brand IDs (sent as the `userId` and `blogId` query parameters).

1. **API token** (`user_token`): In Metricool, go to **Account Settings** > **API** and copy the REST API access token. If you regenerate the token in Metricool, update it in Airbyte too, because the old token stops working.
2. **User ID** (`user_id`): Open any brand in the Metricool web app and copy the number after `userId=` in the browser URL. For example, in `https://app.metricool.com/evolution/web?blogId=11111&userId=2222222`, the user ID is `2222222`.
3. **Brand IDs** (`blog_ids`): In the same URL, the number after `blogId=` is the ID of the brand you have open. Repeat for each brand you want to sync. Metricool calls these "blogs" in its API, which is why the field is named `blog_ids`.

You can also sync only the `brands` stream first: it lists every brand your user ID has access to along with its `id`, so you can copy the IDs from there and add them to `blog_ids` afterward.

### Set up the connector in Airbyte

1. In Airbyte, add a new **Metricool** source.
2. Enter your **User Token**, **User ID**, and one or more **Blog IDs**.
3. Optionally set a **Start Date** and **End Date**. Both must be UTC timestamps in the format `YYYY-MM-DDTHH:mm:ssZ`, for example `2026-01-01T00:00:00Z`.
4. Test and save the source.

### Date range behavior

Every stream except `brands` requests data for a date range. The connector derives the range from **Start Date** and **End Date** as follows:

- If you set neither, the range is the 60 days before the current UTC time.
- If you set only **End Date**, the range is the single day before that end date.
- If you set only **Start Date**, the range runs from that date to the current UTC time.
- If you set both and **Start Date** is earlier than **End Date**, the connector uses them as given. If **Start Date** is the same as or later than **End Date**, the connector ignores it and uses the day before **End Date** instead.

Incremental timeline streams use this range only for the first sync. Later syncs start from the saved cursor, and the connector caps the range at **End Date** if you set one, so a fixed **End Date** stops incremental streams from advancing past it.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `user_token` | `string` | Metricool REST API access token from **Account Settings** > **API**. Requires an Advanced or Custom plan. |  |
| `user_id` | `string` | Your Metricool user ID (the `userId` value in the app URL). |  |
| `blog_ids` | `array` | Metricool brand IDs (the `blogId` value in the app URL). Each ID is synced as its own partition. |  |
| `start_date` | `string` | Start of the date range, in `YYYY-MM-DDTHH:mm:ssZ` format. See [Date range behavior](#date-range-behavior). | 60 days before the current time |
| `end_date` | `string` | End of the date range, in `YYYY-MM-DDTHH:mm:ssZ` format. | Current UTC time |

## Streams

The connector reads each stream once per brand in `blog_ids`, except `brands`, which is read once per account. Timeline streams are additionally read once per metric.

| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| brands | id | No pagination | ✅ |  ❌  |
| facebook_competitors | id | No pagination | ✅ |  ❌  |
| facebook_stories | blogId.storyId | No pagination | ✅ |  ❌  |
| facebook_posts | blogId.postId | No pagination | ✅ |  ❌  |
| facebook_reels | blogId.reelId | No pagination | ✅ |  ❌  |
| facebook_stories_timelines | datetime.blogId.metric | No pagination | ✅ |  ✅  |
| facebook_posts_timelines | datetime.blogId.metric | No pagination | ✅ |  ✅  |
| facebook_reels_timelines | datetime.blogId.metric | No pagination | ✅ |  ✅  |
| instagram_competitors | id | No pagination | ✅ |  ❌  |
| instagram_stories | blogId.postId | No pagination | ✅ |  ❌  |
| instagram_posts | blogId.postId | No pagination | ✅ |  ❌  |
| instagram_reels | blogId.reelId | No pagination | ✅ |  ❌  |
| instagram_stories_timelines | datetime.blogId.metric | No pagination | ✅ |  ✅  |
| instagram_posts_timelines | datetime.blogId.metric | No pagination | ✅ |  ✅  |
| instagram_reels_timelines | datetime.blogId.metric | No pagination | ✅ |  ✅  |
| tiktok_posts | blogId.videoId | No pagination | ✅ |  ❌  |
| tiktok_video_timelines | datetime.blogId.metric | No pagination | ✅ |  ✅  |
| tiktok_account_timelines | datetime.blogId.metric | No pagination | ✅ |  ✅  |
| linkedin_posts | postId | No pagination | ✅ |  ❌  |
| twitter_posts | id | No pagination | ✅ |  ❌  |
| youtube_posts | videoId | No pagination | ✅ |  ❌  |

### Brands

`brands` lists the brands (Metricool "blogs") your user ID can access, including each brand's `id`, `title`, and `url`, and which social networks are connected to it. It doesn't use `blog_ids` or the date range.

### Content streams

The `*_posts`, `*_stories`, and `*_reels` streams return one record per piece of content published in the date range, with that content's engagement statistics. `facebook_competitors` and `instagram_competitors` return the competitor profiles you track in Metricool for each brand; the connector requests at most 100 competitors per brand and does not paginate beyond that.

### Timeline streams

The `*_timelines` streams return daily values for a fixed list of metrics. Each record holds one metric for one brand on one day: the `datetime` field is the day (normalized to UTC), `metric` is the metric name, `blogId` is the brand, and `value` is the number. To build a wide table with one column per metric, pivot on `metric` downstream.

The timeline streams are the only incremental streams. They use `datetime` as the cursor.

## Limitations

- Metricool's public API documentation doesn't list rate limits. You can see your current API usage under **Account Settings** > **API** in Metricool.
- No stream paginates. Competitor streams are capped at 100 records per brand, and content streams return whatever the API returns for the requested date range in a single response.

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.35 | 2026-09-10 | [79626](https://github.com/airbytehq/airbyte/pull/79626) | Add `url` and `title` fields to the `brands` stream schema |
| 0.0.34 | 2026-09-08 | [85550](https://github.com/airbytehq/airbyte/pull/85550) | Update dependencies |
| 0.0.33 | 2026-08-18 | [84645](https://github.com/airbytehq/airbyte/pull/84645) | Update dependencies |
| 0.0.32 | 2026-08-11 | [84006](https://github.com/airbytehq/airbyte/pull/84006) | Update dependencies |
| 0.0.31 | 2026-08-04 | [83524](https://github.com/airbytehq/airbyte/pull/83524) | Update dependencies |
| 0.0.30 | 2026-07-28 | [82987](https://github.com/airbytehq/airbyte/pull/82987) | Update dependencies |
| 0.0.29 | 2026-07-21 | [82487](https://github.com/airbytehq/airbyte/pull/82487) | Update dependencies |
| 0.0.28 | 2026-07-14 | [81904](https://github.com/airbytehq/airbyte/pull/81904) | Update dependencies |
| 0.0.27 | 2026-06-30 | [81164](https://github.com/airbytehq/airbyte/pull/81164) | Update dependencies |
| 0.0.26 | 2026-06-23 | [80557](https://github.com/airbytehq/airbyte/pull/80557) | Update dependencies |
| 0.0.25 | 2026-06-16 | [79943](https://github.com/airbytehq/airbyte/pull/79943) | Update dependencies |
| 0.0.24 | 2026-06-09 | [79417](https://github.com/airbytehq/airbyte/pull/79417) | Update dependencies |
| 0.0.23 | 2026-06-02 | [78839](https://github.com/airbytehq/airbyte/pull/78839) | Update dependencies |
| 0.0.22 | 2026-04-28 | [77342](https://github.com/airbytehq/airbyte/pull/77342) | Update dependencies |
| 0.0.21 | 2026-04-21 | [76677](https://github.com/airbytehq/airbyte/pull/76677) | Update dependencies |
| 0.0.20 | 2026-03-31 | [75807](https://github.com/airbytehq/airbyte/pull/75807) | Update dependencies |
| 0.0.19 | 2026-03-17 | [74565](https://github.com/airbytehq/airbyte/pull/74565) | Update dependencies |
| 0.0.18 | 2026-02-24 | [73809](https://github.com/airbytehq/airbyte/pull/73809) | Update dependencies |
| 0.0.17 | 2026-02-17 | [73392](https://github.com/airbytehq/airbyte/pull/73392) | Update dependencies |
| 0.0.16 | 2026-02-10 | [73188](https://github.com/airbytehq/airbyte/pull/73188) | Update dependencies |
| 0.0.15 | 2026-01-20 | [72034](https://github.com/airbytehq/airbyte/pull/72034) | Update dependencies |
| 0.0.14 | 2026-01-14 | [71527](https://github.com/airbytehq/airbyte/pull/71527) | Update dependencies |
| 0.0.13 | 2025-12-18 | [70748](https://github.com/airbytehq/airbyte/pull/70748) | Update dependencies |
| 0.0.12 | 2025-11-25 | [70118](https://github.com/airbytehq/airbyte/pull/70118) | Update dependencies |
| 0.0.11 | 2025-11-18 | [69550](https://github.com/airbytehq/airbyte/pull/69550) | Update dependencies |
| 0.0.10 | 2025-10-29 | [69063](https://github.com/airbytehq/airbyte/pull/69063) | Update dependencies |
| 0.0.9 | 2025-10-21 | [68413](https://github.com/airbytehq/airbyte/pull/68413) | Update dependencies |
| 0.0.8 | 2025-10-14 | [67838](https://github.com/airbytehq/airbyte/pull/67838) | Update dependencies |
| 0.0.7 | 2025-10-07 | [67376](https://github.com/airbytehq/airbyte/pull/67376) | Update dependencies |
| 0.0.6 | 2025-09-30 | [66340](https://github.com/airbytehq/airbyte/pull/66340) | Update dependencies |
| 0.0.5 | 2025-09-09 | [65802](https://github.com/airbytehq/airbyte/pull/65802) | Update dependencies |
| 0.0.4 | 2025-08-23 | [65179](https://github.com/airbytehq/airbyte/pull/65179) | Update dependencies |
| 0.0.3 | 2025-08-16 | [64965](https://github.com/airbytehq/airbyte/pull/64965) | Update dependencies |
| 0.0.2 | 2025-08-15 | [64942](https://github.com/airbytehq/airbyte/pull/64942) | Fix docker image entrypoint for platform syncs |
| 0.0.1 | 2025-08-06 | | Initial release by [@santigiova](https://github.com/santigiova) via Connector Builder |

</details>
