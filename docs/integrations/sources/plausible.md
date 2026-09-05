# Plausible

The Plausible source connector syncs daily website metrics from [Plausible Analytics](https://plausible.io/) using the [Stats API v1](https://plausible.io/docs/stats-api-v1) `timeseries` endpoint. It works with Plausible Cloud and with self-hosted Plausible instances.

## Prerequisites

- A Plausible account with at least one site. On Plausible Cloud, the Stats API is a [Business plan feature](https://plausible.io/docs/stats-api).
- A Stats API key. To create one, sign in to Plausible, click your account name in the top-right menu, go to **Settings** > **API Keys**, click **New API Key**, and choose the **Stats API** key type. Plausible shows the key only once, so copy it before you leave the page.

## Set up the Plausible source connector

1. Log in to your [Airbyte Cloud](https://cloud.airbyte.com/workspaces) account or your self-managed Airbyte workspace.
2. Click **Sources**, then click **+ New source**.
3. Select **Plausible** from the list of connectors.
4. Fill in the following fields:

   - **Plausible API key**: The Stats API key you created.
   - **Target website domain**: The site you want to sync, exactly as it appears in the `domain` field of your Plausible site settings. Don't include a scheme or a `www.` prefix. For example, use `airbyte.com`, not `https://www.airbyte.com`.
   - **API URL**: Only set this if you self-host Plausible. Enter the full base URL of your instance's Stats API, including the `/api/v1/stats` path and no trailing slash, for example `https://plausible.example.com/api/v1/stats`. The connector appends `/timeseries` to this value. Leave the field empty to use Plausible Cloud at `https://plausible.io/api/v1/stats`.
   - **Data start date**: The earliest date to sync, in `YYYY-MM-DD` format. Defaults to `2019-01-01`.

5. Click **Set up source**.

## Supported sync modes

| Feature           | Supported? |
| :---------------- | :--------- |
| Full Refresh Sync | Yes        |
| Incremental Sync  | No         |

Each sync requests the entire range from your start date through today's date in Coordinated Universal Time, then replaces the data in your destination. Set **Data start date** as late as your use case allows: a longer range means more data transferred on every sync.

## Supported streams

The connector syncs one stream, `stats`, from the [timeseries endpoint](https://plausible.io/docs/stats-api-v1#get-apiv1statstimeseries). Each record is one day of site-wide stats, keyed on `date`, and contains these [metrics](https://plausible.io/docs/stats-api-v1#metrics):

| Field            | Description                                       |
| :--------------- | :------------------------------------------------ |
| `date`           | The day the stats cover, in the site's time zone. |
| `visitors`       | Unique visitors.                                  |
| `visits`         | Visits or sessions.                               |
| `pageviews`      | Pageview events.                                  |
| `bounce_rate`    | Bounce rate percentage.                           |
| `visit_duration` | Visit duration, in seconds.                       |

The connector drops days with no recorded visits, so you may see gaps in the date sequence for low-traffic sites.

Plausible is a privacy-first analytics service, and its Stats API is less granular than analytics APIs such as Google Analytics. You can't read individual pageviews or custom events, and dimensions such as referrer, entry page, and exit page are only available through the API's `breakdown` endpoint, which this connector doesn't sync. Other v1 metrics, including `views_per_visit`, `events`, and `time_on_page`, aren't synced either.

## Performance considerations

Plausible limits Stats API keys to [600 requests per hour](https://plausible.io/docs/stats-api-v1) by default. Each sync of the `stats` stream uses a single request, so the limit is unlikely to affect this connector. Contact Plausible if you need more capacity.

## Limitations

Plausible has released a [Stats API v2](https://plausible.io/docs/stats-api) and marks v1 as legacy. This connector still uses v1. If Plausible retires v1 on your instance, syncs fail until Airbyte updates the connector.

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject        |
|:--------|:-----------| :------------------------------------------------------- | :------------- |
| 0.2.16 | 2026-07-28 | [83200](https://github.com/airbytehq/airbyte/pull/83200) | Remove invalid hostname pattern from `api_url` config field |
| 0.2.15 | 2026-06-02 | [78893](https://github.com/airbytehq/airbyte/pull/78893) | Update dependencies |
| 0.2.14 | 2025-05-24 | [60528](https://github.com/airbytehq/airbyte/pull/60528) | Update dependencies |
| 0.2.13 | 2025-05-10 | [60098](https://github.com/airbytehq/airbyte/pull/60098) | Update dependencies |
| 0.2.12 | 2025-05-03 | [59483](https://github.com/airbytehq/airbyte/pull/59483) | Update dependencies |
| 0.2.11 | 2025-04-27 | [59083](https://github.com/airbytehq/airbyte/pull/59083) | Update dependencies |
| 0.2.10 | 2025-04-19 | [58482](https://github.com/airbytehq/airbyte/pull/58482) | Update dependencies |
| 0.2.9 | 2025-04-12 | [57854](https://github.com/airbytehq/airbyte/pull/57854) | Update dependencies |
| 0.2.8 | 2025-04-05 | [57358](https://github.com/airbytehq/airbyte/pull/57358) | Update dependencies |
| 0.2.7 | 2025-03-29 | [56803](https://github.com/airbytehq/airbyte/pull/56803) | Update dependencies |
| 0.2.6 | 2025-03-22 | [56236](https://github.com/airbytehq/airbyte/pull/56236) | Update dependencies |
| 0.2.5 | 2025-03-08 | [55536](https://github.com/airbytehq/airbyte/pull/55536) | Update dependencies |
| 0.2.4 | 2025-03-01 | [55010](https://github.com/airbytehq/airbyte/pull/55010) | Update dependencies |
| 0.2.3 | 2025-02-23 | [54559](https://github.com/airbytehq/airbyte/pull/54559) | Update dependencies |
| 0.2.2 | 2025-02-15 | [48194](https://github.com/airbytehq/airbyte/pull/48194) | Update dependencies |
| 0.2.1 | 2024-08-16 | [44196](https://github.com/airbytehq/airbyte/pull/44196) | Bump source-declarative-manifest version |
| 0.2.0 | 2024-08-14 | [44085](https://github.com/airbytehq/airbyte/pull/44085) | Refactor connector to manifest-only format |
| 0.1.14 | 2024-08-12 | [43731](https://github.com/airbytehq/airbyte/pull/43731) | Update dependencies |
| 0.1.13 | 2024-08-10 | [43680](https://github.com/airbytehq/airbyte/pull/43680) | Update dependencies |
| 0.1.12 | 2024-08-06 | [43048](https://github.com/airbytehq/airbyte/pull/43048) | new API URL config option available |
| 0.1.11 | 2024-08-03 | [43252](https://github.com/airbytehq/airbyte/pull/43252) | Update dependencies |
| 0.1.10 | 2024-07-27 | [42793](https://github.com/airbytehq/airbyte/pull/42793) | Update dependencies |
| 0.1.9 | 2024-07-20 | [41918](https://github.com/airbytehq/airbyte/pull/41918) | Update dependencies |
| 0.1.8 | 2024-07-10 | [41403](https://github.com/airbytehq/airbyte/pull/41403) | Update dependencies |
| 0.1.7 | 2024-07-09 | [41120](https://github.com/airbytehq/airbyte/pull/41120) | Update dependencies |
| 0.1.6 | 2024-07-06 | [40992](https://github.com/airbytehq/airbyte/pull/40992) | Update dependencies |
| 0.1.5 | 2024-06-25 | [40502](https://github.com/airbytehq/airbyte/pull/40502) | Update dependencies |
| 0.1.4 | 2024-06-22 | [40185](https://github.com/airbytehq/airbyte/pull/40185) | Update dependencies |
| 0.1.3 | 2024-06-04 | [38974](https://github.com/airbytehq/airbyte/pull/38974) | [autopull] Upgrade base image to v1.2.1 |
| 0.1.2 | 2024-05-28 | [38660](https://github.com/airbytehq/airbyte/pull/38660) | Make connector compatible with Builder |
| 0.1.1 | 2024-05-21 | [38494](https://github.com/airbytehq/airbyte/pull/38494) | [autopull] base image + poetry + up_to_date |
| 0.1.0 | 2022-10-30 | [18657](https://github.com/airbytehq/airbyte/pull/18657) | Initial commit |

</details>
