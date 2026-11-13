# Ayrshare

[Ayrshare](https://www.ayrshare.com) is a social media API for posting to and reading from Facebook, Instagram, TikTok, YouTube, LinkedIn, Threads, Bluesky, Pinterest and other networks on behalf of many users. This connector syncs an Ayrshare account's User Profiles, the posts and comments on each profile's linked networks, and account- and post-level analytics.

## Prerequisites

- An Ayrshare account with API access. The account streams use User Profiles, which need the **Business** plan.
- The **API key** from the Ayrshare dashboard (**API Key** page).
- Optional, for the profile streams: the **Profile Key** of each User Profile to read. Ayrshare returns a Profile Key only in the response to `POST /profiles`, when the profile is created; `GET /profiles` never includes it. On plans that show it, the dashboard also lists it. Save the keys when your application creates profiles.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API key of the Primary Profile, sent as a Bearer token. | |
| `profile_keys` | `string` | Comma-separated Profile Keys of the User Profiles whose posts, analytics and comments to read. Leave empty to sync only the account streams. | |
| `platforms` | `array` | Networks to read per profile. A network a profile hasn't linked is skipped. | facebook, instagram, tiktok, youtube, linkedin, threads, bluesky, pinterest |

X/Twitter isn't in the default list: since March 2026 Ayrshare needs your own X API credentials in request headers for it, which this connector doesn't send.

## Streams

| Stream Name | Endpoint | Primary Key | Pagination | Needs Profile Keys | Supports Full Sync | Supports Incremental |
|-------------|----------|-------------|------------|--------------------|--------------------|----------------------|
| account | `GET /user` | refId | No pagination | | ✅ | ❌ |
| profiles | `GET /profiles` | refId | Cursor | | ✅ | ❌ |
| profile_health | `GET /profiles?refId=…&include=…` per profile | refId | No pagination | | ✅ | ❌ |
| profile_action_log | `GET /profiles?actionLog=365` | refId, action, created | No pagination | | ✅ | ❌ |
| profile_counts_daily | `GET /profiles?actionLog=365` | reported | No pagination | | ✅ | ❌ |
| profile_users | `GET /user/batch` (signed file) | refId | No pagination | | ✅ | ❌ |
| post_history | `GET /history` per profile | id | No pagination (1,000 posts per profile) | ✅ | ✅ | ❌ |
| platform_posts | `GET /history/{platform}` per profile and network | ref_id, platform, id | Cursor | ✅ | ✅ | ❌ |
| social_analytics | `POST /analytics/social` per profile and network | ref_id, platform | No pagination | ✅ | ✅ | ❌ |
| social_analytics_daily | `POST /analytics/social` (`daily`, last quarter) | ref_id, platform | No pagination | ✅ | ✅ | ❌ |
| post_analytics | `POST /analytics/post` per `post_history` post | post_id | No pagination | ✅ | ✅ | ❌ |
| comments | `GET /comments/{id}` per `post_history` post | post_id | No pagination | ✅ | ✅ | ❌ |
| platform_comments | `GET /comments/{id}?searchPlatformId=true` per recent `platform_posts` post | platform, commentId | No pagination | ✅ | ✅ | ❌ |

Profile streams carry `ref_id`, the profile's `refId`, so rows join to `profiles`. Profile Keys are never written to a record.

### Stream notes

- **post_history**, **post_analytics** and **comments** cover posts sent through Ayrshare. **platform_posts** and **platform_comments** cover every post on the linked networks, including ones published natively.
- **platform_posts** keeps the whole post in `raw`, because each network returns a different shape. Within one sync, YouTube's uploads playlist can list a video twice; dedupe on `ref_id, platform, id`.
- **platform_comments** returns one row per top-level comment, with replies nested in `replies`, for posts created in the last 90 days that have comments. YouTube reports no comment count, so every recent video is checked. Videos with comments turned off are skipped. `commenter_name` and `commenter_id` normalise each network's fields (Facebook `from.name`/`from.id`, Instagram `from.username`/`from.id`, TikTok `username`/`userId`, YouTube `userName`/`channelUrl`). The originals stay in `raw`.
- **social_analytics** and **platform_comments** are snapshots: sync them as **Full Refresh | Append** to keep history. **platform_posts** in append mode also keeps posts that a later sync can't reach (see below).
- **social_analytics_daily** only requests the networks with daily analytics (Facebook, Google Business Profile, Instagram, Snapchat, TikTok, YouTube).
- **profile_users** reads Ayrshare's batch file. The file at the signed URL is empty for about 40 seconds after the request, so the connector waits for it (up to about 4 minutes). Ayrshare creates at most one new batch file every 3 minutes.

### Error handling

- 401/403 fail the sync as a configuration error (bad API key or Profile Key, or an endpoint your plan doesn't include).
- 429 and 5xx are retried, honouring `Retry-After`, then with exponential backoff.
- Networks a profile hasn't linked (codes 103 and 156) and accounts awaiting Meta identity verification (code 326) are skipped.
- A profile with no posts (code 221) is skipped.
- On `/history/{platform}`, Ayrshare occasionally rejects one of its own paging cursors (404, code 1). The connector stops that profile and network for the sync and logs it, instead of failing. A later sync normally pages through.

## Limitations

- Every profile is asked about every configured network, so each unlinked profile and network pair costs one request per sync.
- Not included: direct messages (Messaging add-on), link analytics (Max Pack), ads (Ads add-on), reviews, and configuration endpoints such as the media library, auto-schedule, feeds and webhooks.

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.1.0 | 2026-11-13 | [PR_NUMBER](https://github.com/airbytehq/airbyte/pull/PR_NUMBER) | New Source: Ayrshare |

</details>
