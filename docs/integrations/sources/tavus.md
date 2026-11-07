# Tavus

This page contains the setup guide and reference information for the [Tavus](https://www.tavus.io/) source connector. The connector reads your Tavus replicas, videos, conversations, personas, and speeches from the [Tavus API](https://docs.tavus.io/api-reference/overview).

## Prerequisites

- A Tavus account
- A Tavus API key

### Create a Tavus API key

1. Sign in to the [Tavus PAL Maker](https://maker.tavus.io/dev) and select **API Key** in the sidebar.
2. Click **Create New Key**.
3. Enter a name for the key. If you restrict the key to specific IP addresses and use Airbyte Cloud, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to the key's allowed IPs.
4. Click **Create API Key**, then copy the key.

For more information, see [Authentication](https://docs.tavus.io/api-reference/authentication) in the Tavus documentation.

## Set up the Tavus connector

1. In Airbyte, create a new source and select **Tavus**.
2. For **API Key**, enter your Tavus API key.
3. For **Start date**, enter a UTC date and time in the format `YYYY-MM-DDTHH:MM:SSZ`, for example `2024-01-01T00:00:00Z`. This value is required. The connector uses it as the starting value of the `updated_at` cursor for incremental streams.
4. Click **Set up source**.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. Your Tavus API key. You can find this in your Tavus account settings or API dashboard. |  |
| `start_date` | `string` | Start date. UTC date and time in the format `YYYY-MM-DDTHH:MM:SSZ`. |  |

## Streams

| Stream Name | Tavus endpoint | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|----------------|-------------|------------|---------------------|----------------------|
| replicas | `GET /v2/replicas` | replica_id | DefaultPaginator | ✅ |  ✅  |
| videos | `GET /v2/videos` | video_id | DefaultPaginator | ✅ |  ❌  |
| conversations | `GET /v2/conversations` | conversation_id | DefaultPaginator | ✅ |  ✅  |
| personas | `GET /v2/personas` | persona_id | DefaultPaginator | ✅ |  ✅  |
| speeches | `GET /v2/speech` | speech_id | DefaultPaginator | ✅ |  ✅  |

Tavus has renamed some resources in its current documentation. Replicas are now called [faces](https://docs.tavus.io/api-reference/faces/list-faces), and personas are now called [PALs](https://docs.tavus.io/api-reference/pals/list-pals). The connector still uses the original endpoint paths and field names, such as `replica_id` and `persona_id`.

Incremental streams use `updated_at` as the cursor field. The `videos` stream supports only full refresh syncs.

## Limitations and troubleshooting

- **Every sync reads all pages.** The Tavus list endpoints don't support filtering by date, so the connector requests every page of each stream on every sync, including incremental syncs. The connector requests 50 records per page.
- **The `speeches` stream can sync zero records without an error.** If your Tavus plan doesn't include access to speeches, the Tavus API returns HTTP `500` with the message `Need subscription plan`. The connector ignores HTTP `500` responses for this stream, so the sync succeeds but the `speeches` stream is empty. Because the connector ignores all HTTP `500` responses for this stream, a temporary Tavus server error can also cause missing `speeches` records for that sync.
- **Rate limiting.** If Tavus returns HTTP `429`, the connector waits and retries the request.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.54 | 2026-11-04 | [90391](https://github.com/airbytehq/airbyte/pull/90391) | Simplify the `speeches` stream error handler configuration; no behavior change |
| 0.0.53 | 2026-11-03 | [90756](https://github.com/airbytehq/airbyte/pull/90756) | Update dependencies |
| 0.0.52 | 2026-10-27 | [90053](https://github.com/airbytehq/airbyte/pull/90053) | Update dependencies |
| 0.0.51 | 2026-10-20 | [89412](https://github.com/airbytehq/airbyte/pull/89412) | Update dependencies |
| 0.0.50 | 2026-10-13 | [88829](https://github.com/airbytehq/airbyte/pull/88829) | Update dependencies |
| 0.0.49 | 2026-10-06 | [88069](https://github.com/airbytehq/airbyte/pull/88069) | Update dependencies |
| 0.0.48 | 2026-09-29 | [87363](https://github.com/airbytehq/airbyte/pull/87363) | Update dependencies |
| 0.0.47 | 2026-09-22 | [86837](https://github.com/airbytehq/airbyte/pull/86837) | Update dependencies |
| 0.0.46 | 2026-09-15 | [86241](https://github.com/airbytehq/airbyte/pull/86241) | Update dependencies |
| 0.0.45 | 2026-09-08 | [85708](https://github.com/airbytehq/airbyte/pull/85708) | Update dependencies |
| 0.0.44 | 2026-08-18 | [84779](https://github.com/airbytehq/airbyte/pull/84779) | Update dependencies |
| 0.0.43 | 2026-08-11 | [84124](https://github.com/airbytehq/airbyte/pull/84124) | Update dependencies |
| 0.0.42 | 2026-08-04 | [83648](https://github.com/airbytehq/airbyte/pull/83648) | Update dependencies |
| 0.0.41 | 2026-07-28 | [83154](https://github.com/airbytehq/airbyte/pull/83154) | Update dependencies |
| 0.0.40 | 2026-07-21 | [82622](https://github.com/airbytehq/airbyte/pull/82622) | Update dependencies |
| 0.0.39 | 2026-07-14 | [82037](https://github.com/airbytehq/airbyte/pull/82037) | Update dependencies |
| 0.0.38 | 2026-06-30 | [81293](https://github.com/airbytehq/airbyte/pull/81293) | Update dependencies |
| 0.0.37 | 2026-06-23 | [80666](https://github.com/airbytehq/airbyte/pull/80666) | Update dependencies |
| 0.0.36 | 2026-06-16 | [80082](https://github.com/airbytehq/airbyte/pull/80082) | Update dependencies |
| 0.0.35 | 2026-06-09 | [79526](https://github.com/airbytehq/airbyte/pull/79526) | Update dependencies |
| 0.0.34 | 2026-06-02 | [79049](https://github.com/airbytehq/airbyte/pull/79049) | Update dependencies |
| 0.0.33 | 2026-04-28 | [77414](https://github.com/airbytehq/airbyte/pull/77414) | Update dependencies |
| 0.0.32 | 2026-04-21 | [76794](https://github.com/airbytehq/airbyte/pull/76794) | Update dependencies |
| 0.0.31 | 2026-03-31 | [75780](https://github.com/airbytehq/airbyte/pull/75780) | Update dependencies |
| 0.0.30 | 2026-03-17 | [75041](https://github.com/airbytehq/airbyte/pull/75041) | Update dependencies |
| 0.0.29 | 2026-03-10 | [74581](https://github.com/airbytehq/airbyte/pull/74581) | Update dependencies |
| 0.0.28 | 2026-02-24 | [73834](https://github.com/airbytehq/airbyte/pull/73834) | Update dependencies |
| 0.0.27 | 2026-02-10 | [73126](https://github.com/airbytehq/airbyte/pull/73126) | Update dependencies |
| 0.0.26 | 2026-01-20 | [72107](https://github.com/airbytehq/airbyte/pull/72107) | Update dependencies |
| 0.0.25 | 2026-01-14 | [71577](https://github.com/airbytehq/airbyte/pull/71577) | Update dependencies |
| 0.0.24 | 2025-12-18 | [70603](https://github.com/airbytehq/airbyte/pull/70603) | Update dependencies |
| 0.0.23 | 2025-11-25 | [70044](https://github.com/airbytehq/airbyte/pull/70044) | Update dependencies |
| 0.0.22 | 2025-11-18 | [69555](https://github.com/airbytehq/airbyte/pull/69555) | Update dependencies |
| 0.0.21 | 2025-10-29 | [69013](https://github.com/airbytehq/airbyte/pull/69013) | Update dependencies |
| 0.0.20 | 2025-10-21 | [68540](https://github.com/airbytehq/airbyte/pull/68540) | Update dependencies |
| 0.0.19 | 2025-10-14 | [67875](https://github.com/airbytehq/airbyte/pull/67875) | Update dependencies |
| 0.0.18 | 2025-10-07 | [67457](https://github.com/airbytehq/airbyte/pull/67457) | Update dependencies |
| 0.0.17 | 2025-09-30 | [66878](https://github.com/airbytehq/airbyte/pull/66878) | Update dependencies |
| 0.0.16 | 2025-09-23 | [66358](https://github.com/airbytehq/airbyte/pull/66358) | Update dependencies |
| 0.0.15 | 2025-09-09 | [65677](https://github.com/airbytehq/airbyte/pull/65677) | Update dependencies |
| 0.0.14 | 2025-08-24 | [65433](https://github.com/airbytehq/airbyte/pull/65433) | Update dependencies |
| 0.0.13 | 2025-08-10 | [64810](https://github.com/airbytehq/airbyte/pull/64810) | Update dependencies |
| 0.0.12 | 2025-07-26 | [63970](https://github.com/airbytehq/airbyte/pull/63970) | Update dependencies |
| 0.0.11 | 2025-07-19 | [63649](https://github.com/airbytehq/airbyte/pull/63649) | Update dependencies |
| 0.0.10 | 2025-07-12 | [63071](https://github.com/airbytehq/airbyte/pull/63071) | Update dependencies |
| 0.0.9 | 2025-07-05 | [62728](https://github.com/airbytehq/airbyte/pull/62728) | Update dependencies |
| 0.0.8 | 2025-06-28 | [62209](https://github.com/airbytehq/airbyte/pull/62209) | Update dependencies |
| 0.0.7 | 2025-06-14 | [60446](https://github.com/airbytehq/airbyte/pull/60446) | Update dependencies |
| 0.0.6 | 2025-05-10 | [60137](https://github.com/airbytehq/airbyte/pull/60137) | Update dependencies |
| 0.0.5 | 2025-05-04 | [59607](https://github.com/airbytehq/airbyte/pull/59607) | Update dependencies |
| 0.0.4 | 2025-04-27 | [59000](https://github.com/airbytehq/airbyte/pull/59000) | Update dependencies |
| 0.0.3 | 2025-04-19 | [58383](https://github.com/airbytehq/airbyte/pull/58383) | Update dependencies |
| 0.0.2 | 2025-04-12 | [57929](https://github.com/airbytehq/airbyte/pull/57929) | Update dependencies |
| 0.0.1 | 2025-04-05 | [#57022](https://github.com/airbytehq/airbyte/pull/57022) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>
