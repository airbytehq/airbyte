# HypeAuditor

[HypeAuditor](https://hypeauditor.com) is an influencer marketing platform for finding creators, running campaigns with them and measuring the results. This connector syncs HypeAuditor's Campaign Management data: campaigns, the influencers and posts in each one, and the campaign reports (overview, posts, engagement, audience, e-commerce, spendings and influencers). It also syncs the creators in your My Network list.

## Prerequisites

- A HypeAuditor account with API access to Campaign Management. Some reports, such as e-commerce, depend on your plan; campaigns without a report are skipped.
- Your **Auth ID** and **Auth Token**. Find them in HypeAuditor under **Settings** > **API**, or ask [HypeAuditor support](mailto:support@hypeauditor.com) to enable API access.

## Setup guide

1. In Airbyte, create a new source and select **HypeAuditor**.
2. Enter your **Auth ID** and **Auth Token**.
3. Select **Set up source**. The connection check lists your campaigns, so it fails if the credentials are wrong.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `auth_id` | `string` | Your numeric API client ID, sent as the `X-Auth-Id` header. | |
| `auth_token` | `string` | Your API token, sent as the `X-Auth-Token` header. | |

## Streams

All endpoints are under `https://hypeauditor.com/api/v2/campaign-management/campaigns`, except `creators`. Every stream other than `campaigns` and `creators` makes one or more requests per campaign.

| Stream Name | Endpoint | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|----------|-------------|------------|--------------------|----------------------|
| campaigns | `GET /` | campaign_id | Offset (100) | ✅ | ❌ |
| campaign_influencers | `GET /{id}/influencers` | campaign_id, influencer_id | Offset (100) | ✅ | ❌ |
| campaign_posts | `GET /{id}/posts` | campaign_id, post_id | Offset (100) | ✅ | ❌ |
| campaign_posts_recent | `GET /{id}/posts/recent` | campaign_id, post_id | No pagination (30 posts) | ✅ | ❌ |
| campaign_report_posts | `GET /{id}/report/posts` | campaign_id, post_id | Offset by position (50) | ✅ | ❌ |
| campaign_report_overview | `GET /{id}/report/overview` | campaign_id, type | No pagination | ✅ | ❌ |
| campaign_report_engagement | `GET /{id}/report/engagement` | campaign_id, type | No pagination | ✅ | ❌ |
| campaign_report_overview_engagement | `GET /{id}/report/overview-engagement` | campaign_id, date | No pagination | ✅ | ❌ |
| campaign_report_overview_payments | `GET /{id}/report/overview-engagement` | campaign_id, date | No pagination | ✅ | ❌ |
| campaign_report_audience | `GET /{id}/report/audience` | campaign_id | No pagination | ✅ | ❌ |
| campaign_report_ecom | `GET /{id}/report/ecom` | campaign_id | No pagination | ✅ | ❌ |
| campaign_report_spendings | `GET /{id}/report/spendings` | campaign_id | No pagination | ✅ | ❌ |
| campaign_report_influencers | `GET /{id}/report/influencers` | campaign_id, influencer_id | No pagination | ✅ | ❌ |
| creators | `GET https://hypeauditor.com/api/method/auditor.creators/` | creator_id | Cursor | ✅ | ❌ |

Records are synced as the API returns them, plus the key fields in the table. Nested objects such as `basic`, `metrics` and `accounts` are kept whole, so flatten them in your destination.

### Stream notes

- **campaign_posts** keys on the post's `basic.id`. Posts without one are dropped.
- **campaign_report_posts** can return fewer posts than **campaign_posts** for the same campaign, because the report leaves out some posts it can't deliver. If you need every post, fill the gaps from **campaign_posts**: each report metric has a matching field there. For example, the report's `reach` is `metrics.reach_est.value` in **campaign_posts**, not `metrics.reach`.
- **campaign_report_overview** and **campaign_report_engagement** return one row per platform (`type`: `all`, `ig`, `tt`, `yt` and so on).
- **campaign_report_overview_engagement** and **campaign_report_overview_payments** read the `engagementHistory` and `paymentHistory` lists of the same response. In API v1 this report was called `engagement-growth`.
- In posts, `socialType` is HypeAuditor's platform code: 1 is Instagram, 2 is YouTube and 3 is TikTok.
- Every stream is a snapshot of the current state. To keep history, for example a post's metrics over time, sync with **Full Refresh | Append**.

### Error handling

- 401 and 403 fail the sync as a configuration error.
- 429 is retried, honouring `Retry-After`, and 5xx with exponential backoff, up to 6 times.
- On the campaigns list, any other 4xx fails the sync, so a failed request never looks like an empty account.
- On per-campaign endpoints, 400, 402 and 404 skip that campaign. 402 means the report isn't on your plan.
- On `/posts/recent`, a 500 also skips that campaign without retrying: HypeAuditor returns it consistently for slow responses on large campaigns.

### Pagination

Most endpoints page by offset and stop on the first short page. `/report/posts` is different: it pages over positions but can drop posts from a page, so a page of 50 can return 49 rows while the next page still starts at offset 50. The connector advances that stream by the page size and stops only on an empty page, which costs one extra request per campaign.

## Limitations

- There is no incremental sync. The API has no "updated since" filter, so every sync reads every campaign.
- `campaign_posts_recent` returns at most 30 recent posts per campaign. The endpoint has no paging, and its response time grows with the page size until it times out with a server error on campaigns with many posts.
- HypeAuditor's API rate limits apply to your account. A full sync makes roughly 15 requests per campaign when every stream is selected.

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.1.0 | 2026-11-15 | [PR_NUMBER](https://github.com/airbytehq/airbyte/pull/PR_NUMBER) | New Source: HypeAuditor |

</details>
