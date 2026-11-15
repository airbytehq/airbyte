# Zernio

[Zernio](https://zernio.com) is a social media API for publishing to and reading from Facebook, Instagram, TikTok, YouTube, LinkedIn, Pinterest, Threads, Bluesky and other networks, with analytics, an inbox and creator campaigns. This connector syncs a Zernio team's profiles and connected social accounts, the posts on those accounts with post- and account-level analytics, audience demographics, comments, logs and creator campaigns.

## Prerequisites

- A Zernio account with API access.
- An **API key** from the Zernio dashboard (**API Keys** page). One key reads every profile and connected account on the team, so no per-profile keys are needed.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | Zernio API key, sent as a Bearer token. | |
| `start_date` | `string` | Earliest date (`YYYY-MM-DD`) for post analytics, post timelines, follower stats and daily metrics. Zernio only holds what it has synced since each account was connected, so an earlier date costs a few empty requests. | 2025-01-01 |

## Streams

| Stream Name | Endpoint | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|----------|-------------|------------|--------------------|----------------------|
| profiles | `GET /profiles` | _id | No pagination | ✅ | ❌ |
| accounts | `GET /accounts` | _id | Cursor | ✅ | ❌ |
| account_health | `GET /accounts/{id}/health` per account | accountId | No pagination | ✅ | ❌ |
| account_groups | `GET /account-groups` | _id | No pagination | ✅ | ❌ |
| users | `GET /users` | _id | No pagination | ✅ | ❌ |
| usage | `GET /usage-stats` | | No pagination | ✅ | ❌ |
| posts | `GET /posts?source=zernio` | _id | Cursor | ✅ | ❌ |
| external_posts | `GET /posts?source=external` per account | _id | Cursor | ✅ | ❌ |
| post_analytics | `GET /analytics` per account and calendar year | _id | Page | ✅ | ❌ |
| post_timeline | `GET /analytics/post-timeline` per `post_analytics` post | post_id, platform, date | No pagination | ✅ | ❌ |
| follower_stats | `GET /accounts/follower-stats` per account and calendar year | account_id, date | No pagination | ✅ | ❌ |
| daily_metrics | `GET /analytics/daily-metrics` per account and attribution | account_id, attribution, date | No pagination | ✅ | ❌ |
| facebook_page_insights | `GET /analytics/facebook/page-insights` per Facebook account | account_id | No pagination | ✅ | ❌ |
| instagram_account_insights | `GET /analytics/instagram/account-insights` per Instagram account | account_id | No pagination | ✅ | ❌ |
| instagram_follower_history | `GET /analytics/instagram/follower-history` per Instagram account | account_id | No pagination | ✅ | ❌ |
| instagram_daily_totals | `GET /analytics/instagram/account-insights` (totals) per Instagram account and day | account_id, day | No pagination | ✅ | ❌ |
| tiktok_account_insights | `GET /analytics/tiktok/account-insights` per TikTok account | account_id | No pagination | ✅ | ❌ |
| youtube_channel_insights | `GET /analytics/youtube/channel-insights` per YouTube account | account_id | No pagination | ✅ | ❌ |
| audience_demographics | `GET /analytics/{platform}/demographics` per account | account_id | No pagination | ✅ | ❌ |
| commented_posts | `GET /inbox/comments` per account | accountId, id | Cursor | ✅ | ❌ |
| comments | `GET /inbox/comments/{postId}` per post with comments | account_id, post_id, id | Cursor | ✅ | ❌ |
| logs | `GET /logs` per log type | | Offset | ✅ | ✅ |
| creator_campaigns | `GET /creator-campaigns` | id | Offset | ✅ | ❌ |
| creator_campaign_participants | `GET /creator-campaigns/{id}/participants` | id | Offset | ✅ | ❌ |
| creator_campaign_submissions | `GET /creator-campaigns/{id}/submissions` | id | Offset | ✅ | ❌ |

Account-scoped streams carry `account_id`, so rows join to `accounts`.

### Stream notes

- **accounts** includes over-limit profiles and the accounts creators connected to the team's creator campaigns (`includeCreatorAccounts=true`). Team-wide reads leave those accounts out unless a request names them, so every account-scoped stream is read per account.
- **posts** covers posts created through Zernio. **external_posts** covers every post Zernio synced from each connected account, including ones published natively. **post_analytics** has lifetime metrics for both, and **post_timeline** the same metrics day by day.
- **post_analytics** and **follower_stats** are read one calendar year at a time, because the API accepts at most 366 days per request.
- **daily_metrics** reads two attributions: `publish` puts each post's lifetime metrics on its publish day, and `received` puts engagement on the day it arrived.
- The insight streams return the last 89 days (the endpoints' maximum) as one record per account, with `metrics` holding `{name: {total, values: [{date, value}]}}`. Instagram serves only `reach` as a daily series, so **instagram_daily_totals** reads the other account metrics (views, accounts engaged, interactions, profile views and more) as single-day totals for 2, 3 and 4 days ago, allowing for Meta's reporting delay.
- The insight streams, **instagram_daily_totals** and **audience_demographics** are snapshots: sync them as **Full Refresh | Append** to keep history past the API's window, and take the latest `_airbyte_extracted_at` per account, metric and date.
- **audience_demographics** covers Facebook (country and city), Instagram and TikTok (age, gender, country and city) and YouTube (viewer age, gender and country). Accounts with too few followers (about 100) are skipped.
- **comments** has one row per top-level comment, with replies nested in `replies`, for every post whose `commentCount` is above zero.
- **logs** covers the `publishing`, `connections`, `token_refresh`, `workflow_event` and `comment_automation` log types. Zernio keeps 90 days of logs; incremental sync on `created_at` keeps history beyond that. Rows have no ID, and the cursor re-reads its boundary second, so dedupe on the whole row.

### Error handling

- A bad, revoked or expired API key fails the sync as a configuration error.
- 429 and 5xx are retried, honouring `Retry-After`, then with exponential backoff.
- YouTube analytics run on Zernio's own daily Google quota. When it's used up, the API returns 429 with `details.quotaExhausted` until midnight Pacific time. Those requests are skipped instead of retried, so **youtube_channel_insights** and YouTube demographics can be empty for a sync; the next sync fills in the 89-day window.
- Per-account and per-post 400, 401, 403, 404, 409, 412, 422 and 424 responses are skipped: a network that doesn't serve the endpoint, a missing scope, too few followers for demographics, an expired social token or a deleted post. Team-wide lists still fail on any 4xx.

## Limitations

- Zernio only returns data it has synced since each account was connected.
- Account insights are read for Facebook, Instagram, TikTok and YouTube. Posts, analytics and comments from other networks are included in the generic streams.
- Not included: direct messages, ads, API request logs, and derived aggregates such as best posting times, which can be computed from the synced data.

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.1.0 | 2026-11-15 | [PRNUMBER](https://github.com/airbytehq/airbyte/pull/PRNUMBER) | New Source: Zernio |

</details>
