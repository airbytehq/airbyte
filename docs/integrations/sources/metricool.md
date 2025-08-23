# Metricool
The Metricool connector enables you to extract comprehensive social media analytics data from multiple platforms through Metricool’s unified API. This connector supports data extraction from Facebook, Instagram, TikTok, LinkedIn, Twitter (X), and YouTube, providing detailed insights into your social media performance.

Key Features:
- Multi-Platform Support: Extract data from 6 major social media platforms in a single connector
- Comprehensive Analytics: Access post-level metrics, timeline data, competitor analysis, and content performance
- Flexible Date Range: Configure custom date ranges for data extraction (defaults to 60 days if not specified)
- Multiple Content Types: Supports various content formats including posts, reels, stories, and videos

Supported Data Streams:
- Brand Information: Basic account and profile data
- Content Analytics: Posts, reels, stories, and videos with engagement metrics
- Timeline Data: Historical performance metrics tracked over time
- Competitor Analysis: Available for Facebook and Instagram

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `user_token` | `string` | User Token. User token to authenticate API requests. Find it in the Account Settings menu, API section of your Metricool account. |  |
| `user_id` | `string` | User ID. Account ID |  |
| `blog_ids` | `array` | Blog IDs. Brand IDs |  |
| `start_date` | `string` | Start Date. If not set, defaults to 60 days back. If below &quot;End Date&quot;, defaults to 1 day before &quot;End Date&quot; |  |
| `end_date` | `string` | End Date. If not set, defaults to current datetime. |  |

## Streams
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

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.4 | 2025-08-23 | [65179](https://github.com/airbytehq/airbyte/pull/65179) | Update dependencies |
| 0.0.3 | 2025-08-16 | [64965](https://github.com/airbytehq/airbyte/pull/64965) | Update dependencies |
| 0.0.2 | 2025-08-14 | [64942](https://github.com/airbytehq/airbyte/pull/64942) | Fix docker image entrypoint for platform syncs |
| 0.0.1 | 2025-08-06 | | Initial release by [@santigiova](https://github.com/santigiova) via Connector Builder |

</details>
