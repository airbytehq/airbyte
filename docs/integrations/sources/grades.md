# Grades.com

[Grades.com](https://www.grades.com) is a review management platform: it collects a business's reviews from Google,
Yelp, Facebook, Healthgrades and dozens of other review sites, drafts replies with a review agent, sends review
requests and tracks what AI assistants say about the business (AI Reputation). This connector syncs that data from the
[Grades.com REST API v1](https://app.grades.com/api/documentation) into your warehouse: your businesses, every review
(removed ones included), replies, daily review stats, the review agent's queue, AI Reputation history, review radar
mentions and review requests.

## Prerequisites

- A Grades.com account with at least one business (any plan; some streams need a plan feature, see below).
- A secret API key: in [my.grades.com](https://my.grades.com) > **Connect your AI** > **API keys** > **Create key**,
  with the scopes `reviews:read` and `companies:read`. The key is shown once. A key reaches every business its owner is a
  member of; an agency member's key reaches every client location of the agency. A key can also be limited to some
  businesses when it is created.

## Setup guide

1. Create the API key as described above.
2. In Airbyte, add a new source and pick **Grades.com**.
3. Paste the key into **API Key**.
4. Optional: list the uuids of the businesses to sync in **Businesses** (the `locations` stream shows them). Empty = every
   business the key reaches.
5. Optional: **Start Date** (reviews published on or after it; default: all reviews), **Daily Stats Start Date**
   (default: 90 days ago), **Include Review Text** (default on: the text and title of each review are your own data;
   off drops them from `reviews` and `agent_actions`), **Lookback Window (Days)** (default 30).
6. Click **Set up source**. The connection check reads `GET /api/v1/companies` (needs `companies:read`) and the stats
   of the first business, `GET /api/v1/companies/{uuid}/stats` (needs `reviews:read`), so a key without either scope
   fails the check with the scope to add.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. A Grades.com secret API key (starts with `gk_live_`) with the scopes `reviews:read` and `companies:read`. |  |
| `company_uuids` | `array<string>` | Businesses. The uuids of the businesses to sync. Empty = every business the key reaches. |  |
| `start_date` | `string` | Start Date. Sync reviews published on or after this date (YYYY-MM-DD). | 2005-01-01 |
| `stats_start_date` | `string` | Daily Stats Start Date. First day of the daily stats streams (one request per business and day). | 90 days ago |
| `include_review_text` | `boolean` | Include Review Text. Sync the text and title of each review. | true |
| `lookback_days` | `integer` | Lookback Window (Days). Incremental syncs re-read reviews published this many days before the last sync, so new replies, edits and removals on recent reviews arrive. | 30 |

## Supported sync modes

| Feature | Supported |
|---------|-----------|
| Full Refresh Sync | Yes |
| Incremental Sync | Yes (`reviews`, `review_stats_daily`, `agent_actions`, `ai_reputation_history`, `review_request_stats_daily`) |

## Streams

Every stream except `locations` runs once per business, and every row carries `company_uuid`.

| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental | API |
|-------------|-------------|------------|---------------------|----------------------|-----|
| locations | uuid | Cursor | ✅ | ❌ | `GET /companies` |
| sources | company_uuid.driver | No pagination | ✅ | ❌ | `GET /companies/{uuid}/sources` |
| reviews | uuid | Cursor | ✅ | ✅ (`published_at`) | `GET /companies/{uuid}/reviews` |
| review_replies | review_uuid | Cursor | ✅ | ❌ | `GET /companies/{uuid}/reviews?has_company_response=true` |
| review_stats | company_uuid | No pagination | ✅ | ❌ | `GET /companies/{uuid}/stats` |
| review_stats_daily | company_uuid.date | No pagination | ✅ | ✅ (`date`) | `GET /companies/{uuid}/locations/stats` |
| agent_actions | uuid | Cursor | ✅ | ✅ (`updated_at`, client side) | `GET /companies/{uuid}/agent/actions` |
| ai_reputation_history | company_uuid.run_id.engine | No pagination | ✅ | ✅ (`run_at`) | `GET /companies/{uuid}/radar/ai-perception` |
| ai_reputation_probes | id | No pagination | ✅ | ❌ | `GET /companies/{uuid}/radar/ai-perception` |
| radar_mentions | id | Cursor | ✅ | ❌ | `GET /companies/{uuid}/radar/mentions` |
| review_flags | uuid | Cursor | ✅ | ❌ | `GET /companies/{uuid}/flags` |
| review_requests | id | Cursor | ✅ | ❌ | `GET /companies/{uuid}/review-requests` |
| review_request_contacts | id | Cursor | ✅ | ❌ | `GET /companies/{uuid}/review-requests/contacts` |
| review_request_campaigns | id | No pagination | ✅ | ❌ | `GET /companies/{uuid}/review-requests/campaigns` |
| review_request_opt_outs | company_uuid.id | Cursor | ✅ | ❌ | `GET /companies/{uuid}/review-requests/opt-outs` |
| review_request_stats_daily | company_uuid.date | No pagination | ✅ | ✅ (`date`) | `GET /companies/{uuid}/review-requests/stats` |

Notes:

- `reviews` includes reviews removed from their review site (`removed_at` set): Grades.com keeps them in its archive.
  The API filters on the publish date only, so incremental syncs re-read the last `lookback_days` days of reviews to
  pick up replies, edits and removals; changes to older reviews arrive with a full refresh.
- `review_stats` is a snapshot (the current totals); sync it in append mode to keep a history.
- `review_stats_daily` reads the group view of an HQ, so an HQ returns a row per location. A location that belongs to an
  HQ is skipped on its own and arrives with its HQ when the key reaches the HQ with access to all locations. Days follow
  the HQ's timezone.
- `ai_reputation_history` returns at most the newest 100 checks per assistant on the first sync.
- Streams whose data the business's plan does not include (for example AI Reputation on a claimed listing, review
  requests below Premium) or that need a role the key's owner lacks (review requests need an admin) skip that business
  instead of failing the sync.

## Limitations and rate limits

The API allows 120 requests per minute per key. The connector budgets 110 requests per minute and, on a `429`, waits for
the `Retry-After` header before retrying; `5xx` answers are retried with exponential backoff. The daily stats streams
make one request per business and day, so a first sync over a long `stats_start_date` takes longer for accounts with many
locations. Before the per-day requests they send one request per business for today: a key without `reviews:read` fails
the stream on that request instead of on every day, and a business the endpoint skips (plan, role, location under an HQ)
is not asked day by day.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
|---------|------|--------------|---------|
| 0.1.0 | 2026-11-10 | [TBD](https://github.com/airbytehq/airbyte/pulls) | Initial release: 16 streams (businesses, reviews, replies, stats, review agent, AI Reputation, review radar, review requests) |

</details>
