# Privatus Analytics

Your website numbers sit in one tool. Your sales, sign-ups and ad costs sit in others. So it is hard to tell which pages and which links bring in real customers.

[Privatus Analytics](https://privatusanalytics.com) is website analytics that counts visitors without cookies. This source copies its numbers into your warehouse every day: your sites, visitors and pageviews per day, top pages, the sites that sent you visitors, goals and events.

With all of it in one place, you can put traffic next to revenue, build your own charts, and keep your history for as long as you like.

## Prerequisites

- A Privatus Analytics account with at least one site.
- An API token for the workspace you want to copy.

## Setup guide

### Step 1: Make an API token

1. Sign in at [privatusanalytics.com](https://privatusanalytics.com).
2. Open **Workspace settings**, then **API tokens**.
3. Make a new token and copy it. It starts with `pat_`.

A token reads one workspace. To copy two workspaces, set up two sources.

### Step 2: Set up the source in Airbyte

1. In Airbyte, click **Sources**, then **New source**, and pick **Privatus Analytics**.
2. Paste the token into **API token**.
3. Set **Start date** to the first day you want to copy, for example `2026-01-01`.
4. To copy only some sites, add their IDs to **Site IDs**. A site ID looks like `pa_AB12CD34EF`. Leave it empty to copy every site.
5. Click **Set up source**.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_token` | `string` | API token. Open Workspace settings, then API tokens, and make a new token. It starts with pat_. |  |
| `start_date` | `string` | Start date. The first day to copy, in the form YYYY-MM-DD. Days are counted in each site's own time zone. |  |
| `site_ids` | `array` | Site IDs. Only copy these sites. Leave it empty to copy every site in the workspace. |  |
| `lookback_days` | `integer` | Days to read again. How many recent days each sync reads again, so today's numbers stay right as the day goes on. | 2 |

## Streams

| Stream Name | Primary Key | Cursor | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|--------|------------|---------------------|----------------------|
| workspaces | id | | DefaultPaginator | ✅ | ❌ |
| sites | id | | DefaultPaginator | ✅ | ❌ |
| goals | id | | DefaultPaginator | ✅ | ❌ |
| daily_stats | site_id.date | date | No pagination | ✅ | ✅ |
| pages | site_id.date.value | date | DefaultPaginator | ✅ | ✅ |
| referrers | site_id.date.value | date | DefaultPaginator | ✅ | ✅ |
| goal_conversions | site_id.date.goal_id | date | DefaultPaginator | ✅ | ✅ |
| events | site_id.date.value | date | DefaultPaginator | ✅ | ✅ |

- **daily_stats** has one row per site per day: visitors, visits, pageviews, views per visit, bounce rate, visit length and revenue.
- **pages**, **referrers**, **goal_conversions** and **events** have one row per site, per day, per page (or referrer, goal, event). `value` holds the page path, the referring domain, the goal name or the event name. An empty referrer means a direct visit.
- **goals** lists the goals set up on each site.

Every row from a site has `site_id`, so all tables join on it. Days follow the time zone set on each site. Durations are in milliseconds.

Use **Incremental | Append + Deduped** for the daily streams. Each sync reads the last few days again (see `lookback_days`), and the primary key replaces the old rows with the new ones.

## Performance considerations

The daily streams make one request per site per day, and one more for every 1,000 rows. A large site can have tens of thousands of pages a day. The API allows a set number of requests per hour, based on your plan. When the limit is reached, the source waits for the time the API gives in its `Retry-After` header and goes on. A long start date on many sites can take a few hours the first time. After that, each sync only reads the last few days.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2026-10-26 | [PR_NUMBER](https://github.com/airbytehq/airbyte/pull/PR_NUMBER) | Initial release |

</details>
