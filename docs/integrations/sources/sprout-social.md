# Sprout Social

[Sprout Social](https://sproutsocial.com) is a social media management platform. This connector syncs a Sprout Social account's customers, connected profiles and account metadata, plus daily profile analytics and post-level analytics for Facebook, Instagram, LinkedIn, X (Twitter), YouTube, TikTok, Pinterest and Threads profiles.

## Prerequisites

- A Sprout Social plan that includes API access.
- An **API token**. In Sprout Social, open **Settings** > **Global Features** > **API** and generate a token. Use a token dedicated to Airbyte.
- The **customer ID** of each Sprout Social customer to sync. Once the token is set up, the `clients` stream lists every customer the token can access, or call `GET https://api.sproutsocial.com/v1/metadata/client` with the token.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_token` | `string` | Sprout Social API token, sent as a Bearer token. | |
| `customer_ids` | `array` | Sprout Social customer IDs to sync. Every stream except `clients` is read once per customer. | |
| `start_date` | `string` | Earliest day for profile and post analytics, as `YYYY-MM-DD`. | |
| `profile_lookback_days` | `integer` | Days of profile analytics re-read on every sync, so late-arriving numbers are updated. Between 1 and 364. | 30 |
| `post_lookback_days` | `integer` | Days of posts re-read on every sync, so lifetime metrics on recent posts stay current. | 365 |
| `profile_ids` | `array` | Optional `customer_profile_id`s to restrict the sync to. Leave empty to sync every profile. | |

## Streams

| Stream Name | Endpoint | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|----------|-------------|------------|--------------------|----------------------|
| clients | `GET /v1/metadata/client` | customer_id | No pagination | ✅ | ❌ |
| customer_profiles | `GET /v1/{customer_id}/metadata/customer` | customer_id, customer_profile_id | No pagination | ✅ | ❌ |
| tags | `GET /v1/{customer_id}/metadata/customer/tags` | customer_id, tag_id | No pagination | ✅ | ❌ |
| groups | `GET /v1/{customer_id}/metadata/customer/groups` | customer_id, group_id | No pagination | ✅ | ❌ |
| users | `GET /v1/{customer_id}/metadata/customer/users` | customer_id, id | No pagination | ✅ | ❌ |
| topics | `GET /v1/{customer_id}/metadata/customer/topics` | customer_id, id | No pagination | ✅ | ❌ |
| teams | `GET /v1/{customer_id}/metadata/customer/teams` | customer_id, id | No pagination | ✅ | ❌ |
| queues | `GET /v1/{customer_id}/metadata/customer/queues` | customer_id, id | No pagination | ✅ | ❌ |
| profile_analytics | `POST /v1/{customer_id}/analytics/profiles` per profile | customer_profile_id, reporting_period_by_day | Page number | ✅ | ✅ |
| post_analytics | `POST /v1/{customer_id}/analytics/posts` per profile | guid | Page number | ✅ | ✅ |

Every record carries an integer `customer_id`, so rows from several customers can be told apart.

Recommended sync modes: **Full Refresh | Overwrite** for the metadata streams, and **Incremental | Append + Deduped** for `profile_analytics` and `post_analytics`.

### Stream notes

- **profile_analytics** has one row per profile per day. The cursor is `reporting_period_by_day`, and state is kept per profile. Requests are sliced into periods of at most 364 days, because Sprout Social rejects longer reporting periods.
- **post_analytics** has one row per post, with the post's fields (`text`, `perma_link`, `from`, `internal` tags, `visual_media`, `hashtags` and others) and its lifetime metrics. The cursor is the post's `created_time`. Because lifetime metrics keep changing after a post is published, each sync re-reads the last `post_lookback_days` days of posts.
- Sprout Social needs an explicit list of metrics for each network. The connector requests the metrics that each network supports. The metric names are flattened into columns, with dots and parentheses replaced: `lifetime.impressions` becomes `lifetime_impressions`, and `reporting_period.by(day)` becomes `reporting_period_by_day`. Breakdown metrics, such as followers by country, stay objects.
- Profiles on networks without a metric list (for example Bluesky) appear in `customer_profiles` but are skipped by the analytics streams.
- `guid` keeps Sprout Social's network prefix, for example `p:12345_67890`.
- On posts, Sprout Social returns `customer_profile_id` as a string. The connector casts it to an integer to match `customer_profiles`.
- Daily profile rows use each network's own reporting time zone. Post timestamps are UTC.

### Error handling

- 429 responses are retried after the `Retry-After` delay, otherwise with exponential backoff.
- 5xx responses are retried 5 times with exponential backoff, and then the sync fails, so a gap in the data is never silent.
- 401 and 403 responses fail the sync. Check that the token is valid and that it can access every configured customer.

## Limitations

- Sprout Social allows 60 requests per minute and 250,000 requests per month for each token. The connector stays under 55 requests per minute and respects the `X-RateLimit-Remaining` header. Each profile costs at least one analytics request per stream and per year of history, so a first sync with a long history across many profiles can take a while.
- Only API token authentication is supported. Sprout Social's OAuth 2.0 client credentials flow isn't.
- Not included: the listening, messages (Smart Inbox), cases and publishing endpoints.

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.1.0 | 2026-11-15 | [93006](https://github.com/airbytehq/airbyte/pull/93006) | New Source: Sprout Social |

</details>
